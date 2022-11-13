import sqlite3

DB_NAME = 'sqlite.db'
TABLE_NAME = 'favorites'


class FavoritesDB:
    def __init__(self, db_name=DB_NAME):
        self.db_name = db_name
        self.table_name = TABLE_NAME
        self.__sqlite_connection = self.__get_connection(db_name)
        self.create_table()

    def create_table(self):
        cursor = self.__sqlite_connection.cursor()
        sqlite_query = f'''CREATE TABLE IF NOT EXISTS {self.table_name} (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            program_name TEXT NOT NULL,
                            user_id INTEGER NOT NULL);'''
        cursor.execute(sqlite_query)
        self.__sqlite_connection.commit()
        cursor.close()

    def add_program(self, program_name: str, user_id: int):
        if self.get_program(program_name, user_id):
            return

        cursor = self.__sqlite_connection.cursor()
        insert_query = f"""INSERT INTO {self.table_name}
                       (program_name, user_id)
                       VALUES ('{program_name}', {user_id});"""
        cursor.execute(insert_query)
        self.__sqlite_connection.commit()
        cursor.close()

    def get_program(self, program_name: str, user_id: int):
        cursor = self.__sqlite_connection.cursor()
        select_query = f"""SELECT * FROM {self.table_name}
                           WHERE program_name='{program_name}'
                           AND user_id={user_id};"""
        cursor.execute(select_query)
        record = cursor.fetchone()
        return record

    def get_favorites(self, user_id: int) -> list:
        cursor = self.__sqlite_connection.cursor()
        select_query = f"""SELECT id, program_name FROM {self.table_name}
                        WHERE user_id={user_id};"""
        cursor.execute(select_query)
        records = cursor.fetchall()
        return records

    def del_program(self, program_id: int):
        cursor = self.__sqlite_connection.cursor()
        select_query = f"""DELETE FROM {self.table_name}
                           WHERE id={program_id};"""
        cursor.execute(select_query)
        self.__sqlite_connection.commit()

    @staticmethod
    def __get_connection(db_name):
        try:
            connection = sqlite3.connect(db_name)
            return connection
        except sqlite3.Error as error:
            print("Ошибка при подключении к sqlite", error)

    def __del__(self):
        if self.__sqlite_connection:
            self.__sqlite_connection.close()
