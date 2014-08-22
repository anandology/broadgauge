import web
import string
import random
import json
import datetime

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

    @classmethod
    def new(cls, **kw):
        id = get_db().insert(cls.TABLE, **kw)
        return cls.find(id=id)

    def __hash__(self):
        return self.id

    def dict(self):
        d = {}
        rules = {
            datetime.datetime: datetime.datetime.isoformat,
            datetime.date: datetime.date.isoformat
        }
        for k, v in self.items():
            if k.startswith("_"):
                continue
            for cls, converter in rules.items():
                if isinstance(v, cls):
                    v = converter(v)
                    break
            d[k] = v
        return d


class User(Model):
    TABLE = "users"

    @classmethod
    def new(cls, name, email, phone=None, **kw):
        if 'username' not in kw:
            kw['username'] = cls._suggest_username(email)

        id = get_db().insert("users", name=name, email=email, phone=phone, **kw)
        return cls.find(id=id)

    @staticmethod
    def _suggest_username(email):
        """suggests a username based on email.
        """
        basename = email.split("@")[0]
        username = basename
        for i in range(1, 100):
            if not User.find(username=username):
                return username
            username = "{}-{}".format(basename, i)

        # select a random prefix it above attempt fails
        suffix = "".join(random.choice(string.lowercase) for i in range(4))
        return "{}-{}".format(basename, suffix)

    def update(self, **kw):
        get_db().update("users", where='id=$id', vars=self, **kw)
        dict.update(self, kw)

    def make_trainer(self):
        self.update(is_trainer=True)

    def is_trainer(self):
        return self['is_trainer']

    def is_admin(self):
        return self['is_admin']

    @classmethod
    def find_all_org_members(cls):
        result = get_db().query(
            "SELECT distinct(users.*) FROM users" +
            " JOIN organization_members on user_id=users.id")
        return [cls(row) for row in result]

class Organization(Model):
    TABLE = "organization"

    @classmethod
    def new(cls, name, city):
        id = get_db().insert("organization", name=name, city=city)
        return cls.find(id=id)

    def add_member(self, user, role):
        get_db().insert("organization_members", org_id=self.id, user_id=user.id, role=role)

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

    def can_update(self, user):
        if not user:
            return False
        else:
            return user.is_admin() or self.is_member(user)

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

    def update(self, **kw):
        get_db().update("workshop", where='id=$id', vars=self, **kw)
        dict.update(self, kw)

    def get_trainer(self):
        return self.trainer_id and User.find(id=self.trainer_id)

    def set_trainer(self, trainer):
        self.update(trainer_id=trainer.id, status='confirmed')

    def get_org(self):
        return Organization.find(id=self.org_id)

    def record_interest(self, trainer):
        """Record that the given trainer has shown interest to conduct
        the this workshop.
        """
        get_db().insert("workshop_trainers", workshop_id=self.id, trainer_id=trainer.id)

    def cancel_interest(self, trainer):
        """Record that the given trainer has shown interest to conduct
        the this workshop.
        """
        get_db().delete("workshop_trainers",
            where="workshop_id=$self.id AND trainer_id=$trainer.id",
            vars=locals())

    def get_interested_trainers(self):
        db = get_db()
        rows = db.where("workshop_trainers", workshop_id=self.id)
        ids = [row.trainer_id for row in rows]
        if ids:
            rows = db.query("SELECT * FROM users WHERE id IN $ids", vars={"ids": ids})
            return [User(row) for row in rows]
        else:
            return []

    def is_interested_trainer(self, user):
        rows = get_db().where("workshop_trainers",
            workshop_id=self.id,
            trainer_id=user.id).list()
        return bool(rows)

    def get_comments(self):
        return Comment.findall(workshop_id=self.id, order='created')

    def add_comment(self, user, comment):
        return Comment.new(
            workshop_id=self.id,
            author_id=user.id,
            comment=comment)

    def get_followers(self):
        followers = set()
        # add org members
        followers.update(m for m, role in self.get_org().get_members())

        # add trainers
        if self.status == 'pending':
            followers.update(self.get_interested_trainers())
        elif self.status == 'confirmed':
            followers.add(self.get_trainer)

        # add commenters
        followers.update(c.get_author() for c in self.get_comments())
        print followers
        return list(followers)

    def dict(self):
        d = dict(self)
        d['date'] = self.date and self.date.isoformat()
        return d

class Comment(Model):
    TABLE = "comment"

    def get_author(self):
        return User.find(id=self.author_id)

    def get_workshop(self):
        return Workshop.find(id=self.author_id)

class Activity(Model):
    TABLE = "activity"

    @classmethod
    def get_recent_activity(cls, limit=50, offset=0):
        return cls.findall(limit=limit, offset=offset, order='tstamp desc')

    @classmethod
    def new(cls, type, user, info):
        id = get_db().insert("activity",
            type=type,
            user_id=user and user.id,
            user_name=user and user.name,
            info=json.dumps(info))
        return Activity.find(id=id)
