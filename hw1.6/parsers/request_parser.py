from typing import Optional
from pydantic import BaseModel, validator


class RequestParser(BaseModel):
    type_r: str
    queue_name: Optional[str] = None
    idx: Optional[str] = None
    length: Optional[int] = None
    data: Optional[str] = None

    def __init__(self, request_str: str):
        request_list = request_str.split(maxsplit=3)
        data = self.init_data_dict(request_list)
        super().__init__(**data)

    @staticmethod
    def init_data_dict(request_list: list):
        data = {"type_r": request_list[0]}
        if data["type_r"] == "ADD":
            data["queue_name"] = request_list[1]
            data["length"] = request_list[2]
            data["data"] = request_list[3]
        if data["type_r"] == "GET":
            data["queue_name"] = request_list[1]
        if data["type_r"] in ("ACK", "IN"):
            data["queue_name"] = request_list[1]
            data["idx"] = request_list[2]
        return data

    @validator('type_r')
    def not_allowed_request(cls, v):
        allowed_requests = ("ADD", "GET", "ACK", "IN", "SAVE")
        if v not in allowed_requests:
            raise ValueError(
                'request type should be ADD, GET, ACK, IN, or SAVE '
            )
        return v

    @validator('queue_name')
    def too_long_queue_name(cls, v):
        if len(v) > 1000:
            raise ValueError('Queue name length must be less than 1000')
        return v

    @validator('length')
    def data_length(cls, v):
        if v > 10**6:
            raise ValueError('task must have length less than 10^6')
        return v

    @validator('idx')
    def check_id_len(cls, v):
        if len(v) >= 128:
            raise ValueError('idx must have length less or equal 128')
        return v
