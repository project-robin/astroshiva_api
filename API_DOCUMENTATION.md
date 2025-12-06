# Astro-Shiva API v2.0.0 - Complete Documentation

**Base URL:** `https://astroshiva-api.onrender.com`  
**Protocol:** HTTPS  
**Authentication:** None required (Public API)  
**Rate Limit:** None (Fair use policy)  
**CORS:** Enabled for all origins

---

## Quick Start

### Simple Example (JavaScript)
```javascript
fetch('https://astroshiva-api.onrender.com/api/chart', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    name: "John Doe",
    dob: "1990-05-15",
    tob: "14:30:00",
    place: "Mumbai, India",
    latitude: 19.0760,
    longitude: 72.8777,
    timezone: "+5.5"
  })
})
.then(res => res.json())
.then(data => console.log(data));
```

---

## API Endpoints

### 1. Generate Birth Chart (POST)
**Primary endpoint for generating complete astrological data.**

**Endpoint:** `POST /api/chart`

**Request Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "name": "John Doe",
  "dob": "1990-05-15",
  "tob": "14:30:00",
  "place": "Mumbai, India",
  "latitude": 19.0760,
  "longitude": 72.8777,
  "timezone": "+5.5",
  "charts": ["D1", "D9"]
}
```

**Field Descriptions:**

| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| `name` | string | Yes | Person's full name | "John Doe" |
| `dob` | string | Yes | Date of birth (YYYY-MM-DD) | "1990-05-15" |
| `tob` | string | Yes | Time of birth (HH:MM:SS) | "14:30:00" |
| `place` | string | Yes | Place of birth (reference only) | "Mumbai, India" |
| `latitude` | number | Yes | Latitude coordinate | 19.0760 |
| `longitude` | number | Yes | Longitude coordinate | 72.8777 |
| `timezone` | string | Yes | GMT offset (e.g., "+5.5", "-5.0") | "+5.5" |
| `charts` | array | No | List of charts to return (default: all) | ["D1", "D9"] |

**Available Charts:**
`D1` (Rashi), `D2`, `D3`, `D4`, `D7`, `D9` (Navamsa), `D10`, `D12`, `D16`, `D20`, `D24`, `D27`, `D30`, `D40`, `D45`, `D60`

**Response (200 OK):**
```json
{
  "status": "success",
  "data": {
    "meta": {
      "api_version": "2.0.0",
      "calculation_engine": "jyotishganit + swisseph",
      "ayanamsa": "Lahiri (Chitrapaksha)"
    },
    "divisional_charts": { ... },
    "jaimini_karakas": { ... },
    "panchadha_maitri": { ... },
    "current_transits": { ... },
    "yogas": [ ... ],
    "panchang": { ... },
    "dashas": { ... }
  }
}
```

---

### 2. Generate Birth Chart (GET)
**Lightweight alternative using query parameters.**

**Endpoint:** `GET /api/chart-get`

**Query Parameters:**
```
?name=John%20Doe
&dob=1990-05-15
&tob=14:30:00
&place=Mumbai
&latitude=19.0760
&longitude=72.8777
&timezone=+5.5
&charts=D1,D9
```

**Example:**
```bash
curl "https://astroshiva-api.onrender.com/api/chart-get?name=John&dob=1990-05-15&tob=14:30:00&place=Mumbai&latitude=19.0760&longitude=72.8777&timezone=+5.5&charts=D1,D9"
```

---

### 3. Test Endpoint
**Pre-filled test data for quick verification.**

**Endpoint:** `GET /api/chart-test`

**Example:**
```bash
curl https://astroshiva-api.onrender.com/api/chart-test
```

---

### 4. Health Check
**Verify API availability.**

**Endpoint:** `GET /health`

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2023-10-27T10:00:00",
  "service": "astro-shiva-api"
}
```

---

## Complete Response Schema

### Top-Level Structure
```json
{
  "status": "success",
  "data": {
    "meta": { ... },
    "divisional_charts": { ... },
    "jaimini_karakas": { ... },
    "panchadha_maitri": { ... },
    "current_transits": { ... },
    "yogas": [ ... ],
    "panchang": { ... },
    "dashas": { ... }
  }
}
```

