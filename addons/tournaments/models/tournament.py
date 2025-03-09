import json

import pytz

from odoo import models, fields, api

SELECTION_DAY_OF_WEEK = [
    ("saturday", "Saturday"),
    ("sunday", "Sunday"),
    ("other", "Other"),
]

SELECTION_TYPE = [
    ("contest", "Contest"),
    ("bracket", "Brackets"),
    ("roundrobin", "Round-Robin"),
]


class Tournament(models.Model):
    _name = "tournaments.tournament"
    _description = "Tournament"
    _order = "scheduled_start"

    _sql_constraints = [
        (
            "name_uniq",
            "UNIQUE(name)",
            "A Tournament with the same name already exists. Names must be uniques.",
        )
    ]

    _inherit = [
        "tournaments.scheduled",
        "tournaments.extid",
        "mail.thread",
        "mail.activity.mixin",
    ]

    name = fields.Char(
        string="Tournament Name",
        help="The name of the tournament",
        required=True,
    )

    type = fields.Selection(
        string="Tournament Type",
        help="Type of tournament",
        selection=SELECTION_TYPE,
        required=True,
        default="contest",
    )

    parent_id = fields.Many2one(
        string="Parent",
        help="Parent tournament",
        comodel_name="tournaments.tournament",
        tracking=True,
    )

    game_id = fields.Many2one(
        string="Game",
        help="Game",
        comodel_name="tournaments.game",
        required=True,
        tracking=True,
    )

    game_logo_image = fields.Image(string="Game Logo", related="game_id.logo_image")

    game_pegi_age_logo = fields.Image(
        string="Game Tournament PEGI Age Label", related="game_id.pegi_age_id.logo"
    )

    platform_id = fields.Many2one(
        string="Platform",
        help="Platform",
        comodel_name="tournaments.platform",
        required=True,
        tracking=True,
    )

    platform_logo_image = fields.Image(
        string="Platform Logo", related="platform_id.logo_image"
    )

    day_of_week = fields.Selection(
        string="Day of week",
        help="Day of week",
        selection=SELECTION_DAY_OF_WEEK,
        compute="_compute_day_of_week",
        store=True,
    )

    kanban_color = fields.Integer(
        string="Kanban color", help="Kanban color", compute="_compute_kanban_color"
    )

    entrant_ids = fields.One2many(
        string="Entrants",
        help="Entrants",
        comodel_name="tournaments.entrant",
        inverse_name="tournament_id",
        readonly=True,
    )

    entrant_count = fields.Integer(
        string="Entrant count",
        help="Entrant count",
        compute="_compute_entrant_count",
        readonly=True,
    )

    match_ids = fields.One2many(
        string="Matches",
        help="Matches",
        comodel_name="tournaments.match",
        inverse_name="tournament_id",
    )

    match_count = fields.Integer(
        string="Matches count", help="Matches count", compute="_compute_match_count"
    )

    @api.depends("entrant_ids")
    def _compute_entrant_count(self):
        for rec in self:
            rec.entrant_count = len(rec.entrant_ids)

    @api.depends("scheduled_start")
    def _compute_day_of_week(self):
        for rec in self:
            isoweekday: int = (
                rec.scheduled_start.replace(tzinfo=pytz.UTC)
                .astimezone(pytz.timezone("Europe/Rome"))
                .isoweekday()
            )

            if isoweekday == 6:
                rec.day_of_week = "saturday"
            elif isoweekday == 7:
                rec.day_of_week = "sunday"
            else:
                rec.day_of_week = "other"

    @api.depends("day_of_week")
    def _compute_kanban_color(self):
        for rec in self:
            kanban_color: int = 0

            if rec.day_of_week == "saturday":
                kanban_color = 3
            elif rec.day_of_week == "sunday":
                kanban_color = 4

            rec.kanban_color = kanban_color

    @api.depends("match_ids")
    def _compute_match_count(self):
        for rec in self:
            rec.match_count = len(rec.match_ids)

    def display_entrants(self):
        self.ensure_one()

        action = self.env["ir.actions.actions"]._for_xml_id(
            "tournaments.action_entrant_list"
        )
        action["domain"] = [("tournament_id", "=", self.id)]
        context = json.loads(action["context"])
        context.update({"default_tournament_id": self.id})
        action["context"] = json.dumps(context)
        return action

    def display_matches(self):
        self.ensure_one()

        action = self.env["ir.actions.actions"]._for_xml_id(
            "tournaments.action_match_list"
        )
        action["domain"] = [("tournament_id", "=", self.id)]
        context = json.loads(action["context"])
        context.update({"default_tournament_id": self.id})
        action["context"] = json.dumps(context)
        return action

    def update_state(self):
        for rec in self:
            if rec.scheduled_state not in ["scheduled", "running"]:
                continue

            matches_states: set = {x.state for x in rec.match_ids}
            if not matches_states:
                continue

            if "running" in matches_states:
                start_list = [x.real_start for x in rec.match_ids if x.real_start]
                rec.write(
                    {
                        "scheduled_state": "running",
                        "real_start": start_list and min(start_list) or None,
                    }
                )

            elif matches_states.issubset({"done", "canceled"}):
                end_list = [x.real_end for x in rec.match_ids if x.real_end]
                rec.write(
                    {
                        "scheduled_state": "done",
                        "real_end": end_list and max(end_list) or None,
                    }
                )
