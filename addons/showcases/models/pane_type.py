from odoo import models, fields
from odoo.tools.translate import _


class PaneType(models.Model):
    _name = "tournaments.pane.type"
    _description = "Showcase Pane Type"

    _inherit = [
        "mail.thread",
        "mail.activity.mixin",
    ]

    _sql_constraints = [
        (
            "name_uniq",
            "UNIQUE(name)",
            _("A Pane with the same name already exists. Names must be uniques"),
        ),
        (
            "tag_uniq",
            "UNIQUE(tag)",
            _("A Pane with the same tag already exists. Tags must be uniques"),
        ),
    ]

    name = fields.Char(string="Name", help="Pane name", required=True, tracking=True)

    tag = fields.Char(string="Tag", help="Pane tag", required=True, tracking=True)
