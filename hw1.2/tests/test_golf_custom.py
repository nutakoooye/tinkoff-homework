from unittest import TestCase

from golf import HitsMatch, HolesMatch, Player


class HitsMatchTestCase(TestCase):
    def several_hit(self, match, num_hit, success=False):
        for _ in range(num_hit):
            match.hit(success)

    def test_one_player(self):
        players = [Player('Bob'), ]
        match = HitsMatch(1, players)
        match.hit()
        self.assertFalse(match.finished)
        self.assertEqual(match.get_table(), [
            ('Bob',),
            (None,),
        ])
        with self.assertRaises(RuntimeError):
            match.get_winners()
        self.several_hit(match, 8)
        self.assertTrue(match.finished)
        with self.assertRaises(RuntimeError):
            match.hit()
        self.assertEqual(match.get_winners(), players)

    def test_equal_scores(self):
        players = [Player('A'), Player('B'), Player('C'), Player('D')]
        match = HitsMatch(4, players)
        match.hit(True)
        match.hit()
        match.hit(True)
        match.hit()
        self.assertEqual(match.get_table(), [
            ('A', 'B', 'C', 'D'),
            (1, None, 1, None),
            (None, None, None, None),
            (None, None, None, None),
            (None, None, None, None),
        ])
        self.several_hit(match, 16)
        self.assertFalse(match.finished)
        self.assertEqual(match.get_table(), [
            ('A', 'B', 'C', 'D'),
            (1, 10, 1, 10),
            (None, None, None, None),
            (None, None, None, None),
            (None, None, None, None),
        ])
        self.several_hit(match, 20)
        self.several_hit(match,4,True)
        self.assertEqual(match.get_table(), [
            ('A', 'B', 'C', 'D'),
            (1, 10, 1, 10),
            (6, 6, 6, 6),
            (None, None, None, None),
            (None, None, None, None),
        ])
        match.hit()
        match.hit(True)
        match.hit()
        match.hit(True)
        self.assertEqual(match.get_table(), [
            ('A', 'B', 'C', 'D'),
            (1, 10, 1, 10),
            (6, 6, 6, 6),
            (None, 1, None, 1),
            (None, None, None, None),
        ])
        self.several_hit(match, 52)
        self.assertTrue(match.finished)
        self.assertEqual(match.get_table(), [
            ('A', 'B', 'C', 'D'),
            (1, 10, 1, 10),
            (6, 6, 6, 6),
            (10, 1, 10, 1),
            (10, 10, 10, 10),
        ])
        with self.assertRaises(RuntimeError):
            match.hit()
        self.assertEqual(match.get_winners(), players)

    def test_all_hit(self):
        players = [Player('A'), Player('B'), Player('C'), Player('D')]
        match = HitsMatch(4, players)
        self.several_hit(match, 16, True)
        self.assertTrue(match.finished)
        self.assertEqual(match.get_table(),[
            ('A', 'B', 'C', 'D'),
            (1, 1, 1, 1),
            (1, 1, 1, 1),
            (1, 1, 1, 1),
            (1, 1, 1, 1),
        ])

        with self.assertRaises(RuntimeError):
            match.hit()

        self.assertEqual(match.get_winners(), players)

    def test_all_miss(self):
        players = [Player('A'), Player('B'), Player('C'), Player('D')]
        match = HitsMatch(4, players)
        with self.assertRaises(RuntimeError):
            match.get_winners()
        self.several_hit(match, 144)
        self.assertEqual(match.finished, True)
        self.assertEqual(match.get_table(), [
            ('A', 'B', 'C', 'D'),
            (10, 10, 10, 10),
            (10, 10, 10, 10),
            (10, 10, 10, 10),
            (10, 10, 10, 10),
        ])
        self.assertEqual(match.get_winners(), players)


class HolesMatchTestCase(TestCase):
    def several_hit(self, match, num_hit, success=False):
        for _ in range(num_hit):
            match.hit(success)

    def test_one_player(self):
        players = [Player('Bob'), ]
        match = HolesMatch(1, players)
        match.hit()
        self.assertFalse(match.finished)
        self.assertEqual(match.get_table(), [
            ('Bob',),
            (None,),
        ])
        with self.assertRaises(RuntimeError):
            match.get_winners()
        self.several_hit(match, 9)
        self.assertEqual(match.get_table(), [
            ('Bob',),
            (0,),
        ])
        self.assertTrue(match.finished)
        self.assertEqual(match.get_winners(), players)

    def test_equal_scores(self):
        players = [Player('A'), Player('B'), Player('C'), Player('D')]
        match = HolesMatch(4, players)
        self.several_hit(match,2)
        self.several_hit(match,2, True)
        self.assertEqual(match.get_table(), [
            ('A', 'B', 'C', 'D'),
            (0, 0, 1, 1),
            (None, None, None, None),
            (None, None, None, None),
            (None, None, None, None),
        ])
        match.hit(True)
        self.several_hit(match, 2)
        match.hit(True)
        self.assertEqual(match.get_table(), [
            ('A', 'B', 'C', 'D'),
            (0, 0, 1, 1),
            (1, 1, 0, 0),
            (None, None, None, None),
            (None, None, None, None),
        ])
        self.several_hit(match, 80)
        self.assertTrue(match.finished)
        self.assertEqual(match.get_table(), [
            ('A', 'B', 'C', 'D'),
            (0, 0, 1, 1),
            (1, 1, 0, 0),
            (0, 0, 0, 0),
            (0, 0, 0, 0),
        ])
        with self.assertRaises(RuntimeError):
            match.hit()
        self.assertEqual(match.get_winners(), players)

    def test_all_hit(self):
        players = [Player('A'), Player('B'), Player('C'), Player('D')]
        match = HolesMatch(4, players)
        self.several_hit(match, 16, True)
        self.assertTrue(match.finished)
        self.assertEqual(match.get_table(),[
            ('A', 'B', 'C', 'D'),
            (1, 1, 1, 1),
            (1, 1, 1, 1),
            (1, 1, 1, 1),
            (1, 1, 1, 1),
        ])

        with self.assertRaises(RuntimeError):
            match.hit()

        self.assertEqual(match.get_winners(), players)

    def test_all_miss(self):
        players = [Player('A'), Player('B'), Player('C'), Player('D')]
        match = HolesMatch(4, players)
        with self.assertRaises(RuntimeError):
            match.get_winners()
        self.several_hit(match, 160)
        self.assertEqual(match.finished, True)
        self.assertEqual(match.get_table(), [
            ('A', 'B', 'C', 'D'),
            (0, 0, 0, 0),
            (0, 0, 0, 0),
            (0, 0, 0, 0),
            (0, 0, 0, 0),
        ])
        self.assertEqual(match.get_winners(), players)