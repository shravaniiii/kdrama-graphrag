# 드라마 Intelligence — K-Drama GraphRAG Engine

A knowledge graph intelligence system for Korean dramas, combining 
Microsoft GraphRAG for multi-hop reasoning with Neo4j for graph 
traversal and recommendation.


---

## What It Does

**Ask** complex questions and get reasoned answers:
- "Which dramas share the enemies-to-lovers trope?"
- "Why did Crash Landing on You resonate globally?"
- "What makes Squid Game different from other survival dramas?"

**Recommend** similar dramas based on shared narrative tropes:
- Input: Goblin → Output: Kiss Goblin, Tale of the Nine-Tailed, 365: Repeat the Year

**Explore** an interactive knowledge graph of any drama's tropes, actors, and genres.

---

## Architecture

```
Data Layer
├── MDL Dataset — 1637 Korean dramas with tags, synopsis, cast
├── Wikipedia API — plot summaries for GraphRAG indexing
└── TMDB API — drama posters and actor photos

Knowledge Graph
├── Microsoft GraphRAG — 130 communities, 8 custom entity types
├── Neo4j AuraDB — 1839 tropes, 1817 actors, 31 genres
└── HuggingFace Hub — graph index storage

Application
├── FastAPI — REST backend
├── Streamlit — three-tab frontend (Ask, Recommend, Explore)
└── PyVis — interactive graph visualization
```

---

## Key Stats

| Metric | Value |
|--------|-------|
| Dramas indexed | 1,637 |
| Unique tropes | 1,839 |
| Actors | 1,817 |
| Graph communities | 130 |
| Entity types | 8 (person, org, geo, event, trope, theme, genre, relationship_type) |

---

## Tech Stack

- **Microsoft GraphRAG 2.2.1** — knowledge graph construction
- **OpenAI GPT-4o-mini** — entity extraction + reasoning
- **Neo4j AuraDB** — graph database for traversal queries
- **PyVis** — interactive graph visualization
- **Streamlit** — frontend
- **FastAPI** — REST API
- **TMDB API** — drama posters and actor images
- **HuggingFace Hub** — graph index storage
- **Python 3.11**

---

## Challenges & Solutions

**Challenge:** GraphRAG default entity types missed K-drama specific concepts.

**Solution:** Added 4 custom entity types (trope, theme, genre, relationship_type). 
Communities grew from 4 → 130.

**Challenge:** MDL scraper returning wrong dramas due to search ambiguity.

**Solution:** Found existing Kaggle dataset with 5000 MDL dramas — better 
data quality, less engineering risk.

**Challenge:** GraphRAG query taking 30-60 seconds per query.

**Solution:** Added @st.cache_data caching (ttl=3600) so repeated 
queries return instantly. First-time queries still take 30-60 seconds 
due to subprocess overhead — loading the full graph into memory on 
each call. 

**Production fix identified:** Replace subprocess with a persistent 
query engine that keeps the graph in memory, reducing latency to 
5-10 seconds. Not yet implemented due to deployment memory constraints 
on free tier hosting.

**Challenge:** Streamlit Cloud incompatible with GraphRAG (Python 3.14 vs <3.13).

**Solution:** Deployed on Render with Python 3.11 via render.yaml. Memory 
constraint (512MB) identified as next blocker for free tier.

---

## Setup

```bash
git clone https://github.com/Shravaniiii/kdrama-graphrag
cd kdrama-graphrag
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Environment variables
cp .env.example .env
# Add: GRAPHRAG_API_KEY, TMDB_API_KEY, HF_TOKEN, NEO4J_URI, NEO4J_PASSWORD

# Run backend
uvicorn src.api:app --reload --port 8000

# Run frontend
streamlit run src/app.py
```

---

## Future Plans

- [ ] Playwright scraper for MyDramaList (currently using Kaggle dataset)
- [ ] Reddit r/kdrama sentiment data via PRAW
- [ ] Persistent GraphRAG query engine (target: 5-10s latency)
- [ ] Meilisearch pre-filter layer
- [ ] AWS EC2 deployment with GitHub Actions weekly re-index
- [ ] Drama comparison feature
- [ ] User feedback mechanism

---

## Status

- [x] Data pipeline (1637 dramas)
- [x] GraphRAG indexing (130 communities)
- [x] Neo4j graph database
- [x] Recommendation engine
- [x] PyVis knowledge graph visualization
- [x] FastAPI backend
- [x] Streamlit frontend with TMDB images
- [ ] Production deployment (needs 1GB+ RAM instance)
