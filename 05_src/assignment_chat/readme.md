# Assignment 2 — Toronto City Tour Assistant

## Overview
This project implements a conversational **City Tour Assistant** focused on Toronto.  
The assistant acts as a *Tour Assistant based in Toronto* and helps users with:

- Weather interpretation and clothing advice
- Attraction recommendations and local tips
- Transit suggestions
- One-day trip planning

The application uses **Gradio** as a chat interface and integrates three required services.

---

## Persona
The assistant’s personality:

> Friendly, practical, and reliable.  
> Prioritizes tools and local knowledge.  
> Avoids fabricating facts.

## File + folder structure
```markdown
05_src/
└── assignment_chat/
    ├── app.py
    ├── readme.md
    ├── __init__.py
    ├── core/
    │   ├── config.py
    │   ├── guardrails.py
    │   ├── llm.py
    │   ├── memory.py
    │   └── router.py
    ├── services/
    │   ├── weather_service.py
    │   ├── semantic_service.py
    │   └── planner_service.py
    ├── data/
    │   └── toronto_travel_tips.csv
    └── db/
        └── (Chroma persistent files will be created here after ingestion)
```

## System Architecture

```markdown
      Gradio UI (app.py)
        │           │
        ▼           ▼
   guardrails.py.   semantic_service.py (Build/Refresh Chroma DB) 
        │             └── build_chroma_from_csv()
        ▼
   router.py decides intent
        │
        ├── weather_service.py (API only)
        │
        ├── semantic_service.py
        │       └── llm.embed()
        │
        └── function calling (plan trip)
                └── llm.chat()
```


Services implemented:

| Service | Purpose |
|---|---|
| Service 1 | Weather API (Open-Meteo) |
| Service 2 | Semantic search using Chroma DB |
| Service 3 | Function calling for itinerary planning |

## Embedding Process

The project uses OpenAI embeddings and a Chroma PersistentClient to enable semantic search over a local Toronto attractions dataset.

The embedding process converts natural language text into numerical vector representations, allowing similarity-based retrieval instead of keyword matching.

### 1. Dataset

File:
```markdown
05_src/assignment_chat/data/toronto_travel_tips.csv
```

Each row represents a Toronto attraction and includes:

| Field | Example | Description
|---|---|---|
| id | TOR_001 | Unique ID
| name | Royal Ontario Museum | Name
| category | museum / park / food / shopping | Category
| indoor | true/false | Whether the place is indoor
| neighborhood | Downtown | Area / neighborhood
| transit | subway / streetcar / bus | Transit tag
| price_level | low / medium / high | Price level
| duration_hours | 2 | Recommended visit duration
| best_for | family, date, solo | Suitable audience
| highlights | dinosaurs, exhibits… | Key highlights
| tips | buy tickets online… | Tips
| text | (Combine the above fields into a natural language paragraph) | Main text used for embeddings

Note:
Use the `text` field for embeddings. The other fields are used for result enrichment (for example: indoor/outdoor, budget, duration in the final answer).

File data example - 10 lines:
```markdown
id,name,category,indoor,neighborhood,transit,price_level,duration_hours,best_for,highlights,tips,text
TOR_001,Royal Ontario Museum,museum,true,Downtown,subway,medium,2,family;solo,"Dinosaurs, world cultures, interactive exhibits","Buy tickets online to skip lines","Royal Ontario Museum is a large indoor museum in Downtown Toronto near subway access. It is medium priced and great for families or solo travelers. Highlights include dinosaur fossils and world culture exhibits. Plan about 2 hours and buy tickets online to skip lines."
TOR_002,Distillery District,shopping,false,Old Toronto,streetcar,low,2,date;friends,"Historic streets, cafes, art galleries","Best visited in afternoon for photos","Distillery District is an outdoor historic pedestrian area in Old Toronto. It is low cost and perfect for couples or friends. Expect art galleries, cafes and cobblestone streets. Best visited in the afternoon."
TOR_003,CN Tower,landmark,true,Downtown,subway,high,1,family;solo,"SkyPod view, glass floor","Book tickets early morning to avoid crowds","CN Tower is an iconic indoor observation tower in Downtown Toronto with subway access. It is high priced but offers amazing skyline views. Expect about 1 hour visit."
TOR_004,Ripley’s Aquarium,attraction,true,Downtown,subway,medium,2,family,"Underwater tunnel, sharks","Arrive early to avoid peak crowds","Ripley’s Aquarium is a family friendly indoor attraction near CN Tower. Medium price and ideal for kids. Plan around 2 hours."
TOR_005,High Park,park,false,West End,subway,low,2,family;solo,"Nature trails, cherry blossoms","Spring cherry blossom season is busiest","High Park is a large outdoor park accessible by subway in the West End. Free to visit and great for walking or picnics."
TOR_006,St Lawrence Market,food,true,Downtown,streetcar,low,1,foodies,"Local food vendors, peameal bacon sandwich","Go before lunch rush","St Lawrence Market is an indoor food market in Downtown Toronto. Low cost and perfect for food lovers. Visit before lunch rush."
TOR_007,Toronto Islands,park,false,Harbourfront,ferry,low,4,family;date,"Beach, skyline view, biking","Take the ferry early morning","Toronto Islands are outdoor islands accessible by ferry. Low cost and ideal for half day trips with biking and beaches."
TOR_008,Aga Khan Museum,museum,true,North York,bus,medium,2,solo;date,"Islamic art, modern architecture","Combine with nearby park visit","Aga Khan Museum is an indoor museum in North York featuring Islamic art and architecture."
TOR_009,Kensington Market,shopping,false,Downtown,streetcar,low,2,friends,"Vintage shops, street art","Best visited daytime","Kensington Market is an outdoor neighborhood famous for vintage shops and street art."
TOR_010,Art Gallery of Ontario,museum,true,Downtown,subway,medium,2,solo;date,"Canadian art, modern art","Free entry certain evenings","Art Gallery of Ontario is a major indoor museum in Downtown Toronto with modern and Canadian art collections."

```

