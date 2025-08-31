from fastapi import FastAPI, HTTPException
from typing import List, Optional
from pydantic import BaseModel
import json

app = FastAPI(
    title="Uganda Locale API",
    description="API for Uganda administrative divisions - districts, counties, sub-counties, parishes, and villages",
    version="1.0.0"
)

class Location(BaseModel):
    id: str
    name: str

class UgandaLocale:
    def __init__(self):
        # Sample data structure - in production this would come from a database
        self.data = {
            "districts": [
                {"id": "1", "name": "Kampala"},
                {"id": "2", "name": "Wakiso"},
                {"id": "3", "name": "Mukono"},
                {"id": "42", "name": "Gulu"},
                {"id": "5", "name": "Jinja"}
            ],
            "counties": {
                "1": [  # Kampala
                    {"id": "101", "name": "Central Division"},
                    {"id": "102", "name": "Kawempe Division"},
                    {"id": "103", "name": "Makindye Division"},
                    {"id": "104", "name": "Nakawa Division"},
                    {"id": "105", "name": "Rubaga Division"}
                ],
                "2": [  # Wakiso
                    {"id": "201", "name": "Busiro County"},
                    {"id": "202", "name": "Kyadondo County"}
                ],
                "42": [  # Gulu
                    {"id": "4201", "name": "Gulu Municipality"},
                    {"id": "4202", "name": "Aswa County"},
                    {"id": "4203", "name": "Omoro County"},
                    {"id": "4204", "name": "Paicho County"}
                ]
            },
            "sub_counties": {
                "4204": [  # Paicho County
                    {"id": "420401", "name": "Paicho Sub County"},
                    {"id": "420402", "name": "Awach Sub County"},
                    {"id": "420403", "name": "Lapul Sub County"},
                    {"id": "420404", "name": "Lukole Sub County"}
                ]
            },
            "parishes": {
                "420401": [  # Paicho Sub County
                    {"id": "42040101", "name": "Paicho Parish"},
                    {"id": "42040102", "name": "Olwal Parish"},
                    {"id": "42040103", "name": "Parabongo Parish"}
                ]
            },
            "villages": {
                "42040101": [  # Paicho Parish
                    {"id": "4204010101", "name": "Paicho Central Village"},
                    {"id": "4204010102", "name": "Paicho East Village"},
                    {"id": "4204010103", "name": "Paicho West Village"}
                ]
            }
        }

    def get_districts(self) -> List[dict]:
        return self.data["districts"]

    def get_counties(self, district_id: str) -> List[dict]:
        return self.data["counties"].get(district_id, [])

    def get_sub_counties(self, county_id: str) -> List[dict]:
        return self.data["sub_counties"].get(county_id, [])

    def get_parishes(self, sub_county_id: str) -> List[dict]:
        return self.data["parishes"].get(sub_county_id, [])

    def get_villages(self, parish_id: str) -> List[dict]:
        return self.data["villages"].get(parish_id, [])

# Initialize the locale service
uga_locale = UgandaLocale()

@app.get("/", summary="API Information")
async def root():
    return {
        "message": "Uganda Locale API",
        "description": "API for Uganda administrative divisions",
        "endpoints": {
            "districts": "/districts",
            "counties": "/counties/{district_id}",
            "sub_counties": "/sub-counties/{county_id}",
            "parishes": "/parishes/{sub_county_id}",
            "villages": "/villages/{parish_id}"
        }
    }

@app.get("/districts", response_model=List[Location], summary="Get all districts")
async def get_districts():
    """
    Get all districts in Uganda.
    """
    districts = uga_locale.get_districts()
    return districts

@app.get("/counties/{district_id}", response_model=List[Location], summary="Get counties in a district")
async def get_counties(district_id: str):
    """
    Get all counties in the specified district.
    """
    # Verify district exists
    districts = uga_locale.get_districts()
    district_exists = any(d["id"] == district_id for d in districts)
    
    if not district_exists:
        raise HTTPException(status_code=404, detail=f"District with id '{district_id}' not found")
    
    counties = uga_locale.get_counties(district_id)
    return counties

@app.get("/sub-counties/{county_id}", response_model=List[Location], summary="Get sub-counties in a county")
async def get_sub_counties(county_id: str):
    """
    Get all sub-counties in the specified county.
    """
    sub_counties = uga_locale.get_sub_counties(county_id)
    if not sub_counties:
        raise HTTPException(status_code=404, detail=f"No sub-counties found for county id '{county_id}'")
    return sub_counties

@app.get("/parishes/{sub_county_id}", response_model=List[Location], summary="Get parishes in a sub-county")
async def get_parishes(sub_county_id: str):
    """
    Get all parishes in the specified sub-county.
    """
    parishes = uga_locale.get_parishes(sub_county_id)
    if not parishes:
        raise HTTPException(status_code=404, detail=f"No parishes found for sub-county id '{sub_county_id}'")
    return parishes

@app.get("/villages/{parish_id}", response_model=List[Location], summary="Get villages in a parish")
async def get_villages(parish_id: str):
    """
    Get all villages in the specified parish.
    """
    villages = uga_locale.get_villages(parish_id)
    if not villages:
        raise HTTPException(status_code=404, detail=f"No villages found for parish id '{parish_id}'")
    return villages

@app.get("/health", summary="Health check")
async def health_check():
    """
    Simple health check endpoint.
    """
    return {"status": "healthy", "message": "Uganda Locale API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)