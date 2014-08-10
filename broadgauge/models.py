import web


@web.memoize
def get_db():
    if 'database_url' in web.config:
        return web.database(web.config.database_url)
    else:
        return web.database(**web.config.db_parameters)


class ResultSet:
    """Iterator wrapper over database result.

    Provides utilities like first, list etc.
    """
    def __init__(self, seq, model=web.storage):
        self.model = model
        self.seq = iter(seq)

    def list(self):
        return list(self)

    def __iter__(self):
        return self

    def __next__(self):
        return self.model(next(self.seq))
    next = __next__

    def first(self):
        """Returns the first element from the database result or None.
        """
        try:
            return next(self)
        except StopIteration:
            return None


class Model(web.storage):
    """Base model.
    """
    @classmethod
    def where(cls, **kw):
        result = get_db().where(cls.TABLE, **kw)
        return ResultSet(result, model=cls)

    @classmethod
    def find(cls, **kw):
        """Returns the first item matching the constraints specified as keywords.
        """
        return cls.where(**kw).first()

    @classmethod
    def findall(cls, **kw):
        """Returns the first item matching the constraints specified as keywords.
        """
        return cls.where(**kw).list()


class User(Model):
    TABLE = "users"

    @classmethod
    def new(cls, name, email, phone=None, **kw):
        id = get_db().insert("users", name=name, email=email, phone=phone, **kw)
        return cls.find(id=id)

    def update(self, **kw):
        get_db().update("users", where='id=$id', vars=self, **kw)
        dict.update(self, kw)

    def is_trainer(self):
        return self['is_trainer']

    def is_admin(self):
        return self['is_admin']

class Organization(Model):
    TABLE = "organization"

    @classmethod
    def new(cls, name, city):
        id = get_db().insert("organization", name=name, city=city)
        return cls.find(id=id)

    def add_member(self, user, role):
        get_db().insert("organization_members", user_id=user.id, role=role)

    def get_workshops(self, status=None):
        """Returns list of workshops by this organiazation.
        """
        wheres = {}
        if status:
            wheres['status'] = status
        return Workshop.findall(org_id=self.id, order='date desc', **wheres)

    def add_new_workshop(self, title, description,
                         expected_participants, date):
        return Workshop.new(self, title, description,
                            expected_participants, date)

    def is_admin(self, email):
        """Returns True of given email is an admin of this org.
        """
        if not email:
            return False

        # Admin user is admin of every org
        if web.config.get('admin_user') == email:
            return True

        admin = self.get_admin()
        if admin and admin.email == email:
            return True

        return False

    def is_member(self, user):
        result = get_db().query(
            "SELECT * FROM organization_members" +
            " WHERE org_id=$self.id AND user_id=$user.id",
            vars=locals())
        return bool(result)

    def get_members(self):
        result = get_db().query(
            "SELECT users.*, role FROM users" +
            " JOIN organization_members ON organization_members.user_id=users.id" +
            " WHERE organization_members.org_id=$self.id", vars=locals())

        def make_member(row):
            role = row.pop('role')
            member = User(row)
            return member, role

        return [make_member(row) for row in result]

class Workshop(Model):
    TABLE = "workshop"

    @classmethod
    def new(cls, org, title, description, expected_participants, date):
        id = get_db().insert("workshop",
                             org_id=org.id,
                             title=title,
                             description=description,
                             expected_participants=expected_participants,
                             date=date)
        return cls.find(id=id)

    def get_org(self):
        return Organization.find(id=self.org_id)

    def record_interest(self, trainer):
        """Record that the given trainer has shown interest to conduct
        the this workshop.
        """
        get_db().insert("workshop_trainers", workshop_id=self.id, trainer_id=trainer.id)

    def get_interested_trainers(self):
        db = get_db()
        rows = db.where("workshop_trainers", workshop_id=self.id)
        ids = [row.trainer_id for row in row]
        rows = db.query(
                "SELECT users.*, trainers.*" +
                " FROM users, trainers" +
                " WHERE users.id=trainers.user_id AND trainers.id IN $ids",
                vars={"ids": ids})
        return [Trainer(row) for row in rows]
