"""
FastAPI Web Server for Astro-Shiva API
High-performance async API for Vedic Astrology calculations
Deployed on Render
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from astro_engine import AstroEngine

# Initialize FastAPI app
app = FastAPI(
    title="Astro-Shiva Vedic Astrology API",
    description="Free, local, offline Vedic Astrology calculations using jyotishganit",
    version="2.4.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS for API clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize astrology engine
engine = AstroEngine()


# Pydantic models for request/response validation
class ChartRequest(BaseModel):
    name: str = Field(..., description="Person's name")
    dob: str = Field(..., description="Date of birth (YYYY-MM-DD)", example="1990-01-15")
    tob: str = Field(..., description="Time of birth (HH:MM:SS)", example="12:30:00")
    place: str = Field(..., description="Place of birth", example="New York")
    latitude: float = Field(..., ge=-90, le=90, description="Latitude coordinate", example=40.7128)
    longitude: float = Field(..., ge=-180, le=180, description="Longitude coordinate", example=-74.0060)
    timezone: str = Field(..., description="Timezone offset (e.g., +5.5)", example="+5.5")
    charts: Optional[List[str]] = Field(None, description="List of charts to generate (e.g. ['D1', 'D9'])")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "K",
                "dob": "2001-05-26",
                "tob": "21:48:00",
                "place": "Ahmednagar, Maharashtra",
                "latitude": 19.0948,
                "longitude": 74.7489,
                "timezone": "+5.5",
                "charts": ["D1", "D9", "D10"]
            }
        }


class SuccessResponse(BaseModel):
    status: str = "success"
    data: Dict[str, Any]


# Routes
@app.get("/", tags=["Health"])
async def root():
    """API information and available endpoints"""
    return {
        "status": "online",
        "service": "Astro-Shiva Vedic Astrology API",
        "version": "2.4.0",
        "framework": "FastAPI",
        "deployment": "Render",
        "endpoints": {
            "/": "API info",
            "/health": "Health check",
            "/docs": "Interactive API documentation (Swagger UI)",
            "/redoc": "API documentation (ReDoc)",
            "/api/chart": "Generate birth chart (POST)",
            "/api/chart-get": "Generate chart via GET params",
        },
        "timestamp": datetime.now().isoformat()
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "astro-shiva-api"
    }


@app.post("/api/chart", response_model=SuccessResponse, tags=["Astrology"])
async def generate_chart(request: ChartRequest):
    """
    Generate complete Vedic astrology birth chart
    
    Returns:
    - All divisional charts (D1-D60)
    - Vimshottari Dasha
    - Shadbala & Ashtakavarga
    - Nakshatras
    - Panchang
    """
    try:
        chart = engine.generate_full_chart(
            name=request.name,
            dob=request.dob,
            tob=request.tob,
            place=request.place,
            latitude=request.latitude,
            longitude=request.longitude,
            timezone=request.timezone,
            charts=request.charts
        )
        
        return SuccessResponse(status="success", data=chart)
    
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail={
                "status": "error",
                "error": str(e),
                "type": "ValueError"
            }
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "error": "Chart generation failed",
                "type": type(e).__name__
            }
        )


@app.get("/api/chart-get", tags=["Astrology"])
async def generate_chart_get(
    name: str = Query(..., description="Person's name"),
    dob: str = Query(..., description="Date of birth (YYYY-MM-DD)"),
    tob: str = Query(..., description="Time of birth (HH:MM:SS)"),
    place: str = Query(..., description="Place of birth"),
    latitude: float = Query(..., ge=-90, le=90, description="Latitude"),
    longitude: float = Query(..., ge=-180, le=180, description="Longitude"),
    timezone: str = Query(..., description="Timezone offset"),
    charts: Optional[str] = Query(None, description="Comma-separated list of charts (e.g. 'D1,D9')")
):
    """Generate chart using GET parameters (alternative to POST)"""
    try:
        charts_list = None
        if charts:
            import re
            from urllib.parse import unquote

            decoded = unquote(charts)
            sanitized = re.sub(r'["\'\s]+', '', decoded)
            charts_list = [chart.upper() for chart in sanitized.split(',') if chart]
            if not charts_list:
                raise ValueError("At least one valid divisional chart must be requested.")
        
        chart = engine.generate_full_chart(
            name=name,
            dob=dob,
            tob=tob,
            place=place,
            latitude=latitude,
            longitude=longitude,
            timezone=timezone,
            charts=charts_list
        )
        
        return {"status": "success", "data": chart}
    
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail={
                "status": "error",
                "error": str(e),
                "type": "ValueError"
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "error": "Chart generation failed",
                "type": type(e).__name__
            }
        )


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    print("🚀 Astro-Shiva API starting...")
    print("📚 jyotishganit library loaded")
    print("✅ Ready to serve astrology charts!")


# For local development
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
