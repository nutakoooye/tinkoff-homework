from unittest import TestCase
from pathlib import Path
import unittest
import time
import socket
import subprocess
import shutil

PACKAGE_LEN = 10000


class ServerBaseTest(TestCase):
    def setUp(self):
        self.server = subprocess.Popen(["python3", "server.py", "-p", "6666"])
        time.sleep(0.5)

    def tearDown(self):
        self.server.terminate()
        self.server.wait()

    def send(self, command):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(("127.0.0.1", 6666))
        s.send(command)
        data = self.receive(s, command)
        # data = s.recv(1000000)
        s.close()
        return data

    @staticmethod
    def receive(conn, command: bytes):
        """receive big data

        Normal recv cannot be received at once
        1000000 bytes, so we break it into packers

        """
        data = conn.recv(PACKAGE_LEN)
        if command.decode().startswith("GET") and data.decode() != "NONE":
            idx, task_length, task = data.decode().split(maxsplit=2)
            expected_len = len(idx) + len(task_length) + int(task_length) + 2
            received_len = PACKAGE_LEN
            while received_len <= expected_len + PACKAGE_LEN:
                data += conn.recv(PACKAGE_LEN)
                received_len += PACKAGE_LEN
        return data

    def server_restart(
        self,
        ipx: str = "0.0.0.0",
        port: str = "6666",
        path: str = "./",
        timeout: int = 300,
    ):
        self.server.terminate()
        self.server.wait()
        self.server = subprocess.Popen(
            [
                "python3",
                "server.py",
                "-p",
                port,
                "-i",
                ipx,
                "-c",
                path,
                "-t",
                str(timeout),
            ]
        )
        time.sleep(0.5)

    def test_long_long_input(self):
        data = "1234567890" * 100000
        data = "{} {}".format(len(data), data)
        data = data.encode("utf")
        task_id = self.send(b"ADD 1 " + data)
        self.assertEqual(b"YES", self.send(b"IN 1 " + task_id))
        self.assertEqual(task_id + b" " + data, self.send(b"GET 1"))

    def test_two_queues(self):
        first_task_id = self.send(b"ADD 1 11 first task")
        second_task_id = self.send(b"ADD 2 12 second task")

        self.assertEqual(b"YES", self.send(b"IN 1 " + first_task_id))
        self.assertEqual(b"YES", self.send(b"IN 2 " + second_task_id))
        self.assertEqual(b"NO", self.send(b"IN 2 " + first_task_id))
        self.assertEqual(b"NO", self.send(b"IN 1 " + second_task_id))

    def test_save_data_after_restart(self):
        self.server_restart(path="./storage/ab")
        first_task_id = self.send(b"ADD 1 11 first task")
        second_task_id = self.send(b"ADD 2 12 second task")

        self.assertEqual(b"YES", self.send(b"IN 1 " + first_task_id))
        self.assertEqual(b"YES", self.send(b"IN 2 " + second_task_id))
        self.assertEqual(b"OK", self.send(b"SAVE"))

        self.server_restart(path="./storage/ab/state.pkl")
        self.assertEqual(b"YES", self.send(b"IN 1 " + first_task_id))
        self.assertEqual(b"YES", self.send(b"IN 2 " + second_task_id))
        self.assertEqual(b"OK", self.send(b"SAVE"))

        self.server_restart(path="./storage/ba")
        self.assertEqual(b"NO", self.send(b"IN 1 " + first_task_id))
        self.assertEqual(b"NO", self.send(b"IN 2 " + second_task_id))
        temp_dir = Path("./storage")
        shutil.rmtree(temp_dir)

    def test_returning_task_in_queue_after_timeout(self):
        self.server_restart(timeout=1)
        first_task_id = self.send(b"ADD 1 11 first task")
        second_task_id = self.send(b"ADD 1 12 second task")

        self.assertEqual(
            first_task_id + b" 11 first task", self.send(b"GET 1")
        )
        self.assertEqual(
            second_task_id + b" 12 second task", self.send(b"GET 1")
        )

        time.sleep(1)

        self.assertEqual(
            first_task_id + b" 11 first task", self.send(b"GET 1")
        )
        self.assertEqual(
            second_task_id + b" 12 second task", self.send(b"GET 1")
        )


if __name__ == "__main__":
    unittest.main()
