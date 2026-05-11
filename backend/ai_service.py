from groq import Groq
import json
import os

from knowledge_base import REAL_ESTATE_KNOWLEDGE


client = Groq(
    api_key="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"
)

# Load properties once at startup
_properties_path = os.path.join(os.path.dirname(__file__), "data", "properties.json")
with open(_properties_path) as _f:
    PROPERTIES = json.load(_f)

def detect_intent(user_message):

    prompt = f"""
    Classify the user message into one of the intents below.

    Intents:
    - property_search  → user wants to find/see/check/buy/rent a property or asks if properties exist in a location
    - follow_up        → user is refining or adding to a previous property search (e.g. "what about 2 BHK?", "show cheaper ones")
    - area_advice      → user wants to know about a locality, sector, or city
    - investment_advice → user wants investment guidance
    - market_info      → user asks about market trends, prices, or news
    - casual_chat      → greetings or off-topic messages

    Examples:
    "Do you have any property near Noida Sector 62" → property_search
    "Show me 2 BHK flats in Gurgaon" → property_search
    "Is there anything in Sector 137?" → property_search
    "What about under 1 crore?" → follow_up
    "Tell me about Sector 62" → area_advice
    "Is Noida good for investment?" → investment_advice
    "What are current property prices?" → market_info
    "Hi" → casual_chat

    Return ONLY the intent name, nothing else.

    Message:
    {user_message}
    """

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0
    )

    intent = response.choices[0].message.content.strip()

    print("DETECTED INTENT:", intent)

    return intent

def real_estate_chat(user_message):

    properties_summary = json.dumps(
        [
            {
                "id": p["id"],
                "city": p["city"],
                "location": p["location"],
                "bhk": p["bhk"],
                "price": p["price"],
                "near_metro": p["near_metro"],
                "furnished": p["furnished"],
                "parking": p["parking"],
                "property_type": p["property_type"],
                "rental_yield": p["rental_yield"]
            }
            for p in PROPERTIES
        ],
        indent=2
    )

    prompt = f"""
    You are an expert Indian real estate consultant.

    Use the market knowledge and available property listings below to answer user questions.

    Market Knowledge:
    {REAL_ESTATE_KNOWLEDGE}

    Available Property Listings:
    {properties_summary}

    User Question:
    {user_message}

    Rules:
    - Be conversational and sound like an experienced consultant
    - When relevant, reference specific available listings by location, BHK, and price
    - Give practical, actionable advice
    - Keep answers concise
    - Do NOT fabricate properties that are not in the listings above
    """

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content


def extract_requirements(user_message, previous_memory):

    prompt = f"""
    You are an AI real estate assistant.

    Your task:
    1. Analyze current user message
    2. Analyze previous search memory
    3. Return UPDATED COMPLETE property requirements

    IMPORTANT RULES:
    - Keep previous values if user does not change them
    - Update values if user changes them
    - Remove values if user rejects them
    - Return ONLY valid JSON
    - No explanation
    - Use null for missing values

    Previous Memory:
    {json.dumps(previous_memory)}

    User Message:
    {user_message}

    Final JSON Format:
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

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0
    )

    text = response.choices[0].message.content.strip()

    print("RAW AI RESPONSE:", text)

    text = text.replace("```json", "")
    text = text.replace("```", "")

    return json.loads(text)