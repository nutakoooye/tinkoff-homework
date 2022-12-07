import os
import time
import requests
import threading

from unittest import TestCase

from server import ServerURL


class TestServerURL(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        d1_neigb = {
            "b": {"host": "localhost", "port": 8082},
            "c": {"host": "localhost", "port": 8083},
        }
        d1 = ServerURL(
            port=8081,
            path="tests/tmp_for_tests/a/",
            neighbors=d1_neigb,
            save_copies=False,
        )

        d2_neigb = {
            "a": {"host": "localhost", "port": 8081},
            "c": {"host": "localhost", "port": 8083},
        }
        d2 = ServerURL(
            port=8082,
            path="tests/tmp_for_tests/b/",
            neighbors=d2_neigb,
            save_copies=True,
        )

        d3_neigb = {
            "a": {"host": "localhost", "port": 8081},
            "b": {"host": "localhost", "port": 8082},
        }
        d3 = ServerURL(
            port=8083,
            path="tests/tmp_for_tests/c/",
            neighbors=d3_neigb,
            save_copies=True,
        )

        thr1 = threading.Thread(target=d1.run, daemon=True)
        thr2 = threading.Thread(target=d2.run, daemon=True)
        thr3 = threading.Thread(target=d3.run, daemon=True)

        thr1.start()
        thr2.start()
        thr3.start()

        time.sleep(1)  # starting daemons

    def setUp(self) -> None:
        self.d1_url = "http://127.0.0.1:8081/"
        self.d2_url = "http://127.0.0.1:8082/"
        self.d3_url = "http://127.0.0.1:8083/"

    def test_get_file_from_daemon(self):
        response = requests.get(self.d1_url + "ax")
        self.assertEqual(response.text, "ax")

    def test_get_file_with_redirect(self):
        response = requests.get(self.d1_url + "bx")
        self.assertEqual(response.text, "bx")

    def test_get_non_exist_file(self):
        response = requests.get(self.d2_url + "fdvsc")
        self.assertEqual(response.text, "<h1>404 - File not found</h1>")

    def test_saving_copies(self):
        num_files_before_saving = len(os.listdir("tests/tmp_for_tests/b/"))
        self.assertEqual(num_files_before_saving, 1)

        res_a = requests.get(self.d2_url + "ax")
        res_c = requests.get(self.d2_url + "cx")

        num_files_after_saving = len(os.listdir("tests/tmp_for_tests/b/"))
        self.assertEqual(num_files_after_saving, 3)

        os.remove("tests/tmp_for_tests/b/ax")
        os.remove("tests/tmp_for_tests/b/cx")

    def test_not_saving_copies(self):
        num_files_before_saving = len(os.listdir("tests/tmp_for_tests/a/"))
        self.assertEqual(num_files_before_saving, 1)

        res_b = requests.get(self.d1_url + "bx")
        res_c = requests.get(self.d1_url + "cx")

        num_files_after_saving = len(os.listdir("tests/tmp_for_tests/a/"))
        self.assertEqual(num_files_before_saving, num_files_after_saving)
