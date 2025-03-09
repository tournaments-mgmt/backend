from odoo import models, fields, api
from odoo.exceptions import ValidationError


class BadWord(models.Model):
    _name = "tournaments.badword"
    _description = "Bad Word"
    _rec_name = "word"

    _sql_constraints = [("word_uniq", "UNIQUE (word)", "Word must be unique!")]

    _inherit = ["mail.thread", "mail.activity.mixin"]

    word = fields.Char(string="Word", help="Word", readonly=False, tracking=True)

    @api.model
    def validate_name(self, name) -> None:
        for badword in self.search([]):
            if badword.word.lower() in name.lower():
                raise ValidationError("Name invalid")
