import pytest

from tools import appliances
from tools.appliances import add_appliance, list_appliances
from tools.billing import calculate_bill, simulate_change


@pytest.fixture(autouse=True)
def temp_db(tmp_path, monkeypatch):
    monkeypatch.setattr(appliances, "DB", tmp_path / "appliances.json")


def test_zero_units_has_no_energy_charge():
    assert calculate_bill(0)["energy_charge"] == 0


def test_bill_increases_with_units():
    assert calculate_bill(200)["total"] > calculate_bill(100)["total"]


def test_bill_includes_tariff_note():
    assert "tariff_note" in calculate_bill(100)


def test_negative_units_rejected():
    with pytest.raises(ValueError):
        calculate_bill(-5)


def test_bad_watts_rejected():
    with pytest.raises(ValueError):
        add_appliance("fan", 0, 5)


def test_hours_over_24_rejected():
    with pytest.raises(ValueError):
        add_appliance("fan", 60, 30)


def test_add_and_list_appliance():
    add_appliance("AC", 1200, 6)
    result = list_appliances()
    assert result["appliances"][0]["name"] == "ac"
    assert result["total_units"] == 216.0      # 1200W * 6h * 30d / 1000


def test_simulate_change_saves_money():
    add_appliance("ac", 1200, 6)
    result = simulate_change("ac", 4)
    assert result["monthly_saving"] > 0


def test_simulate_unknown_appliance_rejected():
    with pytest.raises(ValueError):
        simulate_change("toaster", 1)