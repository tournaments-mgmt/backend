import datetime
import secrets
import string

from odoo import models, fields, api


class Token(models.Model):
    _name = "tournaments.token"
    _description = "Users Authentication Token for APIs"

    _sql_constraints = [
        ("value_uniq", "UNIQUE (value)", "Value already exists! Must be unique!")
    ]

    value = fields.Char(
        string="Value",
        help="Token value",
        required=True,
        default=lambda self: self._default_value(),
        readonly=True
    )

    res_users_id = fields.Many2one(
        string="User",
        help="Related user",
        comodel_name="res.users",
        required=True,
        readonly=True
    )

    ts_expiration = fields.Datetime(
        string="Expiration",
        help="Token expiration date",
        required=True,
        readonly=True,
        default=lambda self: self._default_ts_expiration(),
    )

    expired = fields.Boolean(
        string="Expired",
        help="Token expired",
        compute="_compute_expired",
        readonly=True
    )

    def _default_value(self) -> str:
        return "".join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))

    def _default_ts_expiration(self) -> datetime.datetime:
        return fields.Datetime.now() + datetime.timedelta(hours=4)

    @api.depends("ts_expiration")
    def _compute_expired(self) -> None:
        for rec in self:
            rec.expired = fields.Datetime.now() - rec.ts_expiration < datetime.timedelta(hours=4)