### Meta Information
```json
"meta": {
  "api_version": "2.0.0",
  "calculation_engine": "jyotishganit + swisseph",
  "ayanamsa": "Lahiri (Chitrapaksha)",
  "timestamp": "2023-10-27T10:00:00"
}
```

### Divisional Charts
```json
"divisional_charts": {
  "D1": {
    "ascendant": {
      "sign": "Leo",
      "sign_id": 5,
      "degree": 14.53,
      "total_degree": 134.53,
      "nakshatra": "Purva Phalguni",
      "pada": 2
    },
    "houses": [
      {
        "house": 1,
        "sign": "Leo",
        "sign_id": 5,
        "cusp": 14.53,
        "madhya": 29.76
      }
      // ... 11 more houses
    ],
    "planets": {
      "Sun": {
        "sign": "Taurus",
        "sign_id": 2,
        "degree": 12.4,
        "total_degree": 42.4,
        "speed": 0.98,
        "is_retrograde": false,
        "house": 10,
        "dignity": "neutral",
        "nakshatra": "Rohini",
        "pada": 3,
        "avasthas": {
          "baaladi": {
            "state": "Young",
            "full_name": "Young (Kumara)"
          },
          "jagradadi": {
            "state": "Awake"
          }
        },
        "kp": {
          "sign_lord": "Venus",
          "nakshatra_lord": "Moon",
          "sub_lord": "Rahu",
          "sub_sub_lord": "Jupiter"
        }
      }
      // ... Moon, Mars, Mercury, Jupiter, Venus, Saturn, Rahu, Ketu
    }
  }
  // ... D9, D10, etc. (if requested)
}
```

### Planet Dignity Values
- `exalted` - Planet in exaltation
- `own` - Planet in own sign
- `moolatrikona` - Planet in moolatrikona
- `friend` - Planet in friend's sign
- `neutral` - Planet in neutral sign
- `enemy` - Planet in enemy's sign
- `debilitated` - Planet in debilitation

### Jaimini Karakas (New in v2.0)
```json
"jaimini_karakas": {
  "Atmakaraka": {
    "planet": "Moon",
    "description": "Significator of the Soul/Self"
  },
  "Amatyakaraka": {
    "planet": "Venus",
    "description": "Significator of Career/Minister"
  },
  "Bhratrukaraka": { "planet": "...", "description": "..." },
  "Matrukaraka": { "planet": "...", "description": "..." },
  "Putrakaraka": { "planet": "...", "description": "..." },
  "Gnatikaraka": { "planet": "...", "description": "..." },
  "Darakaraka": { "planet": "...", "description": "..." }
}
```

### Panchadha Maitri (New in v2.0)
5-fold friendship matrix between planets in this chart.
```json
"panchadha_maitri": {
  "Sun": {
    "Moon": "Great Friend",
    "Mars": "Friend",
    "Saturn": "Great Enemy"
  }
  // ... for all planets
}
```

**Relationship Values:**
- `Great Friend`
- `Friend`
- `Neutral`
- `Enemy`
- `Great Enemy`

### Current Transits (New in v2.0)
Real-time planetary positions relative to birth Moon.
```json
"current_transits": {
  "Saturn": {
    "current_sign": "Aquarius",
    "current_degree": 4.5,
    "house_from_birth_moon": 1,
    "is_retrograde": true
  }
  // ... for all planets
}
```

### Yogas
```json
"yogas": [
  "Gajakesari Yoga",
  "Budhaditya Yoga",
  "Parivartana Yoga",
  "Vipreet Raja Yoga"
]
```

### Panchang
```json
"panchang": {
  "tithi": "Shukla Panchami",
  "vara": "Monday",
  "nakshatra": "Rohini",
  "yoga": "Vishkambha",
  "karana": "Bava"
}
```

