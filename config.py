"""
Configuration module for Vedic Astrology Engine
"""

# Ayanamsa (precession correction) options
AYANAMSA_OPTIONS = {
    "LAHIRI": 1,           # Default, matches JHora/professional software
    "RAMAN": 5,
    "KRISHNAMURTI": 3,
    "USHA_SHASHI": 7,
    "FAGAN_BRADLEY": 9
}

# Default configuration
DEFAULT_CONFIG = {
    "ayanamsa": "LAHIRI",
    "timezone_auto": True,  # Auto-detect from lat/lon
    "precision": "minute",  # Can be "second", "minute", or "degree"
    "include_all_charts": True,
    "house_system": "Placidus"  # Placidus, Koch, Equal, Whole Sign
}

# Divisional charts configuration
DIVISIONAL_CHARTS = {
    "D1": {"name": "Rashi", "division": 1, "uses": "Basic personality"},
    "D2": {"name": "Hora", "division": 2, "uses": "Wealth"},
    "D3": {"name": "Drekkana", "division": 3, "uses": "Siblings"},
    "D4": {"name": "Chaturthamsa", "division": 4, "uses": "Property"},
    "D5": {"name": "Panchamsa", "division": 5, "uses": "Children"},
    "D6": {"name": "Shashthamsa", "division": 6, "uses": "Health"},
    "D7": {"name": "Saptamsa", "division": 7, "uses": "Spouse"},
    "D8": {"name": "Ashtamsa", "division": 8, "uses": "Longevity"},
    "D9": {"name": "Navamsa", "division": 9, "uses": "Marriage"},
    "D10": {"name": "Dasamsa", "division": 10, "uses": "Career"},
    "D12": {"name": "Dwadasamsa", "division": 12, "uses": "Parents"},
    "D16": {"name": "Shodasamsa", "division": 16, "uses": "Vehicles"},
    "D20": {"name": "Vimshamsa", "division": 20, "uses": "Spirituality"},
    "D24": {"name": "Chaturvimsamsa", "division": 24, "uses": "Education"},
    "D27": {"name": "Saptavimsamsa", "division": 27, "uses": "Physical body"},
    "D30": {"name": "Trimsamsa", "division": 30, "uses": "Misfortune"},
    "D40": {"name": "Khavedamsa", "division": 40, "uses": "Well-being"},
    "D45": {"name": "Akshavedamsa", "division": 45, "uses": "Auspiciousness"},
    "D60": {"name": "Shashtiamsa", "division": 60, "uses": "Karma"}
}

# Nakshatra names
NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashirsha",
    "Ardra", "Punarvasu", "Pushya", "Ashlesha", "Magha",
    "Purva Phalguni", "Uttara Phalguni", "Hasta", "Chitra", "Swati",
    "Vishakha", "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha",
    "Uttara Ashadha", "Shravana", "Dhanishtha", "Shatabhisha", "Purva Bhadrapada",
    "Uttara Bhadrapada", "Revati"
]

# Zodiac signs
ZODIAC_SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

# Planets
PLANETS = [
    "Sun", "Moon", "Mars", "Mercury", "Jupiter",
    "Venus", "Saturn", "Rahu", "Ketu"
]

# Dasha lords (in order of Vimshottari)
DASHA_LORDS = [
    "Ketu", "Venus", "Sun", "Moon", "Mars",
    "Rahu", "Jupiter", "Saturn", "Mercury"
]

# Dasha years (Vimshottari)
DASHA_YEARS = {
    "Ketu": 7,
    "Venus": 20,
    "Sun": 6,
    "Moon": 10,
    "Mars": 7,
    "Rahu": 18,
    "Jupiter": 16,
    "Saturn": 19,
    "Mercury": 17
}

# API response format for AI agents
AI_OUTPUT_TEMPLATE = {
    "version": "1.0",
    "status": "success",
    "data": {
        "timestamp": "",
        "person": {
            "name": "",
            "dob": "",
            "tob": "",
            "pob": "",
            "location": {"lat": 0.0, "lon": 0.0}
        },
        "charts": {},
        "analysis": {}
    }
}

# Strength indicators
STRENGTH_LEVELS = {
    "very_strong": {"min": 80, "max": 100},
    "strong": {"min": 60, "max": 79},
    "moderate": {"min": 40, "max": 59},
    "weak": {"min": 20, "max": 39},
    "very_weak": {"min": 0, "max": 19}
}
