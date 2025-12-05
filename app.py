"""
FastAPI Web Server for Astro-Shiva API
High-performance async API for Vedic Astrology calculations
Deploy on Render with frontend on Vercel
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from astro_engine import AstroEngine
import traceback

# Initialize FastAPI app
app = FastAPI(
    title="Astro-Shiva Vedic Astrology API",
    description="Free, local, offline Vedic Astrology calculations using jyotishganit",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS for Vercel frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "https://*.vercel.app",
        "https://*.vercel.com",
        "*"  # Allow all origins - restrict in production
    ],
    allow_credentials=True,
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
    latitude: float = Field(..., description="Latitude coordinate", example=40.7128)
    longitude: float = Field(..., description="Longitude coordinate", example=-74.0060)
    timezone: Optional[str] = Field(None, description="Timezone offset (e.g., +5.5)", example="+5.5")

    class Config:
        schema_extra = {
            "example": {
                "name": "K",
                "dob": "2001-05-26",
                "tob": "21:48:00",
                "place": "Ahmednagar, Maharashtra",
                "latitude": 19.0948,
                "longitude": 74.7489,
                "timezone": "+5.5"
            }
        }


class SuccessResponse(BaseModel):
    status: str = "success"
    data: Dict[str, Any]


class ErrorResponse(BaseModel):
    status: str = "error"
    error: str
    type: Optional[str] = None
    traceback: Optional[str] = None


# Routes
@app.get("/", tags=["Health"])
async def root():
    """API information and available endpoints"""
    return {
        "status": "online",
        "service": "Astro-Shiva Vedic Astrology API",
        "version": "2.0.0",
        "framework": "FastAPI",
        "deployment": "Render",
        "endpoints": {
            "/": "API info",
            "/health": "Health check",
            "/docs": "Interactive API documentation (Swagger UI)",
            "/redoc": "API documentation (ReDoc)",
            "/api/chart": "Generate birth chart (POST)",
            "/api/chart-get": "Generate chart via GET params",
            "/api/chart-test": "Test with sample data"
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
            timezone=request.timezone
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
                "error": str(e),
                "type": type(e).__name__,
                "traceback": traceback.format_exc()
            }
        )


@app.get("/api/chart-get", tags=["Astrology"])
async def generate_chart_get(
    name: str = Query(..., description="Person's name"),
    dob: str = Query(..., description="Date of birth (YYYY-MM-DD)"),
    tob: str = Query(..., description="Time of birth (HH:MM:SS)"),
    place: str = Query(..., description="Place of birth"),
    latitude: float = Query(..., description="Latitude"),
    longitude: float = Query(..., description="Longitude"),
    timezone: Optional[str] = Query(None, description="Timezone offset")
):
    """Generate chart using GET parameters (alternative to POST)"""
    try:
        chart = engine.generate_full_chart(
            name=name,
            dob=dob,
            tob=tob,
            place=place,
            latitude=latitude,
            longitude=longitude,
            timezone=timezone
        )
        
        return {"status": "success", "data": chart}
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "error": str(e),
                "type": type(e).__name__
            }
        )


@app.get("/api/chart-test", tags=["Testing"])
async def test_chart():
    """Test endpoint with sample data (K - 26-05-2001)"""
    try:
        print("🧪 Testing chart generation with sample data...")
        chart = engine.generate_full_chart(
            name="K",
            dob="2001-05-26",
            tob="21:48:00",
            place="Ahmednagar, Maharashtra",
            latitude=19.0948,
            longitude=74.7489,
            timezone="+5.5"
        )
        
        return {
            "status": "success",
            "message": "Test chart generated successfully for K (26-05-2001, 21:48, Ahmednagar)",
            "data": chart
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "error": str(e),
                "traceback": traceback.format_exc()
            }
        )


@app.get("/api/debug-swe", tags=["Debugging"])
async def debug_swe():
    """Debug Swisseph availability and error reporting"""
    import sys
    import subprocess
    
    debug_info = {
        "swisseph_import": False,
        "error": None,
        "sys_path": sys.path,
        "pip_list": []
    }
    
    # Check installed packages
    try:
        # Run pip list
        result = subprocess.run([sys.executable, "-m", "pip", "list"], capture_output=True, text=True)
        debug_info["pip_list"] = result.stdout.splitlines()
    except Exception as e:
        debug_info["pip_list_error"] = str(e)

    try:
        import swisseph as swe
        debug_info["swisseph_import"] = True
        debug_info["swe_file"] = swe.__file__
        
        # Test Calculation
        jd = swe.julday(2000, 1, 1, 12.0)
        res = swe.calc_ut(jd, swe.SUN, swe.FLG_SWIEPH | swe.FLG_SPEED)
        debug_info["test_calc"] = f"Success (SWIEPH): {res}"

    except ImportError as e:
        debug_info["error"] = f"ImportError: {e}"
        # Try finding it manually?
    except Exception as e:
        debug_info["error"] = f"Unexpected error: {str(e)}\n{traceback.format_exc()}"
        
    return debug_info

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
