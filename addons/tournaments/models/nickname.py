from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Nickname(models.Model):
    _name = "tournaments.nickname"
    _description = "Nickname"
    _rec_name = "nickname"

    _sql_constraints = [
        ("name_uniq", "UNIQUE(nickname)", "Name must be unique!"),
    ]

    _inherit = [
        "tournaments.extid",
        "mail.thread",
        "mail.activity.mixin"
    ]

    nickname = fields.Char(
        string="Name",
        help="Nickname",
        required=True,
        index=True,
        tracking=True,
    )

    user_id = fields.Many2one(
        string="User",
        help="Related user",
        comodel_name="res.users",
        tracking=True,
    )

    @api.model_create_multi
    @api.returns("self", lambda value: value.id)
    def create(self, vals_list):
        for vals in vals_list:
            if "nickname" in vals:
                self.validate_nickname(vals["nickname"])

        return super().create(vals_list)

    def write(self, vals):
        if "nickname" in vals:
            self.validate_nickname(vals["nickname"])

        return super().write(vals)

    @api.model
    def validate_nickname(self, nickname) -> None:
        if len(nickname) < 3 or len(nickname) > 64:
            raise ValidationError("Nickname must be between 3 and 64 characters long")

        if self.env["tournaments.badword"].search_count([("word", "ilike", nickname)]) > 0:
            raise ValidationError("Nickname invalid")
