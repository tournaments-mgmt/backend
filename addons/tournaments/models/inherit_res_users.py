import typing

from odoo import models, fields, api


class ResUsers(models.Model):
    _inherit = [
        "res.users"
    ]

    nickname = fields.Char(
        string="Nickname",
        help="Nickname of the user"
    )

    @api.model_create_multi
    def create(self, vals_list) -> typing.Self:
        for vals in vals_list:
            if not vals.get("nickname", None):
                vals["nickname"] = vals["name"]

        return super().create(vals_list)

    def write(self, vals) -> typing.Literal[True]:
        if not vals.get("nickname", None):
            vals["nickname"] = self.name

        return super().write(vals)
