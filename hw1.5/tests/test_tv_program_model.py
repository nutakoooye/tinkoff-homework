import unittest
from tv_program_model import TVProgram


class TVProgramTestCase(unittest.TestCase):
    def test_init_valid_data(self):
        data = {
            "name": "Family Guy",
            "network": {"name": "FOX", "country": {"name": "US"}},
            "summary": "<p><Some summary/p>",
        }
        tv_program = TVProgram(**data)
        self.assertEqual(tv_program.name, "Family Guy")
        self.assertEqual(tv_program.network.name, "FOX")
        self.assertEqual(tv_program.network.country.name, "Us")
        self.assertEqual(tv_program.summary, "<p><Some summary/p>")

    def test_init_invalid_name(self):
        data = {
            "name": "",
            "network": {"name": "FOX", "country": {"name": "US"}},
            "summary": "<p><Some summary/p>",
        }
        with self.assertRaises(ValueError):
            TVProgram(**data)

    def test_init_invalid_network_name(self):
        data = {
            "name": "Family Guy",
            "network": {"name": "", "country": {"name": "US"}},
            "summary": "<p><Some summary/p>",
        }
        with self.assertRaises(ValueError):
            TVProgram(**data)

    def test_init_invalid_network_country_name(self):
        data = {
            "name": "Family Guy",
            "network": {"name": "FOX", "country": {"name": ""}},
            "summary": "<p><Some summary/p>",
        }
        with self.assertRaises(ValueError):
            TVProgram(**data)

    def test_init_invalid_summary(self):
        data = {
            "name": "Family Guy",
            "network": {"name": "FOX", "country": {"name": "US"}},
            "summary": "",
        }
        with self.assertRaises(ValueError):
            TVProgram(**data)

    def test_init_invalid_network(self):
        data = {
            "name": "Family Guy",
            "network": None,
            "summary": "<p><Some summary/p>",
        }
        with self.assertRaises(ValueError):
            TVProgram(**data)

    def test_init_invalid_network_country(self):
        data = {
            "name": "Family Guy",
            "network": {"name": "FOX", "country": None},
            "summary": "<p><Some summary/p>",
        }
        with self.assertRaises(ValueError):
            TVProgram(**data)
