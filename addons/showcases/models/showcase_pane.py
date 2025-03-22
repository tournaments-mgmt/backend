from odoo import models, fields, api


class ShowcasePane(models.Model):
    _name = "tournaments.showcase.pane"
    _description = "Showcase Pane"

    _inherit = [
        "mail.thread",
        "mail.activity.mixin",
    ]

    showcase_id = fields.Many2one(
        string="Showcase",
        help="Related Showcase",
        comodel_name="tournaments.showcase",
        required=True,
        tracking=True,
    )

    pane_id = fields.Many2one(
        string="Pane",
        help="Related Pane",
        comodel_name="tournaments.pane",
        required=True,
        tracking=True,
        onDelete="cascade",
    )

    order = fields.Integer(
        string="Order", help="Order", required=True, default=0, tracking=True
    )

    override_duration = fields.Boolean(
        string="Duration override",
        help="Override default duration",
        default=False,
        tracking=True,
    )

    duration = fields.Integer(
        string="Duration",
        help="Duration (ms)",
        required=True,
        default=10000,
        tracking=True,
    )

    is_next = fields.Boolean(
        string="Is next", help="Is next", compute="_compute_is_next", store=True
    )

    @api.depends("showcase_id.next_showcase_pane_id", "pane_id")
    def _compute_is_next(self):
        for rec in self:
            rec.is_next = bool(
                rec.showcase_id.next_showcase_pane_id.id == rec.pane_id.id
            )

    def action_set_as_next(self):
        self.ensure_one()
        self.showcase_id.next_showcase_pane_id = self.pane_id.id
