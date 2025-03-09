from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("-at_install", "post_install")
class TestPlayer(TransactionCase):
    def test_player_create_normal_no_user(self):
        player_obj = self.env["tournaments.player"]
        player = player_obj.create(
            {
                "name": "test",
                "user_id": False,
            }
        )

        self.assertTrue(player)
        self.assertEqual(player.name, "test")

    def test_player_create_short_no_user(self):
        player_obj = self.env["tournaments.player"]
        with self.assertRaises(ValidationError):
            player_obj.create(
                {
                    "name": "te",
                    "user_id": False,
                }
            )

    def test_player_create_long_no_user(self):
        player_obj = self.env["tournaments.player"]
        with self.assertRaises(ValidationError):
            player_obj.create(
                {
                    "name": "abcdefghijklmnopabcdefghijklmnopabcdefghijklmnopabcdefghijklmnopa",
                    "user_id": False,
                }
            )

    def test_player_create_normal_with_user(self):
        player_obj = self.env["tournaments.player"]
        user_obj = self.env["res.users"]

        user = user_obj.search([("name", "=", "admin")])
        player = player_obj.create(
            {
                "name": "test",
                "user_id": user.id,
            }
        )

        self.assertEqual(player.name, "test")
        self.assertEqual(player.user_id.id, user.id)

    def test_player_create_short_with_user(self):
        player_obj = self.env["tournaments.player"]
        user_obj = self.env["res.users"]

        user = user_obj.search([("name", "=", "admin")])

        with self.assertRaises(ValidationError):
            player_obj.create(
                {
                    "name": "te",
                    "user_id": user.id,
                }
            )

    def test_player_create_long_with_user(self):
        player_obj = self.env["tournaments.player"]
        user_obj = self.env["res.users"]

        user = user_obj.search([("name", "=", "admin")])

        with self.assertRaises(ValidationError):
            player_obj.create(
                {
                    "name": "abcdefghijklmnopabcdefghijklmnopabcdefghijklmnopabcdefghijklmnopa",
                    "user_id": user.id,
                }
            )
