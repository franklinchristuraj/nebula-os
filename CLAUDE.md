# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

NebulaOS is a semantic memory system and knowledge graph for AI agents. It provides persistent, context-aware knowledge using Weaviate (vector database) with built-in text2vec-transformers for automatic embedding generation (384 dimensions, sentence-transformers/all-MiniLM-L6-v2). Self-hosted, privacy-first architecture with local embedding inference.

**Current status**: Phase 1 (Foundation/Schema) complete with auto-vectorization. Phase 2 (Data Ingestion via Make.com pipelines) in progress.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Environment setup
cp .env.example .env  # then fill in WEAVIATE_API_KEY

# Start Weaviate with text2vec-transformers (Docker)
# See weaviate/setup_vectorizer.sh for complete setup
# Or use the docker-compose files:
docker-compose -f weaviate/docker-compose-vectorizer.yml up -d

# Create schema with auto-vectorization (run once after Weaviate is up)
python weaviate/create_schema.py

# Run validation tests
python weaviate/test_schema.py

# Test auto-vectorization
python weaviate/example_auto_vectorization.py
```

No linter or formatter is configured.

## Architecture

### Data Flow

```
Data Sources → Make.com Pipeline → Weaviate DB (Docker + text2vec-transformers) → AI Agents (semantic search)
```

Vectors are generated automatically by Weaviate's built-in text2vec-transformers module using the sentence-transformers/all-MiniLM-L6-v2 model. The transformers inference service runs locally in Docker, keeping all data on-premise. No external API calls required for embeddings.

### Five Collections (Knowledge Graph)

| Collection | Purpose | References |
|------------|---------|------------|
| **Entity** | Foundation layer — concrete nouns (companies, people, projects) | None (referenced by all others) |
| **Strategy** | Goals, frameworks, principles | → Entity, → Strategy (self-ref) |
| **Insight** | Atomic knowledge units — learnings, observations | → Entity, → Strategy, → Insight (self-ref) |
| **Event** | Timeline — meetings, decisions, milestones | → Entity, → Strategy, → Insight |
| **Process** | Operational — procedures, workflows | → Entity, → Strategy |

Entity is the grounding layer; all other collections reference it. Cross-references enable graph traversal queries alongside vector similarity search.

### Key Patterns

- **Domain separation**: Every object tagged `personal`, `work`, or `both` for privacy-aware filtering
- **Superseding pattern**: Objects use `status` (active/superseded/archived) + `superseded_by` UUID instead of versioning — keeps search clean while preserving audit trail
- **Automatic vectorization**: Weaviate generates embeddings on insert using text2vec-transformers - no manual vector management needed
- **Selective vectorization**: Properties marked with `skip_vectorization=True` (metadata, dates, types) are excluded from embedding generation
- **Hybrid search**: Combines vector similarity (cosine/HNSW) with property filters in single queries using `near_text()`

### Weaviate Connection

Connects to local Docker instance: HTTP on port 8081, gRPC on port 50051, authenticated via API key. Connection helper pattern is in `scripts/quick_reference.py`.

## Code Layout

- `weaviate/create_schema.py` — Schema creation for all 5 collections with auto-vectorization (run once)
- `weaviate/test_schema.py` — Comprehensive validation: CRUD, vector search, cross-references, filtering
- `weaviate/example_auto_vectorization.py` — Usage examples with automatic embedding generation
- `weaviate/docker-compose-vectorizer.yml` — Transformers inference service configuration
- `weaviate/setup_vectorizer.sh` — Automated setup script for vectorizer infrastructure
- `scripts/quick_reference.py` — Common Weaviate operations (CRUD, search, stats)
- `scripts/example_usage.py` — End-to-end usage examples (create, search, filter, multi-collection queries)
- `scripts/embedding_helpers.py` — (Deprecated) Legacy manual embedding helpers for Google Embedding 004
- `pipelines/` — Placeholder for Make.com pipeline configs (Phase 2)
- `docs/` — Numbered documentation: vision → architecture → research → implementation → changelog
