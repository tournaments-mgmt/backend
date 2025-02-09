from odoo import models, fields


class PegiContentModel(models.Model):
    _name = "pegi.content"
    _description = "PEGI Content Descriptor"

    name = fields.Char(
        string="Name",
        help="Age Label name"
    )

    logo = fields.Image(
        string="Image",
        help="Logo image"
    )

    description = fields.Html(
        string="Description",
        help="Description"
    )
