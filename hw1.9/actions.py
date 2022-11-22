from abc import ABC, abstractmethod


class Action(ABC):
    def __init__(self, pos: int, from_version: int, to_version: int):
        self.pos = pos
        self.from_version = from_version
        self.to_version = to_version
        self.validate_versions()

    def validate_versions(self):
        if self.to_version < self.from_version:
            raise ValueError
        if self.from_version < 0:
            raise ValueError
        if not isinstance(self.to_version, int):
            raise ValueError
        if not isinstance(self.from_version, int):
            raise ValueError

    @abstractmethod
    def apply(self, old_text: str) -> str:
        pass


class InsertAction(Action):
    def __init__(
        self, pos: int, text: str, from_version: int, to_version: int
    ):
        self.text = text
        super().__init__(pos, from_version, to_version)

    def apply(self, old_text: str) -> str:
        return old_text[: self.pos] + self.text + old_text[self.pos :]


class ReplaceAction(Action):
    def __init__(
        self, pos: int, text: str, from_version: int, to_version: int
    ):
        self.text = text
        super().__init__(pos, from_version, to_version)

    def apply(self, old_text: str) -> str:
        end_pos = len(self.text) + self.pos
        return old_text[: self.pos] + self.text + old_text[end_pos:]


class DeleteAction(Action):
    def __init__(
        self, pos: int, length: int, from_version: int, to_version: int
    ):
        self.length = length
        super().__init__(pos, from_version, to_version)

    def apply(self, old_text: str) -> str:
        if self.length + self.pos > len(old_text):
            raise ValueError

        return old_text[: self.pos] + old_text[self.pos + self.length :]
