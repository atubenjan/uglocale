from fastapi import FastAPI, HTTPException
from typing import List, Optional
from pydantic import BaseModel
import json
import requests
from functools import lru_cache

app = FastAPI(
    title="Uganda Locale API",
    description="Complete API for Uganda administrative divisions - districts, counties, sub-counties, parishes, and villages. Based on the ug-locale npm library data.",
    version="2.0.0"
)

class Location(BaseModel):
    id: str
    name: str

class County(BaseModel):
    id: str
    name: str
    district: str

class SubCounty(BaseModel):
    id: str
    name: str
    county: str

class Parish(BaseModel):
    id: str
    name: str
    subcounty: str

class Village(BaseModel):
    id: str
    name: str
    parish: str

class UgandaLocaleComplete:
    def __init__(self):
        # GitHub URLs for the ug-locale data
        self.base_url = "https://raw.githubusercontent.com/paulgrammer/ug-locale/main"
        self.districts_data = None
        self.counties_data = None
        self.subcounties_data = None
        self.parishes_data = None
        self.villages_data = None
        self._load_data()

    def _load_data(self):
        """Load all data from the ug-locale repository"""
        try:
            print("Loading Uganda administrative data...")
            
            # Load districts
            districts_response = requests.get(f"{self.base_url}/districts.json")
            self.districts_data = districts_response.json()
            print(f"Loaded {len(self.districts_data)} districts")
            
            # Load counties
            counties_response = requests.get(f"{self.base_url}/counties.json")
            self.counties_data = counties_response.json()
            print(f"Loaded {len(self.counties_data)} counties")
            
            # Load subcounties
            subcounties_response = requests.get(f"{self.base_url}/subcounties.json")
            self.subcounties_data = subcounties_response.json()
            print(f"Loaded {len(self.subcounties_data)} subcounties")
            
            # Load parishes
            parishes_response = requests.get(f"{self.base_url}/parishes.json")
            self.parishes_data = parishes_response.json()
            print(f"Loaded {len(self.parishes_data)} parishes")
            
            # Load villages
            villages_response = requests.get(f"{self.base_url}/villages.json")
            self.villages_data = villages_response.json()
            print(f"Loaded {len(self.villages_data)} villages")
            
            print("All data loaded successfully!")
            
        except Exception as e:
            print(f"Error loading data: {e}")
            # Fallback to empty data if loading fails
            self.districts_data = []
            self.counties_data = []
            self.subcounties_data = []
            self.parishes_data = []
            self.villages_data = []

    @lru_cache(maxsize=None)
    def get_districts(self) -> List[dict]:
        """Get all districts"""
        return [{"id": d["id"], "name": d["name"]} for d in self.districts_data]

    @lru_cache(maxsize=None)
    def get_counties(self, district_id: str) -> List[dict]:
        """Get counties for a specific district"""
        return [
            {"id": c["id"], "name": c["name"]} 
            for c in self.counties_data 
            if c["district"] == district_id
        ]

    @lru_cache(maxsize=None)
    def get_sub_counties(self, county_id: str) -> List[dict]:
        """Get sub-counties for a specific county"""
        return [
            {"id": sc["id"], "name": sc["name"]} 
            for sc in self.subcounties_data 
            if sc["county"] == county_id
        ]

    @lru_cache(maxsize=None)
    def get_parishes(self, sub_county_id: str) -> List[dict]:
        """Get parishes for a specific sub-county"""
        return [
            {"id": p["id"], "name": p["name"]} 
            for p in self.parishes_data 
            if p["subcounty"] == sub_county_id
        ]

    @lru_cache(maxsize=None)
    def get_villages(self, parish_id: str) -> List[dict]:
        """Get villages for a specific parish"""
        return [
            {"id": v["id"], "name": v["name"]} 
            for v in self.villages_data 
            if v["parish"] == parish_id
        ]

    def find_district_by_id(self, district_id: str) -> Optional[dict]:
        """Find a district by ID"""
        return next((d for d in self.districts_data if d["id"] == district_id), None)

    def find_county_by_id(self, county_id: str) -> Optional[dict]:
        """Find a county by ID"""
        return next((c for c in self.counties_data if c["id"] == county_id), None)

    def find_subcounty_by_id(self, subcounty_id: str) -> Optional[dict]:
        """Find a sub-county by ID"""
        return next((sc for sc in self.subcounties_data if sc["id"] == subcounty_id), None)

    def find_parish_by_id(self, parish_id: str) -> Optional[dict]:
        """Find a parish by ID"""
        return next((p for p in self.parishes_data if p["id"] == parish_id), None)

    def get_stats(self) -> dict:
        """Get statistics about the data"""
        return {
            "districts": len(self.districts_data),
            "counties": len(self.counties_data),
            "subcounties": len(self.subcounties_data),
            "parishes": len(self.parishes_data),
            "villages": len(self.villages_data)
        }

