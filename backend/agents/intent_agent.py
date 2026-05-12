from agents.client import call_llm, INTENT_MODEL


def detect_intent(user_message):
    """
    Classifies the user message into one of:
    property_search, follow_up, area_advice,
    investment_advice, market_info, casual_chat
    """

    prompt = f"""
    You are an intent classifier for a real estate AI assistant.

    Classify the message into ONLY one intent.

    Intents:

    property_search  - user wants to BUY or FIND a property / flat / apartment
    follow_up        - user refines a previous property search (cheaper, bigger, etc.)
    area_advice      - user asks about a locality, city, area, amenities, malls, schools, metro, infrastructure
    investment_advice - user asks whether a city or area is good for investment
    market_info      - user asks about property prices, trends, news
    casual_chat      - greetings, off-topic, or anything not real-estate related

    KEY RULE:
    If the message asks ABOUT an area (malls, schools, roads, livability, famous places)
    but does NOT mention buying/finding a property → classify as area_advice.
    Only classify as property_search if the user clearly wants to buy/find/see a property.

    Examples:

    "Show 3 BHK in Noida" → property_search
    "I want to buy a flat in Gurgaon" → property_search
    "Do you have any 2 BHK under 80 lakh?" → property_search

    "Anything cheaper?" → follow_up
    "What about 2 BHK?" → follow_up
    "Show me something near metro" → follow_up

    "Tell me about Sector 150" → area_advice
    "Famous malls in Noida" → area_advice
    "What are the best schools near Gurgaon?" → area_advice
    "Is Sector 62 a good area to live?" → area_advice
    "How is the connectivity in Noida Extension?" → area_advice

    "Is Noida good for investment?" → investment_advice
    "Which area gives better rental yield?" → investment_advice

    "Current Gurgaon property prices?" → market_info
    "What is the price trend in Noida?" → market_info

    "Hello" → casual_chat
    "Thanks" → casual_chat

    Return ONLY the intent name.

    Message:
    {user_message}
    """

    intent = call_llm(INTENT_MODEL, prompt)

    intent = intent.strip().lower()

    print("[INTENT]", intent)

    return intent
