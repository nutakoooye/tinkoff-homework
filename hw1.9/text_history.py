from typing import Optional
from actions import Action, InsertAction, ReplaceAction, DeleteAction


class TextHistory:
    def __init__(self, text: str = ''):
        self._text = text
        self._version = 0
        self._actions: list[Action] = []

    @property
    def text(self):
        return self._text

    @property
    def version(self):
        return self._version

    def __validate_pos(self, pos: Optional[int]) -> int:
        if pos is None:
            pos = len(self.text)
        if pos < 0 or pos > len(self.text):
            raise ValueError
        return pos

    def insert(self, text: str, pos: Optional[int] = None) -> int:
        pos = self.__validate_pos(pos)

        action = InsertAction(pos, text, self.version, self.version + 1)
        return self.action(action)

    def replace(self, text: str, pos: Optional[int] = None) -> int:
        pos = self.__validate_pos(pos)

        action = ReplaceAction(pos, text, self.version, self.version + 1)
        return self.action(action)

    def delete(self, pos: int, length: int):
        pos = self.__validate_pos(pos)

        action = DeleteAction(pos, length, self.version, self.version + 1)
        return self.action(action)

    def action(self, action: Action):
        if action.from_version != self.version:
            raise ValueError
        if action.from_version > action.to_version:
            raise ValueError

        self._text = action.apply(self.text)
        self._version = action.to_version
        self._actions.append(action)

        return self.version

    def __unite_actions(self, num: int, action: Action):
        self._actions[num] = action
        del self._actions[num + 1]

    @staticmethod
    def __double_insert(
        act1: InsertAction, act2: InsertAction
    ) -> Optional[InsertAction]:

        old_v, new_v = act1.from_version, act2.to_version
        if act1.pos == act2.pos:
            text = act2.text + act1.text
            act = InsertAction(act1.pos, text, old_v, new_v)
            return act
        if act1.pos + len(act1.text) == act2.pos:
            text = act1.text + act2.text
            act = InsertAction(act1.pos, text, old_v, new_v)
            return act

        return None

    @staticmethod
    def __double_delete(
        act1: DeleteAction, act2: DeleteAction
    ) -> Optional[DeleteAction]:

        if (
            act1.pos <= act2.pos + act2.length
            and act2.pos <= act1.length + act1.pos
        ):
            pos = min(act1.pos, act2.pos)
            length = act1.length + act2.length
            old_v, new_v = act1.from_version, act2.to_version
            act = DeleteAction(pos, length, old_v, new_v)
            return act

        return None

    @staticmethod
    def __double_replace(
        act1: ReplaceAction, act2: ReplaceAction
    ) -> Optional[ReplaceAction]:

        old_v, new_v = act1.from_version, act2.to_version
        if act1.pos == act2.pos + len(act2.text):
            text = act2.text + act1.text
            act = ReplaceAction(act2.pos, text, old_v, new_v)
            return act
        if act1.pos + len(act1.text) == act2.pos:
            text = act1.text + act2.text
            act = ReplaceAction(act1.pos, text, old_v, new_v)
            return act

        return None

    @staticmethod
    def __del_and_ins_eq_repl(
        act1: DeleteAction, act2: InsertAction
    ) -> Optional[ReplaceAction]:

        if act1.pos == act2.pos and act1.length == len(act2.text):
            old_v, new_v = act1.from_version, act2.to_version
            act = ReplaceAction(act1.pos, act2.text, old_v, new_v)
            return act

        return None

    def _compare_two_actions(self, num: int) -> bool:
        action1 = self._actions[num]
        action2 = self._actions[num + 1]
        is_united = False

        match action1, action2:
            case InsertAction() as act1, InsertAction() as act2:
                ins_act = self.__double_insert(act1, act2)
                if ins_act:
                    self.__unite_actions(num, ins_act)
                    is_united = True
            case DeleteAction() as act1, DeleteAction() as act2:
                del_act = self.__double_delete(act1, act2)
                if del_act:
                    self.__unite_actions(num, del_act)
                    is_united = True
            case ReplaceAction() as act1, ReplaceAction() as act2:
                repl_act = self.__double_replace(act1, act2)
                if repl_act:
                    self.__unite_actions(num, repl_act)
                    is_united = True
            case DeleteAction() as act1, InsertAction() as act2:
                repl_act = self.__del_and_ins_eq_repl(act1, act2)
                if repl_act:
                    self.__unite_actions(num, repl_act)
                    is_united = True

        return is_united

    def optimize_actions(self):
        num = 0
        while num < len(self._actions) - 1:
            is_united = self._compare_two_actions(num)
            if not is_united:
                num += 1

    def _version_validator(
        self, from_version: Optional[int], to_version: Optional[int]
    ) -> tuple[int, int]:
        if from_version is None:
            from_version = 0
        if to_version is None:
            to_version = self.version

        if to_version < from_version:
            raise ValueError
        if to_version > self.version:
            raise ValueError
        if from_version < 0:
            raise ValueError
        return from_version, to_version

    def get_actions(
        self,
        start: Optional[int] = None,
        stop: Optional[int] = None,
        optimize: bool = False,
    ) -> list[Action]:

        if optimize:
            self.optimize_actions()

        from_version, to_version = self._version_validator(start, stop)

        actions = [
            action
            for action in self._actions
            if from_version < action.to_version <= to_version
        ]

        return actions