import logging
import os.path

import geoip2
from geoip2.models import City, ASN

from odoo import models, api
from odoo.exceptions import ValidationError
from odoo.tools.translate import _

_logger = logging.getLogger(__name__)


class MaxMindGeoIP2Mixin(models.AbstractModel):
    _name = "maxmind.geoip2"
    _description = "Adds support for MaxMind GeoIP2 Lookups"

    @api.model
    def maxmind_lookup_city(self, address: str = "") -> City:
        return self._lookup(address, db="city")

    @api.model
    def maxmind_lookup_asn(self, address: str = "") -> ASN:
        return self._lookup(address, db="asn")

    def _lookup(self, address: str, db: str = "city"):
        if not address:
            raise ValidationError("Address cannot be empty")

        mmdb_path: str = self._get_db_path(db=db)
        with geoip2.database.Reader(mmdb_path) as reader:
            return getattr(reader, db)(address)

    def _get_db_path(self, db: str) -> str:
        ir_config_parameter_obj = self.env["ir.config_parameter"]

        _logger.debug(f"Looking for database {db}")

        if db == "city":
            param_name = "maxmind_geoip2.db_path_city"
        elif db == "asn":
            param_name = "maxmind_geoip2.db_path_asn"
        else:
            raise ValidationError(_("DB not supported"))

        mmdb_path: str = ir_config_parameter_obj.get_param(param_name, "")
        _logger.debug(f"Parameter {param_name}: \"{mmdb_path}\"")

        if not mmdb_path:
            raise ValidationError(_("MaxMind database path not configured"))
        if not os.path.exists(mmdb_path):
            raise ValidationError(_("MaxMind database not found in path"))

        return mmdb_path
