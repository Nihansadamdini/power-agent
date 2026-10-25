
import json
from pathlib import Path

DB = Path(__file__).parent.parent / "data" / "appliances.json"


def _load():
    return json.loads(DB.read_text(encoding="utf-8")) if DB.exists() else {}


def _save(data):
    DB.parent.mkdir(exist_ok=True)
    DB.write_text(json.dumps(data, indent=2), encoding="utf-8")


def _kwh(a):
    return round(a["watts"] * a["hours_per_day"] * a["days_per_month"] / 1000, 2)


def add_appliance(name, watts, hours_per_day, days_per_month=30):
    name = str(name).strip().lower()
    watts = float(watts)
    hours_per_day = float(hours_per_day)
    days_per_month = float(days_per_month)

    if not name or len(name) > 50:
        raise ValueError("name must be 1-50 characters")
    if not 1 <= watts <= 10000:
        raise ValueError("watts must be between 1 and 10000")
    if not 0 <= hours_per_day <= 24:
        raise ValueError("hours_per_day must be between 0 and 24")
    if not 1 <= days_per_month <= 31:
        raise ValueError("days_per_month must be between 1 and 31")

    data = _load()
    data[name] = {"watts": watts, "hours_per_day": hours_per_day,
                  "days_per_month": days_per_month}
    _save(data)
    return {"saved": name, "monthly_kwh": _kwh(data[name])}


def list_appliances():
    data = _load()
    items = [{"name": n, **a, "monthly_kwh": _kwh(a)} for n, a in data.items()]
    return {"appliances": items,
            "total_units": round(sum(i["monthly_kwh"] for i in items), 2)}