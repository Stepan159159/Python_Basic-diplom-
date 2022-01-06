import sqlite3
import datetime
from typing import Iterable
import functools

class Db:
    def __init__(self, db: str) -> None:
        self.database = sqlite3.connect(db, check_same_thread=False)
        self.database.text_factory = str
        self.cursor = self.database.cursor()
        if len(self.cursor.execute("select * from sqlite_master where type = "
                                   "'table';").fetchall()) == 0:
            self.cursor.execute("CREATE TABLE history("
                           "chat_id TEXT,"
                           "command TEXT,"
                           "date TEXT,"
                           "hotels TEXT);")
            self.database.commit()

    def read(self, chat_id) -> Iterable :
        self.cursor.execute(f"SELECT * FROM history WHERE chat_id = {chat_id}")
        return self.cursor.fetchall()

    def save(self, data: list) -> None:
        data = data[:-1]
        data.append(functools.reduce(lambda x, y: x + y, data[-1]))
        self.cursor.execute("insert into history ('chat_id', 'command', 'date',"
                            " 'hotels') values (\'{0}\', \'{1}\', \'{2}\', \'{3}\');"
                            .format(*data))
        self.database.commit()


class Log:
    def __init__(self, chat_id: str, command: str, db: str) -> None:
        self.__chat_id = chat_id
        self.__command = command
        self.__db = Db(db)
        date = datetime.datetime.now()
        self.__date = date.strftime("%d %B %Y %H:%M:%S")
        del date
        self.__hotels = ""

    def set_hotels(self, hotels: str) -> None:
        self.__hotels = hotels

    def save_for_bd(self) -> None:
        if self.__hotels != "":
            data = [self.__chat_id, self.__command, self.__date, self.__hotels]
            self.__db.save(data)

    def read(self, chat_id):
        return self.__db.read(chat_id)
