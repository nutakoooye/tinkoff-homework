import socket
import pickle
from parsers.request_parser import RequestParser
from parsers.args_parser import parse_args
from pathlib import Path
from collections import defaultdict
from task_queue import TaskQueue

PACKAGE_LEN = 10000
STORAGE_FILENAME = "state.pkl"


class TaskQueueServer:
    def __init__(self, ipx: str, port: int, path: str, timeout: int):
        self.ipx = ipx
        self.port = port
        self.path = path
        self.timeout = timeout
        self.queues: defaultdict = defaultdict(TaskQueue)
        self.extract_state()

    def save_state(self) -> str:
        if Path(self.path).is_file():
            state_path = Path(self.path)
            dir_path = state_path.parent
        else:
            state_path = Path(self.path, STORAGE_FILENAME)
            dir_path = Path(self.path)
        dir_path.mkdir(parents=True, exist_ok=True)

        with open(state_path, "wb") as f:
            pickle.dump(self.queues, f)
        return "OK"

    def extract_state(self):
        if Path(self.path).is_file():
            state_path = Path(self.path)
        else:
            state_path = Path(self.path, STORAGE_FILENAME)

        if state_path.exists():
            with open(state_path, "rb") as f:
                self.queues = pickle.load(f)

    def get_task(self, r_queue):
        try:
            idx, task = r_queue.get(self.timeout)
            return f"{idx} {task.length} {task.data}"
        except ValueError:
            return "NONE"

    @staticmethod
    def ack_task(idx, r_queue):
        try:
            r_queue.ack(idx)
            return "YES"
        except KeyError:
            return "NO"

    @staticmethod
    def in_task(idx, r_queue):
        if r_queue.check_in(idx):
            return "YES"
        return "NO"

    def generate_answer(self, data: str) -> str:
        try:
            request = RequestParser(data)
        except ValueError:
            return "ERROR"

        r_queue = self.queues[request.queue_name]
        if request.type_r == "ADD":
            return r_queue.add(request.length, request.data)
        if request.type_r == "GET":
            return self.get_task(r_queue)
        if request.type_r == "ACK":
            return self.ack_task(request.idx, r_queue)
        if request.type_r == "IN":
            self.in_task(request.idx, r_queue)
        if request.type_r == "SAVE":
            return self.save_state()
        return "unexpected behavior"

    def run(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((self.ipx, self.port))
        sock.listen(10)
        while True:
            conn, addr = sock.accept()
            data = self.receive_data(conn)
            answer = self.generate_answer(data)
            self.send_data(conn, answer)
            conn.close()

    def receive_data(self, conn) -> str:
        data = conn.recv(PACKAGE_LEN)
        type_r, *_ = data.decode().split()
        if type_r == "ADD":
            data = self.receive_long_data(conn, data)
        return data.decode()

    @staticmethod
    def receive_long_data(conn, data: bytes) -> bytes:
        """receive big data

        data -- first received package

        Normal recv cannot be received at once
        1000000 bytes, so we break it into packers

        """
        type_r, queue_n, len_data, _ = data.decode().split(maxsplit=3)
        expected_len = len(type_r) + len(queue_n) + int(len_data) + 2
        received_len = PACKAGE_LEN
        while received_len <= expected_len:
            data += conn.recv(PACKAGE_LEN)
            received_len += PACKAGE_LEN
        return data

    @staticmethod
    def send_data(conn, data: str):
        try:
            conn.sendall(data.encode())
        except ConnectionError:
            print("Client suddenly closed, cannot send")


if __name__ == "__main__":
    args = parse_args()
    server = TaskQueueServer(**args.__dict__)
    server.run()
