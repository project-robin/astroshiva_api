import asyncio
import json
import os
import tempfile
import unittest
from datetime import datetime as RealDateTime

os.environ.setdefault("XDG_DATA_HOME", os.path.join(tempfile.gettempdir(), "astroshiva-test-data"))

import astro_engine
from fastapi import HTTPException
from app import ChartRequest, generate_chart, generate_chart_get, health_check


class FrozenDateTime(RealDateTime):
    @classmethod
    def now(cls, tz=None):
        value = cls(2026, 8, 2, 12, 0, 0)
        return value if tz is None else value.replace(tzinfo=tz)


def dms(value):
    degrees, minutes, seconds = map(int, value.split("-"))
    return degrees + minutes / 60 + seconds / 3600


class AstrologyRegressionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # ponytail: freeze time so current dashas/transits remain regression-testable.
        astro_engine.datetime = FrozenDateTime
        cls.engine = astro_engine.AstroEngine()
        cls.reference = cls.engine.generate_full_chart(
            name="K",
            dob="2001-05-26",
            tob="21:48:00",
            place="Ahmednagar, India",
            latitude=19.3833,
            longitude=74.65,
            timezone="+5.5",
        )

    def test_astrosage_d1_reference(self):
        expected = {
            "Sun": ("Taurus", "11-36-40", "Rohini", 1),
            "Moon": ("Gemini", "28-26-09", "Punarvasu", 3),
            "Mars": ("Sagittarius", "03-46-11", "Mula", 2),
            "Mercury": ("Gemini", "03-17-46", "Mrigashira", 3),
            "Jupiter": ("Taurus", "25-18-11", "Mrigashira", 1),
            "Venus": ("Pisces", "26-27-14", "Revati", 3),
            "Saturn": ("Taurus", "10-39-00", "Rohini", 1),
            "Rahu": ("Gemini", "14-05-42", "Ardra", 3),
            "Ketu": ("Sagittarius", "14-05-42", "Purva Ashadha", 1),
        }
        d1 = self.reference["divisional_charts"]["D1"]
        self.assertEqual(d1["ascendant"]["sign"], "Sagittarius")
        self.assertAlmostEqual(d1["ascendant"]["degree"], dms("19-54-38"), delta=0.02)
        for planet, (sign, degree, nakshatra, pada) in expected.items():
            with self.subTest(planet=planet):
                actual = d1["planets"][planet]
                self.assertEqual(actual["sign"], sign)
                self.assertAlmostEqual(actual["degree"], dms(degree), delta=0.02)
                self.assertEqual(actual["nakshatra"], nakshatra)
                self.assertEqual(actual["pada"], pada)

    def test_parashara_varga_examples(self):
        # Examples from P.V.R. Narasimha Rao's Vedic Astrology: An Integrated Approach.
        engine = astro_engine.AstroEngine()

        def sign(rasi, degree, harmonic):
            return engine._get_planet_varga_sign((rasi - 1) * 30 + degree, harmonic)[0]

        examples = [
            (2, 3, 4, "Taurus"), (2, 14, 4, "Leo"), (2, 23, 4, "Aquarius"),
            (3, 10, 7, "Leo"), (6, 19, 7, "Cancer"),
            (3, 11, 9, "Capricorn"), (8, 19, 9, "Sagittarius"),
            (3, 10, 10, "Virgo"), (8, 19, 10, "Capricorn"),
            (3, 11, 12, "Libra"), (8, 19, 12, "Gemini"),
            (3, 11, 16, "Taurus"), (8, 19, 16, "Gemini"),
            (3, 11, 20, "Pisces"), (8, 19, 20, "Sagittarius"),
            (3, 11, 24, "Aries"), (8, 19, 24, "Libra"),
            (3, 11, 40, "Gemini"), (8, 19, 40, "Scorpio"),
            (3, 11, 45, "Aries"), (8, 19, 45, "Sagittarius"),
            (8, 12 + 58 / 60, 60, "Sagittarius"),
        ]
        for rasi, degree, harmonic, expected in examples:
            with self.subTest(rasi=rasi, degree=degree, harmonic=harmonic):
                self.assertEqual(sign(rasi, degree, harmonic), expected)

        self.assertEqual(
            [sign(rasi, 0.1, 27) for rasi in (1, 2, 3, 4)],
            ["Aries", "Cancer", "Libra", "Capricorn"],
        )
        self.assertEqual(sign(1, 4.9, 30), "Aries")
        self.assertEqual(sign(1, 5.1, 30), "Aquarius")
        self.assertEqual(sign(2, 11.9, 30), "Virgo")
        self.assertEqual(sign(2, 12.1, 30), "Pisces")

        # Cancer 27°43' lagna: the old generic (sign * harmonic) rule returned Cancer.
        self.assertEqual(engine._calculate_varga_ascendant(117.72764153873996, 10)[0], "Sagittarius")

        for harmonic in (2, 3, 4, 7, 9, 10, 12, 16, 20, 24, 27, 30, 40, 45, 60):
            with self.subTest(ascendant_harmonic=harmonic):
                self.assertEqual(
                    engine._calculate_varga_ascendant(259.9168733545986, harmonic),
                    engine._get_planet_varga_sign(259.9168733545986, harmonic),
                )

    def test_complete_response_invariants(self):
        charts = self.reference["divisional_charts"]
        self.assertGreaterEqual(len(charts), 16)
        expected_planets = {"Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"}
        for name, chart in charts.items():
            with self.subTest(chart=name):
                self.assertEqual(len(chart["houses"]), 12)
                self.assertEqual(set(chart["planets"]), expected_planets)
                for planet in chart["planets"].values():
                    self.assertGreaterEqual(planet["degree"], 0)
                    self.assertLess(planet["degree"], 30)
        d1 = charts["D1"]["planets"]
        self.assertAlmostEqual((d1["Rahu"]["total_degree"] - d1["Ketu"]["total_degree"]) % 360, 180)
        self.assertEqual(
            [period["lord"] for period in self.reference["dashas"]["vimshottari"]["mahadasha"][:6]],
            ["Jupiter", "Saturn", "Mercury", "Ketu", "Venus", "Sun"],
        )
        self.assertEqual(self.reference["yogini_dasha"]["starting_yogini"], "Pingala")
        self.assertEqual(
            [period["sign"] for period in self.reference["char_dasha"]["maha_dasha"][:6]],
            ["Sagittarius", "Scorpio", "Libra", "Virgo", "Leo", "Cancer"],
        )
        json.dumps(self.reference, allow_nan=False)

        def error_keys(value, path=()):
            found = []
            if isinstance(value, dict):
                for key, child in value.items():
                    child_path = path + (key,)
                    if "error" in str(key).lower() or "traceback" in str(key).lower():
                        found.append(child_path)
                    found.extend(error_keys(child, child_path))
            elif isinstance(value, list):
                for index, child in enumerate(value):
                    found.extend(error_keys(child, path + (index,)))
            return found

        self.assertEqual(error_keys(self.reference), [])

    def test_varga_signs_match_independent_engine(self):
        for key, reference_chart in self.engine.current_chart.divisional_charts.items():
            chart_name = key.upper()
            actual = self.reference["divisional_charts"][chart_name]
            with self.subTest(chart=chart_name, point="Ascendant"):
                self.assertEqual(actual["ascendant"]["sign"], reference_chart.ascendant.sign)

            reference_planets = {
                occupant.celestial_body: occupant.sign
                for house in reference_chart.houses
                for occupant in house.occupants
            }
            for planet, expected_sign in reference_planets.items():
                with self.subTest(chart=chart_name, planet=planet):
                    self.assertEqual(actual["planets"][planet]["sign"], expected_sign)

    def test_dasha_timelines_against_astrosage(self):
        vimshottari = self.reference["dashas"]["vimshottari"]["mahadasha"]
        expected_lords = ["Jupiter", "Saturn", "Mercury", "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu"]
        self.assertEqual([period["lord"] for period in vimshottari[:9]], expected_lords)
        first_end = RealDateTime.strptime(vimshottari[0]["end_date"], "%Y-%m-%d")
        # The retained AstroSage chart ends Jupiter on 12-Apr-2007. The small
        # tolerance reflects the <0.02° Moon-position variance already tested.
        self.assertLessEqual(abs((first_end - RealDateTime(2007, 4, 12)).days), 5)

        char_dasha = self.reference["char_dasha"]["maha_dasha"]
        expected_char = [
            ("Sagittarius", 5, "26/05/01", "26/05/06"),
            ("Scorpio", 1, "26/05/06", "26/05/07"),
            ("Libra", 5, "26/05/07", "26/05/12"),
            ("Virgo", 3, "26/05/12", "26/05/15"),
            ("Leo", 3, "26/05/15", "26/05/18"),
            ("Cancer", 1, "26/05/18", "26/05/19"),
            ("Gemini", 12, "26/05/19", "26/05/31"),
            ("Taurus", 10, "26/05/31", "26/05/41"),
            ("Aries", 8, "26/05/41", "26/05/49"),
            ("Pisces", 10, "26/05/49", "26/05/59"),
        ]
        self.assertEqual(
            [(p["sign"], p["years"], p["start"], p["end"]) for p in char_dasha[:10]],
            expected_char,
        )

        yogini_start = RealDateTime.strptime(
            self.reference["yogini_dasha"]["periods"][0]["start"], "%d/%m/%Y"
        )
        self.assertLessEqual(abs((yogini_start - RealDateTime(2000, 2, 20)).days), 2)

    def test_determinism_across_locations_and_timezones(self):
        cases = [
            ("New York", "1990-01-15", "12:30:45", 40.7128, -74.006, "-05:00"),
            ("Kathmandu", "1988-06-20", "00:00:01", 27.7172, 85.324, "+05:45"),
            ("Sydney", "1975-11-30", "23:59:59", -33.8688, 151.2093, "+11"),
            ("London", "2012-02-29", "06:15:00", 51.5074, -0.1278, "UTC+0"),
            ("Kiritimati", "2000-01-01", "00:00:00", 1.8721, -157.4278, "+14"),
        ]
        for place, dob, tob, latitude, longitude, timezone in cases:
            kwargs = dict(
                name="Regression Test",
                dob=dob,
                tob=tob,
                place=place,
                latitude=latitude,
                longitude=longitude,
                timezone=timezone,
                charts=["D1", "D9", "D60"],
            )
            with self.subTest(place=place):
                first = astro_engine.AstroEngine().generate_full_chart(**kwargs)
                second = astro_engine.AstroEngine().generate_full_chart(**kwargs)
                self.assertEqual(first, second)

    def test_api_contract(self):
        request = ChartRequest(
            name="API Test",
            dob="1990-01-15",
            tob="12:30:00",
            place="New York",
            latitude=40.7128,
            longitude=-74.006,
            timezone="-5",
            charts=["D1", "D9"],
        )
        response = asyncio.run(generate_chart(request))
        self.assertEqual(response.status, "success")
        self.assertEqual(set(response.data["divisional_charts"]), {"D1", "D9"})
        self.assertEqual(asyncio.run(health_check())["status"], "healthy")

        d9_only = request.model_copy(update={"charts": ["D9"]})
        d9_response = asyncio.run(generate_chart(d9_only))
        self.assertEqual(set(d9_response.data["divisional_charts"]), {"D1", "D9"})

        get_response = asyncio.run(generate_chart_get(
            name="API Test",
            dob="1990-01-15",
            tob="12:30:00",
            place="New York",
            latitude=40.7128,
            longitude=-74.006,
            timezone="-5",
            charts='"D9"',
        ))
        self.assertEqual(set(get_response["data"]["divisional_charts"]), {"D1", "D9"})

        with self.assertRaises(HTTPException) as invalid_chart:
            asyncio.run(generate_chart_get(
                name="API Test",
                dob="1990-01-15",
                tob="12:30:00",
                place="New York",
                latitude=40.7128,
                longitude=-74.006,
                timezone="-5",
                charts="D99",
            ))
        self.assertEqual(invalid_chart.exception.status_code, 400)

    def test_coordinates_are_required(self):
        with self.assertRaisesRegex(ValueError, "Latitude and Longitude are required"):
            astro_engine.AstroEngine().generate_full_chart(
                name="Invalid",
                dob="2000-01-01",
                tob="00:00:00",
                place="Unknown",
            )

    def test_invalid_accuracy_inputs_are_rejected(self):
        valid = dict(
            name="Invalid",
            dob="2000-01-01",
            tob="00:00:00",
            place="Unknown",
            latitude=0,
            longitude=0,
        )
        with self.assertRaisesRegex(ValueError, "Invalid timezone offset"):
            astro_engine.AstroEngine().generate_full_chart(**valid, timezone="IST")
        with self.assertRaisesRegex(ValueError, "Timezone offset must be"):
            astro_engine.AstroEngine().generate_full_chart(**valid, timezone="+15")
        with self.assertRaisesRegex(ValueError, "Unsupported divisional charts"):
            astro_engine.AstroEngine().generate_full_chart(**valid, timezone="+0", charts=["D99"])
        with self.assertRaisesRegex(ValueError, "Latitude must be"):
            astro_engine.AstroEngine().generate_full_chart(**{**valid, "latitude": 91}, timezone="+0")
        with self.assertRaisesRegex(ValueError, "Timezone offset is required"):
            astro_engine.AstroEngine().generate_full_chart(**valid)


if __name__ == "__main__":
    unittest.main(verbosity=2)
