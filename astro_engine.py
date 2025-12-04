"""
Vedic Astrology Engine - Local Free Implementation
Uses jyotishyamitra for 100% free, local, offline calculations
"""

import json
from datetime import datetime
from typing import Dict, Any, Optional, List
import jyotishyamitra as jm


class AstroEngine:
    """Main engine for Vedic Astrology calculations using jyotishyamitra"""
    
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
        longitude: float = None
    ) -> Dict[str, Any]:
        """
        Generate complete astrological chart for birth data
        
        Args:
            name: Person's name
            dob: Date of birth (YYYY-MM-DD)
            tob: Time of birth (HH:MM:SS)
            place: Place of birth
            latitude: Optional latitude coordinate
            longitude: Optional longitude coordinate
        
        Returns:
            Dictionary with complete chart data
        """
        try:
            # Parse date components
            year, month, day = dob.split('-')
            hour, minute, second = (tob.split(':') + ['0', '0'])[:3]
            
            # Calculate timezone offset (default to UTC if not provided)
            # For Indian Standard Time: '+5.5'
            timezone = '+0.0'  # Default to UTC
            
            # Step 1: Input birth data - all parameters must be strings
            jm.input_birthdata(
                name=str(name),
                place=str(place),  # Place of birth is required
                gender="male",  # Default gender, can be parameterized later
                year=str(year),
                month=str(int(month)),
                day=str(int(day)),
                hour=str(int(hour)),
                min=str(int(minute)),  # NOTE: parameter is 'min' not 'minute'
                sec=str(int(second)),
                lattitude=str(latitude) if latitude else "0.0",  # NOTE: double 't'
                longitude=str(longitude) if longitude else "0.0",
                timezone=timezone
            )
            
            # Step 2: Validate the birth data
            validation_result = jm.validate_birthdata()
            if validation_result != "SUCCESS":
                raise ValueError(f"Birth data validation failed: {validation_result}")
            
            # Step 3: Get the validated birth data dictionary
            birth_data = jm.get_birthdata()
            
            # Step 4: Generate full astrological data using the validated data
            astrological_data = jm.generate_astrologicalData(birth_data)
            
            # Store for reference
            self.birth_data = birth_data
            self.current_chart = astrological_data
            
            # Extract and format output
            output = {
                "user_details": {
                    "name": name,
                    "dob": dob,
                    "tob": tob,
                    "pob": place,
                    "latitude": latitude,
                    "longitude": longitude,
                    "generated_at": datetime.now().isoformat()
                },
                "divisional_charts": self._extract_divisional_charts(astrological_data),
                "balas": self._extract_balas(astrological_data),
                "dashas": self._extract_dashas(astrological_data),
                "nakshatras": self._extract_nakshatras(astrological_data),
                "panchang": self._extract_panchang(astrological_data)
            }
            
            return output
            
        except Exception as e:
            raise ValueError(f"Error generating chart: {str(e)}")
    
    def _extract_divisional_charts(self, astrological_data: Dict) -> Dict[str, Any]:
        """Extract all 16 divisional charts (D1-D60)"""
        charts = {}
        
        try:
            # D1 (Rashi chart) is main
            if hasattr(astrological_data, 'D1'):
                charts['D1'] = self._format_chart_data(astrological_data.D1)
            
            # D2-D60 divisional charts
            for i in range(2, 61):
                chart_attr = f'D{i}'
                if hasattr(astrological_data, chart_attr):
                    charts[chart_attr] = self._format_chart_data(getattr(astrological_data, chart_attr))
        except Exception as e:
            print(f"Warning: Could not extract all divisional charts: {e}")
        
        return charts
    
    def _format_chart_data(self, chart) -> Dict[str, Any]:
        """Format individual chart data"""
        try:
            return {
                "ascendant": self._get_sign_info(chart.ascendant) if hasattr(chart, 'ascendant') else None,
                "planets": self._extract_planets(chart),
                "houses": self._extract_houses(chart),
                "aspects": self._extract_aspects(chart) if hasattr(chart, 'aspects') else {}
            }
        except Exception as e:
            return {"error": f"Could not format chart: {e}"}
    
    def _extract_planets(self, chart) -> Dict[str, Any]:
        """Extract planet positions from chart"""
        planets = {}
        
        try:
            if hasattr(chart, 'planets'):
                for planet in chart.planets:
                    planet_name = getattr(planet, 'name', 'Unknown')
                    planets[planet_name] = {
                        "sign": getattr(planet, 'sign', None),
                        "degree": getattr(planet, 'degree', None),
                        "nakshatra": getattr(planet, 'nakshatra', None),
                        "nakshatra_pada": getattr(planet, 'nakshatra_pada', None),
                        "speed": getattr(planet, 'speed', None),
                        "retrograde": getattr(planet, 'retrograde', False)
                    }
        except Exception as e:
            print(f"Warning: Could not extract planets: {e}")
        
        return planets
    
    def _extract_houses(self, chart) -> List[Dict[str, Any]]:
        """Extract house data from chart"""
        houses = []
        
        try:
            if hasattr(chart, 'houses'):
                for i, house in enumerate(chart.houses, 1):
                    houses.append({
                        "house": i,
                        "sign": getattr(house, 'sign', None),
                        "degree": getattr(house, 'degree', None)
                    })
        except Exception as e:
            print(f"Warning: Could not extract houses: {e}")
        
        return houses
    
    def _extract_aspects(self, chart) -> Dict[str, Any]:
        """Extract planetary aspects"""
        aspects = {}
        
        try:
            if hasattr(chart, 'aspects'):
                aspects = chart.aspects
        except Exception as e:
            print(f"Warning: Could not extract aspects: {e}")
        
        return aspects
    
    def _get_sign_info(self, ascendant) -> Dict[str, Any]:
        """Get ascendant sign information"""
        try:
            return {
                "sign": getattr(ascendant, 'sign', None),
                "degree": getattr(ascendant, 'degree', None),
                "nakshatra": getattr(ascendant, 'nakshatra', None)
            }
        except:
            return {}
    
    def _extract_balas(self, astrological_data: Dict) -> Dict[str, Any]:
        """Extract Shadbala and Ashtakavarga"""
        balas = {
            "shadbala": {},
            "ashtakavarga": {}
        }
        
        try:
            if hasattr(astrological_data, 'shadbala'):
                balas['shadbala'] = astrological_data.shadbala
            
            if hasattr(astrological_data, 'ashtakavarga'):
                balas['ashtakavarga'] = astrological_data.ashtakavarga
        except Exception as e:
            print(f"Warning: Could not extract balas: {e}")
        
        return balas
    
    def _extract_dashas(self, astrological_data: Dict) -> Dict[str, Any]:
        """Extract Vimshottari Dasha and other dashas"""
        dashas = {
            "vimshottari": {
                "mahadasha": [],
                "antardasha": [],
                "pratyantardasha": [],
                "current_dasha": None
            },
            "other_dashas": {}
        }
        
        try:
            if hasattr(astrological_data, 'vimshottari'):
                vd = astrological_data.vimshottari
                
                # Mahadasha
                if hasattr(vd, 'mahadasha'):
                    dashas['vimshottari']['mahadasha'] = self._format_dasha_list(vd.mahadasha)
                
                # Antardasha
                if hasattr(vd, 'antardasha'):
                    dashas['vimshottari']['antardasha'] = self._format_dasha_list(vd.antardasha)
                
                # Pratyantardasha
                if hasattr(vd, 'pratyantardasha'):
                    dashas['vimshottari']['pratyantardasha'] = self._format_dasha_list(vd.pratyantardasha)
                
                # Current dasha
                if hasattr(vd, 'current'):
                    dashas['vimshottari']['current_dasha'] = vd.current
        except Exception as e:
            print(f"Warning: Could not extract dashas: {e}")
        
        return dashas
    
    def _format_dasha_list(self, dasha_list) -> List[Dict[str, Any]]:
        """Format dasha period list"""
        formatted = []
        
        try:
            for dasha in dasha_list:
                formatted.append({
                    "lord": getattr(dasha, 'lord', None),
                    "start_date": str(getattr(dasha, 'start_date', None)),
                    "end_date": str(getattr(dasha, 'end_date', None)),
                    "duration_years": getattr(dasha, 'duration', None)
                })
        except Exception as e:
            print(f"Warning: Could not format dasha list: {e}")
        
        return formatted
    
    def _extract_nakshatras(self, astrological_data: Dict) -> Dict[str, Any]:
        """Extract Nakshatra data"""
        nakshatras = {}
        
        try:
            if hasattr(astrological_data, 'nakshatras'):
                for i, nak in enumerate(astrological_data.nakshatras):
                    nakshatras[f'nakshatra_{i}'] = {
                        "name": getattr(nak, 'name', None),
                        "lord": getattr(nak, 'lord', None),
                        "pada": getattr(nak, 'pada', None)
                    }
        except Exception as e:
            print(f"Warning: Could not extract nakshatras: {e}")
        
        return nakshatras
    
    def _extract_panchang(self, astrological_data: Dict) -> Dict[str, Any]:
        """Extract Panchang data (Tithi, Vara, Yoga, Karana)"""
        panchang = {
            "tithi": None,
            "vara": None,
            "yoga": None,
            "karana": None
        }
        
        try:
            if hasattr(astrological_data, 'panchang'):
                p = astrological_data.panchang
                panchang = {
                    "tithi": getattr(p, 'tithi', None),
                    "vara": getattr(p, 'vara', None),
                    "yoga": getattr(p, 'yoga', None),
                    "karana": getattr(p, 'karana', None)
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
            if hasattr(self.current_chart, 'vimshottari'):
                vd = self.current_chart.vimshottari
                
                if hasattr(vd, 'mahadasha'):
                    for i, dasha in enumerate(vd.mahadasha[:count]):
                        dashas.append({
                            "type": "Mahadasha",
                            "lord": getattr(dasha, 'lord', None),
                            "start": str(getattr(dasha, 'start_date', None)),
                            "end": str(getattr(dasha, 'end_date', None)),
                            "duration_years": getattr(dasha, 'duration', None)
                        })
        except Exception as e:
            print(f"Warning: Could not get dasha periods: {e}")
        
        return dashas
    
    def get_divisional_chart(self, chart_type: str) -> Dict[str, Any]:
        """Get specific divisional chart (e.g., 'D9' for Navamsa)"""
        if not self.current_chart:
            raise ValueError("No chart generated. Call generate_full_chart() first.")
        
        try:
            chart_attr = chart_type.upper()
            if hasattr(self.current_chart, chart_attr):
                return self._format_chart_data(getattr(self.current_chart, chart_attr))
            else:
                raise ValueError(f"Chart {chart_type} not available")
        except Exception as e:
            raise ValueError(f"Error getting divisional chart: {e}")
    
    def export_for_ai_agent(self) -> str:
        """Export current chart as JSON for AI Agent consumption"""
        if not self.current_chart:
            raise ValueError("No chart generated. Call generate_full_chart() first.")
        
        try:
            # Create a clean dict structure for AI consumption
            output = {
                "status": "success",
                "data": self.current_chart
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
    print("Testing AstroEngine with jyotishyamitra...")
    
    try:
        engine = AstroEngine()
        
        # Sample birth data (adjust as needed)
        chart = engine.generate_full_chart(
            name="Test Person",
            dob="1990-01-15",
            tob="12:30:00",
            place="New York",
            latitude=40.7128,
            longitude=-74.0060
        )
        
        print("✅ Chart generation successful!")
        print(f"Generated chart with {len(chart.get('divisional_charts', {}))} divisional charts")
        
        # Get dashas
        dashas = engine.get_dasha_periods(5)
        print(f"✅ Retrieved {len(dashas)} dasha periods")
        
        # Export for AI
        ai_json = engine.export_for_ai_agent()
        print("✅ Exported chart for AI Agent")
        print(f"JSON output length: {len(ai_json)} characters")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        test_engine()
    else:
        print("AstroEngine module loaded. Use --test flag to run tests.")
