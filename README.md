# AstroShiva API

FastAPI service for deterministic Vedic astrology calculations using `jyotishganit`, Swiss Ephemeris, Lahiri ayanamsa, and bundled astronomical data.

## Run locally

Requires Python 3.11.

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 8000
```

The first local run does not download ephemeris data: `astronomy_data/de421.bsp` and `astronomy_data/hip_main.dat` are committed with the service.

## API

Health check:

```bash
curl http://localhost:8000/health
```

Generate a chart:

```bash
curl -X POST http://localhost:8000/api/chart \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "K",
    "dob": "2001-05-26",
    "tob": "21:48:00",
    "place": "Ahmednagar, India",
    "latitude": 19.3833,
    "longitude": 74.65,
    "timezone": "+5.5",
    "charts": ["D1", "D9", "D10"]
  }'
```

Interactive documentation is available at `/docs` and `/redoc`. See `API_DOCUMENTATION.md` for the response schema.

## Accuracy regression

```bash
python -m unittest -v test_regression.py
```

The regression suite checks:

- D1 signs, nakshatras, padas, and planetary degrees against the repository's AstroSage reference, with a maximum position difference of `0.02°`.
- All divisional-chart degrees and response invariants.
- Parashara varga examples plus an independent 15-chart/135-planet sign comparison.
- Rahu/Ketu opposition and Vimshottari, Yogini, and Char Dasha timelines.
- Deterministic results across New York, Kathmandu, Sydney, London, and Kiritimati.
- POST API and health-check contracts.
- Required coordinate/timezone validation, fail-fast calculation errors, and strict JSON serialization.

Do not change calculation code or dependency versions unless this suite passes before and after the change.

## Deployment

Render configuration lives in `render.yaml`. The free service is kept active by `.github/workflows/keep-render-awake.yml`.

## Dependency licensing

Swiss Ephemeris uses a dual AGPL/professional license. Before deploying this public API, choose and comply with one of those licenses. The no-cost path is AGPL, which has source-sharing requirements for network services; the repository does not currently contain a project license file.