### Dashas
```json
"dashas": {
  "current": {
    "lord": "Jupiter",
    "start_date": "2020-04-10",
    "end_date": "2028-04-10"
  },
  "upcoming": {
    "mahadashas": {
      "Saturn": { "start": "2028-04-10", "end": "2047-04-10" }
    }
  }
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "status": "error",
  "error": "Latitude and Longitude are required",
  "type": "ValueError"
}
```

### 500 Internal Server Error
```json
{
  "status": "error",
  "error": "Calculation failed",
  "type": "Exception",
  "traceback": "..."
}
```

---

## Code Examples

### JavaScript (Fetch API)
```javascript
async function getChart(birthData) {
  const response = await fetch('https://astroshiva-api.onrender.com/api/chart', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(birthData)
  });
  
  if (!response.ok) {
    throw new Error(`API Error: ${response.status}`);
  }
  
  return await response.json();
}

// Usage
const chart = await getChart({
  name: "John Doe",
  dob: "1990-05-15",
  tob: "14:30:00",
  place: "Mumbai",
  latitude: 19.0760,
  longitude: 72.8777,
  timezone: "+5.5",
  charts: ["D1", "D9"]
});

console.log(chart.data.divisional_charts.D1.ascendant.sign);
```

### Python (Requests)
```python
import requests

def get_chart(birth_data):
    response = requests.post(
        'https://astroshiva-api.onrender.com/api/chart',
        json=birth_data
    )
    response.raise_for_status()
    return response.json()

# Usage
chart = get_chart({
    "name": "John Doe",
    "dob": "1990-05-15",
    "tob": "14:30:00",
    "place": "Mumbai",
    "latitude": 19.0760,
    "longitude": 72.8777,
    "timezone": "+5.5",
    "charts": ["D1", "D9"]
})

print(chart['data']['divisional_charts']['D1']['ascendant']['sign'])
```

### cURL
```bash
curl -X POST https://astroshiva-api.onrender.com/api/chart \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "dob": "1990-05-15",
    "tob": "14:30:00",
    "place": "Mumbai",
    "latitude": 19.0760,
    "longitude": 72.8777,
    "timezone": "+5.5",
    "charts": ["D1", "D9"]
  }'
```

---

## Best Practices

### 1. Optimize Payload Size
**Always specify which charts you need:**
```json
{
  "charts": ["D1", "D9"]  // Only request what you'll use
}
```

Default (no `charts` parameter) returns all 16 divisional charts, which can be 50KB+.

### 2. Handle Errors Gracefully
```javascript
try {
  const chart = await getChart(data);
} catch (error) {
  console.error('Chart generation failed:', error);
  // Show user-friendly error message
}
```

### 3. Cache Results
Birth charts don't change. Cache them client-side:
```javascript
const cacheKey = `${dob}_${tob}_${latitude}_${longitude}`;
localStorage.setItem(cacheKey, JSON.stringify(chart));
```

### 4. Validate Input
- Ensure latitude is between -90 and 90
- Ensure longitude is between -180 and 180
- Validate date format (YYYY-MM-DD)
- Validate time format (HH:MM:SS)

### 5. Display Loading States
API response time: ~2-5 seconds (depending on server load).

---

## CORS Policy

The API allows requests from **all origins** (`*`).

You can call it from:
- Web browsers (any domain)
- Mobile apps
- Desktop applications
- Server-side applications

---

## Rate Limiting

Currently: **No rate limits**

Fair use policy:
- Don't spam the API
- Don't use for commercial scraping
- For high-volume usage, contact for dedicated instance

---

## Support & Contact

**API Issues:** Check `/health` endpoint first  
**Documentation:** This file  
**Source Code:** Available on request

---

## Version History

### v2.0.0 (Current)
- Added Jaimini Karakas
- Added Planetary Avasthas (Baaladi, Jagradadi)
- Added KP System (Sub-Lord, Sub-Sub-Lord)
- Added Panchadha Maitri
- Added Live Transits
- Upgraded Yoga detection
- Added `charts` parameter for payload optimization
- Cleaned up JSON structure

### v1.1.0
- Basic chart generation
- All 16 divisional charts
- Vimshottari Dasha
- Panchang

---

## License

**Free to use** for personal and commercial projects.  
Attribution appreciated but not required.
