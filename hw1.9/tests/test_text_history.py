from unittest import TestCase

from text_history import TextHistory, InsertAction, ReplaceAction, DeleteAction
from actions import InsertAction, ReplaceAction, DeleteAction


class TextHistoryTestCase(TestCase):
    def test_text__trivial(self):
        h = TextHistory()

        self.assertEqual('', h.text)
        with self.assertRaises(AttributeError):
            h.text = 'NEW'

    def test_version__trivial(self):
        h = TextHistory()

        self.assertEqual(0, h.version)
        with self.assertRaises(AttributeError):
            h.version = 42

    def test_action(self):
        h = TextHistory()
        action = InsertAction(pos=0, text='abc', from_version=0, to_version=10)

        self.assertEqual(10, h.action(action))
        self.assertEqual('abc', h.text)
        self.assertEqual(10, h.version)

    def test_action__bad(self):
        h = TextHistory()
        action = InsertAction(
            pos=0, text='abc', from_version=10, to_version=10
        )

        with self.assertRaises(ValueError):
            h.action(action)

    def test_insert(self):
        h = TextHistory()

        self.assertEqual(1, h.insert('abc'))
        self.assertEqual('abc', h.text)
        self.assertEqual(1, h.version)

        self.assertEqual(2, h.insert('xyz', pos=2))
        self.assertEqual('abxyzc', h.text)
        self.assertEqual(2, h.version)

        self.assertEqual(3, h.insert('END'))
        self.assertEqual('abxyzcEND', h.text)
        self.assertEqual(3, h.version)

        self.assertEqual(4, h.insert('BEGIN', pos=0))
        self.assertEqual('BEGINabxyzcEND', h.text)
        self.assertEqual(4, h.version)

    def test_insert__bad(self):
        h = TextHistory()
        self.assertEqual(1, h.insert('abc'))

        with self.assertRaises(ValueError):
            h.insert('abc', pos=10)

        with self.assertRaises(ValueError):
            h.insert('abc', pos=-1)

    def test_replace(self):
        h = TextHistory()

        self.assertEqual(1, h.replace('abc'))
        self.assertEqual('abc', h.text)
        self.assertEqual(1, h.version)

        self.assertEqual(2, h.replace('xyz', pos=2))
        self.assertEqual('abxyz', h.text)
        self.assertEqual(2, h.version)

        self.assertEqual(3, h.replace('X', pos=2))
        self.assertEqual('abXyz', h.text)
        self.assertEqual(3, h.version)

        self.assertEqual(4, h.replace('END'))
        self.assertEqual('abXyzEND', h.text)
        self.assertEqual(4, h.version)

    def test_replace__bad(self):
        h = TextHistory()
        self.assertEqual(1, h.insert('abc'))

        with self.assertRaises(ValueError):
            h.replace('abc', pos=10)

        with self.assertRaises(ValueError):
            h.replace('abc', pos=-1)

    def test_delete(self):
        h = TextHistory()
        self.assertEqual(1, h.insert('abc xyz'))

        self.assertEqual(2, h.delete(pos=1, length=2))
        self.assertEqual('a xyz', h.text)
        self.assertEqual(2, h.version)

        self.assertEqual(3, h.delete(pos=3, length=0))
        self.assertEqual('a xyz', h.text)
        self.assertEqual(3, h.version)

    def test_delete__bad(self):
        h = TextHistory()
        self.assertEqual(1, h.insert('abc'))

        with self.assertRaises(ValueError):
            h.delete(pos=10, length=2)

        with self.assertRaises(ValueError):
            h.delete(pos=1, length=3)

        with self.assertRaises(ValueError):
            h.delete(pos=-1, length=2)

    def test_get_actions(self):
        h = TextHistory()
        h.insert('a')
        h.insert('bc')
        h.replace('B', pos=1)
        h.delete(pos=0, length=1)
        self.assertEqual('Bc', h.text)

        actions = h.get_actions(1)

        self.assertEqual(3, len(actions))
        insert, replace, delete = actions
        self.assertIsInstance(insert, InsertAction)
        self.assertIsInstance(replace, ReplaceAction)
        self.assertIsInstance(delete, DeleteAction)

        # insert
        self.assertEqual(1, insert.from_version)
        self.assertEqual(2, insert.to_version)
        self.assertEqual('bc', insert.text)
        self.assertEqual(1, insert.pos)

        # replace
        self.assertEqual(2, replace.from_version)
        self.assertEqual(3, replace.to_version)
        self.assertEqual('B', replace.text)
        self.assertEqual(1, replace.pos)

        # delete
        self.assertEqual(3, delete.from_version)
        self.assertEqual(4, delete.to_version)
        self.assertEqual(0, delete.pos)
        self.assertEqual(1, delete.length)

    def test_get_actions__bad(self):
        h = TextHistory()
        h.insert('a')
        h.insert('b')
        h.insert('c')

        with self.assertRaises(ValueError):
            h.get_actions(0, 10)
        with self.assertRaises(ValueError):
            h.get_actions(10, 10)
        with self.assertRaises(ValueError):
            h.get_actions(2, 1)
        with self.assertRaises(ValueError):
            h.get_actions(-1, 1)

    def test_get_actions__empty(self):
        h = TextHistory()
        self.assertEqual([], h.get_actions())

        h.insert('a')
        self.assertEqual([], h.get_actions(0, 0))


