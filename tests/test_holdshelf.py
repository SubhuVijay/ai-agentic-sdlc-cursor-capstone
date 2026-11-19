import json
import sys
import unittest
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from holdshelf.catalog import Catalog, Hold
from holdshelf.server import BadWindowError, ShelfApp, parse_window_days

TODAY = date(2026, 11, 18)


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

    def test_page_includes_the_long_waiting_section(self):
        status, page = self.app.handle("GET", "/")
        self.assertEqual(status, 200)
        self.assertIn("/api/holds/overdue", page)
        self.assertIn("windowDays=", page)
        self.assertIn("encodeURIComponent", page)
        self.assertIn("Not Found", page)
        self.assertIn("No ready hold is past the pickup window.", page)
        self.assertIn("Could not load long-waiting holds.", page)
        self.assertIn("API unreachable", page)
        self.assertIn("Long-waiting holds", page)
        self.assertIn("Show long-waiting holds", page)
        self.assertIn('type="number"', page)
        self.assertIn('min="1"', page)
        self.assertIn('step="1"', page)
        self.assertIn('value="7"', page)
        self.assertIn("Mark picked up", page)
        self.assertIn("The hold shelf is empty.", page)
        self.assertNotIn("console.log", page)

    def test_unknown_path_returns_404(self):
        status, body = self.app.handle("GET", "/api/other")
        self.assertEqual(status, 404)
        self.assertIn("error", body)


class OverdueQueryTests(unittest.TestCase):
    def test_hold_accepts_a_missing_ready_since(self):
        hold = Hold("X", "T", "P", None, "ready")
        self.assertIsNone(hold.ready_since)
        self.assertEqual(hold.status, "ready")
        self.assertIsNone(hold.phone)

    def test_seed_window_7_returns_only_the_sixteen_day_hold(self):
        holds = Catalog().list_overdue(7, TODAY)
        self.assertEqual([hold["id"] for hold in holds], ["H-1042"])
        self.assertEqual(holds[0]["daysWaiting"], 16)
        self.assertEqual(holds[0]["phone"], "555-0142")
        self.assertNotIn("H-1048", [hold["id"] for hold in holds])
        self.assertNotIn("H-1102", [hold["id"] for hold in holds])
        self.assertNotIn("H-0991", [hold["id"] for hold in holds])

    def test_exact_seven_days_is_excluded(self):
        catalog = Catalog([
            Hold("H-exact", "Title", "Patron", "2026-11-11", "ready", "555-0100"),
        ])
        self.assertEqual(catalog.list_overdue(7, TODAY), [])

    def test_h1048_is_included_at_window_1_with_a_null_phone(self):
        holds = Catalog().list_overdue(1, TODAY)
        by_id = {hold["id"]: hold for hold in holds}
        self.assertIn("H-1048", by_id)
        self.assertEqual(by_id["H-1048"]["daysWaiting"], 2)
        self.assertIsNone(by_id["H-1048"]["phone"])

    def test_h1048_is_excluded_at_window_2(self):
        ids = [hold["id"] for hold in Catalog().list_overdue(2, TODAY)]
        self.assertNotIn("H-1048", ids)

    def test_picked_up_hold_is_excluded(self):
        catalog = Catalog()
        for window in (1, 7, 3650):
            ids = [hold["id"] for hold in catalog.list_overdue(window, TODAY)]
            self.assertNotIn("H-0991", ids)

    def test_missing_or_unparseable_ready_since_is_excluded(self):
        catalog = Catalog([
            Hold("H-none", "Title", "Patron", None, "ready"),
            Hold("H-empty", "Title", "Patron", "", "ready"),
            Hold("H-bad", "Title", "Patron", "not-a-date", "ready"),
            Hold("H-1042", "The Thursday Murder Club", "Maya Chen", "2026-11-02", "ready", "555-0142"),
        ])
        for window in (1, 7):
            ids = [hold["id"] for hold in catalog.list_overdue(window, TODAY)]
            self.assertEqual(ids, ["H-1042"])

    def test_future_ready_since_is_excluded(self):
        catalog = Catalog([
            Hold("H-future", "Title", "Patron", "2026-11-25", "ready", "555-0100"),
        ])
        self.assertEqual(catalog.list_overdue(1, TODAY), [])

    def test_seed_window_3650_returns_an_empty_list(self):
        self.assertEqual(Catalog().list_overdue(3650, TODAY), [])

    def test_sorts_longest_wait_first_then_id(self):
        catalog = Catalog([
            Hold("H-B", "Title", "Patron", "2026-11-08", "ready"),
            Hold("H-C", "Title", "Patron", "2026-11-01", "ready"),
            Hold("H-A", "Title", "Patron", "2026-11-01", "ready"),
            Hold("H-D", "Title", "Patron", "2026-11-10", "ready"),
        ])
        holds = catalog.list_overdue(7, TODAY)
        self.assertEqual(
            [(hold["id"], hold["daysWaiting"]) for hold in holds],
            [("H-A", 17), ("H-C", 17), ("H-B", 10), ("H-D", 8)],
        )

    def test_result_keys(self):
        holds = Catalog().list_overdue(7, TODAY)
        self.assertEqual(
            list(holds[0].keys()),
            ["id", "title", "patron", "readySince", "status", "phone", "daysWaiting"],
        )

    def test_list_holds_keeps_a_missing_ready_since(self):
        catalog = Catalog([Hold("H-none", "Title", "Patron", None, "ready", "555-0100")])
        listed = catalog.list_holds()
        self.assertEqual(len(listed), 1)
        self.assertIsNone(listed[0]["readySince"])
        self.assertEqual(listed[0]["phone"], "555-0100")
        self.assertEqual(
            list(listed[0].keys()),
            ["id", "title", "patron", "readySince", "status", "phone"],
        )


