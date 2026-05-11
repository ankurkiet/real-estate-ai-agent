from fastapi import FastAPI
from pydantic import BaseModel
import json

app = FastAPI()


# Load properties
with open("data/properties.json") as f:
    properties = json.load(f)


class PropertyRequest(BaseModel):

    city: str | None = None
    location: str | None = None
    bhk: int | None = None
    budget: int | None = None
    purpose: str | None = None
    near_metro: bool | None = None
    furnished: bool | None = None
    parking: bool | None = None
    property_type: str | None = None


@app.post("/match-properties")
def match_properties(request: PropertyRequest):

    matches = []

    for property in properties:

        score = 0
        reasons = []

        # City
        if request.city:
            if property["city"].lower() != request.city.lower():
                continue
            score += 20

        # Location (partial match, e.g. "Sector 62" matches "Sector 62")
        if request.location:
            if request.location.lower() not in property["location"].lower():
                continue
            score += 20

        # BHK
        if request.bhk:
            if property["bhk"] != request.bhk:
                continue
            score += 20

        # Budget
        if request.budget:
            if property["price"] <= request.budget:
                score += 20
                reasons.append("Within budget")

        # Metro
        print("request near metro:" , request.near_metro)
        if request.near_metro:
            if property["near_metro"]:
                score += 15
                reasons.append("Near metro")

        # Furnished
        if request.furnished:
            if property["furnished"]:
                score += 10
                reasons.append("Fully furnished")

        # Parking
        if request.parking:
            if property["parking"]:
                score += 10
                reasons.append("Parking available")

        # Investment
        if request.purpose == "investment":

            if property["rental_yield"] >= 5:
                score += 20
                reasons.append("Good rental yield")

        property["match_score"] = score
        property["reasons"] = reasons

        matches.append(property)

    # Sort best matches first
    matches.sort(
        key=lambda x: x["match_score"],
        reverse=True
    )

    return {
        "matches": matches
    }