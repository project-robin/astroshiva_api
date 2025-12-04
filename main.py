"""
Main application - Free Vedic Astrology using jyotishyamitra
No external API calls - 100% local and offline
"""

import json
import argparse
from datetime import datetime
from pathlib import Path
from astro_engine import AstroEngine


def main():
    """Main application entry point"""
    parser = argparse.ArgumentParser(
        description="Free Vedic Astrology Calculator - Local & Offline"
    )
    
    parser.add_argument("--name", type=str, help="Person's name")
    parser.add_argument("--dob", type=str, help="Date of birth (YYYY-MM-DD)")
    parser.add_argument("--tob", type=str, help="Time of birth (HH:MM:SS)")
    parser.add_argument("--place", type=str, help="Place of birth")
    parser.add_argument("--lat", type=float, help="Latitude coordinate")
    parser.add_argument("--lon", type=float, help="Longitude coordinate")
    parser.add_argument("--chart", type=str, help="Specific chart to generate (e.g., D9, D10)")
    parser.add_argument("--output", type=str, help="Output file path (JSON)")
    parser.add_argument("--test", action="store_true", help="Run test calculation")
    
    args = parser.parse_args()
    
    engine = AstroEngine()
    
    if args.test:
        # Run test with sample data
        print("Running test calculation...")
        chart = engine.generate_full_chart(
            name="Test Subject",
            dob="1990-01-15",
            tob="12:30:00",
            place="New York",
            latitude=40.7128,
            longitude=-74.0060
        )
        
        print("✅ Test calculation successful!")
        print(f"   Charts generated: {len(chart['divisional_charts'])}")
        print(f"   Dasha periods: {len(chart['dashas']['vimshottari']['mahadasha'])}")
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(chart, f, indent=2, default=str)
            print(f"✅ Output saved to: {args.output}")
        else:
            print(json.dumps(chart, indent=2, default=str))
        
        return
    
    # Validate required arguments
    if not all([args.name, args.dob, args.tob, args.place]):
        parser.print_help()
        print("\nError: --name, --dob, --tob, and --place are required")
        return
    
    try:
        # Generate chart
        print(f"Generating chart for {args.name}...")
        chart = engine.generate_full_chart(
            name=args.name,
            dob=args.dob,
            tob=args.tob,
            place=args.place,
            latitude=args.lat,
            longitude=args.lon
        )
        
        # Get specific chart if requested
        if args.chart:
            print(f"Extracting {args.chart} chart...")
            chart_data = engine.get_divisional_chart(args.chart)
            output = {
                "chart_type": args.chart,
                "data": chart_data
            }
        else:
            output = chart
        
        # Output results
        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w') as f:
                json.dump(output, f, indent=2, default=str)
            print(f"✅ Chart saved to: {args.output}")
        else:
            print(json.dumps(output, indent=2, default=str))
        
        print("✅ Calculation complete!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
