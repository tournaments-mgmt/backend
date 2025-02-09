from odoo import models, fields

SELECTION_SCHEDULED_STATE = [
    ("draft", "Draft"),
    ("scheduled", "Scheduled"),
    ("running", "Running"),
    ("done", "Completed"),
    ("canceled", "Canceled"),
]


class Scheduled(models.AbstractModel):
    _name = "tournaments.scheduled"
    _description = "Scheduled item"

    _inherit = [
        "mail.thread",
        "mail.activity.mixin"
    ]

    scheduled_state = fields.Selection(
        string="State",
        help="Scheduled state",
        selection=SELECTION_SCHEDULED_STATE,
        required=True,
        default="draft",
        tracking=True,
    )

    scheduled_start = fields.Datetime(
        string="Scheduled Start",
        help="Scheduled Date & Time of Start",
        required=True,
        tracking=True,
    )

    scheduled_end = fields.Datetime(
        string="Scheduled End",
        help="Scheduled Date & Time of End",
        tracking=True,
    )

    real_start = fields.Datetime(
        string="Start",
        help="Real Date & Time of Start",
        tracking=True,
        readonly=True
    )

    real_end = fields.Datetime(
        string="End",
        help="Real Date & Time of End",
        tracking=True,
        readonly=True
    )

    def action_confirm(self, propagate: bool = True) -> None:
        for rec in self:
            if rec.scheduled_state not in ["draft"]:
                continue

            rec.write({
                "scheduled_state": "scheduled",
                "real_start": None,
                "real_end": None
            })

    def action_start(self, propagate: bool = True) -> None:
        for rec in self:
            if rec.scheduled_state not in ["scheduled"]:
                continue

            rec.write({
                "scheduled_state": "running",
                "real_start": fields.Datetime.now(),
                "real_end": None
            })

    def action_end(self, propagate: bool = True) -> None:
        for rec in self:
            if rec.scheduled_state not in ["running"]:
                continue

            rec.write({
                "scheduled_state": "done",
                "real_end": fields.Datetime.now()
            })

    def action_cancel(self, propagate: bool = True):
        for rec in self:
            if rec.scheduled_state not in ["scheduled", "running"]:
                continue

            rec.write({
                "scheduled_state": "canceled",
                "real_end": fields.Datetime.now()
            })

    def action_reset(self, propagate: bool = True):
        for rec in self:
            if rec.scheduled_state not in ["scheduled", "running", "canceled"]:
                continue

            rec.write({
                "scheduled_state": "draft",
                "real_start": None,
                "real_end": None
            })
