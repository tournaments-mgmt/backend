from odoo.tests import TransactionCase, tagged


@tagged("-at_install", "post_install")
class TestMaxMindGeoIPMixin(TransactionCase):
    def test_maxmind_lookup_city_invalid(self):
        mixin_obj = self.env["maxmind.geoip2"]

        with self.assertRaises(ValueError):
            mixin_obj.maxmind_lookup_city()

        with self.assertRaises(ValueError):
            mixin_obj.maxmind_lookup_city("")

    def test_maxmind_lookup_asn_invalid(self):
        mixin_obj = self.env["maxmind.geoip2"]

        with self.assertRaises(ValueError):
            mixin_obj.maxmind_lookup_asn()

        with self.assertRaises(ValueError):
            mixin_obj.maxmind_lookup_asn("")

    def test_maxmind_lookup_city_valid(self):
        mixin_obj = self.env["maxmind.geoip2"]

        response = mixin_obj.maxmind_lookup_city("1.1.1.1")
        self.assertTrue(response)

    def test_maxmind_lookup_asn_valid(self):
        mixin_obj = self.env["maxmind.geoip2"]

        response = mixin_obj.maxmind_lookup_asn("1.1.1.1")
        self.assertTrue(response)
