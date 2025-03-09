from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Player(models.Model):
    _name = "tournaments.player"
    _description = "Player"

    _sql_constraints = [
        ("name_uniq", "UNIQUE(name)", "Name must be unique!"),
    ]

    _inherit = ["tournaments.extid", "mail.thread", "mail.activity.mixin"]

    name = fields.Char(
        string="Name",
        help="Name",
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
            if "name" in vals:
                self.validate_name(vals["name"])

        return super().create(vals_list)

    def write(self, vals):
        if "name" in vals:
            self.validate_name(vals["name"])

        return super().write(vals)

    @api.model
    def validate_name(self, name) -> None:
        if len(name) < 3 or len(name) > 64:
            raise ValidationError("Name must be between 3 and 64 characters long")
