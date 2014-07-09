import unittest
import web
from ..models import User, Trainer, get_db
import os

class DBTestCase(unittest.TestCase):
    def setUp(self):
        # clear the memoize cache
        get_db.cache.clear()
        web.config.db_parameters = dict(dbn='sqlite', db=":memory:")        
        self.load_schema()

    def load_schema(self):
        db = get_db()
        sql = self.read_schema()
        # what is called seial in postgres is called integer in sqlite
        sql = sql.replace("serial", "integer")

        # sqlite can execute only one statement in a query
        for part in sql.split(";"):
            db.query(part)

    def read_schema(self):
        dirname = os.path.dirname
        root = dirname(dirname(__file__))
        return open(os.path.join(root, "schema.sql")).read()

class UserTest(DBTestCase):
    def test_new(self):
        name, email, phone = 'User 1', 'user1@example.com', '1234567890'
        u = User.new(name=name, email=email, phone=phone)
        self.assertEquals(u.name, name)
        self.assertEquals(u.email, email)
        self.assertEquals(u.phone, phone)
        self.assertNotEquals(u.id, None)

    def test_find(self):
        name, email, phone = 'User 1', 'user1@example.com', '1234567890'
        u = User.new(name=name, email=email, phone=phone)
        self.assertEquals(User.find(id=u.id), u)

    def test_update(self):
        name, email, phone = 'User 1', 'user1@example.com', '1234567890'
        u = User.new(name=name, email=email, phone=phone)
        u.update(name='User 2')
        self.assertEquals(u.name, 'User 2')
        self.assertEquals(User.find(id=u.id).name, 'User 2')

class TrainerTest(DBTestCase):
    def test_new(self):
        name, email, phone = 'User 1', 'user1@example.com', '1234567890'
        city = 'Bangalore'
        u = Trainer.new(name=name, email=email, phone=phone, city=city)
        self.assertEquals(u.name, name)
        self.assertEquals(u.email, email)
        self.assertEquals(u.phone, phone)
        self.assertEquals(u.city, city)
        self.assertNotEquals(u.id, None)

    def test_find(self):
        name, email, phone = 'User 1', 'user1@example.com', '1234567890'
        city = 'Bangalore'

        u = Trainer.new(name=name, email=email, phone=phone, city=city)
        self.assertEquals(Trainer.find(id=u.id), u)
        self.assertTrue(isinstance(Trainer.find(id=u.id), Trainer))

    def test_update(self):
        name, email, phone = 'User 1', 'user1@example.com', '1234567890'
        city = 'Bangalore'
        u = Trainer.new(name=name, email=email, phone=phone, city=city)
        u.update(name='User 2', city='Pune')
        self.assertEquals(u.name, 'User 2')
        self.assertEquals(u.city, 'Pune')

        u2 = Trainer.find(id=u.id)
        self.assertEquals(u, u2)

if __name__ == '__main__':
    unittest.main()