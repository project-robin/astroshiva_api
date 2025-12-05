"""
Vedic Astrology Engine - Local Free Implementation
Uses jyotishganit for 100% free, local, offline calculations
"""

import json
from datetime import datetime
from typing import Dict, Any, Optional, List

from jyotishganit import calculate_birth_chart, get_birth_chart_json


class AstroEngine:
    """Main engine for Vedic Astrology calculations using jyotishganit"""
    
    def __init__(self):
        """Initialize the astrology engine"""
        self.current_chart = None
        self.birth_data = None
    
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
                # Convert string timezone to float
                tz_offset = float(timezone)
            
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
                "nakshatras": self._extract_nakshatras(chart),
                "panchang": self._extract_panchang(chart)
            }
            
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
            # D1 (Rashi chart) is main
            charts['D1'] = self._format_chart_data(chart.d1_chart)
            
            # D2-D60 divisional charts
            for chart_name, divisional_chart in chart.divisional_charts.items():
                charts[chart_name.upper()] = self._format_chart_data(divisional_chart)
        except Exception as e:
            print(f"Warning: Could not extract all divisional charts: {e}")
        
        return charts
    
    def _format_chart_data(self, chart_obj) -> Dict[str, Any]:
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
                    "lord": ascendant_lord
                },
                "planets": {},
                "houses": []
            }
            
            # Extract planet positions
            for planet in chart_obj.planets:
                formatted["planets"][planet.celestial_body] = {
                    "sign": planet.sign,
                    "degree": planet.sign_degrees,
                    "nakshatra": planet.nakshatra,
                    "pada": planet.pada,
                    "house": planet.house,
                    "retrograde": getattr(planet, 'retrograde', False)
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
                
                # Upcoming mahadashas - it's a dictionary
                if hasattr(chart.dashas, 'upcoming'):
                    upcoming = chart.dashas.upcoming
                    # Check if it's a dictionary or object with mahadashas attribute
                    if isinstance(upcoming, dict) and 'mahadashas' in upcoming:
                        for lord, period in upcoming['mahadashas'].items():
                            dashas['vimshottari']['mahadasha'].append({
                                "lord": lord,
                                "start_date": str(period.get('start', '')),
                                "end_date": str(period.get('end', ''))
                            })
                    elif hasattr(upcoming, 'mahadashas'):
                        for lord, period in upcoming.mahadashas.items():
                            dashas['vimshottari']['mahadasha'].append({
                                "lord": lord,
                                "start_date": str(period.get('start', '')),
                                "end_date": str(period.get('end', ''))
                            })
        except Exception as e:
            print(f"Warning: Could not extract dashas: {e}")
        
        return dashas
    
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
            return json.dumps(error_output, indent=2)


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
