from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("-at_install", "post_install")
class TestBadword(TransactionCase):
    def test_badword_validate_norecords_false(self):
        self.env["tournaments.badword"].validate_name(False)

    def test_badword_validate_norecords_empty(self):
        self.env["tournaments.badword"].validate_name("")

    def test_badword_validate_onerecord_test(self):
        badword_obj = self.env["tournaments.badword"]
        badword_obj.create([{"word": "test"}])
        with self.assertRaises(ValidationError):
            badword_obj.validate_name("test")

    def test_badword_validate_onerecord_test_complex(self):
        badword_obj = self.env["tournaments.badword"]
        badword_obj.create([{"word": "test"}])
        with self.assertRaises(ValidationError):
            badword_obj.validate_name("another test")
        with self.assertRaises(ValidationError):
            badword_obj.validate_name("another test")
        with self.assertRaises(ValidationError):
            badword_obj.validate_name("anothertest")

    def test_badword_validate_tworecord_test_complex(self):
        badword_obj = self.env["tournaments.badword"]
        badword_obj.create([{"word": "test1"}, {"word": "test2"}])

        badword_obj.validate_name("test")
        badword_obj.validate_name("another test")
        badword_obj.validate_name("anothertest")
        with self.assertRaises(ValidationError):
            badword_obj.validate_name("test1")
        with self.assertRaises(ValidationError):
            badword_obj.validate_name("anothertest1")
        with self.assertRaises(ValidationError):
            badword_obj.validate_name("test2")
        with self.assertRaises(ValidationError):
            badword_obj.validate_name("anothertest2")
        with self.assertRaises(ValidationError):
            badword_obj.validate_name("test1test2")
        with self.assertRaises(ValidationError):
            badword_obj.validate_name("test1 test2")
        with self.assertRaises(ValidationError):
            badword_obj.validate_name("another test1 test2")
