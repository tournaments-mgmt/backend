import typing

from odoo import models, fields, api


class Entrant(models.Model):
    _name = "tournaments.entrant"
    _description = "Entrant"

    _inherit = [
        "tournaments.extid",
        "mail.thread",
        "mail.activity.mixin"
    ]

    name = fields.Char(
        string="Name",
        related="nickname_id.nickname",
        store=True
    )

    tournament_id = fields.Many2one(
        string="Tournament",
        help="The tournament this entrant belongs to",
        comodel_name="tournaments.tournament",
        required=True,
        tracking=True
    )

    nickname_id = fields.Many2one(
        string="Nickname",
        help="The nickname of the entrant",
        comodel_name="tournaments.nickname",
        domain="[]",
        required=True,
        tracking=True
    )

    user_id = fields.Many2one(
        related="nickname_id.user_id",
        readonly=True,
        store=True,
        tracking=True
    )

    confirmed = fields.Boolean(
        string="Confirmed",
        help="Whether or not the entrant has been confirmed",
        default=False,
        tracking=True
    )

    ts_confirmed = fields.Datetime(
        string="Confirmed DateTime",
        help="The date and time the entrant has been confirmed",
        readonly=True,
        tracking=True
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
        for rec in self:
            if not rec.name and ("name" not in vals or not vals["name"]):
                vals["name"] = rec.user_id.nickname

        if "confirmed" in vals:
            vals["ts_confirmed"] = vals["confirmed"] and fields.Datetime.now() or False

        return super().write(vals)
