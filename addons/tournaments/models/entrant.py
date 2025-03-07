import typing

from odoo import models, fields, api


class Entrant(models.Model):
    _name = "tournaments.entrant"
    _description = "Entrant"

    _sql_constraints = [
        ("tournament_user_uniq", "UNIQUE NULLS DISTINCT (user_id, tournament_id)", "Entrant already exists")
    ]

    name = fields.Char(
        string="Name",
        help="The name of the entrant",
    )

    tournament_id = fields.Many2one(
        string="Tournament",
        help="The tournament this entrant belongs to",
        comodel_name="tournaments.tournament",
        required=True
    )

    user_id = fields.Many2one(
        string="User",
        help="The user this entrant belongs to",
        comodel_name="res.users",
        required=False
    )

    @api.onchange("user_id")
    def _onchange_user_id(self):
        for rec in self:
            rec.name = rec.user_id.nickname

    @api.model_create_multi
    def create(self, vals_list) -> typing.Self:
        for vals in vals_list:
            if not vals.get("name", None):
                vals["name"] = self.env["res.users"].browse(vals["user_id"]).nickname

        return super().create(vals_list)

    def write(self, vals) -> typing.Literal[True]:
        if not vals.get("name", None):
            vals["name"] = self.env["res.users"].browse(vals["user_id"]).nickname

        return super().write(vals)
