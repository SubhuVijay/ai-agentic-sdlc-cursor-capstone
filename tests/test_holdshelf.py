import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from holdshelf.catalog import Catalog, Hold
from holdshelf.server import ShelfApp


class HoldShelfTests(unittest.TestCase):
    def setUp(self):
        self.app = ShelfApp(Catalog([
            Hold("H-1042", "The Thursday Murder Club", "Maya Chen", "2026-11-02", "ready", "555-0142"),
            Hold("H-1048", "Braiding Sweetgrass", "Luis Ortega", "2026-11-16", "ready", None),
        ]))

    def test_health(self):
        status, body = self.app.handle("GET", "/api/health")
        self.assertEqual(status, 200)
        self.assertEqual(body, {"status": "ok"})

    def test_lists_holds_and_keeps_a_missing_phone_as_null(self):
        status, body = self.app.handle("GET", "/api/holds")
        self.assertEqual(status, 200)
        by_id = {hold["id"]: hold for hold in body["holds"]}
        self.assertEqual(by_id["H-1042"]["title"], "The Thursday Murder Club")
        self.assertEqual(by_id["H-1042"]["status"], "ready")
        self.assertIsNone(by_id["H-1048"]["phone"])

    def test_pickup_marks_the_hold_and_rejects_a_second_pickup(self):
        status, body = self.app.handle("POST", "/api/holds/H-1042/pickup")
        self.assertEqual(status, 200)
        self.assertEqual(body["hold"]["status"], "picked-up")
        status, body = self.app.handle("POST", "/api/holds/H-1042/pickup")
        self.assertEqual(status, 409)
        self.assertIn("already picked up", body["error"])

    def test_unknown_hold_returns_404(self):
        status, body = self.app.handle("POST", "/api/holds/H-0000/pickup")
        self.assertEqual(status, 404)
        self.assertIn("H-0000", body["error"])

    def test_page_loads_the_hold_api(self):
        status, page = self.app.handle("GET", "/")
        self.assertEqual(status, 200)
        self.assertIn("Hold shelf", page)
        self.assertIn("/api/holds", page)
        self.assertIn("/api/health", page)

    def test_unknown_path_returns_404(self):
        status, body = self.app.handle("GET", "/api/other")
        self.assertEqual(status, 404)
        self.assertIn("error", body)


if __name__ == "__main__":
    unittest.main()