class TextHistoryOptimizeTestCase(TestCase):
    def test_optimize_two_insert(self):
        h = TextHistory()
        h.insert('af')
        h.insert('bc', 2)
        actions = h.get_actions(optimize=True)
        self.assertEqual(len(actions), 1)
        ins_act = InsertAction(0, "afbc", 0, 2)
        self.assertEqual(actions[0].__dict__, ins_act.__dict__)

    def test_optimize_two_insert_reversed(self):
        h = TextHistory()
        h.insert('af')
        h.insert('bc', 0)
        actions = h.get_actions(optimize=True)
        self.assertEqual(len(actions), 1)
        ins_act = InsertAction(0, "bcaf", 0, 2)
        self.assertEqual(actions[0].__dict__, ins_act.__dict__)

    def test_optimize_two_delete(self):
        h = TextHistory("qwerty")
        h.delete(0, 3)
        h.delete(0, 3)
        actions = h.get_actions(optimize=True)
        self.assertEqual(len(actions), 1)
        del_act = DeleteAction(0, 6, 0, 2)
        self.assertEqual(actions[0].__dict__, del_act.__dict__)

    def test_optimize_two_delete_reversed(self):
        h = TextHistory("qwerty")
        h.delete(3, 3)
        h.delete(0, 3)
        actions = h.get_actions(optimize=True)
        self.assertEqual(len(actions), 1)
        del_act = DeleteAction(0, 6, 0, 2)
        self.assertEqual(actions[0].__dict__, del_act.__dict__)

    def test_optimize_two_delete_nested(self):
        h = TextHistory("qwerty")
        h.delete(2, 2)
        h.delete(0, 4)
        actions = h.get_actions(optimize=True)
        self.assertEqual(len(actions), 1)
        del_act = DeleteAction(0, 6, 0, 2)
        self.assertEqual(actions[0].__dict__, del_act.__dict__)

    def test_optimize_two_replace(self):
        h = TextHistory("qwerty")
        h.replace("AAA", 0)
        h.replace("BBB", 3)
        actions = h.get_actions(optimize=True)
        self.assertEqual(len(actions), 1)
        repl_act = ReplaceAction(0, "AAABBB", 0, 2)
        self.assertEqual(actions[0].__dict__, repl_act.__dict__)

    def test_optimize_two_replace_reversed(self):
        h = TextHistory("qwerty")
        h.replace("AAA", 3)
        h.replace("BBB", 0)
        actions = h.get_actions(optimize=True)
        self.assertEqual(len(actions), 1)
        repl_act = ReplaceAction(0, "BBBAAA", 0, 2)
        self.assertEqual(actions[0].__dict__, repl_act.__dict__)

    def test_del_and_ins_eq_repl(self):
        h = TextHistory("qwerty")
        h.delete(3, 3)
        h.insert("CCC", 3)

        actions = h.get_actions(optimize=True)
        self.assertEqual(len(actions), 1)
        repl_act = ReplaceAction(3, "CCC", 0, 2)
        self.assertEqual(actions[0].__dict__, repl_act.__dict__)

    def test_optimize_in_get_actions(self):
        h = TextHistory("ABCDEFGHIJKLMNOPQRSTUVWXWZ")
        h.delete(0, 3)
        h.delete(0, 3)
        h.insert("sixsix", 0)
        h.insert("we", 6)
        h.replace("111", 18)
        h.replace("222", 15)
        optimizing_actions = h.get_actions(optimize=True)
        self.assertEqual(len(optimizing_actions), 3)
        all_actions = h.get_actions()
        self.assertEqual(len(all_actions), 6)
