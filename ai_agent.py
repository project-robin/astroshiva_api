"""
AI Agent Integration Module
Formats astrology data for LLM consumption
"""

import json
from typing import Dict, Any, List
from datetime import datetime
from astro_engine import AstroEngine


class AIAgentInterface:
    """Interface for AI Agent consumption of astrological data"""
    
    def __init__(self):
        self.engine = AstroEngine()
    
    def process_birth_data(self, birth_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process birth data for AI Agent analysis
        
        Args:
            birth_info: Dictionary with name, dob, tob, place, latitude, longitude
        
        Returns:
            Formatted data for AI consumption
        """
        chart = self.engine.generate_full_chart(**birth_info)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "person": {
                "name": birth_info.get('name'),
                "birth_date": birth_info.get('dob'),
                "birth_time": birth_info.get('tob'),
                "birth_place": birth_info.get('place')
            },
            "astrological_profile": self._create_profile(chart),
            "current_periods": self._get_current_periods(chart),
            "predictions": self._generate_ai_insights(chart)
        }
    
    def _create_profile(self, chart: Dict[str, Any]) -> Dict[str, Any]:
        """Create condensed astrological profile"""
        d1 = chart['divisional_charts'].get('D1', {})
        
        profile = {
            "ascendant": d1.get('ascendant', {}),
            "sun_sign": self._get_planet_sign(d1, 'Sun'),
            "moon_sign": self._get_planet_sign(d1, 'Moon'),
            "planetary_strengths": self._calculate_strengths(chart),
            "key_characteristics": self._extract_characteristics(chart)
        }
        
        return profile
    
    def _get_planet_sign(self, chart_data: Dict, planet: str) -> Dict[str, Any]:
        """Get planet position in sign"""
        planets = chart_data.get('planets', {})
        return planets.get(planet, {})
    
    def _calculate_strengths(self, chart: Dict[str, Any]) -> Dict[str, float]:
        """Calculate planetary strengths from Shadbala"""
        balas = chart.get('balas', {})
        shadbala = balas.get('shadbala', {})
        
        strengths = {}
        try:
            if isinstance(shadbala, dict):
                strengths = shadbala
        except:
            pass
        
        return strengths
    
    def _extract_characteristics(self, chart: Dict[str, Any]) -> List[str]:
        """Extract key astrological characteristics"""
        characteristics = []
        d1 = chart['divisional_charts'].get('D1', {})
        
        # Ascendant characteristics
        asc = d1.get('ascendant', {})
        if asc and asc.get('sign'):
            characteristics.append(f"Ascendant in {asc['sign']}")
        
        # Moon characteristics
        moon = d1.get('planets', {}).get('Moon', {})
        if moon and moon.get('sign'):
            characteristics.append(f"Moon in {moon['sign']}")
        
        return characteristics
    
    def _get_current_periods(self, chart: Dict[str, Any]) -> Dict[str, Any]:
        """Get currently active dasha and periods"""
        dashas = chart.get('dashas', {})
        vimshottari = dashas.get('vimshottari', {})
        
        periods = {
            "current_mahadasha": vimshottari.get('current_dasha'),
            "upcoming_periods": vimshottari.get('mahadasha', [])[:3]
        }
        
        return periods
    
    def _generate_ai_insights(self, chart: Dict[str, Any]) -> Dict[str, str]:
        """Generate insights for AI Agent"""
        insights = {
            "career": self._career_insights(chart),
            "relationships": self._relationship_insights(chart),
            "health": self._health_insights(chart),
            "finance": self._finance_insights(chart)
        }
        
        return insights
    
    def _career_insights(self, chart: Dict[str, Any]) -> str:
        """Generate career-related insights"""
        d10 = chart['divisional_charts'].get('D10', {})
        if d10:
            return "Career chart (D10) analyzed. Review planetary positions in 10th house."
        return "Career analysis pending D10 chart generation."
    
    def _relationship_insights(self, chart: Dict[str, Any]) -> str:
        """Generate relationship insights"""
        d9 = chart['divisional_charts'].get('D9', {})
        if d9:
            return "Relationship chart (D9/Navamsa) analyzed. Review Venus and 7th house."
        return "Relationship analysis pending D9 chart generation."
    
    def _health_insights(self, chart: Dict[str, Any]) -> str:
        """Generate health insights"""
        d12 = chart['divisional_charts'].get('D12', {})
        if d12:
            return "Health chart (D12) analyzed. Review lagna and 6th house."
        return "Health analysis pending D12 chart generation."
    
    def _finance_insights(self, chart: Dict[str, Any]) -> str:
        """Generate finance insights"""
        d20 = chart['divisional_charts'].get('D20', {})
        if d20:
            return "Finance chart (D20/Vimshamsa) analyzed. Review 2nd and 11th houses."
        return "Finance analysis pending D20 chart generation."
    
    def export_for_llm(self, birth_info: Dict[str, Any], format: str = "json") -> str:
        """
        Export astrological data in format optimized for LLM
        
        Args:
            birth_info: Birth information dictionary
            format: Output format ('json' or 'markdown')
        
        Returns:
            Formatted string for LLM consumption
        """
        data = self.process_birth_data(birth_info)
        
        if format == "markdown":
            return self._to_markdown(data)
        else:
            return json.dumps(data, indent=2, default=str)
    
    def _to_markdown(self, data: Dict[str, Any]) -> str:
        """Convert to markdown format for LLM"""
        md = []
        
        person = data['person']
        md.append(f"# Astrological Profile: {person['name']}")
        md.append(f"\n**Birth Details:**")
        md.append(f"- Date: {person['birth_date']}")
        md.append(f"- Time: {person['birth_time']}")
        md.append(f"- Place: {person['birth_place']}")
        
        profile = data['astrological_profile']
        md.append(f"\n## Astrological Profile\n")
        md.append(f"- **Ascendant:** {profile['ascendant']}")
        md.append(f"- **Sun Sign:** {profile['sun_sign']}")
        md.append(f"- **Moon Sign:** {profile['moon_sign']}")
        
        periods = data['current_periods']
        md.append(f"\n## Current Periods\n")
        if periods['current_mahadasha']:
            md.append(f"- **Current Dasha:** {periods['current_mahadasha']}")
        
        insights = data['predictions']
        md.append(f"\n## Life Areas Analysis\n")
        md.append(f"- **Career:** {insights['career']}")
        md.append(f"- **Relationships:** {insights['relationships']}")
        md.append(f"- **Health:** {insights['health']}")
        md.append(f"- **Finance:** {insights['finance']}")
        
        return "\n".join(md)


def test_ai_interface():
    """Test AI Agent interface"""
    print("Testing AI Agent Interface...")
    
    birth_info = {
        "name": "Test Person",
        "dob": "1990-01-15",
        "tob": "12:30:00",
        "place": "New York",
        "latitude": 40.7128,
        "longitude": -74.0060
    }
    
    try:
        ai = AIAgentInterface()
        
        # Test JSON export
        json_output = ai.export_for_llm(birth_info, format="json")
        print("✅ JSON export successful")
        
        # Test Markdown export
        md_output = ai.export_for_llm(birth_info, format="markdown")
        print("✅ Markdown export successful")
        print("\nSample Markdown Output:")
        print(md_output[:500] + "...")
        
        return True
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        test_ai_interface()
    else:
        print("AI Agent Interface module loaded.")
