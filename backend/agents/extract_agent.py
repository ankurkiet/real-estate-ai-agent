import re
import json

from agents.client import call_llm, EXTRACT_MODEL


# ─────────────────────────────────────────────
# JSON HELPERS
# ─────────────────────────────────────────────

def _extract_json_object(text):
    """
    Strips <think>...</think> reasoning blocks (qwen model),
    then extracts and parses the first {...} JSON object found.
    """

    cleaned = re.sub(
        r"<think>.*?</think>",
        "",
        text,
        flags=re.DOTALL | re.IGNORECASE
    ).strip()

    cleaned = cleaned.replace("```json", "").replace("```", "")

    start = cleaned.find("{")
    end   = cleaned.rfind("}")

    if start == -1 or end == -1:
        raise ValueError("Model response did not contain a JSON object")

    return json.loads(cleaned[start:end + 1])


def _parse_budget_value(value):
    """
    Converts string budgets like '1 crore', '50 lakh', '5000000'
    into plain integers. Passes through None and existing ints.
    """

    if value is None:
        return None

    if isinstance(value, (int, float)):
        return int(value)

    if not isinstance(value, str):
        return value

    lowered = value.lower().replace(",", "").strip()

    crore_match = re.search(r"(\d+(?:\.\d+)?)\s*(crore|cr)", lowered)
    if crore_match:
        return int(float(crore_match.group(1)) * 10_000_000)

    lakh_match = re.search(r"(\d+(?:\.\d+)?)\s*lakh", lowered)
    if lakh_match:
        return int(float(lakh_match.group(1)) * 100_000)

    number_match = re.search(r"\d+(?:\.\d+)?", lowered)
    if number_match:
        return int(float(number_match.group(0)))

    return value


def _normalize_requirements(requirements):
    """
    Ensures budget is an int and bhk is an int wherever possible.
    """

    normalized = dict(requirements)

    if "budget" in normalized:
        normalized["budget"] = _parse_budget_value(normalized["budget"])

    if normalized.get("bhk") is not None:
        try:
            normalized["bhk"] = int(normalized["bhk"])
        except (TypeError, ValueError):
            pass

    return normalized


# ─────────────────────────────────────────────
# REQUIREMENT EXTRACTION
# ─────────────────────────────────────────────

def extract_requirements(user_message, previous_memory):
    """
    Merges the new user message with the existing search memory
    and returns an updated dict of property filter requirements.
    """

    prompt = f"""
    You are a real estate AI assistant.

    Your task:
    - Understand current message
    - Understand previous memory
    - Return updated property requirements

    RULES:
    - Preserve old values unless changed
    - Update when user changes filter
    - Set value to null if removed
    - Return ONLY valid JSON
    - No explanation

    Previous Memory:
    {json.dumps(previous_memory)}

    User Message:
    {user_message}

    FINAL JSON FORMAT:

    {{
        "city": null,
        "location": null,
        "bhk": null,
        "budget": null,
        "purpose": null,
        "near_metro": null,
        "furnished": null,
        "parking": null,
        "property_type": null
    }}
    """

    text = call_llm(EXTRACT_MODEL, prompt)

    try:
        requirements = _extract_json_object(text)
        result = _normalize_requirements(requirements)
    except (ValueError, Exception) as e:
        print(f"[EXTRACT] JSON parse failed ({e}), keeping previous memory")
        result = dict(previous_memory)

    print("[EXTRACT]", result)

    return result