# Initialize the locale service
print("Initializing Uganda Locale API with complete dataset...")
uga_locale = UgandaLocaleComplete()

@app.get("/", summary="API Information")
async def root():
    return {
        "message": "Uganda Locale API - Complete Dataset",
        "description": "Complete API for Uganda administrative divisions based on ug-locale npm library",
        "version": "2.0.0",
        "data_source": "https://github.com/paulgrammer/ug-locale",
        "endpoints": {
            "districts": "/districts",
            "counties": "/counties/{district_id}",
            "sub_counties": "/sub-counties/{county_id}",
            "parishes": "/parishes/{sub_county_id}",
            "villages": "/villages/{parish_id}",
            "stats": "/stats"
        },
        "stats": uga_locale.get_stats()
    }

@app.get("/districts", response_model=List[Location], summary="Get all districts")
async def get_districts():
    """
    Get all districts in Uganda.
    Returns the complete list of all 146+ districts.
    """
    districts = uga_locale.get_districts()
    return districts

@app.get("/counties/{district_id}", response_model=List[Location], summary="Get counties in a district")
async def get_counties(district_id: str):
    """
    Get all counties in the specified district.
    
    Example: /counties/5 returns counties in Gulu district
    """
    # Verify district exists
    district = uga_locale.find_district_by_id(district_id)
    if not district:
        raise HTTPException(
            status_code=404, 
            detail=f"District with id '{district_id}' not found"
        )
    
    counties = uga_locale.get_counties(district_id)
    return counties

@app.get("/sub-counties/{county_id}", response_model=List[Location], summary="Get sub-counties in a county")
async def get_sub_counties(county_id: str):
    """
    Get all sub-counties in the specified county.
    
    Example: /sub-counties/15 returns sub-counties in Aswa County
    """
    county = uga_locale.find_county_by_id(county_id)
    if not county:
        raise HTTPException(
            status_code=404, 
            detail=f"County with id '{county_id}' not found"
        )
    
    sub_counties = uga_locale.get_sub_counties(county_id)
    if not sub_counties:
        raise HTTPException(
            status_code=404, 
            detail=f"No sub-counties found for county '{county['name']}' (id: {county_id})"
        )
    return sub_counties

@app.get("/parishes/{sub_county_id}", response_model=List[Location], summary="Get parishes in a sub-county")
async def get_parishes(sub_county_id: str):
    """
    Get all parishes in the specified sub-county.
    
    Example: /parishes/38 returns parishes in a specific sub-county
    """
    subcounty = uga_locale.find_subcounty_by_id(sub_county_id)
    if not subcounty:
        raise HTTPException(
            status_code=404, 
            detail=f"Sub-county with id '{sub_county_id}' not found"
        )
    
    parishes = uga_locale.get_parishes(sub_county_id)
    if not parishes:
        raise HTTPException(
            status_code=404, 
            detail=f"No parishes found for sub-county '{subcounty['name']}' (id: {sub_county_id})"
        )
    return parishes

@app.get("/villages/{parish_id}", response_model=List[Location], summary="Get villages in a parish")
async def get_villages(parish_id: str):
    """
    Get all villages in the specified parish.
    
    Example: /villages/38 returns villages in a specific parish
    """
    parish = uga_locale.find_parish_by_id(parish_id)
    if not parish:
        raise HTTPException(
            status_code=404, 
            detail=f"Parish with id '{parish_id}' not found"
        )
    
    villages = uga_locale.get_villages(parish_id)
    if not villages:
        raise HTTPException(
            status_code=404, 
            detail=f"No villages found for parish '{parish['name']}' (id: {parish_id})"
        )
    return villages

@app.get("/stats", summary="Get data statistics")
async def get_stats():
    """
    Get statistics about the dataset.
    """
    return {
        "dataset": "Complete Uganda Administrative Divisions",
        "source": "https://github.com/paulgrammer/ug-locale",
        "stats": uga_locale.get_stats(),
        "data_collection": "Official Uganda Passport website",
        "last_updated": "2024"
    }

@app.get("/health", summary="Health check")
async def health_check():
    """
    Advanced health check with data validation.
    """
    stats = uga_locale.get_stats()
    is_healthy = all(count > 0 for count in stats.values())
    
    return {
        "status": "healthy" if is_healthy else "unhealthy",
        "message": "Uganda Locale API with complete dataset",
        "data_loaded": is_healthy,
        "stats": stats
    }

# Search endpoints (bonus features)
@app.get("/search/districts/{query}", summary="Search districts by name")
async def search_districts(query: str):
    """
    Search for districts by name (case-insensitive partial match).
    
    Example: /search/districts/gulu
    """
    query_lower = query.lower()
    districts = uga_locale.get_districts()
    matches = [
        district for district in districts 
        if query_lower in district["name"].lower()
    ]
    
    if not matches:
        raise HTTPException(
            status_code=404, 
            detail=f"No districts found matching '{query}'"
        )
    
    return matches

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)