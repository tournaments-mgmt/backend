from odoo import models, fields


class Game(models.Model):
    _name = "tournaments.game"
    _description = "Game"
    _order = "name"

    _inherit = ["mail.thread", "mail.activity.mixin"]

    _sql_constraints = [
        (
            "name_uniq",
            "UNIQUE(name)",
            "A Game with the same name already exists. Names must be uniques",
        ),
        (
            "tag_uniq",
            "UNIQUE(tag)",
            "A Game with the same tag already exists. Tags must be uniques",
        ),
    ]

    active = fields.Boolean(string="Active", help="Active", default=True, tracking=True)

    name = fields.Char(string="Name", help="Game name", required=True)

    tag = fields.Char(string="Tag", help="Game tag", required=True)

    year = fields.Integer(string="Year", help="Year")

    supported_platform_ids = fields.Many2many(
        string="Platforms",
        help="Supported Platforms",
        comodel_name="tournaments.platform",
        relation="tournaments_game_supported_platform_rel",
        column1="game_id",
        column2="platform_id",
    )

    logo_image = fields.Image(
        string="Logo",
        help="Logo image",
        max_width=1024,
        max_height=1024,
        verify_resolution=True,
    )

    pegi_age_id = fields.Many2one(
        string="PEGI Age Label",
        help="PEGI Age Label",
        comodel_name="pegi.age",
        required=False,
    )

    pegi_age_logo = fields.Image(
        string="Game PEGI Age Label", related="pegi_age_id.logo"
    )

    pegi_content_descriptor_ids = fields.Many2many(
        string="PEGI Content Descriptors",
        help="PEGI Content Descriptors",
        comodel_name="pegi.content",
        relation="tournaments_game_pegi_content_rel",
        column1="game_id",
        column2="content_id",
    )

    background_image = fields.Image(
        string="Background",
        help="Background image",
        max_width=1920,
        max_height=1080,
        verify_resolution=True,
    )