class WindowParserTests(unittest.TestCase):
    MESSAGE = "windowDays must be a whole number of days from 1 to 3650."

    def assert_rejected(self, raw: list[str]) -> None:
        with self.assertRaises(BadWindowError) as caught:
            parse_window_days(raw)
        message = str(caught.exception)
        self.assertEqual(caught.exception.args, (self.MESSAGE,))
        self.assertEqual(message, self.MESSAGE)
        self.assertIsInstance(caught.exception, ValueError)
        for value in raw:
            if value and value not in self.MESSAGE:
                self.assertNotIn(value, message)

    def test_omitted_window_defaults_to_seven(self):
        self.assertEqual(parse_window_days(None), 7)
        self.assertEqual(parse_window_days([]), 7)

    def test_seven_with_and_without_a_leading_zero(self):
        self.assertEqual(parse_window_days(["7"]), 7)
        self.assertEqual(parse_window_days(["07"]), 7)

    def test_lower_and_upper_bounds(self):
        self.assertEqual(parse_window_days(["1"]), 1)
        self.assertEqual(parse_window_days(["3650"]), 3650)

    def test_non_numeric_values_are_rejected(self):
        for raw in (["abc"], ["7days"], [""]):
            self.assert_rejected(raw)

    def test_zero_negative_and_decimal_values_are_rejected(self):
        for raw in (["0"], ["00"], ["-1"], ["7.5"], ["7.0"]):
            self.assert_rejected(raw)

    def test_signs_spaces_newlines_and_non_ascii_digits_are_rejected(self):
        for raw in (["+7"], [" 7"], ["7\n"], ["\u0667"]):
            self.assert_rejected(raw)

    def test_repeated_window_is_rejected(self):
        self.assert_rejected(["7", "9"])

    def test_above_the_upper_bound_is_rejected(self):
        self.assert_rejected(["3651"])

    def test_very_long_digit_string_is_rejected(self):
        self.assert_rejected(["9" * 5000])


