import datetime
import peewee


db = peewee.SqliteDatabase('people.db')


class Person(peewee.Model):
    user_id = peewee.CharField()
    command = peewee.CharField()
    date = peewee.DateTimeField()
    hotels = peewee.CharField()

    class Meta:
        database = db


class Users:
    users = dict()

    def __init__(self, user_id, command, mode) -> None:
        self.start = datetime.datetime.now()
        self.city = None
        self.check_in = None
        self.check_out = None
        self.hotels_count = None
        self.load_image = False
        self.load_image_count = None
        self.price_min = 0
        self.price_max = 999999999
        self.command = command
        self.mode = mode
        self.hotels = None
        self.user_id = user_id
        Users.add_user(user_id, self)

    @staticmethod
    def get_user(user_id) -> 'Users':
        if Users.users.get(user_id) is None:
            new_user = Users(user_id, None, None)
            return new_user
        return Users.users.get(user_id)

    @classmethod
    def add_user(cls, user_id, user) -> None:
        cls.users[user_id] = user

    def save(self) -> None:
        with db:
            Person.create_table()
            usr = Person(user_id=self.user_id, command=self.command,
                         date=self.start, hotels=
                         f"{[A['name'] for A in self.hotels[:self.hotels_count]]}")

    @staticmethod
    def read(user_id) -> list:
        with db:
            lst = []
            for elem in Person.select().where(Person.user_id == user_id):
                try:
                    q = eval(elem.hotels)
                    z = q if q != [] else ["Ничего не нашлось"]
                except Exception:
                    pass
                lst += [elem.command, elem.date] + z + ["="*50]
            return lst
