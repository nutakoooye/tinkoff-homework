import os
from unittest import TestCase
from database_tools import FavoritesDB
import sqlite3


class TestFavoritesDB(TestCase):
    def setUp(self) -> None:
        self.connection = sqlite3.connect("sqlite.db")
        self.cursor = self.connection.cursor()
        self.favorites_db = FavoritesDB("sqlite.db")

    def tearDown(self) -> None:
        self.cursor.close()
        self.connection.close()

    @classmethod
    def tearDownClass(cls) -> None:
        os.remove("sqlite.db")

    def clear_table(self):
        self.cursor.execute("DELETE FROM favorites;")
        self.connection.commit()

    def rebuild_database(self):
        # rebuilding the database to get the correct keys
        self.tearDown()
        self.tearDownClass()
        self.setUp()

    def test_create_database(self):
        self.favorites_db.create_table()
        self.cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table';"
        )
        tables = self.cursor.fetchall()
        self.assertEqual(len(tables), 2)
        self.assertEqual(tables[0][0], "favorites")

    def test_add_program(self):
        self.favorites_db.add_program("Name", 10)
        self.cursor.execute("SELECT program_name, user_id FROM favorites;")
        rows = self.cursor.fetchall()
        self.assertEqual(len(rows), 1)
        self.assertEqual(
            rows[0],
            (
                "Name",
                10,
            ),
        )

        self.clear_table()

    def test_add_two_identical(self):
        self.favorites_db.add_program("Name", 10)
        self.favorites_db.add_program("Name", 10)
        self.cursor.execute("SELECT program_name, user_id FROM favorites;")
        rows = self.cursor.fetchall()

        self.assertEqual(len(rows), 1)
        self.assertEqual(
            rows[0],
            (
                "Name",
                10,
            ),
        )

        self.clear_table()

    def test_get_program(self):
        self.rebuild_database()

        self.favorites_db.add_program("Name1", 1)
        self.favorites_db.add_program("Name2", 2)
        record = self.favorites_db.get_program("Name1", 1)
        expected_record = (1, "Name1", 1)
        self.assertEqual(record, expected_record)

        self.clear_table()

    def test_del_program(self):
        self.rebuild_database()

        self.favorites_db.add_program("Name1", 1)
        self.cursor.execute("SELECT * FROM favorites;")
        num_rows = len(self.cursor.fetchall())
        self.assertEqual(num_rows, 1)

        self.favorites_db.del_program(1)
        self.cursor.execute("SELECT * FROM favorites;")
        num_rows = len(self.cursor.fetchall())
        self.assertEqual(num_rows, 0)
