"""Holds waiting on the library shelf."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass
class Hold:
    id: str
    title: str
    patron: str
    ready_since: str | None
    status: str
    phone: str | None = None


def seed_holds() -> list[Hold]:
    """Return the shelf as it stood on the morning of 18 November 2026."""
    return [
        Hold("H-1042", "The Thursday Murder Club", "Maya Chen", "2026-11-02", "ready", "555-0142"),
        Hold("H-1048", "Braiding Sweetgrass", "Luis Ortega", "2026-11-16", "ready", None),
        Hold("H-1102", "The Heaven and Earth Grocery Store", "Priya Shah", "2026-11-12", "ready", "555-0177"),
        Hold("H-0991", "Project Hail Mary", "Imani Brooks", "2026-10-28", "picked-up", "555-0190"),
    ]


class Catalog:
    def __init__(self, holds: list[Hold] | None = None) -> None:
        source = seed_holds() if holds is None else holds
        self._holds = {hold.id: Hold(**hold.__dict__) for hold in source}

    def list_holds(self) -> list[dict]:
        return [self.to_dict(hold) for hold in self._holds.values()]

    def list_overdue(self, window_days: int, today: date) -> list[dict]:
        overdue: list[dict] = []
        for hold in self._holds.values():
            if hold.status != "ready":
                continue
            if hold.ready_since is None or hold.ready_since == "":
                continue
            try:
                ready = date.fromisoformat(hold.ready_since)
            except (ValueError, TypeError):
                continue
            days_waiting = (today - ready).days
            if days_waiting > window_days:
                row = self.to_dict(hold)
                row["daysWaiting"] = days_waiting
                overdue.append(row)
        overdue.sort(key=lambda row: (-row["daysWaiting"], row["id"]))
        return overdue

    def mark_picked_up(self, hold_id: str) -> tuple[str, dict | None]:
        hold = self._holds.get(hold_id)
        if hold is None:
            return "missing", None
        if hold.status == "picked-up":
            return "already", self.to_dict(hold)
        hold.status = "picked-up"
        return "ok", self.to_dict(hold)

    @staticmethod
    def to_dict(hold: Hold) -> dict:
        return {
            "id": hold.id,
            "title": hold.title,
            "patron": hold.patron,
            "readySince": hold.ready_since,
            "status": hold.status,
            "phone": hold.phone,
        }
