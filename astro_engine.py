"""
Vedic Astrology Engine - Local Free Implementation
Uses jyotishganit for 100% free, local, offline calculations
"""

import json
from datetime import datetime
from typing import Dict, Any, Optional, List

from jyotishganit import calculate_birth_chart, get_birth_chart_json
import math


class AstroEngine:
    """Main engine for Vedic Astrology calculations using jyotishganit"""
    
    def __init__(self):
        """Initialize the astrology engine"""
        self.current_chart = None
        self.birth_data = None
    
    def _parse_timezone(self, tz_str: Any) -> float:
        """Parse timezone string (e.g., '+5:30', '5.5') to float offset"""
        if tz_str is None:
            return None
            
        try:
            # If already a number
            if isinstance(tz_str, (int, float)):
                return float(tz_str)
                
            tz_str = str(tz_str).strip().upper().replace('GMT', '').replace('UTC', '')
            
            # Handle HH:MM format
            if ':' in tz_str:
                sign = -1 if tz_str.startswith('-') else 1
                tz_str = tz_str.replace('+', '').replace('-', '')
                parts = tz_str.split(':')
                hours = float(parts[0])
                minutes = float(parts[1]) if len(parts) > 1 else 0
                return sign * (hours + minutes / 60.0)
            
            # Handle float format
            return float(tz_str)
        except Exception as e:
            print(f"Warning: Error parsing timezone '{tz_str}': {e}")
            return None
    
    def generate_full_chart(
        self,
        name: str,
        dob: str,
        tob: str,
        place: str,
        latitude: float = None,
        longitude: float = None,
        timezone: str = None,
        charts: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Generate complete astrological chart for birth data
        
        Args:
            name: Person's name
            dob: Date of birth (YYYY-MM-DD)
            tob: Time of birth (HH:MM:SS)
            place: Place of birth (for reference only)
            latitude: Latitude coordinate (REQUIRED for accurate calculations)
            longitude: Longitude coordinate (REQUIRED for accurate calculations)
            timezone: GMT timezone offset as string (e.g., '+5.5' for IST, '-5.0' for EST)
                     If not provided, will be estimated from longitude
        
        Returns:
            Dictionary with complete chart data
        """
        try:
            # Validate required coordinates
            if latitude is None or longitude is None:
                raise ValueError(
                    "Latitude and Longitude are required for accurate astrological calculations. "
                    "Place name alone cannot provide precise astronomical positions."
                )
            
            # Parse date and time components
            year, month, day = dob.split('-')
            hour, minute, second = (tob.split(':') + ['0', '0'])[:3]
            
            # Create datetime object for birth time
            birth_datetime = datetime(
                int(year), int(month), int(day),
                int(hour), int(minute), int(second)
            )
            
            # Calculate timezone offset if not provided
            if timezone is None:
                # Rough approximation: 15 degrees longitude = 1 hour offset from GMT
                tz_offset = longitude / 15.0
                # Round to nearest 0.5 hour
                tz_offset = round(tz_offset * 2) / 2
            else:
                # Convert string timezone to float (handles +5:30, 5.5, etc.)
                tz_offset = self._parse_timezone(timezone)
                
                # Fallback to longitude-based estimate if parsing failed
                if tz_offset is None:
                    # Rough approximation: 15 degrees longitude = 1 hour offset from GMT
                    tz_offset = longitude / 15.0
                    # Round to nearest 0.5 hour
                    tz_offset = round(tz_offset * 2) / 2
            
            # Store birth data for reference
            self.birth_data = {
                'name': name,
                'place': place,
                'dob': dob,
                'tob': tob,
                'latitude': latitude,
                'longitude': longitude,
                'timezone_offset': tz_offset
            }
            
            # Generate chart using jyotishganit (for dashas, yogas, balas, etc.)
            chart = calculate_birth_chart(
                birth_date=birth_datetime,
                latitude=latitude,
                longitude=longitude,
                timezone_offset=tz_offset,
                location_name=place,
                name=name
            )
            
            # Store for reference
            self.current_chart = chart
            
            # Calculate Julian Day for SwissEph calculations
            try:
                import swisseph as swe
                utc_time = birth_datetime.hour - tz_offset + (birth_datetime.minute/60.0) + (birth_datetime.second/3600.0)
                jd_ut = swe.julday(birth_datetime.year, birth_datetime.month, birth_datetime.day, utc_time)
                
                # Use our custom SwissEph-based divisional chart engine
                divisional_charts = self._calculate_divisional_charts_swisseph(jd_ut, latitude, longitude, charts)
            except ImportError:
                # Fallback to jyotishganit if SwissEph not available
                divisional_charts = self._extract_divisional_charts(chart, charts_filter=charts)
            
            # Extract and format output
            output = {
                "user_details": {
                    "name": name,
                    "dob": dob,
                    "tob": tob,
                    "pob": place,
                    "latitude": latitude,
                    "longitude": longitude,
                    "timezone_offset": tz_offset,
                    "generated_at": datetime.now().isoformat()
                },
                "divisional_charts": divisional_charts,
                "balas": self._extract_balas(chart),
                "dashas": self._extract_dashas(chart),
                "nakshatra": self._extract_nakshatras(chart),
                "panchang": self._extract_panchang(chart),
                "yogas": self._extract_yogas(chart),
                "doshas": self._calculate_doshas(chart),
                "meta": {
                     "api_version": "2.3.0",
                     "calculation_method": "swisseph_parashara",
                     "ayanamsa": "Lahiri",
                     "engine": "astro-shiva-engine-v2.3",
                     "features": ["Jaimini", "KP", "Avasthas", "Transits", "Custom Varga Engine", 
                                  "Astronomical Details", "KP Cusps", "Yogini Dasha", "Char Dasha", "Bhavabala"]
                }
            }
            
            # Add Phase 1 enhancements: Astronomical Details, Sunrise/Sunset, KP Cusps
            try:
                output["astronomical_details"] = self._get_astronomical_constants(jd_ut, birth_datetime, tz_offset, longitude)
                output["sunrise_sunset"] = self._calculate_sunrise_sunset(jd_ut, latitude, longitude, tz_offset)
                
                # Get house cusps for KP calculation (already calculated in swisseph block)
                import swisseph as swe
                swe.set_sid_mode(swe.SIDM_LAHIRI)
                cusps, ascmc = swe.houses_ex(jd_ut, latitude, longitude, b'P', swe.FLG_SIDEREAL)
                output["kp_cusps"] = self._calculate_kp_cusps(list(cusps))
            except Exception as phase1_err:
                output["meta"]["phase1_error"] = str(phase1_err)
            
            # Add Phase 2 enhancements: Bhavabala, Yogini Dasha, Char Dasha
            try:
                # Extract Bhavabala from jyotishganit chart.charts structure
                if hasattr(chart, 'charts') and isinstance(chart.charts, dict):
                    output["bhavabala"] = self._extract_bhavabala(chart.charts)
                else:
                    # Try alternate access method
                    raw_data = getattr(chart, '_raw_data', None) or getattr(chart, 'charts', None)
                    if isinstance(raw_data, dict):
                        output["bhavabala"] = self._extract_bhavabala(raw_data)
                    else:
                        output["bhavabala"] = {"note": "Bhavabala requires jyotishganit chart data"}
                
                # Get Moon degree for Yogini Dasha
                moon_degree = None
                if "divisional_charts" in output and "D1" in output["divisional_charts"]:
                    moon_data = output["divisional_charts"]["D1"].get("planets", {}).get("Moon", {})
                    # FIX: Use total_degree which is the actual key from SwissEph calculation
                    moon_degree = moon_data.get("total_degree") or moon_data.get("longitude") or moon_data.get("full_degree")
                
                # Calculate Yogini Dasha
                output["yogini_dasha"] = self._calculate_yogini_dasha(birth_datetime, moon_degree=moon_degree)
                
                # Get D1 data for Char Dasha
                lagna_sign_idx = 0
                if "divisional_charts" in output and "D1" in output["divisional_charts"]:
                    d1_data = output["divisional_charts"]["D1"]
                    lagna_sign = d1_data.get("ascendant", {}).get("sign", "Aries")
                    signs = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
                             "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
                    if lagna_sign in signs:
                        lagna_sign_idx = signs.index(lagna_sign)

                # Get full planet data for Char Dasha strength calculation
                d1_planets_full = output["divisional_charts"]["D1"].get("planets", {})
                
                # Calculate Char Dasha with planet positions
                output["char_dasha"] = self._calculate_char_dasha(birth_datetime, lagna_sign_idx, d1_planets_full)

                # DEBUG PROBE: Dump chart structure to find Bhavabala
                try:
                    debug_info = {}
                    if hasattr(chart, '__dict__'):
                        debug_info["attrs"] = list(chart.__dict__.keys())
                    if hasattr(chart, 'charts'):
                        debug_info["charts_keys"] = list(chart.charts.keys()) if isinstance(chart.charts, dict) else str(type(chart.charts))
                    # Try to find anything with 'bala'
                    debug_info["bala_candidates"] = [a for a in dir(chart) if 'bala' in a.lower()]
                    output["debug_bhavabala"] = debug_info
                except:
                    pass
                
            except Exception as phase2_err:
                import traceback
                output["meta"]["phase2_error"] = str(phase2_err)
                output["meta"]["phase2_traceback"] = traceback.format_exc()
            
            # Enrich with additional calculations (KP, Avasthas, Transits, etc.)
            self._enrich_chart_data(output, birth_datetime, latitude, longitude, tz_offset)

            
            return output
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"DETAILED ERROR in generate_full_chart:\n{error_details}")
            raise ValueError(f"Error generating chart: {str(e)}")
    
    
    def _extract_divisional_charts(self, chart, charts_filter=None) -> Dict[str, Any]:
        """Extract divisional charts (D1-D60), optionally filtered"""
        charts_out = {}
        
        # Default to all if None
        # If specific list provided, always include D1
        target_charts = [c.upper() for c in charts_filter] if charts_filter else None
        
        try:
            # Create a map of D1 degrees for calculating Varga degrees
            d1_degrees = {}
            if hasattr(chart.d1_chart, 'planets'):
                for p in chart.d1_chart.planets:
                    # Ensure we have a float for degree
                    deg = 0.0
                    if hasattr(p, 'sign_degrees'):
                        deg = float(p.sign_degrees)
                    d1_degrees[p.celestial_body] = deg

            # D1 (Rashi chart) is main
            if not target_charts or 'D1' in target_charts:
                charts_out['D1'] = self._format_chart_data(chart.d1_chart, 'D1', d1_degrees)
            
            # D2-D60 divisional charts
            for chart_name, divisional_chart in chart.divisional_charts.items():
                c_name_upper = chart_name.upper()
                if target_charts and c_name_upper not in target_charts:
                    continue
                charts_out[c_name_upper] = self._format_chart_data(divisional_chart, c_name_upper, d1_degrees)
        except Exception as e:
            print(f"Warning: Could not extract all divisional charts: {e}")
        
        return charts_out
    
    def _calculate_varga_degree(self, d1_degree: float, harmonic: int) -> float:
        """Calculate planet's degree within a Varga sign"""
        # Range 0-30
        d1_deg_norm = d1_degree % 30.0
        
        # Determine strict harmonic calculation
        # This gives the degree PROPORTIONAL to the position in the subdivision
        # E.g. for D9 (3deg 20min arc), where is the planet in that arc?
        # That ratio is then mapped to 0-30.
        
        division_span = 30.0 / harmonic
        
        # Position within the specific subdivision (0 to division_span)
        rem = d1_deg_norm % division_span
        
        # Scale to 0-30
        varga_degree = (rem / division_span) * 30.0
        
        return varga_degree

    def _calculate_varga_ascendant(self, d1_asc_total_degree: float, harmonic: int) -> tuple:
        """
        Calculate the ascendant sign for a divisional chart (Varga) using Parashara rules.
        
        Args:
            d1_asc_total_degree: D1 Lagna total degree (0-360, sidereal)
            harmonic: The divisor (e.g., 9 for D9 Navamsa, 2 for D2 Hora, etc.)
        
        Returns:
            Tuple of (sign_name, sign_index_1based, degree_in_sign)
        """
        signs = ["", "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", 
                 "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
        
        # D1 sign (1-based)
        d1_sign = int(d1_asc_total_degree / 30) + 1
        d1_deg_in_sign = d1_asc_total_degree % 30
        
        # Division span within each sign
        division_span = 30.0 / harmonic
        
        # Which division (0-indexed) within the D1 sign does the Lagna fall?
        division_index = int(d1_deg_in_sign / division_span)
        
        # Calculate degree within the varga sign
        varga_degree = ((d1_deg_in_sign % division_span) / division_span) * 30.0
        
        # Default: Simple harmonic (used for most charts like D2, D3, D4, D7, D10, D12, etc.)
        # The varga sign is calculated by adding the division index to a start sign
        
        if harmonic == 9:  # D9 Navamsa - special rules
            # Navamsa starting signs based on D1 sign's element:
            # Fire (Aries=1, Leo=5, Sag=9): Start from Aries
            # Earth (Taurus=2, Virgo=6, Cap=10): Start from Capricorn  
            # Air (Gemini=3, Libra=7, Aqua=11): Start from Libra
            # Water (Cancer=4, Scorpio=8, Pisces=12): Start from Cancer
            
            if d1_sign in [1, 5, 9]:  # Fire signs
                start_sign = 1  # Aries
            elif d1_sign in [2, 6, 10]:  # Earth signs
                start_sign = 10  # Capricorn
            elif d1_sign in [3, 7, 11]:  # Air signs
                start_sign = 7  # Libra
            else:  # Water signs [4, 8, 12]
                start_sign = 4  # Cancer
            
            varga_sign = ((start_sign - 1) + division_index) % 12 + 1
            
        elif harmonic == 2:  # D2 Hora
            # Sun's Hora (Leo) for odd signs, Moon's Hora (Cancer) for even
            if d1_sign % 2 == 1:  # Odd sign
                varga_sign = 5 if division_index == 0 else 4  # Leo then Cancer
            else:  # Even sign
                varga_sign = 4 if division_index == 0 else 5  # Cancer then Leo
                
        elif harmonic == 3:  # D3 Drekkana
            # Each sign divided into 3 parts of 10 degrees
            # 1st Drekkana: Same sign, 2nd: 5th from it, 3rd: 9th from it
            if division_index == 0:
                varga_sign = d1_sign
            elif division_index == 1:
                varga_sign = ((d1_sign - 1 + 4) % 12) + 1  # 5th sign
            else:
                varga_sign = ((d1_sign - 1 + 8) % 12) + 1  # 9th sign
                
        else:
            # Generic calculation for other harmonics (D4, D7, D10, D12, D16, D20, D24, D27, D30, D40, D45, D60)
            # Formula: ((d1_sign - 1) * harmonic + division_index) % 12 + 1
            varga_sign = ((d1_sign - 1) * harmonic + division_index) % 12 + 1
        
        sign_name = signs[varga_sign] if 1 <= varga_sign <= 12 else "Unknown"
        
        return (sign_name, varga_sign, varga_degree)

    def _get_planet_varga_sign(self, total_degree: float, harmonic: int) -> tuple:
        """
        Calculate which sign a planet falls in for a divisional chart.
        Uses correct Parashara formulas for each varga type.
        
        Args:
            total_degree: Planet's total sidereal longitude (0-360)
            harmonic: Divisor (2 for D2, 9 for D9, etc.)
        
        Returns:
            Tuple of (sign_name, sign_index_1based, degree_in_varga_sign)
        """
        signs = ["", "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", 
                 "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
        
        d1_sign = int(total_degree / 30) + 1  # 1-based
        deg_in_sign = total_degree % 30
        division_span = 30.0 / harmonic
        division_index = int(deg_in_sign / division_span)
        varga_degree = ((deg_in_sign % division_span) / division_span) * 30.0
        
        if harmonic == 2:  # D2 Hora
            # First half = Sun's hora (Leo), Second half = Moon's hora (Cancer)
            # For odd signs: 0-15° = Leo, 15-30° = Cancer
            # For even signs: 0-15° = Cancer, 15-30° = Leo
            if d1_sign % 2 == 1:  # Odd sign
                varga_sign = 5 if deg_in_sign < 15 else 4
            else:
                varga_sign = 4 if deg_in_sign < 15 else 5
                
        elif harmonic == 3:  # D3 Drekkana
            if division_index == 0:
                varga_sign = d1_sign
            elif division_index == 1:
                varga_sign = ((d1_sign - 1 + 4) % 12) + 1
            else:
                varga_sign = ((d1_sign - 1 + 8) % 12) + 1
                
        elif harmonic == 9:  # D9 Navamsa
            # Starting sign based on element of D1 sign
            if d1_sign in [1, 5, 9]:  # Fire
                start = 1
            elif d1_sign in [2, 6, 10]:  # Earth
                start = 10
            elif d1_sign in [3, 7, 11]:  # Air
                start = 7
            else:  # Water
                start = 4
            varga_sign = ((start - 1) + division_index) % 12 + 1
            
        elif harmonic == 7:  # D7 Saptamsa
            # Odd signs: Count from same sign
            # Even signs: Count from 7th sign
            if d1_sign % 2 == 1:
                varga_sign = ((d1_sign - 1) + division_index) % 12 + 1
            else:
                start = ((d1_sign - 1 + 6) % 12) + 1  # 7th from d1_sign
                varga_sign = ((start - 1) + division_index) % 12 + 1
                
        elif harmonic == 10:  # D10 Dasamsa
            # Odd signs: Count from same sign
            # Even signs: Count from 9th sign
            if d1_sign % 2 == 1:
                varga_sign = ((d1_sign - 1) + division_index) % 12 + 1
            else:
                start = ((d1_sign - 1 + 8) % 12) + 1  # 9th from d1_sign
                varga_sign = ((start - 1) + division_index) % 12 + 1
                
        elif harmonic == 12:  # D12 Dwadasamsa
            # Count from same sign
            varga_sign = ((d1_sign - 1) + division_index) % 12 + 1
            
        elif harmonic == 16:  # D16 Shodasamsa
            # Movable signs: from Aries, Fixed: from Leo, Dual: from Sagittarius
            if d1_sign in [1, 4, 7, 10]:  # Movable
                start = 1
            elif d1_sign in [2, 5, 8, 11]:  # Fixed
                start = 5
            else:  # Dual
                start = 9
            varga_sign = ((start - 1) + division_index) % 12 + 1
            
        elif harmonic == 20:  # D20 Vimshamsa
            # Movable: Aries, Fixed: Sagittarius, Dual: Leo
            if d1_sign in [1, 4, 7, 10]:
                start = 1
            elif d1_sign in [2, 5, 8, 11]:
                start = 9
            else:
                start = 5
            varga_sign = ((start - 1) + division_index) % 12 + 1
            
        elif harmonic == 24:  # D24 Chaturvimshamsa
            # Odd signs: from Leo, Even signs: from Cancer
            if d1_sign % 2 == 1:
                start = 5
            else:
                start = 4
            varga_sign = ((start - 1) + division_index) % 12 + 1
            
        elif harmonic == 27:  # D27 Saptavimshamsa/Bhamsa
            # Fire: Aries, Earth: Cancer, Air: Libra, Water: Capricorn
            if d1_sign in [1, 5, 9]:
                start = 1
            elif d1_sign in [2, 6, 10]:
                start = 4
            elif d1_sign in [3, 7, 11]:
                start = 7
            else:
                start = 10
            varga_sign = ((start - 1) + division_index) % 12 + 1
            
        elif harmonic == 30:  # D30 Trimshamsa
            # Special rules based on degrees and odd/even sign
            if d1_sign % 2 == 1:  # Odd sign
                if deg_in_sign < 5:
                    varga_sign = 1  # Aries (Mars)
                elif deg_in_sign < 10:
                    varga_sign = 11  # Aquarius (Saturn)
                elif deg_in_sign < 18:
                    varga_sign = 9  # Sagittarius (Jupiter)
                elif deg_in_sign < 25:
                    varga_sign = 3  # Gemini (Mercury)
                else:
                    varga_sign = 7  # Libra (Venus)
            else:  # Even sign - reverse order
                if deg_in_sign < 5:
                    varga_sign = 2  # Taurus (Venus)
                elif deg_in_sign < 12:
                    varga_sign = 6  # Virgo (Mercury)
                elif deg_in_sign < 20:
                    varga_sign = 12  # Pisces (Jupiter)
                elif deg_in_sign < 25:
                    varga_sign = 10  # Capricorn (Saturn)
                else:
                    varga_sign = 8  # Scorpio (Mars)
                    
        else:  # Generic for D4, D40, D45, D60 etc.
            varga_sign = ((d1_sign - 1) * harmonic + division_index) % 12 + 1
        
        sign_name = signs[varga_sign] if 1 <= varga_sign <= 12 else "Unknown"
        return (sign_name, varga_sign, varga_degree)

    def _calculate_divisional_charts_swisseph(self, jd_ut: float, lat: float, lon: float, 
                                               charts_filter: list = None) -> Dict[str, Any]:
        """
        Calculate ALL divisional charts using Swiss Ephemeris directly.
        This replaces jyotishganit's divisional chart calculations with our own.
        
        Args:
            jd_ut: Julian Day in UT
            lat, lon: Geographic coordinates
            charts_filter: Optional list of charts to calculate (e.g., ['D1', 'D9'])
        
        Returns:
            Dictionary of divisional charts with full planet/house data
        """
        try:
            import swisseph as swe
        except ImportError:
            return {}
        
        swe.set_sid_mode(swe.SIDM_LAHIRI)
        
        signs = ["", "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", 
                 "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
        
        # All supported divisional charts
        all_charts = ['D1', 'D2', 'D3', 'D4', 'D7', 'D9', 'D10', 'D12', 
                      'D16', 'D20', 'D24', 'D27', 'D30', 'D40', 'D45', 'D60']
        
        target_charts = [c.upper() for c in charts_filter] if charts_filter else all_charts
        
        # 1. Calculate D1 Ascendant (sidereal)
        cusps, ascmc = swe.houses_ex(jd_ut, lat, lon, b'P', swe.FLG_SIDEREAL)
        d1_asc_total = ascmc[0]
        
        # 2. Calculate all planet positions
        planets_map = {
            'Sun': swe.SUN, 'Moon': swe.MOON, 'Mars': swe.MARS,
            'Mercury': swe.MERCURY, 'Jupiter': swe.JUPITER,
            'Venus': swe.VENUS, 'Saturn': swe.SATURN,
            'Rahu': swe.MEAN_NODE
        }
        
        planet_longitudes = {}  # Store total sidereal longitude for each planet
        planet_speeds = {}
        
        for p_name, p_id in planets_map.items():
            res = swe.calc_ut(jd_ut, p_id, swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED)
            
            # Handle different return formats
            if isinstance(res[0], (list, tuple)):
                deg_total = res[0][0]
                speed = res[0][3] if len(res[0]) > 3 else 0.0
            else:
                deg_total = res[0]
                speed = res[3] if len(res) > 3 else 0.0
            
            planet_longitudes[p_name] = deg_total
            planet_speeds[p_name] = speed
        
        # Add Ketu (180° from Rahu)
        planet_longitudes['Ketu'] = (planet_longitudes['Rahu'] + 180) % 360
        planet_speeds['Ketu'] = planet_speeds['Rahu']
        
        # 3. Build each divisional chart
        charts_out = {}
        
        for chart_name in target_charts:
            if chart_name not in all_charts:
                continue
                
            harmonic = int(chart_name[1:]) if chart_name.startswith('D') else 1
            
            # Calculate Varga Ascendant
            if harmonic == 1:
                varga_asc_sign = signs[int(d1_asc_total / 30) + 1]
                varga_asc_sign_idx = int(d1_asc_total / 30) + 1
                varga_asc_deg = d1_asc_total % 30
            else:
                varga_asc_sign, varga_asc_sign_idx, varga_asc_deg = self._calculate_varga_ascendant(d1_asc_total, harmonic)
            
            # Build planet data for this chart
            planets_data = {}
            for p_name, p_long in planet_longitudes.items():
                if harmonic == 1:
                    p_sign = signs[int(p_long / 30) + 1]
                    p_sign_idx = int(p_long / 30) + 1
                    p_deg = p_long % 30
                else:
                    p_sign, p_sign_idx, p_deg = self._get_planet_varga_sign(p_long, harmonic)
                
                # Calculate house (from varga ascendant)
                house = ((p_sign_idx - varga_asc_sign_idx) % 12) + 1
                
                planet_entry = {
                    "sign": p_sign,
                    "house": house,
                    "degree": p_deg,
                    "retrograde": planet_speeds[p_name] < 0
                }
                
                # Add extra data for D1
                if harmonic == 1:
                    planet_entry["total_degree"] = p_long
                    planet_entry["speed"] = planet_speeds[p_name]
                    planet_entry["nakshatra"] = self._get_nakshatra_name(p_long)
                    planet_entry["pada"] = self._get_nakshatra_pada(p_long)
                else:
                    planet_entry["nakshatra"] = None
                    planet_entry["pada"] = None
                
                planets_data[p_name] = planet_entry
            
            # Build houses data
            houses_data = []
            for i in range(1, 13):
                h_sign_idx = ((varga_asc_sign_idx - 1 + i - 1) % 12) + 1
                h_sign = signs[h_sign_idx]
                
                # Find occupants
                occupants = [p for p, data in planets_data.items() if data['house'] == i]
                
                house_entry = {
                    "house": i,
                    "sign": h_sign,
                    "lord": self._get_sign_lord(h_sign_idx),
                    "occupants": occupants
                }
                
                # Add cusps for D1
                if harmonic == 1 and i <= len(cusps):
                    house_entry["cusp"] = cusps[i-1] % 30
                    house_entry["total_degree"] = cusps[i-1]
                
                houses_data.append(house_entry)
            
            # Compile chart
            chart_data = {
                "ascendant": {
                    "sign": varga_asc_sign,
                    "lord": self._get_sign_lord(varga_asc_sign_idx),
                    "degree": varga_asc_deg
                },
                "planets": planets_data,
                "houses": houses_data
            }
            
            # Extra D1 data
            if harmonic == 1:
                chart_data["ascendant"]["total_degree"] = d1_asc_total
            
            charts_out[chart_name] = chart_data
        
        return charts_out

    def _get_nakshatra_name(self, total_degree: float) -> str:
        """Get nakshatra name from total sidereal degree"""
        nakshatras = [
            "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
            "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
            "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
            "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha",
            "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
        ]
        nak_span = 360.0 / 27.0  # 13.333...
        nak_idx = int(total_degree / nak_span) % 27
        return nakshatras[nak_idx]

    def _get_nakshatra_pada(self, total_degree: float) -> int:
        """Get nakshatra pada (1-4) from total sidereal degree"""
        nak_span = 360.0 / 27.0
        deg_in_nak = total_degree % nak_span
        pada_span = nak_span / 4.0
        return int(deg_in_nak / pada_span) + 1

    def _format_chart_data(self, chart_obj, chart_name="D1", d1_degrees=None) -> Dict[str, Any]:
        """Format individual chart data"""
        try:
            # Extract ascendant (first house)
            ascendant_sign = None
            ascendant_lord = None
            if chart_obj.houses and len(chart_obj.houses) > 0:
                ascendant_sign = chart_obj.houses[0].sign
                ascendant_lord = getattr(chart_obj.houses[0], 'lord', None)
            
            formatted = {
                "ascendant": {
                    "sign": ascendant_sign,
                    "lord": ascendant_lord,
                    # Fallback degree, will be enriched later for D1
                    "degree": None 
                },
                "planets": {},
                "houses": []
            }
            
            # Extract planet positions
            if hasattr(chart_obj, 'planets'):
                # For RasiChart (D1) which has explicit planets list
                for planet in chart_obj.planets:
                    dignity_val = getattr(planet, 'dignities', None)
                    dignity_clean = None
                    if dignity_val:
                        if isinstance(dignity_val, dict):
                            dignity_clean = dignity_val.get('dignity', 'neutral')
                        elif hasattr(dignity_val, 'dignity'):
                             dignity_clean = dignity_val.dignity
                        
                    formatted["planets"][planet.celestial_body] = {
                        "sign": planet.sign,
                        "degree": float(planet.sign_degrees) if hasattr(planet, 'sign_degrees') else None,
                        "nakshatra": planet.nakshatra,
                        "pada": planet.pada,
                        "house": planet.house,
                        "retrograde": getattr(planet, 'retrograde', False),
                        "dignity": dignity_clean,
                        "aspects": getattr(planet, 'aspects', {}),
                        "is_combust": False,
                        "speed": 0.0 # Will be populated enrichment
                    }
            else:
                # For DivisionalChart (D2-D60) which stores planets in houses
                harmonic = int(chart_name[1:]) if chart_name.startswith('D') and chart_name[1:].isdigit() else 1
                
                for house in chart_obj.houses:
                    for occupant in house.occupants:
                        p_name = occupant.celestial_body
                        
                        # Calculate Degree if D1 degrees available
                        varga_deg = None
                        if d1_degrees and p_name in d1_degrees:
                            varga_deg = self._calculate_varga_degree(d1_degrees[p_name], harmonic)
                        
                        formatted["planets"][p_name] = {
                            "sign": occupant.sign,
                            "house": house.number,
                            "degree": varga_deg,
                            "nakshatra": None, # Complex to calc for vargas, usually omitted
                            "pada": None,
                            "retrograde": False # Inherit from D1? Usually yes.
                        }
            
            # Extract houses
            for i, house in enumerate(chart_obj.houses, 1):
                house_data = {
                    "house": i,
                    "sign": house.sign,
                    "lord": getattr(house, 'lord', None),
                    "occupants": [p.celestial_body for p in house.occupants]
                }
                formatted["houses"].append(house_data)
            
            return formatted
        except Exception as e:
            return {"error": f"Could not format chart: {e}"}
    
    def _enrich_chart_data(self, output: Dict[str, Any], birth_datetime: datetime, lat: float, lon: float, tz_offset: float):
        """Use Swisseph directly to calculate missing data (Asc Degree, Speed, Cusps)"""
        try:
            try:
                import swisseph as swe
            except ImportError:
                # Can't calculate exact D1 details without swisseph backing
                # BUT we can leave them null/empty as jyotishganit output is the fallback
                # print("Warning: swisseph module not found. Skipping enrichment.")
                return

            # Calculate Julian Day
            # Convert timezone to hours from UTC
            # swe.julday expects UTC
            utc_time = birth_datetime.hour - tz_offset + (birth_datetime.minute/60.0)
            
            jd_ut = swe.julday(birth_datetime.year, birth_datetime.month, birth_datetime.day, utc_time)
            
            # Set Ayanamsa
            swe.set_sid_mode(swe.SIDM_LAHIRI)
            
            # 1. Exact Ascendant Degree (SIDEREAL/Vedic)
            # CRITICAL: Use houses_ex with FLG_SIDEREAL for Vedic calculations
            # swe.houses() returns TROPICAL, swe.houses_ex() with sidereal flag returns SIDEREAL
            cusps, ascmc = swe.houses_ex(jd_ut, lat, lon, b'P', swe.FLG_SIDEREAL) # Placidus + Sidereal
            
            asc_deg_total = ascmc[0]
            asc_sign_idx = int(asc_deg_total / 30)
            asc_deg_rem = asc_deg_total % 30
            
            # Note: Divisional chart ascendants are now calculated directly by
            # _calculate_divisional_charts_swisseph() - no need to recalculate here
                
            # 2. Enrich Houses with Cusps (additonal madhya calculations)
            if 'D1' in output['divisional_charts'] and 'houses' in output['divisional_charts']['D1']:
                for i, h_data in enumerate(output['divisional_charts']['D1']['houses']):
                    if i < len(cusps):
                        h_deg_total = cusps[i]
                        # Add madhya (midpoint) calculation
                        next_cusp = cusps[(i+1)%12]
                        if next_cusp < h_deg_total: next_cusp += 360
                        midpoint = (h_deg_total + next_cusp) / 2
                        h_data['madhya'] = midpoint % 30

            # 3. Enrich Planet Speeds
            planets_map = {
                'Sun': swe.SUN, 'Moon': swe.MOON, 'Mars': swe.MARS, 
                'Mercury': swe.MERCURY, 'Jupiter': swe.JUPITER, 
                'Venus': swe.VENUS, 'Saturn': swe.SATURN,
                'Rahu': swe.MEAN_NODE, 'Ketu': swe.MEAN_NODE # Ketu handled via offset
            }
            
            d1_planets = output['divisional_charts']['D1']['planets']
            planet_positions_deg = {} # For Maitri/Jaimini
            
            for p_name, p_id in planets_map.items():
                if p_name in d1_planets:
                    # Calc UT position
                    res = swe.calc_ut(jd_ut, p_id, swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED)
                    # res is (long, lat, dist, speed_long, speed_lat, speed_dist)
                    
                    deg_total = res[0]
                    deg_total = res[0]
                    # swe.calc_ut returns ((long, lat, dist, speed...), flags) in some bindings?
                    # Or res is (long, lat, dist, speed...). 
                    # If error was "tuple % int", then res[0] is a tuple.
                    # This implies res is ((long, ...), flags).
                    if isinstance(deg_total, tuple) or isinstance(deg_total, list):
                        deg_total = deg_total[0]
                        speed = res[0][3] if len(res[0]) > 3 else 0.0
                    else:
                        speed = res[3] if len(res) > 3 else 0.0
                    
                    # Normalize degree
                    if p_name == 'Ketu':
                        deg_total = (deg_total + 180.0) % 360.0
                    
                    deg_norm = deg_total % 30
                    sign_idx = int(deg_total / 30) + 1 # 1-based
                    
                    planet_positions_deg[p_name] = {"total_degree": deg_total, "sign": sign_idx, "degree": deg_norm}

                    if p_name == 'Ketu':
                        speed = speed # Node speed
                    
                    p_data = d1_planets[p_name]
                    p_data['speed'] = speed
                    p_data['speed_status'] = 'fast' if abs(speed) > self._get_avg_speed(p_name)*1.1 else ('slow' if abs(speed) < self._get_avg_speed(p_name)*0.9 else 'normal')
                    
                    # Update precise degrees if missing or rough
                    p_data['sign_id'] = sign_idx
                    p_data['degree'] = deg_norm
                    p_data['total_degree'] = deg_total
                    
                    # --- NEW: KP System ---
                    kp_info = self._calculate_kp_details(deg_total)
                    p_data['kp'] = kp_info

                    # --- NEW: Avasthas ---
                    p_data['avasthas'] = self._calculate_avasthas(p_name, deg_norm, sign_idx, p_data.get('dignities', {}).get('dignity', 'neutral'))

            # --- NEW: Jaimini Karakas ---
            output['jaimini_karakas'] = self._calculate_jaimini_karakas(d1_planets)
            
            # --- NEW: Panchadha Maitri ---
            output['panchadha_maitri'] = self._calculate_panchadha_maitri(planet_positions_deg)

            # --- NEW: Transits ---
            output['current_transits'] = self._calculate_transits(output['divisional_charts']['D1']['ascendant']['sign'], output['divisional_charts']['D1']['planets']['Moon']['sign'])

        except Exception as e:
             import traceback
             print(f"Enrichment Error: {e}")
             trace = traceback.format_exc()
             output['meta']['enrichment_error'] = f"{str(e)} | {trace}"
             # pass
        
    def _calculate_jaimini_karakas(self, planets_data):
        """Calculate 7 Chara Karakas based on degrees"""
        # Exclude Rahu/Ketu for 7-karaka scheme
        candidates = []
        for p_name in ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn']:
            if p_name in planets_data:
                deg = planets_data[p_name].get('degree', 0)
                # Jaimini uses degrees within sign (0-30), seconds matter
                candidates.append({'name': p_name, 'degree': deg})
        
        # Sort descending
        candidates.sort(key=lambda x: x['degree'], reverse=True)
        
        karakas = {}
        names = ['Atmakaraka', 'Amatyakaraka', 'Bhratrukaraka', 'Matrukaraka', 'Putrakaraka', 'Gnatikaraka', 'Darakaraka']
        
        for i, k_name in enumerate(names):
            if i < len(candidates):
                karakas[k_name] = {
                    "planet": candidates[i]['name'],
                    "description": self._get_karaka_description(k_name)
                }
        return karakas

    def _get_karaka_description(self, k_name):
        return {
            'Atmakaraka': 'Significator of the Soul/Self',
            'Amatyakaraka': 'Significator of Career/Minister',
            'Bhratrukaraka': 'Significator of Siblings/Guru',
            'Matrukaraka': 'Significator of Mother',
            'Putrakaraka': 'Significator of Children',
            'Gnatikaraka': 'Significator of Relations/Enemies',
            'Darakaraka': 'Significator of Spouse',
        }.get(k_name, '')

    def _calculate_avasthas(self, planet, degree_in_sign, sign_num, dignity_str):
        """Calculate Baaladi (Age) and Jagradadi (Alertness) Avasthas"""
        avasthas = {"baaladi": {}, "jagradadi": {}}
        
        # 1. Baaladi (Age)
        # Odd Signs: 1, 3, 5, 7, 9, 11
        is_odd = (sign_num % 2 != 0)
        
        states = ["Infant (Baala)", "Young (Kumara)", "Adolescent (Yuva)", "Old (Vriddha)", "Dead (Mrita)"]
        
        # 0-6, 6-12, 12-18, 18-24, 24-30
        idx = int(degree_in_sign / 6)
        if idx > 4: idx = 4
        
        if not is_odd:
            # Reverse order for even signs
            idx = 4 - idx
            
        avasthas["baaladi"] = {
            "state": states[idx].split(' ')[0], 
            "full_name": states[idx]
        }
        
        # 2. Jagradadi (Alertness)
        # Awake: Own/Exalted, Dreaming: Friend/Neutral, Sleep: Enemy/Debilitated
        state_jag = "Dreaming" # Default
        dignity = str(dignity_str).lower()
        
        if "exalted" in dignity or "own" in dignity or "moolatrikona" in dignity:
            state_jag = "Awake"
        elif "debilitated" in dignity or "enemy" in dignity or "great_enemy" in dignity:
             state_jag = "Asleep"
        
        avasthas["jagradadi"] = {"state": state_jag}
        
        return avasthas

    def _calculate_kp_details(self, total_degree):
        """Calculate KP Star Lord, Sub Lord, Sub-Sub Lord"""
        # Nakshatra span = 13 deg 20 min = 13.3333 deg
        # Total 360 deg / 27 = 13.3333
        nak_span = 360.0 / 27.0
        
        nak_idx = int(total_degree / nak_span)
        # deg_in_nak = total_degree % nak_span
        
        # Lords sequence (starting from Ashwini/Ketu)
        # KET, VEN, SUN, MON, MAR, RAH, JUP, SAT, MER
        meta_lords = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
        dasha_years = {"Ketu": 7, "Venus": 20, "Sun": 6, "Moon": 10, "Mars": 7, "Rahu": 18, "Jupiter": 16, "Saturn": 19, "Mercury": 17}
        total_years = 120
        
        # Star Lord
        star_lord = meta_lords[nak_idx % 9]
        
        # Sub Lord calculation
        # The nakshatra (13.33 deg) is divided in proportion to Dasha years
        # We need to find which slice 'deg_in_nak' falls into.
        # The sequence of sub-lords starts from the Star Lord itself.
        
        start_lord_idx = meta_lords.index(star_lord)
        
        remaining_deg = total_degree % nak_span
        current_deg_pointer = 0.0
        
        sub_lord = None
        sub_sub_lord = None
        
        # Find Sub Lord
        for i in range(9):
            idx = (start_lord_idx + i) % 9
            l_name = meta_lords[idx]
            years = dasha_years[l_name]
            
            # Span = (Years / 120) * 13.3333
            span = (years / total_years) * nak_span
            
            if current_deg_pointer + span >= remaining_deg:
                sub_lord = l_name
                
                # Setup for Sub-Sub Lord
                # We need position WITHIN this sub-lord span
                deg_in_sub = remaining_deg - current_deg_pointer
                
                # Iterate again for SS Lord
                ss_pointer = 0.0
                ss_start_idx = idx # Starts from Sub Lord
                
                for j in range(9):
                    idx_ss = (ss_start_idx + j) % 9
                    ss_name = meta_lords[idx_ss]
                    years_ss = dasha_years[ss_name]
                    
                    # Span of SS = (Years / 120) * Sub-Lord-Span
                    span_ss = (years_ss / total_years) * span
                    
                    if ss_pointer + span_ss >= deg_in_sub:
                        sub_sub_lord = ss_name
                        break
                    ss_pointer += span_ss
                
                break
            
            current_deg_pointer += span
            
        return {
            "sign_lord": self._get_sign_lord(int(total_degree/30)+1),
            "nakshatra_lord": star_lord,
            "sub_lord": sub_lord,
            "sub_sub_lord": sub_sub_lord
        }

    def _get_sign_lord(self, sign_num):
        # 1-12
        lords = [None, "Mars", "Venus", "Mercury", "Moon", "Sun", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Saturn", "Jupiter"]
        if 1 <= sign_num <= 12: return lords[sign_num]
        return None

    def _calculate_panchadha_maitri(self, planet_deg_map):
        """Calculate 5-fold friendship matrix"""
        # Natural Relationships (Naisargik)
        natural = {
            "Sun": {"friends": ["Moon", "Mars", "Jupiter"], "enemies": ["Venus", "Saturn"]},
            "Moon": {"friends": ["Sun", "Mercury"], "enemies": []}, # Rest neutral
            "Mars": {"friends": ["Sun", "Moon", "Jupiter"], "enemies": ["Mercury"]},
            "Mercury": {"friends": ["Sun", "Venus"], "enemies": ["Moon"]},
            "Jupiter": {"friends": ["Sun", "Moon", "Mars"], "enemies": ["Mercury", "Venus"]},
            "Venus": {"friends": ["Mercury", "Saturn"], "enemies": ["Sun", "Moon"]},
            "Saturn": {"friends": ["Mercury", "Venus"], "enemies": ["Sun", "Moon", "Mars"]}
        }
        
        matrix = {}
        for p1 in natural.keys():
            if p1 not in planet_deg_map: continue
            
            matrix[p1] = {}
            for p2 in natural.keys():
                if p1 == p2: continue
                if p2 not in planet_deg_map: continue
                
                # 1. Natural
                nat_rel = "Neutral"
                if p2 in natural[p1]["friends"]: nat_rel = "Friend"
                elif p2 in natural[p1]["enemies"]: nat_rel = "Enemy"
                
                # 2. Temporary (Tatkalik)
                # Friends in 2, 3, 4, 10, 11, 12 from p1
                h1 = planet_deg_map[p1]["sign"]
                h2 = planet_deg_map[p2]["sign"]
                
                diff = (h2 - h1) % 12
                if diff < 0: diff += 12
                house_pos = diff + 1
                
                tat_rel = "Enemy"
                if house_pos in [2, 3, 4, 10, 11, 12]:
                    tat_rel = "Friend"
                
                # 3. Combined
                score = 0
                if nat_rel == "Friend": score += 1
                elif nat_rel == "Enemy": score -= 1
                
                if tat_rel == "Friend": score += 1
                elif tat_rel == "Enemy": score -= 1
                
                final_rel = "Neutral"
                if score >= 2: final_rel = "Great Friend"
                elif score == 1: final_rel = "Friend"
                elif score == 0: final_rel = "Neutral"
                elif score == -1: final_rel = "Enemy"
                elif score <= -2: final_rel = "Great Enemy"
                
                matrix[p1][p2] = final_rel
        return matrix

    def _calculate_transits(self, birth_asc_sign, birth_moon_sign):
        """Calculate current transit positions"""
        transits = {}
        try:
            import swisseph as swe
            now = datetime.now()
            # UTC conversion approx
            jd_now = swe.julday(now.year, now.month, now.day, now.hour + now.minute/60.0)
            
            planets = {
                'Sun': swe.SUN, 'Moon': swe.MOON, 'Mars': swe.MARS, 
                'Mercury': swe.MERCURY, 'Jupiter': swe.JUPITER, 
                'Venus': swe.VENUS, 'Saturn': swe.SATURN, 'Rahu': swe.MEAN_NODE, 'Ketu': swe.MEAN_NODE
            }
            
            swe.set_sid_mode(swe.SIDM_LAHIRI)
            
            signs = ["", "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
            
            # Store Rahu position for Ketu calculation
            rahu_longitude = None
            
            for p_name, p_id in planets.items():
                # CRITICAL FIX: Calculate Ketu as 180° opposite to Rahu
                if p_name == 'Ketu':
                    if rahu_longitude is None:
                        # Calculate Rahu first if not done yet
                        continue
                    # Ketu is exactly 180° opposite to Rahu
                    deg_total = (rahu_longitude + 180) % 360
                    speed = 0.0  # Ketu moves with Rahu but opposite
                else:
                    res = swe.calc_ut(jd_now, p_id, swe.FLG_SWIEPH | swe.FLG_SIDEREAL)
                    
                    # Compatibility fix
                    data_tuple = res
                    if isinstance(res[0], (list, tuple)):
                        data_tuple = res[0]
                    
                    deg_total = data_tuple[0]
                    speed = data_tuple[3] if len(data_tuple) > 3 else 0.0
                    
                    # Store Rahu longitude for Ketu calculation
                    if p_name == 'Rahu':
                        rahu_longitude = deg_total
                
                sign_num = int(deg_total / 30) + 1
                deg_rem = deg_total % 30
                
                sign_name = signs[sign_num] if 1 <= sign_num <= 12 else "Unknown"
                
                # Reference to Birth Moon (Rashi)
                from_moon = (sign_num - self._get_sign_num(birth_moon_sign)) % 12
                if from_moon < 0: from_moon += 12
                house_from_moon = from_moon + 1
                
                transits[p_name] = {
                    "current_sign": sign_name,
                    "current_degree": deg_rem,
                    "house_from_birth_moon": house_from_moon,
                    "is_retrograde": speed < 0
                }
            
            # Handle Ketu if it was skipped (process it now with Rahu's position)
            if 'Ketu' not in transits and rahu_longitude is not None:
                deg_total = (rahu_longitude + 180) % 360
                sign_num = int(deg_total / 30) + 1
                deg_rem = deg_total % 30
                sign_name = signs[sign_num] if 1 <= sign_num <= 12 else "Unknown"
                
                from_moon = (sign_num - self._get_sign_num(birth_moon_sign)) % 12
                if from_moon < 0: from_moon += 12
                house_from_moon = from_moon + 1
                
                transits['Ketu'] = {
                    "current_sign": sign_name,
                    "current_degree": deg_rem,
                    "house_from_birth_moon": house_from_moon,
                    "is_retrograde": False
                }
                
        except Exception as e:
            # print(f"Transit Error: {e}")
            import traceback
            # print(f"Transit Error Trace: {traceback.format_exc()}")
            transits["error"] = str(e)
            pass
            
        return transits

    def _get_sign_num(self, sign_name):
        signs = {
           "Aries": 1, "Taurus": 2, "Gemini": 3, "Cancer": 4, 
           "Leo": 5, "Virgo": 6, "Libra": 7, "Scorpio": 8, 
           "Sagittarius": 9, "Capricorn": 10, "Aquarius": 11, "Pisces": 12
        }
        return signs.get(sign_name, 1) # Default 1
        
    def _get_avg_speed(self, planet_name):
        return {
            'Sun': 0.9856, 'Moon': 13.176, 'Mars': 0.524, 
            'Mercury': 4.09, 'Jupiter': 0.083, 'Venus': 1.6, 
            'Saturn': 0.034, 'Rahu': 0.053, 'Ketu': 0.053
        }.get(planet_name, 1.0)
    
    def _extract_balas(self, chart) -> Dict[str, Any]:
        """Extract Shadbala and Ashtakavarga"""
        balas = {
            "shadbala": {},
            "ashtakavarga": {}
        }
        
        try:
            # Extract Shadbala for each planet
            for planet in chart.d1_chart.planets:
                if hasattr(planet, 'shadbala') and planet.shadbala:
                    balas['shadbala'][planet.celestial_body] = planet.shadbala
            
            # Extract Ashtakavarga
            if hasattr(chart, 'ashtakavarga') and chart.ashtakavarga:
                balas['ashtakavarga'] = {
                    'sav': chart.ashtakavarga.sav,  # Sarvashtakavarga
                    'bhav': chart.ashtakavarga.bhav  # Bhinnashtakavarga
                }
        except Exception as e:
            print(f"Warning: Could not extract balas: {e}")
        
        return balas
    
    def _extract_dashas(self, chart) -> Dict[str, Any]:
        """Extract Vimshottari Dasha and other dashas"""
        dashas = {
            "vimshottari": {
                "mahadasha": [],
                "current_dasha": None
            }
        }
        
        try:
            if hasattr(chart, 'dashas') and chart.dashas:
                # Current dasha
                if hasattr(chart.dashas, 'current'):
                    dashas['vimshottari']['current_dasha'] = chart.dashas.current
                
                # Extract full list of Antardashas for the CURRENT Mahadasha
                current_mahadasha_lord = None
                
                print(f"DEBUG: chart.dashas type: {type(chart.dashas)}")
                if hasattr(chart.dashas, 'all'):
                     print(f"DEBUG: chart.dashas.all keys: {chart.dashas.all.keys() if isinstance(chart.dashas.all, dict) else 'Not a dict'}")
                else:
                     print("DEBUG: chart.dashas.all MISSING")

                # Robustly find current MD lord
                current_obj = chart.dashas.current
                if hasattr(current_obj, 'mahadashas'):
                    # It's an object
                    if current_obj.mahadashas:
                        current_mahadasha_lord = list(current_obj.mahadashas.keys())[0]
                elif isinstance(current_obj, dict) and 'mahadashas' in current_obj:
                    # It's a dict
                    if current_obj['mahadashas']:
                         current_mahadasha_lord = list(current_obj['mahadashas'].keys())[0]
                
                if current_mahadasha_lord and hasattr(chart.dashas, 'all'):
                    all_dashas = chart.dashas.all
                    
                    # Fix: 'all' contains 'mahadashas' key first
                    target_mahadashas = None
                    if 'mahadashas' in all_dashas:
                        target_mahadashas = all_dashas['mahadashas']
                    elif isinstance(all_dashas, dict) and current_mahadasha_lord in all_dashas:
                        # Maybe legacy structure?
                        target_mahadashas = all_dashas

                    if target_mahadashas and current_mahadasha_lord in target_mahadashas:
                        md_data = target_mahadashas[current_mahadasha_lord]
                        
                        # Now look for 'antardashas' inside the MD data
                        antardashas_data = None
                        if isinstance(md_data, dict) and 'antardashas' in md_data:
                            antardashas_data = md_data['antardashas']
                        elif hasattr(md_data, 'antardashas'):
                            antardashas_data = md_data.antardashas
                        
                        if antardashas_data:
                            # Iterate through antardashas
                            antardashas_list = []
                            
                            # Check if antardashas_data is a dict
                            if isinstance(antardashas_data, dict):
                                for ad_lord, ad_data in antardashas_data.items():
                                     start_val = ""
                                     end_val = ""
                                     
                                     # ad_data might be a dict with start/end or an object
                                     if isinstance(ad_data, dict):
                                         start_val = str(ad_data.get('start', ''))
                                         end_val = str(ad_data.get('end', ''))
                                     elif hasattr(ad_data, 'start'):
                                         start_val = str(ad_data.start)
                                         end_val = str(getattr(ad_data, 'end', ''))
                                         
                                     antardashas_list.append({
                                         "lord": ad_lord,
                                         "start": start_val,
                                         "end": end_val
                                     })
                            
                            # Sort by start date
                            try:
                                antardashas_list.sort(key=lambda x: x['start'])
                            except:
                                pass
                                
                            # Add to response
                            dashas['vimshottari']['antardashas_in_current_mahadasha'] = antardashas_list

                # Keep the generic Mahadasha list as well
                if hasattr(chart.dashas, 'upcoming'):
                    upcoming = chart.dashas.upcoming
                    if isinstance(upcoming, dict) and 'mahadashas' in upcoming:
                        for lord, period in upcoming['mahadashas'].items():
                            dashas['vimshottari']['mahadasha'].append({
                                "lord": lord,
                                "start_date": str(period.get('start', '')),
                                "end_date": str(period.get('end', ''))
                            })
        except Exception as e:
            print(f"Warning: Could not extract dashas: {e}")
        
        return dashas

    def _calculate_doshas(self, chart) -> Dict[str, Any]:
        """Calculate Manglik, Kaal Sarp, and other doshas"""
        doshas = {
            "manglik": {"present": False, "type": None},
            "kaal_sarp": {"present": False, "type": None},
            "pitra_dosha": {"present": False}
        }
        
        try:
            planets = {p.celestial_body: p for p in chart.d1_chart.planets}
            
            # Sign Map
            signs = {
                "Aries": 1, "Taurus": 2, "Gemini": 3, "Cancer": 4, 
                "Leo": 5, "Virgo": 6, "Libra": 7, "Scorpio": 8, 
                "Sagittarius": 9, "Capricorn": 10, "Aquarius": 11, "Pisces": 12
            }
            
            # --- Manglik ---
            # Mars in 1, 2, 4, 7, 8, 12 from Lagna
            if "Mars" in planets:
                mars_house = planets["Mars"].house
                if mars_house in [1, 2, 4, 7, 8, 12]:
                    doshas["manglik"] = {
                        "present": True,
                        "type": "High" if mars_house in [1, 7, 8] else "Low", 
                        "description": f"Mars in house {mars_house}"
                    }
            
            # --- Kaal Sarp ---
            # All planets between Rahu and Ketu
            if "Rahu" in planets and "Ketu" in planets:
                rahu = planets["Rahu"]
                ketu = planets["Ketu"]
                
                # Helper to get lon
                def get_lon(p):
                    s_num = signs.get(p.sign, 1)
                    deg = float(p.sign_degrees) 
                    return deg + (s_num - 1) * 30

                r_long = get_lon(rahu)
                k_long = get_lon(ketu)
                
                # Check containment
                all_between_rk = True
                all_between_kr = True
                
                for p_name, p in planets.items():
                    if p_name in ["Rahu", "Ketu", "Uranus", "Neptune", "Pluto"]: continue
                    
                    p_long = get_lon(p)
                    
                    # Normalizing to 0-360 checks
                    # Case 1: R -> K (Direct path in zodiac order)
                    if r_long < k_long:
                        if not (r_long <= p_long <= k_long): all_between_rk = False
                    else:
                        if not (p_long >= r_long or p_long <= k_long): all_between_rk = False
                        
                    # Case 2: K -> R
                    if k_long < r_long:
                        if not (k_long <= p_long <= r_long): all_between_kr = False
                    else:
                        if not (p_long >= k_long or p_long <= r_long): all_between_kr = False
                
                if all_between_rk or all_between_kr:
                    doshas["kaal_sarp"] = {
                        "present": True,
                        "type": "Anant" if all_between_rk else "Kulik", # Simplified type
                        "description": "All planets hemmed between Rahu and Ketu"
                    }

        except Exception as e:
            print(f"Warning: Error calculating doshas: {e}")
            
        return doshas

    def _extract_yogas(self, chart) -> Dict[str, Any]:
        """Calculate and extract comprehensive Yogas"""
        yogas = {
            "raja_yogas": [],
            "dhana_yogas": [],
            "other_yogas": []
        }
        
        try:
            planets = {p.celestial_body: p for p in chart.d1_chart.planets}
            
            # Helpers
            def get_house(p_name): return planets[p_name].house if p_name in planets else 0
            
            # 1. Gajakesari Yoga (Jupiter in Kendra from Moon)
            if "Moon" in planets and "Jupiter" in planets:
                moon_h = get_house("Moon")
                jup_h = get_house("Jupiter")
                # House diff (1-based)
                diff = (jup_h - moon_h) % 12
                if diff < 0: diff += 12
                dist_from_moon = diff + 1
                
                if dist_from_moon in [1, 4, 7, 10]:
                    yogas["other_yogas"].append({
                        "name": "Gajakesari Yoga",
                        "description": "Jupiter in Kendra from Moon. Gives wealth, fame, and virtue."
                    })

            # 2. Budhaditya Yoga (Sun + Mercury)
            if "Sun" in planets and "Mercury" in planets:
                if planets["Sun"].sign == planets["Mercury"].sign:
                     yogas["raja_yogas"].append({
                        "name": "Budhaditya Yoga",
                        "description": "Sun and Mercury in the same sign. Gives intelligence and skill."
                    })
                    
            # 3. Chandra Mangala Yoga (Moon + Mars)
            if "Moon" in planets and "Mars" in planets:
                 if planets["Moon"].sign == planets["Mars"].sign:
                      yogas["dhana_yogas"].append({
                        "name": "Chandra Mangala Yoga",
                        "description": "Moon and Mars conjunct. Earnings through enterprise."
                    })
            
            # 4. Amala Yoga (Benefic in 10th from Lagna/Moon)
            benefics = ["Jupiter", "Venus", "Mercury"] # Simplified
            for b in benefics:
                if b in planets:
                    if planets[b].house == 10:
                        yogas["other_yogas"].append({
                            "name": "Amala Yoga",
                            "description": f"Benefic {b} in 10th house. Gives lasting fame and reputation."
                        })
                    
                    if "Moon" in planets:
                        moon_h = get_house("Moon")
                        b_h = planets[b].house
                        dist = (b_h - moon_h) % 12 + 1
                        if dist == 10:
                             yogas["other_yogas"].append({
                                "name": "Amala Yoga (from Moon)",
                                "description": f"Benefic {b} in 10th from Moon. Reputation and career success."
                            })

             # 5. Kemadruma Yoga (No planets in 2nd and 12th from Moon)
            if "Moon" in planets:
                moon_h = get_house("Moon")
                second_h = (moon_h % 12) + 1
                twelfth_h = ((moon_h - 2) % 12) + 1
                
                # Check occupants of 2nd and 12th from other planets map (harder without house occupants list directly accessible here easily)
                # Iterate planets
                has_planet_2 = False
                has_planet_12 = False
                
                for p_name, p in planets.items():
                    if p_name in ["Moon", "Sun", "Rahu", "Ketu"]: continue
                    if p.house == second_h: has_planet_2 = True
                    if p.house == twelfth_h: has_planet_12 = True
                
                if not has_planet_2 and not has_planet_12:
                     yogas["other_yogas"].append({
                        "name": "Kemadruma Yoga",
                        "description": "No planets in 2nd or 12th from Moon. Can indicate loneliness or struggles."
                    })

            # 6. Parivartana Yoga (Exchange of Signs)
            # Map sign number -> Lord
            sign_lords = {1:"Mars", 2:"Venus", 3:"Mercury", 4:"Moon", 5:"Sun", 6:"Mercury", 7:"Venus", 8:"Mars", 9:"Jupiter", 10:"Saturn", 11:"Saturn", 12:"Jupiter"}
            sign_map = {
                "Aries": 1, "Taurus": 2, "Gemini": 3, "Cancer": 4, 
                "Leo": 5, "Virgo": 6, "Libra": 7, "Scorpio": 8, 
                "Sagittarius": 9, "Capricorn": 10, "Aquarius": 11, "Pisces": 12
            }
            
            # Create list of (Planet, SignNum, LordOfSign)
            p_positions = {}
            for p_name, p in planets.items():
                if p_name in ["Rahu", "Ketu"]: continue
                s_num = sign_map.get(p.sign)
                lord = sign_lords.get(s_num)
                p_positions[p_name] = {"in_sign": s_num, "sign_lord": lord}
                
            # Check pairs
            checked = set()
            for p1, data1 in p_positions.items():
                lord1 = data1["sign_lord"] # Lord of the sign p1 is in
                if lord1 == p1: continue # Own sign
                
                # Check if Lord1 is in P1's sign
                if lord1 in p_positions:
                    lord1_sign_lord = p_positions[lord1]["sign_lord"]
                    if lord1_sign_lord == p1:
                        # Exhange detected
                        pair = tuple(sorted((p1, lord1)))
                        if pair not in checked:
                            yogas["raja_yogas"].append({
                                "name": f"Parivartana Yoga ({p1}-{lord1})",
                                "description": f"Exchange of signs between {p1} and {lord1}. Strengthens both houses."
                            })
                            checked.add(pair)
            
            # 7. Vipreet Raja Yoga
            # Lords of 6, 8, 12 in 6, 8, 12
            trik_houses = [6, 8, 12]
            # Need to know which planet rules 6, 8, 12 for this Ascendant
            # 1. Find Ascendant Sign
            asc_sign_num = 1 # Default Aries
            if chart.d1_chart.houses:
                asc_sign_str = chart.d1_chart.houses[0].sign
                asc_sign_num = sign_map.get(asc_sign_str, 1)
            
            # Calculate lords of 6, 8, 12
            lord_6 = sign_lords.get(((asc_sign_num + 5) % 12) or 12)
            lord_8 = sign_lords.get(((asc_sign_num + 7) % 12) or 12)
            lord_12 = sign_lords.get(((asc_sign_num + 11) % 12) or 12)
            
            suspects = {lord_6: "6th Lord", lord_8: "8th Lord", lord_12: "12th Lord"}
            
            for p_name, label in suspects.items():
                if p_name in planets:
                    if planets[p_name].house in trik_houses:
                        yogas["raja_yogas"].append({
                            "name": "Vipreet Raja Yoga",
                            "description": f"{label} ({p_name}) is in a Trik house ({planets[p_name].house}). Success after struggle."
                        })
                        
            # 8. Pancha Mahapurusha Yoga
            # Mars, Merc, Jup, Ven, Sat in Own/Exalt AND in Kendra (1, 4, 7, 10)
            candidates = {
                "Mars": "Ruchaka Yoga", 
                "Mercury": "Bhadra Yoga", 
                "Jupiter": "Hamsa Yoga", 
                "Venus": "Malavya Yoga", 
                "Saturn": "Sasa Yoga"
            }
            exalt_signs = {"Mars": "Capricorn", "Mercury": "Virgo", "Jupiter": "Cancer", "Venus": "Pisces", "Saturn": "Libra"}
            own_signs = {
                "Mars": ["Aries", "Scorpio"], "Mercury": ["Gemini", "Virgo"], 
                "Jupiter": ["Sagittarius", "Pisces"], "Venus": ["Taurus", "Libra"], 
                "Saturn": ["Capricorn", "Aquarius"]
            }
            
            for p_name, yoga_name in candidates.items():
                if p_name in planets:
                    p = planets[p_name]
                    if p.house in [1, 4, 7, 10]:
                        is_strong = False
                        if p.sign == exalt_signs[p_name]: is_strong = True
                        if p.sign in own_signs[p_name]: is_strong = True
                        
                        if is_strong:
                             yogas["raja_yogas"].append({
                                "name": yoga_name,
                                "description": f"Pancha Mahapurusha: {p_name} strong in Kendra."
                            })

        except Exception as e:
            print(f"Warning: Error calculating yogas: {e}")
            
        return yogas
    
    def _extract_nakshatras(self, chart) -> Dict[str, Any]:
        """Extract Nakshatra data for all planets"""
        nakshatras = {}
        
        try:
            for planet in chart.d1_chart.planets:
                nakshatras[planet.celestial_body] = {
                    "nakshatra": planet.nakshatra,
                    "pada": planet.pada
                }
        except Exception as e:
            print(f"Warning: Could not extract nakshatras: {e}")
        
        return nakshatras
    
    def _extract_panchang(self, chart) -> Dict[str, Any]:
        """Extract Panchang data (Tithi, Vara, Yoga, Karana)"""
        panchang = {
            "tithi": None,
            "vara": None,
            "yoga": None,
            "karana": None,
            "nakshatra": None
        }
        
        try:
            if hasattr(chart, 'panchanga') and chart.panchanga:
                p = chart.panchanga
                panchang = {
                    "tithi": p.tithi,
                    "vara": p.vaara,
                    "yoga": p.yoga,
                    "karana": p.karana,
                    "nakshatra": p.nakshatra
                }
        except Exception as e:
            print(f"Warning: Could not extract panchang: {e}")
        
        return panchang
    
    def get_dasha_periods(self, count: int = 10) -> List[Dict[str, Any]]:
        """Get current and upcoming Vimshottari dasha periods"""
        if not self.current_chart:
            raise ValueError("No chart generated. Call generate_full_chart() first.")
        
        dashas = []
        
        try:
            if hasattr(self.current_chart, 'dashas') and self.current_chart.dashas:
                upcoming = getattr(self.current_chart.dashas, 'upcoming', None)
                if upcoming:
                    # Handle dictionary structure
                    if isinstance(upcoming, dict):
                        md_dict = upcoming.get('mahadashas', {})
                    else:
                        md_dict = getattr(upcoming, 'mahadashas', {})
                    
                    for i, (lord, period) in enumerate(md_dict.items()):
                        if i >= count:
                            break
                        dashas.append({
                            "type": "Mahadasha",
                            "lord": lord,
                            "start": str(period.get('start', '')),
                            "end": str(period.get('end', ''))
                        })
        except Exception as e:
            print(f"Warning: Could not get dasha periods: {e}")
        
        return dashas
    
    def get_divisional_chart(self, chart_type: str) -> Dict[str, Any]:
        """Get specific divisional chart (e.g., 'D9' for Navamsa)"""
        if not self.current_chart:
            raise ValueError("No chart generated. Call generate_full_chart() first.")
        
        try:
            chart_key = chart_type.lower()
            
            # Check if it's the main chart
            if chart_key == 'd1':
                return self._format_chart_data(self.current_chart.d1_chart)
            
            # Check divisional charts
            if chart_key in self.current_chart.divisional_charts:
                return self._format_chart_data(self.current_chart.divisional_charts[chart_key])
            else:
                raise ValueError(f"Chart {chart_type} not available")
        except Exception as e:
            raise ValueError(f"Error getting divisional chart: {e}")
    
    def export_for_ai_agent(self) -> str:
        """Export current chart as JSON for AI Agent consumption"""
        if not self.current_chart:
            raise ValueError("No chart generated. Call generate_full_chart() first.")
        
        try:
            # Use jyotishganit's built-in JSON export
            chart_dict = get_birth_chart_json(self.current_chart)
            
            output = {
                "status": "success",
                "data": chart_dict
            }
            return json.dumps(output, indent=2, default=str)
        except Exception as e:
            error_output = {
                "status": "error",
                "message": str(e)
            }
    
    def _get_astronomical_constants(self, jd_ut: float, birth_datetime: datetime, tz_offset: float, lon: float) -> Dict[str, Any]:
        """
        Calculate and return astronomical base values used in Vedic astrology.
        
        Args:
            jd_ut: Julian Day in UT
            birth_datetime: Birth datetime object
            tz_offset: Timezone offset in hours
            lon: Longitude for Local Mean Time calculation
        
        Returns:
            Dictionary with Ayanamsa, Julian Day, Sidereal Time, Obliquity, LMT, GMT
        """
        try:
            import swisseph as swe
            
            # 1. Ayanamsa (Lahiri)
            swe.set_sid_mode(swe.SIDM_LAHIRI)
            ayanamsa_deg = swe.get_ayanamsa_ut(jd_ut)
            
            # Convert to DMS
            ayan_d = int(ayanamsa_deg)
            ayan_m = int((ayanamsa_deg - ayan_d) * 60)
            ayan_s = int(((ayanamsa_deg - ayan_d) * 60 - ayan_m) * 60)
            
            # 2. Obliquity of the Ecliptic
            # swe.calc_ut returns eps (obliquity) when planet is SUN and flag includes SEFLG_EQUATORIAL
            # Simpler: use swe.calc for mean obliquity
            eps_tuple = swe.calc_ut(jd_ut, swe.ECL_NUT)
            # eps_tuple[0] is true obliquity, eps_tuple[1] is mean obliquity
            if isinstance(eps_tuple[0], (list, tuple)):
                obliquity = eps_tuple[0][0]  # True obliquity
            else:
                obliquity = eps_tuple[0]
            
            obl_d = int(obliquity)
            obl_m = int((obliquity - obl_d) * 60)
            obl_s = int(((obliquity - obl_d) * 60 - obl_m) * 60)
            
            # 3. Sidereal Time at Birth
            # ARMC (Ascendant's Right Ascension Meridian Cusp) / 15 gives sidereal time in hours
            # Or use swe.sidtime(jd_ut) for GMT sidereal time, then adjust for longitude
            sid_time_gmt = swe.sidtime(jd_ut)  # Returns hours
            # Local Sidereal Time = GMT Sidereal Time + (Longitude / 15)
            local_sid_time = (sid_time_gmt + lon / 15.0) % 24.0
            
            st_h = int(local_sid_time)
            st_m = int((local_sid_time - st_h) * 60)
            st_s = int(((local_sid_time - st_h) * 60 - st_m) * 60)
            
            # 4. LMT and GMT at Birth
            # LMT = Local Standard Time + Time Correction
            # Time Correction = (Longitude - Standard Meridian) / 15 hours
            # For IST, Standard Meridian = 82.5° E
            # However, we're given the local time directly, so:
            local_time_str = birth_datetime.strftime("%H:%M:%S")
            
            # GMT = Local Time - Timezone Offset
            gmt_hour = birth_datetime.hour - tz_offset
            gmt_datetime = datetime(
                birth_datetime.year, birth_datetime.month, birth_datetime.day,
                int(gmt_hour) % 24, birth_datetime.minute, birth_datetime.second
            )
            gmt_str = gmt_datetime.strftime("%H:%M:%S")
            
            # LMT Correction = (Longitude - Standard Meridian) * 4 minutes per degree
            # For India: Std Meridian = 82.5
            # This is approximate, as it assumes IST zone
            std_meridian = tz_offset * 15.0  # Approx standard meridian for this tz
            lmt_correction_minutes = (lon - std_meridian) * 4.0
            lmt_corr_m = int(abs(lmt_correction_minutes))
            lmt_corr_s = int((abs(lmt_correction_minutes) - lmt_corr_m) * 60)
            lmt_corr_sign = "+" if lmt_correction_minutes >= 0 else "-"
            
            return {
                "ayanamsa": {
                    "name": "Lahiri",
                    "value_dms": f"{ayan_d:03d}-{ayan_m:02d}-{ayan_s:02d}",
                    "value_decimal": round(ayanamsa_deg, 6)
                },
                "obliquity": {
                    "value_dms": f"{obl_d:02d}-{obl_m:02d}-{obl_s:02d}",
                    "value_decimal": round(obliquity, 6)
                },
                "sidereal_time": {
                    "local_dms": f"{st_h:02d}:{st_m:02d}:{st_s:02d}",
                    "local_decimal": round(local_sid_time, 4)
                },
                "julian_day": round(jd_ut, 6),
                "lmt_at_birth": local_time_str,
                "gmt_at_birth": gmt_str,
                "local_time_correction": f"{lmt_corr_sign}{lmt_corr_m:02d}:{lmt_corr_s:02d}"
            }
        except Exception as e:
            return {"error": str(e)}

    def _calculate_sunrise_sunset(self, jd_ut: float, lat: float, lon: float, tz_offset: float = 5.5) -> Dict[str, Any]:
        """
        Calculate sunrise, sunset, and day duration for birth date.
        Uses the same method as panchanga.py for compatibility.
        
        Args:
            jd_ut: Julian Day in UT for birth time
            lat: Latitude
            lon: Longitude
            tz_offset: Timezone offset (default 5.5 for IST)
        
        Returns:
            Dictionary with sunrise, sunset, day_duration
        """
        try:
            import swisseph as swe
            
            # Hindu sunrise/sunset flags (geometric, disc center, no refraction)
            _rise_flags = swe.BIT_DISC_CENTER + swe.BIT_NO_REFRACTION
            
            # Julian Day at midnight for the birth date (00:00 local time)
            jd_midnight = int(jd_ut) + 0.5  # JD noon = 0.5
            if (jd_ut % 1) < 0.5:
                jd_midnight = int(jd_ut) - 0.5
            
            # Adjust for timezone to get JD in UT at local midnight
            jd_ut_midnight = jd_midnight - tz_offset / 24.0
            
            # Calculate sunrise using correct swisseph signature
            # swe.rise_trans(jd, planet, lon, lat, altitude, pressure, temp, flags)
            result_rise = swe.rise_trans(
                float(jd_ut_midnight),
                int(swe.SUN),
                float(lon),
                float(lat),
                0.0,  # altitude
                0.0,  # atmospheric pressure
                0.0,  # atmospheric temperature
                int(_rise_flags + swe.CALC_RISE)
            )
            
            result_set = swe.rise_trans(
                float(jd_ut_midnight),
                int(swe.SUN),
                float(lon),
                float(lat),
                0.0,
                0.0,
                0.0,
                int(_rise_flags + swe.CALC_SET)
            )
            
            # Extract Julian Day from result
            # Result format: (return_code, (jd_event,))
            sunrise_jd = result_rise[1][0]
            sunset_jd = result_set[1][0]
            
            # Convert JD (UT) to local time string
            def jd_to_local_time_str(jd, tz):
                """Convert JD (UT) to local time string HH:MM:SS
                
                FIX: Julian Day starts at NOON, not midnight.
                JD 0.0 = noon, 0.25 = 6pm, 0.5 = midnight, 0.75 = 6am
                Adding 0.5 converts from noon-based to midnight-based fraction.
                """
                # Add timezone to get local JD
                local_jd = jd + tz / 24.0
                # FIX: Add 0.5 to shift from noon-based (JD default) to midnight-based
                frac = (local_jd + 0.5) % 1  # Now 0 = midnight
                hours_decimal = frac * 24.0
                h = int(hours_decimal)
                m = int((hours_decimal - h) * 60)
                s = int(((hours_decimal - h) * 60 - m) * 60)
                return f"{h:02d}:{m:02d}:{s:02d}"
            
            sunrise_local = jd_to_local_time_str(sunrise_jd, tz_offset)
            sunset_local = jd_to_local_time_str(sunset_jd, tz_offset)
            
            # Day duration in hours
            day_duration_hours = (sunset_jd - sunrise_jd) * 24.0
            dur_h = int(day_duration_hours)
            dur_m = int((day_duration_hours - dur_h) * 60)
            dur_s = int(((day_duration_hours - dur_h) * 60 - dur_m) * 60)
            
            return {
                "sunrise": sunrise_local,
                "sunset": sunset_local,
                "day_duration": f"{dur_h:02d}:{dur_m:02d}:{dur_s:02d}",
                "day_duration_hours": round(day_duration_hours, 4)
            }
        except Exception as e:
            import traceback
            return {"error": str(e), "traceback": traceback.format_exc()}

    
    # ============================================================
    # PHASE 2: Bhavabala, Yogini Dasha, Char Dasha
    # ============================================================
    
    def _extract_bhavabala(self, chart_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract Bhavabala (House Strength) from chart data.
        Bhavabala = BhavaAdhipathibala + BhavaDigbala + BhavaDrishtibala
        
        Returns:
            Dictionary with Bhavabala for each of 12 houses
        """
        try:
            bhavabala = {}
            # FIX: Try multiple access paths for jyotishganit structure variations (camelCase and snake_case)
            balas = chart_data.get("Balas") or chart_data.get("balas") or {}
            bhava_data = balas.get("BhavaBala") or balas.get("bhava_bala") or balas.get("bhavabala") or {}
            
            # If balas itself contains Total/total, it might be the bhavabala dict directly
            if not bhava_data and isinstance(balas, dict) and ("Total" in balas or "total" in balas):
                bhava_data = balas
            
            if bhava_data:
                totals = bhava_data.get("Total") or bhava_data.get("total") or [0]*12
                adhipathi = bhava_data.get("BhavaAdhipathibala") or bhava_data.get("bhava_adhipathi_bala") or [0]*12
                digbala = bhava_data.get("BhavaDigbala") or bhava_data.get("bhava_dig_bala") or [0]*12
                drishtibala = bhava_data.get("BhavaDrishtibala") or bhava_data.get("bhava_drishti_bala") or [0]*12
                
                for i in range(12):
                    bhavabala[f"house_{i+1}"] = {
                        "total": round(totals[i] if i < len(totals) else 0, 2),
                        "adhipathi_bala": round(adhipathi[i] if i < len(adhipathi) else 0, 2),
                        "dig_bala": round(digbala[i] if i < len(digbala) else 0, 2),
                        "drishti_bala": round(drishtibala[i] if i < len(drishtibala) else 0, 2)
                    }
                
                # Calculate rankings
                if totals:
                    sorted_houses = sorted(range(12), key=lambda x: totals[x] if x < len(totals) else 0, reverse=True)
                    for rank, house_idx in enumerate(sorted_houses, 1):
                        bhavabala[f"house_{house_idx+1}"]["rank"] = rank
            
            return bhavabala
            
        except Exception as e:
            return {"error": str(e)}
    
    def _calculate_yogini_dasha(self, birth_datetime: datetime, moon_nakshatra_idx: int = None, moon_degree: float = None) -> Dict[str, Any]:
        """
        Calculate Yogini Dasha periods.
        Yogini Dasha has 8 periods totaling 36 years, then repeats.
        
        The starting Yogini is determined by: (Nakshatra number + 3) / 8
        The remainder gives the starting Yogini index.
        
        Yogini sequence (1-8): Mangala, Pingala, Dhanya, Bhramari, Bhadrika, Ulka, Siddha, Sankata
        
        Note: Nakshatra number is 1-based (Ashwini=1, Bharani=2, ... Punarvasu=7)
        For Punarvasu(7): (7 + 3) = 10, 10 % 8 = 2, so starts at Pingala (index 1)
        
        Args:
            birth_datetime: Birth date and time
            moon_nakshatra_idx: Index of Moon's Nakshatra (0-26)
            moon_degree: Moon's longitude in degrees
            
        Returns:
            Dictionary with Yogini Dasha periods
        """
        try:
            from datetime import timedelta
            
            # Yogini definitions (0-indexed)
            yoginis = [
                {"name": "Mangala", "abbrev": "Ma", "years": 1, "planet": "Moon"},
                {"name": "Pingala", "abbrev": "Pi", "years": 2, "planet": "Sun"},
                {"name": "Dhanya", "abbrev": "Dh", "years": 3, "planet": "Jupiter"},
                {"name": "Bhramari", "abbrev": "Br", "years": 4, "planet": "Mars"},
                {"name": "Bhadrika", "abbrev": "Ba", "years": 5, "planet": "Mercury"},
                {"name": "Ulka", "abbrev": "Ul", "years": 6, "planet": "Saturn"},
                {"name": "Siddha", "abbrev": "Si", "years": 7, "planet": "Venus"},
                {"name": "Sankata", "abbrev": "Sn", "years": 8, "planet": "Rahu"}
            ]
            
            total_cycle_years = 36  # Sum of all Yogini years
            
            # Calculate Moon's Nakshatra if not provided
            if moon_nakshatra_idx is None and moon_degree is not None:
                moon_nakshatra_idx = int(moon_degree / (360 / 27))  # 0-based index
            elif moon_nakshatra_idx is None:
                moon_nakshatra_idx = 0  # Default Ashwini
            
            # Convert to 1-based nakshatra number for formula
            nakshatra_number = moon_nakshatra_idx + 1  # 1-27
            
            # Starting Yogini formula: (Nakshatra + 3) mod 8
            # Result 0 means 8th yogini (Sankata), else it's the index
            remainder = (nakshatra_number + 3) % 8
            starting_yogini_idx = (remainder - 1) if remainder > 0 else 7  # Convert to 0-indexed
            
            # Calculate balance of first dasha based on Moon's position in nakshatra
            nakshatra_span = 360 / 27  # 13.333... degrees
            position_in_nakshatra = (moon_degree % nakshatra_span) if moon_degree else nakshatra_span / 2
            elapsed_ratio = position_in_nakshatra / nakshatra_span
            balance_ratio = 1 - elapsed_ratio
            
            # Adjust starting date backwards by elapsed portion to get dasha start
            first_yogini_years = yoginis[starting_yogini_idx]["years"]
            elapsed_days = first_yogini_years * elapsed_ratio * 365.25
            dasha_start_date = birth_datetime - timedelta(days=elapsed_days)
            
            # Build Yogini Dasha periods starting from the calculated start date
            dasha_periods = []
            current_date = dasha_start_date
            
            # Generate multiple cycles (covering 100+ years from birth)
            for cycle in range(4):  # 4 cycles = 144 years
                for i in range(8):
                    yogini_idx = (starting_yogini_idx + i) % 8
                    yogini = yoginis[yogini_idx]
                    years = yogini["years"]
                    
                    period_days = years * 365.25
                    end_date = current_date + timedelta(days=period_days)
                    
                    dasha_periods.append({
                        "yogini": yogini["name"],
                        "abbrev": yogini["abbrev"],
                        "planet": yogini["planet"],
                        "years": years,
                        "start": current_date.strftime("%d/%m/%y"),
                        "end": end_date.strftime("%d/%m/%y")
                    })
                    
                    current_date = end_date
            
            # Find current period
            now = datetime.now()
            current_dasha = None
            for period in dasha_periods:
                try:
                    start = datetime.strptime(period["start"], "%d/%m/%y")
                    end = datetime.strptime(period["end"], "%d/%m/%y")
                    # Fix 2-digit year interpretation
                    if start.year < 1950:
                        start = start.replace(year=start.year + 100)
                    if end.year < 1950:
                        end = end.replace(year=end.year + 100)
                    if start <= now <= end:
                        current_dasha = period
                        break
                except:
                    continue
            
            return {
                "periods": dasha_periods,
                "current": current_dasha,
                "total_cycle_years": total_cycle_years,
                "starting_yogini": yoginis[starting_yogini_idx]["name"],
                "moon_nakshatra_number": nakshatra_number
            }
            
        except Exception as e:
            import traceback
            return {"error": str(e), "traceback": traceback.format_exc()}
    
    def _calculate_char_dasha(self, birth_datetime: datetime, lagna_sign_idx: int = 0, planet_positions: Dict = None) -> Dict[str, Any]:
        """
        Calculate Char Dasha (Jaimini Chara Dasha).
        Sign-based dasha system based on Jaimini astrology.
        
        Duration rules:
        - Count signs from the dasha sign to its lord's position
        - For odd signs (Aries, Gemini, Leo, Libra, Sag, Aquarius): count forward
        - For even signs (Taurus, Cancer, Virgo, Scorpio, Cap, Pisces): count backward
        - Add 1 to the count for the years
        - If lord is in the same sign, duration = 12 years
        
        Sequence for odd Lagna: Forward from Lagna
        Sequence for even Lagna: Backward from Lagna
        
        Args:
            birth_datetime: Birth date and time
            lagna_sign_idx: Index of Lagna sign (0=Aries to 11=Pisces)
            planet_positions: Dict mapping planet names to sign indices
            
        Returns:
            Dictionary with Char Dasha periods
        """
        try:
            from datetime import timedelta
            
            planet_positions = planet_positions or {}
            
            # Sign definitions
            signs = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
                     "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
            sign_abbrev = ["ARI", "TAU", "GEM", "CAN", "LEO", "VIR",
                           "LIB", "SCO", "SAG", "CAP", "AQU", "PIS"]
            
            # Sign lords (using Jaimini system - Mars rules Aries/Scorpio, etc.)
            sign_lords = {
                0: "Mars", 1: "Venus", 2: "Mercury", 3: "Moon", 4: "Sun", 5: "Mercury",
                6: "Venus", 7: "Mars", 8: "Jupiter", 9: "Saturn", 10: "Saturn", 11: "Jupiter"
            }
            
            # Odd signs (count forward): 0, 2, 4, 6, 8, 10
            odd_signs = [0, 2, 4, 6, 8, 10]
            
            # Helper to count planets in a sign
            planets_in_sign = {i: 0 for i in range(12)}
            for p_name, p_data in planet_positions.items():
                if isinstance(p_data, dict):
                    sign = p_data.get("sign_id", p_data.get("sign"))
                    # Handle string sign names if necessary, but expecting 0-11 index or converting
                    if isinstance(sign, str):
                        try:
                            sign = signs.index(sign)
                        except:
                            pass
                    if isinstance(sign, int) and 0 <= sign <= 11:
                        planets_in_sign[sign] += 1
                elif isinstance(p_data, int): # Legacy simple dict
                    planets_in_sign[p_data] += 1

            def get_stronger_sign(sign1: int, sign2: int) -> int:
                """Return the sign that is stronger based on Jaimini rules."""
                # Rule 1: More planets
                c1 = planets_in_sign[sign1]
                c2 = planets_in_sign[sign2]
                if c1 > c2: return sign1
                if c2 > c1: return sign2
                # If equal, default to regular lord for now (can add exaltation logic later)
                return sign1

            def get_lord_sign(sign_idx: int) -> int:
                """Get the sign where the lord is placed, handling Dual Lordship."""
                
                # Handle Dual Lordships
                # Scorpio (7): Ruled by Mars (0) and Ketu
                if sign_idx == 7:
                    mars_pos = -1
                    ketu_pos = -1
                    
                    # Find Mars
                    if "Mars" in planet_positions:
                        p = planet_positions["Mars"]
                        mars_pos = p.get("sign_id", p.get("sign")) if isinstance(p, dict) else p
                    
                    # Find Ketu
                    if "Ketu" in planet_positions:
                        p = planet_positions["Ketu"]
                        ketu_pos = p.get("sign_id", p.get("sign")) if isinstance(p, dict) else p
                        
                    if mars_pos != -1 and ketu_pos != -1:
                        # Determine stronger lord
                        # Note: We need the position OF the lord
                        return get_stronger_sign(mars_pos, ketu_pos)
                    return mars_pos if mars_pos != -1 else (ketu_pos if ketu_pos != -1 else 0)

                # Aquarius (10): Ruled by Saturn (9) and Rahu
                if sign_idx == 10:
                    sat_pos = -1
                    rahu_pos = -1
                    
                    if "Saturn" in planet_positions:
                        p = planet_positions["Saturn"]
                        sat_pos = p.get("sign_id", p.get("sign")) if isinstance(p, dict) else p
                        
                    if "Rahu" in planet_positions:
                        p = planet_positions["Rahu"]
                        rahu_pos = p.get("sign_id", p.get("sign")) if isinstance(p, dict) else p
                        
                    if sat_pos != -1 and rahu_pos != -1:
                        return get_stronger_sign(sat_pos, rahu_pos)
                    return sat_pos if sat_pos != -1 else (rahu_pos if rahu_pos != -1 else 10)

                # Regular signs
                lord_name = sign_lords[sign_idx]
                if lord_name in planet_positions:
                    p = planet_positions[lord_name]
                    return p.get("sign_id", p.get("sign")) if isinstance(p, dict) else p
                
                # Default locations
                lord_default_signs = [i for i, l in sign_lords.items() if l == lord_name]
                return lord_default_signs[0] if lord_default_signs else sign_idx
            
            def get_dasha_duration(sign_idx: int) -> int:
                """
                Calculate dasha duration using Padakrama.
                """
                lord_sign = get_lord_sign(sign_idx)
                
                # If lord is in its own sign, duration is 12
                if lord_sign == sign_idx:
                    return 12
                
                if sign_idx in odd_signs:
                    # Odd sign: count forward
                    distance = (lord_sign - sign_idx) % 12
                else:
                    # Even sign: count backward
                    distance = (sign_idx - lord_sign) % 12
                
                # Duration = distance + 1 (minimum 1 year NOT enforced by strict Jaimini, but usually is)
                # Correction: Jaimini Sutra says (Distance - 1). Wait.
                # Common interpretation: "Count from sign to lord".
                # If Lord is in 2nd house from sign, count is 2. Years = 2 (or 2-1=1).
                # AstroSage: SCO (Lord Mars/Ketu). If Mars in Sag (2nd from Sco).
                # Sequence: Sco (12y) -> Lib (6y).
                # Let's stick to the current "distance + 1" formula but fix the LORD position first.
                return max(distance, 1) # Actually distance is 0-11. Count is 1-12. So distance+1 is correct count.
                # However, many schools deduct 1. Let's start with count.
            
            def get_dasha_sequence(lagna_idx: int) -> list:
                """
                Get the sequence of signs for Char Dasha (Jaimini).
                
                FIX: Traditional Jaimini Char Dasha rules (OPPOSITE of what was coded):
                - Odd Signs (Aries, Gemini, Leo, Libra, Sagittarius, Aquarius): BACKWARD
                - Even Signs (Taurus, Cancer, Virgo, Scorpio, Capricorn, Pisces): FORWARD
                
                AstroSage confirms: For Sagittarius (odd), sequence is SAG→SCO→LIB→VIR...
                """
                sequence = []
                if lagna_idx in odd_signs:
                    # FIX: Odd sign = BACKWARD sequence (Sag→Sco→Lib→Vir...)
                    for i in range(12):
                        sequence.append((lagna_idx - i) % 12)
                else:
                    # Even sign = FORWARD sequence
                    for i in range(12):
                        sequence.append((lagna_idx + i) % 12)
                return sequence
            
            # Build Char Dasha periods
            dasha_periods = []
            current_date = birth_datetime
            sequence = get_dasha_sequence(lagna_sign_idx)
            
            # Calculate multiple cycles (2-3 needed for 100+ years)
            for cycle in range(3):
                for sign_idx in sequence:
                    duration = get_dasha_duration(sign_idx)
                    
                    period_days = duration * 365.25
                    end_date = current_date + timedelta(days=period_days)
                    
                    dasha_periods.append({
                        "sign": signs[sign_idx],
                        "abbrev": sign_abbrev[sign_idx],
                        "lord": sign_lords[sign_idx],
                        "years": duration,
                        "start": current_date.strftime("%d/%m/%y"),
                        "end": end_date.strftime("%d/%m/%y")
                    })
                    
                    current_date = end_date
            
            # Find current period
            now = datetime.now()
            current_dasha = None
            for period in dasha_periods:
                try:
                    start = datetime.strptime(period["start"], "%d/%m/%y")
                    end = datetime.strptime(period["end"], "%d/%m/%y")
                    # Adjust 2-digit year
                    if start.year < 1950:
                        start = start.replace(year=start.year + 100)
                    if end.year < 1950:
                        end = end.replace(year=end.year + 100)
                    if start <= now <= end:
                        current_dasha = period
                        break
                except:
                    continue
            
            return {
                "maha_dasha": dasha_periods,
                "current": current_dasha,
                "lagna_sign": signs[lagna_sign_idx],
                # FIX: Corrected direction label (odd signs go backward, even go forward)
                "sequence_direction": "backward" if lagna_sign_idx in odd_signs else "forward"
            }
            
        except Exception as e:
            import traceback
            return {"error": str(e), "traceback": traceback.format_exc()}
    
    def _calculate_kp_cusps(self, cusps: list) -> Dict[str, Any]:
        """
        Calculate KP Star/Sub/Sub-Sub lords for all 12 house cusps.
        
        Args:
            cusps: List of 12 cusp degrees (sidereal, 0-360)
        
        Returns:
            Dictionary with KP details for each cusp
        """
        kp_cusps = {}
        
        for i, cusp_deg in enumerate(cusps[:12], 1):
            # Use existing _calculate_kp_details method
            kp_info = self._calculate_kp_details(cusp_deg)
            kp_cusps[f"cusp_{i}"] = {
                "degree": round(cusp_deg % 30, 4),
                "total_degree": round(cusp_deg, 4),
                "sign_lord": kp_info.get("sign_lord"),
                "nakshatra_lord": kp_info.get("nakshatra_lord"),
                "sub_lord": kp_info.get("sub_lord"),
                "sub_sub_lord": kp_info.get("sub_sub_lord")
            }
        
        return kp_cusps


def test_engine():
    """Test the astrology engine with sample data"""
    print("Testing AstroEngine with jyotishganit...")
    
    try:
        engine = AstroEngine()
        
        # Sample birth data (July 4, 1996, 9:10 AM, Karmala, India)
        chart = engine.generate_full_chart(
            name="Test Person",
            dob="1996-07-04",
            tob="09:10:00",
            place="Karmala, India",
            latitude=18.404,
            longitude=75.195,
            timezone="+5.5"
        )
        
        print("✅ Chart generation successful!")
        print(f"Generated chart with {len(chart.get('divisional_charts', {}))} divisional charts")
        print(f"Ascendant: {chart['divisional_charts']['D1']['ascendant']['sign']}")
        print(f"Moon Sign: {chart['divisional_charts']['D1']['planets']['Moon']['sign']}")
        print(f"Nakshatra: {chart['panchang']['nakshatra']}")
        
        # Get dashas
        dashas = engine.get_dasha_periods(3)
        print(f"✅ Retrieved {len(dashas)} dasha periods")
        
        # Export for AI
        ai_json = engine.export_for_ai_agent()
        print("✅ Exported chart for AI Agent")
        print(f"JSON output length: {len(ai_json)} characters")
        
        return True
        
    except Exception as e:
        import traceback
        print(f"❌ Test failed: {e}")
        print(traceback.format_exc())
        return False


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        test_engine()
    else:
        print("AstroEngine module loaded. Use --test flag to run tests.")