class OverdueRouteTests(unittest.TestCase):
    ERROR = {"error": "windowDays must be a whole number of days from 1 to 3650."}

    def make_app(self, catalog=None):
        if catalog is None:
            catalog = Catalog()
        return ShelfApp(catalog, today=lambda: TODAY)

    def test_omitted_window_returns_the_sixteen_day_hold(self):
        status, body = self.make_app().handle("GET", "/api/holds/overdue")
        self.assertEqual(status, 200)
        self.assertEqual(body["windowDays"], 7)
        self.assertEqual([hold["id"] for hold in body["holds"]], ["H-1042"])
        hold = body["holds"][0]
        self.assertEqual(hold["daysWaiting"], 16)
        self.assertEqual(hold["patron"], "Maya Chen")
        self.assertEqual(hold["phone"], "555-0142")

    def test_window_7_and_07_match_the_omitted_window(self):
        app = self.make_app()
        _, omitted = app.handle("GET", "/api/holds/overdue")
        for target in (
            "/api/holds/overdue?windowDays=7",
            "/api/holds/overdue?windowDays=07",
        ):
            status, body = app.handle("GET", target)
            self.assertEqual(status, 200)
            self.assertEqual(body["windowDays"], 7)
            self.assertEqual(body["holds"], omitted["holds"])

    def test_window_1_includes_the_hold_with_no_phone(self):
        status, body = self.make_app().handle("GET", "/api/holds/overdue?windowDays=1")
        self.assertEqual(status, 200)
        by_id = {hold["id"]: hold for hold in body["holds"]}
        self.assertEqual(by_id["H-1048"]["daysWaiting"], 2)
        self.assertIsNone(by_id["H-1048"]["phone"])

    def test_window_2_excludes_h1048(self):
        status, body = self.make_app().handle("GET", "/api/holds/overdue?windowDays=2")
        self.assertEqual(status, 200)
        self.assertNotIn("H-1048", [hold["id"] for hold in body["holds"]])

    def test_exact_seven_day_wait_is_excluded(self):
        catalog = Catalog([
            Hold("H-exact", "Title", "Patron", "2026-11-11", "ready", "555-0100"),
            Hold("H-1042", "The Thursday Murder Club", "Maya Chen", "2026-11-02", "ready", "555-0142"),
        ])
        status, body = self.make_app(catalog).handle("GET", "/api/holds/overdue?windowDays=7")
        self.assertEqual(status, 200)
        self.assertEqual([hold["id"] for hold in body["holds"]], ["H-1042"])

    def test_missing_ready_since_is_excluded(self):
        catalog = Catalog([
            Hold("H-none", "Title", "Patron", None, "ready"),
            Hold("H-1042", "The Thursday Murder Club", "Maya Chen", "2026-11-02", "ready", "555-0142"),
        ])
        status, body = self.make_app(catalog).handle("GET", "/api/holds/overdue")
        self.assertEqual(status, 200)
        self.assertNotIn("H-none", [hold["id"] for hold in body["holds"]])

    def test_picked_up_hold_is_excluded(self):
        app = self.make_app()
        for window in (1, 7):
            status, body = app.handle("GET", f"/api/holds/overdue?windowDays={window}")
            self.assertEqual(status, 200)
            self.assertNotIn("H-0991", [hold["id"] for hold in body["holds"]])

    def test_window_3650_returns_an_empty_list(self):
        status, body = self.make_app().handle("GET", "/api/holds/overdue?windowDays=3650")
        self.assertEqual(status, 200)
        self.assertEqual(body["windowDays"], 3650)
        self.assertEqual(body["holds"], [])

    def test_bad_windows_return_the_fixed_error(self):
        message = self.ERROR["error"]
        cases = [
            ("/api/holds/overdue?windowDays=abc", ["abc"]),
            ("/api/holds/overdue?windowDays=7days", ["7days"]),
            ("/api/holds/overdue?windowDays=", [""]),
            ("/api/holds/overdue?windowDays", []),
            ("/api/holds/overdue?windowDays=0", ["0"]),
            ("/api/holds/overdue?windowDays=00", ["00"]),
            ("/api/holds/overdue?windowDays=-1", ["-1"]),
            ("/api/holds/overdue?windowDays=7.5", ["7.5"]),
            ("/api/holds/overdue?windowDays=7.0", ["7.0"]),
            ("/api/holds/overdue?windowDays=%2B7", ["%2B7", "+7"]),
            ("/api/holds/overdue?windowDays=+7", ["+7"]),
            ("/api/holds/overdue?windowDays=%207", ["%207", " 7"]),
            ("/api/holds/overdue?windowDays=7%0A", ["7%0A", "7\n"]),
            ("/api/holds/overdue?windowDays=7&windowDays=9", ["7", "9"]),
            ("/api/holds/overdue?windowDays=3651", ["3651"]),
            ("/api/holds/overdue?windowDays=" + ("9" * 5000), ["9" * 5000]),
        ]
        app = self.make_app()
        for target, rejected in cases:
            status, body = app.handle("GET", target)
            self.assertEqual(status, 400, target)
            self.assertEqual(body, self.ERROR, target)
            self.assertNotIn("holds", body)
            encoded = json.dumps(body)
            for value in rejected:
                if value and value not in message:
                    self.assertNotIn(value, encoded, target)

    def test_misspelled_window_names_use_the_default(self):
        app = self.make_app()
        for target in (
            "/api/holds/overdue?windowdays=abc",
            "/api/holds/overdue?window=3",
        ):
            status, body = app.handle("GET", target)
            self.assertEqual(status, 200)
            self.assertEqual(body["windowDays"], 7)
            self.assertEqual([hold["id"] for hold in body["holds"]], ["H-1042"])

    def test_other_parameters_are_ignored(self):
        status, body = self.make_app().handle("GET", "/api/holds/overdue?windowDays=7&foo=bar")
        self.assertEqual(status, 200)
        self.assertEqual(body["windowDays"], 7)
        self.assertEqual([hold["id"] for hold in body["holds"]], ["H-1042"])

    def test_hold_list_ignores_the_window_query(self):
        app = self.make_app()
        status, plain = app.handle("GET", "/api/holds")
        queried_status, queried = app.handle("GET", "/api/holds?windowDays=abc")
        self.assertEqual(status, 200)
        self.assertEqual(queried_status, 200)
        self.assertEqual(queried, plain)
        self.assertEqual(list(queried.keys()), ["holds"])
        for hold in queried["holds"]:
            self.assertEqual(
                list(hold.keys()),
                ["id", "title", "patron", "readySince", "status", "phone"],
            )

    def test_post_overdue_is_not_the_overdue_view(self):
        status, body = self.make_app().handle("POST", "/api/holds/overdue")
        self.assertEqual(status, 404)
        self.assertEqual(body, {"error": "That page or hold was not found."})
        self.assertNotIn("holds", body)
        self.assertNotIn("windowDays", body)

    def test_pickup_removes_the_hold_from_the_overdue_view(self):
        app = self.make_app()
        status, body = app.handle("POST", "/api/holds/H-1042/pickup")
        self.assertEqual(status, 200)
        self.assertEqual(body["hold"]["status"], "picked-up")
        status, body = app.handle("GET", "/api/holds/overdue")
        self.assertEqual(status, 200)
        self.assertNotIn("H-1042", [hold["id"] for hold in body["holds"]])

    def test_today_defaults_to_the_server_date(self):
        app = ShelfApp(Catalog())
        self.assertIs(app.today.__self__, date)
        self.assertEqual(app.today.__name__, "today")
        self.assertEqual(app.today(), date.today())

    def test_pickup_still_reports_unknown_and_repeat_pickup(self):
        app = self.make_app()
        status, body = app.handle("POST", "/api/holds/H-0000/pickup")
        self.assertEqual(status, 404)
        self.assertIn("H-0000", body["error"])
        status, _body = app.handle("POST", "/api/holds/H-1042/pickup")
        self.assertEqual(status, 200)
        status, body = app.handle("POST", "/api/holds/H-1042/pickup")
        self.assertEqual(status, 409)
        self.assertIn("already picked up", body["error"])


if __name__ == "__main__":
    unittest.main()
