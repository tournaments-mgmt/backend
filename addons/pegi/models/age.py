from odoo import models, fields


class PegiAgeModel(models.Model):
    _name = "pegi.age"
    _description = "PEGI Age Label"

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
