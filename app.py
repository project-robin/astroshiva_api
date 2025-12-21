"""
FastAPI Web Server for Astro-Shiva API
High-performance async API for Vedic Astrology calculations
Deploy on Render with frontend on Vercel
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
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
    charts: Optional[List[str]] = Field(None, description="List of charts to generate (e.g. ['D1', 'D9'])")

    class Config:
        schema_extra = {
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
    timezone: Optional[str] = Query(None, description="Timezone offset"),
    charts: Optional[str] = Query(None, description="Comma-separated list of charts (e.g. 'D1,D9')")
):
    """Generate chart using GET parameters (alternative to POST)"""
    try:
        # CRITICAL FIX: Sanitize charts parameter
        # Strip quotes, whitespace, and special characters
        charts_list = None
        if charts:
            # Remove quotes, extra whitespace, and special characters
            import re
            from urllib.parse import unquote
            
            # First, decode URL encoding (e.g., %22 → ")
            decoded = unquote(charts)
            # Then remove quotes, spaces, and other artifacts
            sanitized = re.sub(r'["\'\s]+', '', decoded)
            
            if sanitized:
                # Split by comma and clean each chart name
                charts_list = [c.strip().upper() for c in sanitized.split(',') if c.strip()]
                # Validate chart names (D1-D60)
                valid_charts = []
                for chart in charts_list:
                    if re.match(r'^D\d{1,2}$', chart):
                        valid_charts.append(chart)
                charts_list = valid_charts if valid_charts else None
        
        # DEFAULT: If charts parameter is empty or malformed, return D1, D9, D10
        # actually, let's just leave it as None so engine returns ALL
        # if not charts_list:
        #    charts_list = ["D1", "D9", "D10"]
        
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


@app.get("/api/verify-calculations", tags=["Debugging"])
async def verify_calculations():
    """
    Verify ayanamsa and house calculations against AstroSage reference data.
    
    Reference Data (AstroSage for K - 26-05-2001, 21:48, Ahmednagar):
    - Ayanamsa: 023-52-34 (Lahiri)
    - Lagna: Sagittarius 19°54'38"
    - D9 Lagna: Aries
    """
    import traceback
    
    verification = {
        "reference": {
            "source": "AstroSage",
            "dob": "2001-05-26",
            "tob": "21:48:00",
            "place": "Ahmednagar (19°23'N, 74°39'E)",
            "ayanamsa": "023°52'34\" (Lahiri)",
            "d1_lagna": "Sagittarius 19°54'38\"",
            "d9_lagna": "Aries",
            "coordinates": {"lat": 19.3833, "lon": 74.65}
        },
        "our_calculation": {},
        "discrepancies": [],
        "root_cause_analysis": {},
        "swisseph_available": False
    }
    
    try:
        import swisseph as swe
        verification["swisseph_available"] = True
        
        # Birth data
        year, month, day = 2001, 5, 26
        hour, minute, second = 21, 48, 0
        timezone = 5.5
        
        # Two coordinate sets to compare
        coords = {
            "astrosage": {"lat": 19.3833, "lon": 74.65},
            "our_geocode": {"lat": 19.0948, "lon": 74.7489}
        }
        
        # Calculate UTC time
        utc_time = hour + minute/60 + second/3600 - timezone
        jd = swe.julday(year, month, day, utc_time)
        
        verification["our_calculation"]["julian_day"] = jd
        
        # 1. Ayanamsa value
        swe.set_sid_mode(swe.SIDM_LAHIRI)
        ayanamsa = swe.get_ayanamsa_ut(jd)
        
        def to_dms(deg):
            d = int(deg)
            m_full = (deg - d) * 60
            m = int(m_full)
            s = (m_full - m) * 60
            return f"{d}°{m}'{s:.2f}\""
        
        verification["our_calculation"]["ayanamsa"] = {
            "decimal": round(ayanamsa, 6),
            "dms": to_dms(ayanamsa),
            "reference_decimal": 23 + 52/60 + 34/3600,
            "difference_arcsec": round(abs(ayanamsa - (23 + 52/60 + 34/3600)) * 3600, 2)
        }
        
        # 2. House system calculations for both coordinate sets
        signs = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
                "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
        
        house_systems = {'P': 'Placidus', 'W': 'Whole Sign', 'E': 'Equal'}
        
        for coord_name, coord_vals in coords.items():
            verification["our_calculation"][f"lagna_{coord_name}"] = {}
            
            for code, name in house_systems.items():
                try:
                    swe.set_sid_mode(swe.SIDM_LAHIRI)
                    # FIXED: Use houses_ex with FLG_SIDEREAL for sidereal (Vedic) calculations
                    # swe.houses() returns tropical, houses_ex with sidereal flag returns sidereal
                    cusps, ascmc = swe.houses_ex(jd, coord_vals["lat"], coord_vals["lon"], bytes(code, 'utf-8'), swe.FLG_SIDEREAL)
                    lagna_total = ascmc[0]
                    sign_idx = int(lagna_total / 30)
                    sign_deg = lagna_total % 30
                    
                    verification["our_calculation"][f"lagna_{coord_name}"][name] = {
                        "sign": signs[sign_idx],
                        "degree": round(sign_deg, 4),
                        "total_degree": round(lagna_total, 4),
                        "dms": to_dms(sign_deg)
                    }
                except Exception as e:
                    verification["our_calculation"][f"lagna_{coord_name}"][name] = {"error": str(e)}
        
        # 3. D9 Navamsa calculation
        def calculate_navamsa_sign(lagna_total_deg):
            one_navamsa = 360 / 108  # 3.333... degrees
            navamsa_num = int(lagna_total_deg / one_navamsa)
            navamsa_sign = navamsa_num % 12
            return signs[navamsa_sign]
        
        # Calculate D9 for both coordinate sets using Placidus
        for coord_name, coord_vals in coords.items():
            try:
                swe.set_sid_mode(swe.SIDM_LAHIRI)
                # FIXED: Use houses_ex for sidereal calculation
                cusps, ascmc = swe.houses_ex(jd, coord_vals["lat"], coord_vals["lon"], b'P', swe.FLG_SIDEREAL)
                lagna_total = ascmc[0]
                d9_sign = calculate_navamsa_sign(lagna_total)
                verification["our_calculation"][f"d9_lagna_{coord_name}"] = d9_sign
            except Exception as e:
                verification["our_calculation"][f"d9_lagna_{coord_name}"] = {"error": str(e)}
        
        # 4. Discrepancy analysis
        reference_lagna_deg = 19 + 54/60 + 38/3600  # 19°54'38"
        our_lagna = verification["our_calculation"].get("lagna_astrosage", {}).get("Placidus", {})
        
        if "degree" in our_lagna:
            diff = abs(reference_lagna_deg - our_lagna["degree"])
            if diff > 0.5:  # More than 0.5 degrees difference
                verification["discrepancies"].append({
                    "field": "D1 Lagna Degree",
                    "reference": f"{reference_lagna_deg:.4f}° ({to_dms(reference_lagna_deg)})",
                    "our_value": f"{our_lagna['degree']:.4f}° ({our_lagna['dms']})",
                    "difference": f"{diff:.4f}° ({diff*60:.2f} arc-min)"
                })
        
        # Check D9 sign match
        ref_d9 = "Aries"
        our_d9 = verification["our_calculation"].get("d9_lagna_astrosage", "Unknown")
        if our_d9 != ref_d9:
            verification["discrepancies"].append({
                "field": "D9 Navamsa Lagna",
                "reference": ref_d9,
                "our_value": our_d9,
                "note": "D9 sign depends directly on D1 Lagna degree; ~3.33° change flips the sign"
            })
        
        # 5. Root cause analysis
        our_geocode_lagna = verification["our_calculation"].get("lagna_our_geocode", {}).get("Placidus", {})
        astrosage_lagna = verification["our_calculation"].get("lagna_astrosage", {}).get("Placidus", {})
        
        if "degree" in our_geocode_lagna and "degree" in astrosage_lagna:
            coord_diff = abs(our_geocode_lagna["degree"] - astrosage_lagna["degree"])
            verification["root_cause_analysis"]["coordinate_impact"] = {
                "lagna_with_our_coords": f"{our_geocode_lagna['sign']} {our_geocode_lagna['dms']}",
                "lagna_with_astrosage_coords": f"{astrosage_lagna['sign']} {astrosage_lagna['dms']}",
                "difference_from_coordinates": f"{coord_diff:.4f}° ({coord_diff*60:.2f} arc-min)",
                "conclusion": "Coordinate geocoding difference accounts for ~" + f"{coord_diff:.1f}° of discrepancy"
            }
        
        verification["root_cause_analysis"]["house_system"] = {
            "current": "Placidus",
            "note": "Traditional Vedic uses Whole Sign; AstroSage may use Equal or Placidus. Need to verify which matches reference."
        }
        
        # Recommendations
        verification["recommendations"] = [
            "1. Use AstroSage's exact coordinates (19.3833, 74.65) instead of geocoding 'Ahmednagar'",
            "2. Add ayanamsa_value to API response metadata for transparency",
            "3. Test with Equal house system if Placidus doesn't match reference",
            "4. D9 discrepancy is derivative of D1 Lagna discrepancy"
        ]
        
    except ImportError as e:
        verification["error"] = f"SwissEph not available: {e}"
    except Exception as e:
        verification["error"] = f"Calculation error: {e}"
        verification["traceback"] = traceback.format_exc()
    
    return verification

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
