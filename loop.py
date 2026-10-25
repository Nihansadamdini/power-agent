import json
import logging
import os
import time

import ollama

from tools import TOOL_FUNCTIONS, TOOL_SCHEMAS

MODEL = os.getenv("AGENT_MODEL", "qwen2.5:7b")
MAX_STEPS = 8          # one request ekata tool-call rounds max
MAX_HISTORY = 20       # system message ekata pase rakinna messages gana

log = logging.getLogger("agent")

SYSTEM = """You are a household electricity bill optimizer for Sri Lankan homes (CEB domestic tariff).

Rules:
- ALWAYS use tools for appliance data, units and bill amounts. Never guess or invent numbers.
- To find savings: first call list_appliances, then calculate_bill with the total units,
  then call simulate_change for the biggest consumer(s).
- If the user asks you to save a plan, call save_plan with a clear markdown summary.
- If a tool returns an error, read the message, fix the arguments and try again,
  or ask the user for the missing information.
- Amounts are in Sri Lankan Rupees (Rs.). Units are kWh.
- After the tools finish, give a short, clear summary in the same language the user used.
"""


def run_tool(name, args):
    """Tool eka safely run karanawa. Error awoth model ta dict ekak widiyata return karanawa."""
    fn = TOOL_FUNCTIONS.get(name)
    if fn is None:
        return {"error": f"Unknown tool '{name}'. Available: {list(TOOL_FUNCTIONS)}"}
    if not isinstance(args, dict):
        return {"error": "Tool arguments must be a JSON object"}
    try:
        return fn(**args)
    except (TypeError, ValueError) as e:       # wrong/missing args, validation failures
        return {"error": f"Invalid input: {e}"}
    except Exception as e:                      # unexpected tool crash
        log.exception("Tool %s crashed", name)
        return {"error": f"Tool failed: {e}"}


def trim_history(messages):
    """System message + last MAX_HISTORY messages witharak rakinawa.
    Tool result ekak kalin tiyena tool_call eken wenwenna epa nisa 'user' message ekakin patan gannawa."""
    if len(messages) <= MAX_HISTORY + 1:
        return messages
    system, rest = messages[0], messages[1:][-MAX_HISTORY:]
    while rest and (rest[0].role if hasattr(rest[0], "role") else rest[0]["role"]) != "user":
        rest = rest[1:]
    return [system] + rest


def chat(messages, user_input):
    """User message ekak process karala final answer eka return karanawa.
    `messages` list eka mutate wenawa (conversation history)."""
    messages.append({"role": "user", "content": user_input})
    log.info("USER: %s", user_input)

    for step in range(1, MAX_STEPS + 1):
        try:
            resp = ollama.chat(model=MODEL, messages=messages, tools=TOOL_SCHEMAS)
        except Exception as e:
            log.error("Ollama error: %s", e)
            return ("Ollama ekata connect wenna bae. 'ollama serve' run wenawada, "
                    f"'{MODEL}' model eka pull karalada balanna.")

        msg = resp.message
        messages.append(msg)

        if not msg.tool_calls:                  # tool ekak naha = final answer
            log.info("ANSWER: %s", msg.content)
            return msg.content or "(empty response)"

        for call in msg.tool_calls:
            name = call.function.name
            args = dict(call.function.arguments or {})
            t0 = time.time()
            result = run_tool(name, args)
            ms = int((time.time() - t0) * 1000)

            print(f"  [step {step}] -> {name}({json.dumps(args)})")
            print(f"            <- {json.dumps(result)}")
            log.info("step=%d tool=%s args=%s result=%s ms=%d",
                     step, name, json.dumps(args), json.dumps(result), ms)

            messages.append({"role": "tool", "tool_name": name,
                             "content": json.dumps(result)})

    log.warning("Hit MAX_STEPS without a final answer")
    return "Steps limit eka giya. Request eka podi karala nawatha try karanna."