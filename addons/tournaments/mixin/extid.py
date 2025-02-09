import base64
import uuid
from io import BytesIO

import qrcode

from odoo import models, fields, api


class ExtID(models.AbstractModel):
    _name = "tournaments.extid"
    _description = "External ID and QR Code"

    extid = fields.Char(
        string="External ID",
        help="External ID",
        required=True,
        default=lambda self: self._default_extid()
    )

    qrcode_image = fields.Binary(
        string="QRCode",
        help="QRCode",
        compute="_compute_qrcode_image"
    )

    def _default_extid(self) -> str:
        return str(uuid.uuid4())

    @api.depends("extid")
    def _compute_qrcode_image(self):
        for rec in self:
            rec.qrcode_image = self.generate_qr_image(rec.extid)

    @api.model
    def generate_qr_image(self, content: str) -> bytes:
        if not content:
            raise ValueError("Invalid string")

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=5,
            border=6,
        )
        qr.add_data(content)
        qr.make(fit=True)

        img = qr.make_image()
        temp = BytesIO()
        img.save(temp, format="PNG")

        return base64.b64encode(temp.getvalue())
