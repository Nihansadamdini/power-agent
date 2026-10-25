
import json
from pathlib import Path

from tools.appliances import _kwh, _load

TARIFF = json.loads(
    (Path(__file__).parent.parent / "tariff.json").read_text(encoding="utf-8")
)

TARIFF_NOTE = TARIFF.get("_note", "")


def _bill(units):
    energy, prev = 0.0, 0
    for b in TARIFF["blocks"]:
        upto = b["upto"] if b["upto"] is not None else float("inf")
        if units > prev:
            energy += (min(units, upto) - prev) * b["rate"]
        prev = upto
    fixed = next(f["fixed"] for f in TARIFF["fixed_charges"]
                 if f["upto"] is None or units <= f["upto"])
    return {"units": round(units, 2), "energy_charge": round(energy, 2),
            "fixed_charge": fixed, "total": round(energy + fixed, 2)}


def calculate_bill(units):
    units = float(units)
    if not 0 <= units <= 5000:
        raise ValueError("units must be between 0 and 5000")
    result = _bill(units)
    result["tariff_note"] = TARIFF_NOTE
    return result


def simulate_change(appliance, new_hours_per_day):
    data = _load()
    key = str(appliance).strip().lower()
    if key not in data:
        raise ValueError(f"Unknown appliance '{key}'. Known: {list(data)}")
    hours = float(new_hours_per_day)
    if not 0 <= hours <= 24:
        raise ValueError("new_hours_per_day must be between 0 and 24")

    before = sum(_kwh(a) for a in data.values())
    changed = dict(data[key], hours_per_day=hours)
    after = before - _kwh(data[key]) + _kwh(changed)

    b, a = _bill(before), _bill(after)
    return {"appliance": key,
            "units_before": round(before, 2), "units_after": round(after, 2),
            "bill_before": b["total"], "bill_after": a["total"],
            "monthly_saving": round(b["total"] - a["total"], 2)}