### 2. Embedding Generation

In Gradio UI, Click Button "Build/Refresh Chroma DB", then it call function build_chroma_from_csv() in semantic_service.py.

During database build (`build_chroma_from_csv()`), the following steps occur:

1. Read the CSV file using pandas.
2. Extract the `text` column.
3. Generate embeddings using:
```markdown
llm.embed(batch_docs)
```

The embed() function calls the OpenAI embedding model (via API Gateway).

Batch size: 64 rows per request (prevents oversized requests).

### 3. Vector Storage (Chroma Persistent DB)

Embeddings are stored using:
```markdown
chromadb.PersistentClient(path=CHROMA_DIR)
```
This creates a file-based vector database inside:
```markdown
05_src/assignment_chat/db/
```

For each document, we store:
- id
- embedding vector
- original text
- metadata (category, neighborhood, transit, etc.)

Chroma uses cosine similarity for nearest-neighbor search.

Important:
This implementation uses Chroma persistent storage — NOT SQLite.


## Service 1 — API Calls (Weather)

**API:** Open-Meteo  
https://open-meteo.com/

The assistant:
1. Calls the weather API
2. Converts JSON into natural language summary:
   - Temperature range
   - Rain probability
   - Clothing advice
   - Outdoor activity suggestion

Example output:
```markdown
Toronto weather today: 5°C–11°C, rain probability 30%.
A light jacket is recommended. Consider a small umbrella.
```

## Service 2 — Semantic Search (Chroma + CSV)

Dataset: `toronto_travel_tips.csv` (300 rows)

Contains:
- attractions
- neighborhoods
- transit tags
- tips and highlights

Pipeline:
```markdown
CSV → OpenAI Embeddings → Chroma Persistent DB → Semantic Search → LLM Summary
```

Vector database:
- Chroma **PersistentClient**
- Stored locally in `/db` folder
- No SQLite database used

Users can ask:
- “What attractions are nearby?”
- “Museum recommendations downtown”
- “Transit tips in Toronto”

## Service 3 — Function Calling (Trip Planner)

Function:
```markdown
plan_day_trip(city, budget, preferences)
```

Inputs:
- city
- budget (low / medium / high)
- preferences (museum / food / nature / shopping / family / date / solo)

Output:
- Morning / Afternoon / Evening itinerary
- Transit advice

The function uses ONLY the local semantic search database  
(no web search) to ensure stable and reproducible results.

## Guardrails

Implemented protections:

### Prompt Security
The assistant refuses:
- Prompt reveal attempts
- System prompt modification attempts
- Instruction override attempts

### Restricted Topics (Assignment Requirement)
The assistant will NOT answer questions about:
- Cats or dogs
- Horoscope / Zodiac / Astrology
- Taylor Swift

## Memory

Session memory stores user preferences such as:
- Budget level
- Traveling with kids
- Indoor vs outdoor preference

Memory is session-based and resets when the app restarts.

## How to Run the App

### 1. Set environment variable

This project uses the **course API Gateway**.

Create or update:
```markdown
05_src/.secrets
```
Add:
```markdown
API_GATEWAY_KEY=your_key_here
```

### 2. Install dependencies

Recommended:
```markdown
pip install gradio chromadb pandas requests python-dotenv openai
```

### 3. Run the app

From repository root:
```markdown
python 05_src/assignment_chat/app.py
```

### 4. Build the vector database (first run only)

Click:
```markdown
Build/Refresh Chroma DB
```

This ingests the CSV and creates embeddings in `/db`.

### 5. Try example prompts

Weather:
- “What should I wear today?”
- "5 days Weather forecast"
- "Is it cold today in Toronto?"

Semantic search:
- “What attractions are nearby?”
- “Museum recommendations downtown Toronto”

Trip planner:
- “Plan a day trip in Toronto, budget low, preferences museum and food”

## Notes

- The repository includes the **code to generate embeddings**.
- Running ingestion is optional but supported via UI button.
- The `/db` folder is created automatically by Chroma.
- The system uses the course OpenAI API gateway endpoint.
- For this assignment, we keep it simple and stable: Toronto only for weather service. If city != Toronto, we still use Toronto coordinates as a fallback.


# End of Assignment