import binascii

import magic

from odoo import models, fields
from odoo.tools.translate import _


class Pane(models.Model):
    _name = "tournaments.pane"
    _description = "Showcase Pane"

    _inherit = [
        "mail.thread",
        "mail.activity.mixin",
    ]

    _sql_constraints = [
        (
            "name_uniq",
            "UNIQUE(name)",
            _("A Pane with the same name already exists. Names must be uniques"),
        )
    ]

    name = fields.Char(string="Name", help="Pane name", required=True, tracking=True)

    duration = fields.Integer(
        string="Duration",
        help="Duration (ms)",
        required=True,
        default=10000,
        tracking=True,
    )

    showcase_pane_ids = fields.One2many(
        string="Showcases",
        help="Showcases",
        comodel_name="tournaments.showcase.pane",
        inverse_name="pane_id",
        readonly=True,
    )

    type_id = fields.Many2one(
        string="Type",
        help="Type of Pane",
        comodel_name="tournaments.pane.type",
        required=True,
        tracking=True,
        onDelete="cascade",
    )

    text_message = fields.Char(string="Message", help="Message to show", tracking=True)

    text_title = fields.Char(string="Title", help="Title to show", tracking=True)

    text_subtitle = fields.Char(
        string="Subtitle", help="Subtitle to show", tracking=True
    )

    text_background_file = fields.Image(
        string="Background Text Image",
        help="Background Text Image to display",
    )

    text_background_file_name = fields.Char(
        string="Background Text image filename",
        help="Background Text image file name",
        tracking=True,
    )

    image_file = fields.Binary(
        string="Image", help="Image to display", attachment=True, tracking=True
    )

    image_file_name = fields.Char(
        string="Image filename", help="Image file name", tracking=True
    )

    image_file_mimetype = fields.Char(
        string="Image MimeType",
        help="Image MimeType",
        compute="_compute_image_file_mimetype",
    )

    video_url = fields.Char(string="Video URL", help="Video URL", tracking=True)

    tournaments_running_show_completed = fields.Boolean(
        string="Show completed",
        help="Show also completed Tournaments",
        default=False,
        tracking=True,
    )

    tournaments_running_show_completed_timeout = fields.Integer(
        string="Timeout", help="Completed Tournaments timout", tracking=True
    )

    tournaments_running_show_next = fields.Boolean(
        string="Show next",
        help="Show also next scheduled Tournaments",
        default=False,
        tracking=True,
    )

    tournaments_running_show_next_interval = fields.Integer(
        string="Interval", help="Next scheduled Tournaments interval", tracking=True
    )

    tournament_matches_tournament_id = fields.Many2one(
        string="Tournament",
        help="Tournament to display",
        comodel_name="tournaments.tournament",
        tracking=True,
    )

    tournament_matches_show_scheduled_time = fields.Boolean(
        string="Show scheduled time in every match",
        help="Show scheduled time in every match",
        default=True,
        tracking=True,
    )

    tournament_classification_items_per_column = fields.Integer(
        string="Items Per Column", help="Items Per Column", default=20, tracking=True
    )

    tournament_classification_column_per_view = fields.Integer(
        string="Column per View", help="Column per View", default=3, tracking=True
    )

    tournament_classification_scores_titles = fields.Char(
        string="Scores Titles",
        help="Scores Titles (Separated by comma)",
        default="Pos,Kill,TOT",
        tracking=True,
    )

    tournament_best_of_matches_round = fields.Integer(
        string="Round to be Shown",
        help="A negative value will allow to ignore this option",
        tracking=True,
    )

    tournament_brackets_teams_count = fields.Integer(
        string="Teams count",
        help="Teams count. A negative value will allow to ignore this option.",
        tracking=True,
    )

    tournament_brackets_round = fields.Integer(
        string="Rounds",
        help="Round to be Shown. A negative value will allow to ignore this option.",
        tracking=True,
    )

    def _compute_image_file_mimetype(self):
        for record in self:
            mimetype_value = magic.from_buffer(
                binascii.a2b_base64(record.image_file), mime=True
            )
            record.image_file_mimetype = mimetype_value
