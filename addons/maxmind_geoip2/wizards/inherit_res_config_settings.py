import logging
import os

from odoo import models, fields

MAXMIND_GEOIP2_DB_PATHS: list[str] = [
    "/opt/mmdb",
    "/opt/geolite2",
    "/ush/share/geolite2",
]

_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    maxmind_geoip2_enabled = fields.Boolean(
        string="Enabled",
        help="Enable/disable MaxMind GeoIP2 Lookups",
        default=False,
        config_parameter="maxmind_geoip2.enabled",
    )

    maxmind_geoip2_db_path_city = fields.Char(
        string="City",
        help="Path to MaxMind GeoIP2 City Database",
        default=lambda self: self._default_maxmind_geoip2_db_path_city(),
        config_parameter="maxmind_geoip2.db_path_city",
    )

    maxmind_geoip2_db_path_asn = fields.Char(
        string="ASN",
        help="Path to MaxMind GeoIP2 ASN Database",
        default=lambda self: self._default_maxmind_geoip2_db_path_asn(),
        config_parameter="maxmind_geoip2.db_path_asn",
    )

    def _default_maxmind_geoip2_db_path_city(self) -> str:
        _logger.info("Searching for MaxMind GeoIP2 City Database")

        for dir_path in MAXMIND_GEOIP2_DB_PATHS:
            file_path: str = os.path.join(dir_path, "GeoLite2-City.mmdb")
            _logger.debug(f"Searching for {file_path}")
            if os.path.exists(file_path):
                _logger.debug(f"Found {file_path}")
                return file_path

        _logger.debug(f"Not found")
        return ""

    def _default_maxmind_geoip2_db_path_asn(self) -> str:
        _logger.info("Searching for MaxMind GeoIP2 ASN Database")

        for dir_path in MAXMIND_GEOIP2_DB_PATHS:
            file_path: str = os.path.join(dir_path, "GeoLite2-ASN.mmdb")
            _logger.debug(f"Searching for {file_path}")
            if os.path.exists(file_path):
                _logger.debug(f"Found {file_path}")
                return file_path

        _logger.debug(f"Not found")
        return ""
