from odoo import models, fields


class Platform(models.Model):
    _name = "tournaments.platform"
    _description = "Platform"

    _inherit = ["mail.thread", "mail.activity.mixin"]

    _sql_constraints = [
        (
            "name_uniq",
            "UNIQUE (name)",
            "There is another Platform with the same name. Names must be unique.",
        ),
        (
            "tag_uniq",
            "UNIQUE (tag)",
            "There is another Platform with the same tag. Tags must be unique.",
        ),
    ]

    active = fields.Boolean(string="Active", help="Active", default=True, tracking=True)

    name = fields.Char(
        string="Name",
        help="Platform name",
        required=True,
    )

    tag = fields.Char(
        string="Tag",
        help="Platform tag",
        required=True,
    )

    supported_games_ids = fields.Many2many(
        string="Games",
        help="Supported games",
        comodel_name="tournaments.game",
        relation="tournaments_game_supported_platform_rel",
        column1="platform_id",
        column2="game_id",
        readonly=True,
    )

    logo_image = fields.Image(
        string="Logo",
        help="Logo image",
        max_width=1024,
        max_height=1024,
        verify_resolution=True,
    )

    note = fields.Html(string="Note", help="Note")
