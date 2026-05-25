# K-Drama GraphRAG Intelligence Engine

A GraphRAG-powered system that builds a knowledge graph from 100 top K-dramas and enables multi-hop reasoning queries — answering complex questions about actors, tropes, cultural impact, and global reach.

## What it does

Unlike traditional search, this system connects entities across dramas to answer questions like:
- "Which K-dramas became global hits and why?"
- "Which actors built careers through specific role types?"
- "Which dramas share the enemies-to-lovers trope with strong female leads?"

## Architecture
Data Pipeline          → Kaggle CSV + Wikipedia API → 100 drama documents
Graph Construction     → Microsoft GraphRAG + GPT-4o-mini → Knowledge graph
Embeddings             → text-embedding-3-small → Vector store (LanceDB)
Query Engine           → Global search (whole graph) + Local search (entities)


## Tech Stack

- Microsoft GraphRAG 2.2.1
- OpenAI GPT-4o-mini (entity extraction + reasoning)
- OpenAI text-embedding-3-small (embeddings)
- Python 3.11

## Setup

```bash
# Clone and install
git clone https://github.com/shravaniiii/kdrama-graphrag
cd kdrama-graphrag
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Add your OpenAI key
echo "GRAPHRAG_API_KEY=your-key" > graphrag_input/.env

# Fetch drama data
python src/fetch_summaries.py

# Build knowledge graph
graphrag index --root ./graphrag_input
```

## Query Examples

```bash
# Global reasoning (whole graph)
graphrag query --root ./graphrag_input --method global \
  --query "Which K-dramas became global hits and why?"

# Local reasoning (specific entities)
graphrag query --root ./graphrag_input --method local \
  --query "Tell me about Park Seo Joon's career trajectory"
```

## Data Sources

- Top 100 K-dramas dataset (Kaggle)
- Plot summaries via Wikipedia REST API

## Status

## Status
- [x] Data pipeline
- [x] GraphRAG indexing  
- [x] Query engine
- [x] FastAPI backend
- [x] Streamlit frontend with TMDB images
- [ ] Cloud deployment (in progress)