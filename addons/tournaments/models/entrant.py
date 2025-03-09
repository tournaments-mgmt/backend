import typing

from odoo import models, fields


class Entrant(models.Model):
    _name = "tournaments.entrant"
    _description = "Entrant"

    _inherit = ["tournaments.extid", "mail.thread", "mail.activity.mixin"]

    name = fields.Char(string="Name", related="player_id.name", store=True)

    tournament_id = fields.Many2one(
        string="Tournament",
        help="The tournament this entrant belongs to",
        comodel_name="tournaments.tournament",
        required=True,
        tracking=True,
    )

    player_id = fields.Many2one(
        string="Player",
        help="The player of the entrant",
        comodel_name="tournaments.player",
        domain="[]",
        required=True,
        tracking=True,
    )

    user_id = fields.Many2one(
        related="player_id.user_id", readonly=True, store=True, tracking=True
    )

    confirmed = fields.Boolean(
        string="Confirmed",
        help="Whether or not the entrant has been confirmed",
        default=False,
        tracking=True,
    )

    ts_confirmed = fields.Datetime(
        string="Confirmed DateTime",
        help="The date and time the entrant has been confirmed",
        readonly=True,
        tracking=True,
    )

    def write(self, vals) -> typing.Literal[True]:
        if "confirmed" in vals:
            vals["ts_confirmed"] = vals["confirmed"] and fields.Datetime.now() or False

        return super().write(vals)
