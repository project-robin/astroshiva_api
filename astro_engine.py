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
        timezone: str = None
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
            
            # Generate chart using jyotishganit (single function call!)
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
                "divisional_charts": self._extract_divisional_charts(chart),
                "balas": self._extract_balas(chart),
                "dashas": self._extract_dashas(chart),
                "nakshatra": self._extract_nakshatras(chart),
                "panchang": self._extract_panchang(chart),
                "yogas": self._extract_yogas(chart),
                "doshas": self._calculate_doshas(chart),
                "meta": {
                     "api_version": "1.1.0",
                     "calculation_method": "nc_lahiri",
                     "ayanamsa": "Lahiri",
                     "engine": "astro-shiva-engine-v2"
                }
            }
            
            # Enrich with direct calculations for missing data
            self._enrich_chart_data(output, birth_datetime, latitude, longitude, tz_offset)
            
            return output
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"DETAILED ERROR in generate_full_chart:\n{error_details}")
            raise ValueError(f"Error generating chart: {str(e)}")
    
    def _extract_divisional_charts(self, chart) -> Dict[str, Any]:
        """Extract all divisional charts (D1-D60)"""
        charts = {}
        
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
            charts['D1'] = self._format_chart_data(chart.d1_chart, 'D1', d1_degrees)
            
            # D2-D60 divisional charts
            for chart_name, divisional_chart in chart.divisional_charts.items():
                c_name_upper = chart_name.upper()
                charts[c_name_upper] = self._format_chart_data(divisional_chart, c_name_upper, d1_degrees)
        except Exception as e:
            print(f"Warning: Could not extract all divisional charts: {e}")
        
        return charts
    
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
                    formatted["planets"][planet.celestial_body] = {
                        "sign": planet.sign,
                        "degree": float(planet.sign_degrees) if hasattr(planet, 'sign_degrees') else None,
                        "nakshatra": planet.nakshatra,
                        "pada": planet.pada,
                        "house": planet.house,
                        "retrograde": getattr(planet, 'retrograde', False),
                        "dignities": getattr(planet, 'dignities', None),
                        "aspects": getattr(planet, 'aspects', {}),
                        "is_combust": False,
                        "speed": 0.0 # Will be populated enrichment
                    }
                    
                    if formatted["planets"][planet.celestial_body]["dignities"] and hasattr(formatted["planets"][planet.celestial_body]["dignities"], 'to_dict'):
                          formatted["planets"][planet.celestial_body]["dignities"] = formatted["planets"][planet.celestial_body]["dignities"].to_dict()
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
            
            # 1. Exact Ascendant Degree
            # swe.houses returns (cusps, ascmc)
            # ascmc[0] is Ascendant
            cusps, ascmc = swe.houses(jd_ut, lat, lon, b'P') # Placidus houses
            
            asc_deg_total = ascmc[0]
            asc_sign_idx = int(asc_deg_total / 30)
            asc_deg_rem = asc_deg_total % 30
            
            # Enrich D1 Ascendant
            if 'D1' in output['divisional_charts']:
                asc_node = output['divisional_charts']['D1']['ascendant']
                asc_node['degree'] = asc_deg_rem
                asc_node['total_degree'] = asc_deg_total
                
            # 2. Enrich Houses with Cusps
            if 'houses' in output['divisional_charts']['D1']:
                for i, h_data in enumerate(output['divisional_charts']['D1']['houses']):
                    # swe cusps are 1-based index in result usually, but tuple is 0-indexed?
                    # swe.houses returns tuple of 12 numbers. cusps[0] is 1st house.
                    if i < len(cusps):
                        h_deg_total = cusps[i]
                        h_data['cusp'] = h_deg_total % 30
                        h_data['total_degree'] = h_deg_total
                        # Calculate madhya (midpoint) roughly
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
            
            for p_name, p_id in planets_map.items():
                if p_name in d1_planets:
                    # Calc UT position
                    res = swe.calc_ut(jd_ut, p_id, swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED)
                    # res is (long, lat, dist, speed_long, speed_lat, speed_dist)
                    
                    speed = res[3]
                    if p_name == 'Ketu':
                        speed = speed # Node speed
                    
                    d1_planets[p_name]['speed'] = speed
                    d1_planets[p_name]['speed_status'] = 'fast' if abs(speed) > self._get_avg_speed(p_name)*1.1 else ('slow' if abs(speed) < self._get_avg_speed(p_name)*0.9 else 'normal')

        except Exception as e:
             # print(f"Warning: Enrichment failed: {e}")
             # Don't spam logs if it fails, just skip
             pass
        
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
                
                has_planet_2 = any(p.house == second_h for name, p in planets.items() if name not in ["Moon", "Sun", "Rahu", "Ketu"])
                has_planet_12 = any(p.house == twelfth_h for name, p in planets.items() if name not in ["Moon", "Sun", "Rahu", "Ketu"])
                
                if not has_planet_2 and not has_planet_12:
                     yogas["other_yogas"].append({
                        "name": "Kemadruma Yoga",
                        "description": "No planets in 2nd or 12th from Moon. Can indicate loneliness or struggles."
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
