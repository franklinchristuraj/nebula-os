# NebulaOS

> **A semantic memory system for AI agents** - An exocortex that enables truly personalized, context-aware AI assistance through structured knowledge graphs and vector search.

[![Status](https://img.shields.io/badge/Status-Active%20Development-blue)]()
[![License](https://img.shields.io/badge/License-MIT-green)]()
[![Weaviate](https://img.shields.io/badge/Weaviate-v1.34+-orange)]()
[![Python](https://img.shields.io/badge/Python-3.9+-blue)]()

---

## 📋 Table of Contents

- [What is NebulaOS?](#what-is-nebulaos)
- [Status](#status)
- [Architecture](#architecture)
- [Collections](#collections)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [Documentation](#documentation)
- [Roadmap](#roadmap)
- [Why Build This?](#why-build-this)

---

## What is NebulaOS?

NebulaOS is a **knowledge graph and exocortex** designed specifically for AI agents. It's a self-hosted semantic memory system that helps AI assistants:

- 🧠 **Remember** entities (companies, teams, products, people) that matter to you
- 💡 **Recall** insights and learnings from conversations, articles, and experiences
- 🎯 **Understand** your strategies, goals, and frameworks
- 📅 **Track** events, decisions, and milestones over time
- 🔧 **Reference** processes and workflows you follow

Instead of generic, stateless responses, NebulaOS enables AI agents to provide **personalized, context-aware assistance** grounded in your knowledge base.

### The Problem

Current AI assistants are:
- **Stateless**: They forget context between conversations
- **Generic**: They lack personal knowledge about your work, relationships, and preferences
- **Fragmented**: Knowledge is scattered across notes, docs, and chat histories
- **Keyword-based**: Traditional search misses conceptual connections

### The Solution

NebulaOS provides:
- **Persistent Memory**: Structured knowledge that survives across conversations
- **Semantic Search**: Find knowledge by meaning using 768-dimensional vector embeddings (Google Embedding 004)
- **Knowledge Graph**: Five core collections with cross-references for rich context
- **Privacy-First**: Self-hosted on your infrastructure, you control the data

---

## Status

| Component | Status | Details |
|-----------|--------|---------|
| **Schema Design** | ✅ Complete | 5 collections defined, cross-references mapped |
| **Weaviate Implementation** | ✅ Complete | All collections created and validated |
| **Test Suite** | ✅ Passing | CRUD, vector search, cross-references, filters |
| **Documentation** | ✅ Complete | Vision, architecture, research, implementation |
| **Embedding Pipeline** | 🔄 In Progress | Make.com pipeline for Google Embedding 004 |
| **Data Migration** | 📋 Planned | Migrate existing notes and insights |
| **Agent Integration** | 📋 Planned | Query API for Claude/GPT |

**Current Version**: 1.0  
**Last Updated**: February 9, 2026  
**Production Ready**: ✅ Schema and infrastructure validated

---

## Architecture

### System Overview

```
┌──────────────────┐
│  Data Sources    │  Readwise, bookmarks, meeting notes, manual input
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  Make.com        │  • Generate 768-dim vectors (Google Embedding 004)
│  Pipeline        │  • Format for Weaviate schema
└────────┬─────────┘  • HTTP POST to Weaviate
         │
         ▼
┌──────────────────┐
│  Weaviate DB     │  • 5 collections with cross-references
│  (Docker)        │  • HNSW index for vector similarity
└────────┬─────────┘  • Property filtering + semantic search
         │
         ▼
┌──────────────────┐
│  AI Agents       │  • Semantic search queries
│  (Claude, GPT)   │  • Context retrieval for conversations
└──────────────────┘
```

### Technology Stack

- **Vector Database**: [Weaviate](https://weaviate.io/) (self-hosted, Docker)
- **Embeddings**: Google text-embedding-004 (768 dimensions)
- **Indexing**: HNSW (Hierarchical Navigable Small World)
- **Distance Metric**: Cosine similarity
- **Client**: Python 3.9+ with `weaviate-client>=4.0.0`

---

## Collections

NebulaOS uses **five core collections** to organize knowledge:

### 1. Entity (Foundation)
**Organizations, teams, products, projects, and people**

```
Properties: name, entity_type, domain, description, notes, status, timestamps
References: None (foundation for other collections)
Use Case: "Tell me about KPMG"
```

### 2. Insight (Knowledge Units)
**Atomic learnings, observations, ideas, patterns, mental models**

```
Properties: content, source_name, source_type, domain, tags, status, confidence, timestamps
References: → Entity, → Strategy, → Insight (self)
Use Case: "What have I learned about prompt engineering?"
```

### 3. Strategy (Goals & Frameworks)
**Goals, frameworks, principles, methodologies**

```
Properties: title, content, strategy_type, domain, time_horizon, validity dates, status, timestamps
References: → Entity, → Strategy (self)
Use Case: "Show frameworks for AI governance"
```

### 4. Event (Historical Timeline)
**Meetings, decisions, milestones, announcements**

```
Properties: title, event_type, summary, participants, domain, event_date, outcomes, action_items, timestamps
References: → Entity, → Strategy, → Insight
Use Case: "What decisions did we make in Q1 2026?"
```

### 5. Process (Operational Knowledge)
**Procedures, workflows, how-tos**

```
Properties: title, content, domain, triggers, status, timestamps
References: → Entity, → Strategy
Use Case: "How do I prepare for client workshops?"
```

### Cross-Reference Graph

```
                    ┌─────────┐
                    │ Entity  │ (foundation)
                    └────┬────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
    ┌────▼─────┐   ┌────▼────┐    ┌────▼────┐
    │ Strategy │◄──┤ Insight │    │ Process │
    └────┬─────┘   └────┬────┘    └────┬────┘
         │              │              │
         │         ┌────▼────┐         │
         └────────►│  Event  │◄────────┘
                   └─────────┘
```

---

## Quick Start

### Prerequisites

- Docker (for Weaviate)
- Python 3.9+
- Google AI API key (for embeddings)

### 1. Clone Repository

```bash
git clone https://github.com/franklinchristuraj/nebula-os.git
cd nebula-os
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Up Environment

```bash
cp .env.example .env
# Edit .env with your API keys:
# - WEAVIATE_API_KEY
# - GOOGLE_API_KEY
```

### 4. Start Weaviate (Docker)

```bash
docker run -d \
  --name weaviate-secure \
  -p 8081:8080 \
  -p 50051:50051 \
  -e AUTHENTICATION_APIKEY_ENABLED=true \
  -e AUTHENTICATION_APIKEY_ALLOWED_KEYS=your-api-key-here \
  -e AUTHENTICATION_APIKEY_USERS=admin \
  -e PERSISTENCE_DATA_PATH=/var/lib/weaviate \
  -v weaviate_data:/var/lib/weaviate \
  cr.weaviate.io/semitechnologies/weaviate:1.34.4
```

### 5. Create Collections

```bash
python weaviate/create_schema.py
```

Expected output:
```
✅ Created Entity collection
✅ Created Strategy collection
✅ Created Insight collection
✅ Created Event collection
✅ Created Process collection
```

### 6. Validate Installation

```bash
python weaviate/test_schema.py
```

Expected output:
```
✅ All Tests Passed!
  • All 5 collections exist with correct schema
  • Cross-references working correctly
  • Vector search operational (768 dimensions)
```

---

## Project Structure

```
nebula-os/
├── README.md                        # This file
├── LICENSE                          # MIT license
├── requirements.txt                 # Python dependencies
├── .env.example                     # Environment template (no secrets)
├── .gitignore                       # Git ignore rules
│
├── docs/
│   ├── 01-vision.md                 # Vision, mission, purpose, use cases
│   ├── 02-architecture.md           # Schema design, decisions, query patterns
│   ├── 03-research-summary.md       # Agentic memory research findings
│   ├── 04-implementation-summary.md # Technical setup, validation results
│   └── 05-changelog.md              # Running log of progress and learnings
│
├── weaviate/
│   ├── schema/                      # Future: exportable schema JSON
│   ├── create_schema.py             # Collection creation script
│   └── test_schema.py               # Validation tests
│
├── pipelines/                       # Future: Make.com configs/exports
│   └── .gitkeep
│
└── scripts/
    ├── quick_reference.py           # Utility functions and examples
    ├── embedding_helpers.py         # Embedding generation helpers
    └── example_usage.py             # Usage examples and patterns
```

---

## Documentation

Numbered docs guide you chronologically through the thinking:

1. **[Vision & Mission](docs/01-vision.md)** - What is NebulaOS? Why build it? Use cases.
2. **[Architecture](docs/02-architecture.md)** - Schema design, vector configuration, query patterns.
3. **[Research Summary](docs/03-research-summary.md)** - Findings that informed design decisions.
4. **[Implementation Summary](docs/04-implementation-summary.md)** - Technical setup, validation results.
5. **[Changelog](docs/05-changelog.md)** - Running log of progress and learnings.

---

## Roadmap

### ✅ Phase 1: Foundation (Complete - Feb 2026)
- [x] Define schema (5 collections)
- [x] Implement in Weaviate
- [x] Validate with test data
- [x] Document architecture

### 🔄 Phase 2: Data Ingestion (In Progress)
- [ ] Build Make.com pipeline for embedding generation
- [ ] Create HTTP injection endpoints
- [ ] Migrate existing notes/insights
- [ ] Set up automated ingestion from sources (Readwise, bookmarks, meeting notes)

### 📋 Phase 3: Agent Integration (Planned)
- [ ] Build query API for AI agents
- [ ] Create semantic search endpoints
- [ ] Implement context retrieval patterns
- [ ] Test with Claude/GPT integration

### 🔮 Phase 4: Intelligence Layer (Future)
- [ ] Auto-generate insights from events
- [ ] Suggest cross-references
- [ ] Track knowledge evolution (superseded insights)
- [ ] Personalized knowledge recommendations

---

## Why Build This?

**Created by**: Franklin, Human-AI Interaction Architect

As someone who works daily with AI agents (Claude, GPT, etc.), I experienced the frustration of:
- Re-explaining context in every conversation
- AI forgetting what matters to me
- Losing valuable insights captured in previous chats
- Wanting AI to "know" my work relationships and strategies

NebulaOS is the system I wish existed: **a memory layer that makes AI agents truly helpful, not just capable.**

### Design Values

1. **Privacy First**: Self-hosted, you control your data
2. **Open Design**: Architecture and schema documented publicly
3. **AI-Native**: Designed for semantic search and agent consumption, not just human browsing
4. **Pragmatic**: Built with production-ready tools (Weaviate, Google Embeddings), not experimental tech
5. **Evolvable**: Schema supports versioning, superseding, and knowledge evolution

---

## Query Examples

### Semantic Search
```python
from scripts.embedding_helpers import generate_query_embedding

query = "How to make AI agents more reliable?"
query_vector = generate_query_embedding(query)

insight_collection = client.collections.get("Insight")
response = insight_collection.query.near_vector(
    near_vector=query_vector,
    limit=5
)
```

### Property Filtering
```python
from weaviate.classes.query import Filter

entity_collection = client.collections.get("Entity")
response = entity_collection.query.fetch_objects(
    filters=(
        Filter.by_property("domain").equal("work") &
        Filter.by_property("status").equal("active")
    )
)
```

### Graph Traversal
```python
# Find all events involving KPMG
entity_collection = client.collections.get("Entity")
kpmg = entity_collection.query.fetch_objects(
    filters=Filter.by_property("name").equal("KPMG")
)

event_collection = client.collections.get("Event")
events = event_collection.query.fetch_objects(
    filters=Filter.by_property("involvesEntities").contains_any([kpmg.uuid])
)
```

See `scripts/example_usage.py` for more comprehensive examples.

---

## Contributing

This is currently a personal project, but feedback and suggestions are welcome! Feel free to:
- Open issues for bugs or feature requests
- Share how you've used or adapted the schema
- Propose improvements to the architecture

---

## License

MIT License - See [LICENSE](LICENSE) for details.

---

## Contact

**Franklin** - Human-AI Interaction Architect  
Building tools that make AI agents truly helpful.

---

**Status**: ✅ Schema implemented and validated, ready for data ingestion phase  
**Last Updated**: February 9, 2026  
**Version**: 1.0
