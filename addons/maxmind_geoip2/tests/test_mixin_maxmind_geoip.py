import os

from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("-at_install", "post_install")
class TestMaxMindGeoIPMixin(TransactionCase):
    def test_maxmind_lookup_not_supported_db(self):
        mixin_obj = self.env["maxmind.geoip2"]

        with self.assertRaises(ValidationError):
            mixin_obj._get_db_path(db="not_existing")

    def test_maxmind_lookup_empty_path(self):
        ir_config_parameter_obj = self.env["ir.config_parameter"].sudo()
        ir_config_parameter_obj.set_param("maxmind_geoip2.db_path_city", "")
        ir_config_parameter_obj.set_param("maxmind_geoip2.db_path_asn", "")

        mixin_obj = self.env["maxmind.geoip2"]

        with self.assertRaises(ValidationError):
            mixin_obj._get_db_path(db="city")
        with self.assertRaises(ValidationError):
            mixin_obj._get_db_path(db="asn")

    def test_maxmind_lookup_not_found_path(self):
        ir_config_parameter_obj = self.env["ir.config_parameter"].sudo()
        ir_config_parameter_obj.set_param("maxmind_geoip2.db_path_city", "city")
        ir_config_parameter_obj.set_param("maxmind_geoip2.db_path_asn", "asn")

        mixin_obj = self.env["maxmind.geoip2"]

        with self.assertRaises(ValidationError):
            mixin_obj._get_db_path(db="city")
        with self.assertRaises(ValidationError):
            mixin_obj._get_db_path(db="asn")

    def test_maxmind_lookup_valid_path(self):
        city_path, asn_path = self._define_maxmind_database_paths()

        mixin_obj = self.env["maxmind.geoip2"]

        assert mixin_obj._get_db_path(db="city") == city_path
        assert mixin_obj._get_db_path(db="asn") == asn_path

    def test_maxmind_lookup_city_invalid(self):
        self._define_maxmind_database_paths()

        mixin_obj = self.env["maxmind.geoip2"]

        with self.assertRaises(ValidationError):
            mixin_obj.maxmind_lookup_asn()

        with self.assertRaises(ValidationError):
            mixin_obj.maxmind_lookup_city("")

    def test_maxmind_lookup_asn_invalid(self):
        self._define_maxmind_database_paths()

        mixin_obj = self.env["maxmind.geoip2"]

        with self.assertRaises(ValidationError):
            mixin_obj.maxmind_lookup_asn()

        with self.assertRaises(ValidationError):
            mixin_obj.maxmind_lookup_asn("")

    def test_maxmind_lookup_valid(self):
        self._define_maxmind_database_paths()

        mixin_obj = self.env["maxmind.geoip2"]

        assert mixin_obj.maxmind_lookup_city("2.125.160.217")
        assert mixin_obj.maxmind_lookup_asn("1.0.0.1")

    def _define_maxmind_database_paths(self):
        test_assets_path: str = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "static", "test")
        )
        city_path: str = os.path.join(test_assets_path, "GeoLite2-City-Test.mmdb")
        asn_path: str = os.path.join(test_assets_path, "GeoLite2-ASN-Test.mmdb")

        ir_config_parameter_obj = self.env["ir.config_parameter"].sudo()
        ir_config_parameter_obj.set_param("maxmind_geoip2.db_path_city", city_path)
        ir_config_parameter_obj.set_param("maxmind_geoip2.db_path_asn", asn_path)

        return city_path, asn_path
