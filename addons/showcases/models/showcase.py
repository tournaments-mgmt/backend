import logging

from odoo import models, fields, api
from odoo.tools.translate import _

_logger = logging.getLogger(__name__)


class Showcase(models.Model):
    _name = "tournaments.showcase"
    _description = "Showcase"

    _inherit = ["mail.thread", "mail.activity.mixin"]

    _sql_constraints = [
        (
            "name_uniq",
            "UNIQUE(name)",
            _("A Showcase with the same tag already exists. Names must be uniques"),
        ),
        (
            "tag_uniq",
            "UNIQUE(tag)",
            _("A Showcase with the same tag already exists. Tags must be uniques"),
        ),
    ]

    name = fields.Char(
        string="Name", help="Showcase name", required=True, tracking=True
    )

    tag = fields.Char(string="Tag", help="Showcase tag", required=True, tracking=True)

    position = fields.Char(string="Position", help="Showcase position", tracking=True)

    ts_last_contact = fields.Datetime(
        string="Last contact", help="Last contact", required=False, readonly=True
    )

    last_ip_address = fields.Char(
        string="Last IP Address", help="Last IP Address", required=False, readonly=True
    )

    showcase_pane_ids = fields.One2many(
        string="Panes",
        help="Panes",
        comodel_name="tournaments.showcase.pane",
        inverse_name="showcase_id",
    )

    next_showcase_pane_id = fields.Many2one(
        string="Next Showcase Pane",
        help="Next Showcase Pane",
        comodel_name="tournaments.showcase.pane",
        readonly=True,
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if "name" not in vals and "tag" in vals:
                vals["name"] = vals["tag"]
        return super().create(vals_list)

    def compute_next_showcase_pane_id(self):
        showcase_pane_obj = self.env["tournaments.showcase.pane"]

        for rec in self:
            showcase_panes = showcase_pane_obj.search(
                domain=[
                    ("showcase_id", "=", rec.id),
                ],
                order="order, id",
            )

            if not showcase_panes:
                _logger.warning("No tournament pane in playlist")
                rec.next_showcase_pane_id = False
                continue

            if (
                not rec.next_showcase_pane_id
                or rec.next_showcase_pane_id not in showcase_panes
            ):
                rec.next_showcase_pane_id = showcase_panes[0]
            else:
                pane_ids: list[int] = showcase_panes.ids
                pos: int = pane_ids.index(rec.next_showcase_pane_id.id)

                pos += 1
                if pos >= len(pane_ids):
                    pos = 0

                rec.next_showcase_pane_id = showcase_pane_obj.browse(pane_ids[pos]).id
