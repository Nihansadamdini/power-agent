
from tools.appliances import add_appliance, list_appliances
from tools.billing import calculate_bill, simulate_change
from tools.plans import save_plan

TOOL_FUNCTIONS = {
    f.__name__: f
    for f in [add_appliance, list_appliances, calculate_bill,
              simulate_change, save_plan]
}


def _tool(name, desc, props, required):
    return {"type": "function", "function": {
        "name": name, "description": desc,
        "parameters": {"type": "object", "properties": props,
                       "required": required}}}


TOOL_SCHEMAS = [
    _tool("add_appliance",
          "Add or update a household appliance and its monthly usage.",
          {"name": {"type": "string", "description": "e.g. 'AC', 'fridge'"},
           "watts": {"type": "number", "description": "power rating in watts"},
           "hours_per_day": {"type": "number"},
           "days_per_month": {"type": "number", "description": "default 30"}},
          ["name", "watts", "hours_per_day"]),
    _tool("list_appliances",
          "List all appliances with their monthly kWh and total units.",
          {}, []),
    _tool("calculate_bill",
          "Calculate the monthly CEB domestic bill for a number of units (kWh). "
          "Uses the rates in tariff.json, which may be sample values.",
          {"units": {"type": "number"}}, ["units"]),
    _tool("simulate_change",
          "What-if: change one appliance's daily hours and show the bill savings.",
          {"appliance": {"type": "string"},
           "new_hours_per_day": {"type": "number"}},
          ["appliance", "new_hours_per_day"]),
    _tool("save_plan",
          "Save a markdown savings plan to the plans folder.",
          {"title": {"type": "string"}, "content": {"type": "string"}},
          ["title", "content"]),
]