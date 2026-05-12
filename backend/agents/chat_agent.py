from agents.client import call_llm, CHAT_MODEL
from knowledge_base import REAL_ESTATE_KNOWLEDGE


def real_estate_chat(user_message, user_memory=None):
    """
    Responds to general real estate questions as an
    expert Indian real estate consultant.
    """

    memory_context = ""
    if user_memory:
        parts = []
        if user_memory.get("city"):
            parts.append(f"Preferred city: {user_memory['city']}")
        if user_memory.get("location"):
            parts.append(f"Preferred location: {user_memory['location']}")
        if user_memory.get("bhk"):
            parts.append(f"BHK preference: {user_memory['bhk']} BHK")
        if user_memory.get("budget"):
            parts.append(f"Budget: {user_memory['budget']}")
        if user_memory.get("purpose"):
            parts.append(f"Purpose: {user_memory['purpose']}")
        if parts:
            memory_context = "\n    USER SAVED PREFERENCES:\n    " + "\n    ".join(parts) + "\n"

    prompt = f"""
    You are an expert Indian real estate consultant.

    Use:
    1. Real estate knowledge
    2. Available property listings

    to answer user questions professionally.
    {memory_context}
    IMPORTANT: If the user has saved preferences (city/location), tailor your advice specifically to that area unless the user asks about a different place.

    REAL ESTATE KNOWLEDGE:
    {REAL_ESTATE_KNOWLEDGE}

    USER QUESTION:
    {user_message}

    IMPORTANT RULES:
    - Sound like experienced Indian real estate consultant
    - Keep responses VERY SHORT
    - Maximum 80 words
    - Prefer 3-5 bullet points starting with a dash (-)
    - Give direct practical advice only
    - Avoid long explanations
    - Avoid repeating user question
    - Do not fabricate fake projects
    - Mention available listings only if relevant
    - Be mobile-friendly for Telegram chat
    - PLAIN TEXT ONLY: do not use any markdown, asterisks, underscores, or bold symbols
    """

    response = call_llm(CHAT_MODEL, prompt, temperature=0.3)

    # Strip any markdown bold/italic markers the model may still output
    response = response.replace("**", "").replace("__", "")

    return response[:1000]
