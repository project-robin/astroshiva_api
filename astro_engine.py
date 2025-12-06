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
                "divisional_charts": self._extract_divisional_charts(chart, charts_filter=charts),
                "balas": self._extract_balas(chart),
                "dashas": self._extract_dashas(chart),
                "nakshatra": self._extract_nakshatras(chart),
                "panchang": self._extract_panchang(chart),
                "yogas": self._extract_yogas(chart),
                "doshas": self._calculate_doshas(chart),
                "meta": {
                     "api_version": "2.0.0",
                     "calculation_method": "nc_lahiri",
                     "ayanamsa": "Lahiri",
                     "engine": "astro-shiva-engine-v2",
                     "features": ["Jaimini", "KP", "Avasthas", "Transits"]
                }
            }
            
            # Enrich with direct calculations for missing data
            # This now also populates KP, Avasthas etc via _enrich_chart_data -> methods
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
