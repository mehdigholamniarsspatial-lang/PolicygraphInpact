from pathlib import Path
from django.test import SimpleTestCase, override_settings
from django.urls import reverse
from .services import parse_csv

HEADER = "REF_AREA,MEASURE,CLIM_ACT_POL,Climate actions and policies,TIME_PERIOD,OBS_VALUE,OBS_STATUS\n"


class CsvParserTests(SimpleTestCase):
    def test_valid_csv(self):
        raw = (HEADER + "IRL,POL_STRINGENCY,LEV3_TEST,Test policy,2023,5,A\n").encode()
        payload = parse_csv(raw, "test.csv")
        self.assertEqual(payload["meta"]["row_count"], 1)

    def test_rejects_other_country(self):
        raw = (HEADER + "GBR,POL_STRINGENCY,LEV3_TEST,Test policy,2023,5,A\n").encode()
        with self.assertRaisesRegex(ValueError, "Ireland"):
            parse_csv(raw, "test.csv")


class ViewTests(SimpleTestCase):
    def test_health(self):
        self.assertJSONEqual(self.client.get(reverse("dashboard:health")).content, {"status": "ok"})

    def test_dashboard_and_dataset_load(self):
        page = self.client.get(reverse("dashboard:index"))
        self.assertEqual(page.status_code, 200)
        self.assertContains(page, 'id="initial-data"')
        payload = self.client.get(reverse("dashboard:dataset")).json()
        self.assertGreater(payload["meta"]["row_count"], 0)
