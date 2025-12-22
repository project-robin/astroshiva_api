
from astro_engine import AstroEngine
import json

def probe():
    engine = AstroEngine()
    chart = engine.generate_full_chart(
        name="Probe",
        dob="2024-01-01",
        tob="12:00:00",
        place="Delhi",
        latitude=28.6,
        longitude=77.2,
        timezone="+5.5"
    )
    
    # Access the raw chart object if possible, or look at what's extracted
    # The engine stores 'current_chart'
    if hasattr(engine, 'current_chart'):
        raw = engine.current_chart
        if hasattr(raw, 'd1_chart'):
            p0 = raw.d1_chart.planets[0]
            print(f"Planet: {p0.celestial_body}")
            print(f"Attributes: {dir(p0)}")
            print(f"Shadbala Value: {p0.shadbala}")
            if hasattr(p0, 'shadbala_details'):
                print(f"Details: {p0.shadbala_details}")

if __name__ == "__main__":
    probe()
