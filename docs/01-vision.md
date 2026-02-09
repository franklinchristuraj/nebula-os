# NebulaOS Vision & Mission

**Status**: Active Development  
**Version**: 1.0  
**Date**: February 2026

## What is NebulaOS?

NebulaOS is a **knowledge graph and exocortex** designed specifically for AI agents. It's a semantic memory system that helps AI assistants maintain context, learn from interactions, and provide more personalized and informed responses over time.

Think of it as a "second brain" that AI agents can query to understand:
- What entities (companies, teams, products, people) matter to you
- What insights and learnings you've captured
- What strategies and frameworks you use
- What events and decisions have happened
- What processes and workflows you follow

## Mission

**Enable AI agents to provide truly personalized, context-aware assistance by giving them access to a structured, searchable memory of what matters to you.**

## The Problem

Current AI assistants are:
- **Stateless**: They forget context between conversations
- **Generic**: They lack personal knowledge about your work, relationships, and preferences
- **Fragmented**: Knowledge is scattered across notes, docs, and chat histories
- **Not semantic**: Traditional search requires exact keywords, missing conceptual connections

## The Solution

NebulaOS provides:
- **Persistent Memory**: AI agents remember entities, insights, strategies, events, and processes
- **Semantic Search**: Find knowledge by meaning, not just keywords (using vector embeddings)
- **Structured Knowledge**: Five core collections with cross-references for rich context
- **Privacy Control**: Self-hosted on your infrastructure, you control the data

## Core Concepts

### 1. Entity-Centric Design
Everything revolves around entities (companies, teams, products, people). This grounds knowledge in concrete, real-world objects.

### 2. Semantic Vectors
Every piece of knowledge is embedded as a 768-dimensional vector (Google Embedding 004), enabling similarity search and conceptual connections.

### 3. Cross-Referenced Graph
Collections reference each other, creating a knowledge graph:
- Insights → relate to Entities and Strategies
- Events → involve Entities, relate to Strategies, generate Insights
- Processes → apply to Entities, support Strategies

### 4. Domain Separation
Knowledge is tagged as `personal`, `work`, or `both`, enabling context-appropriate responses.

## Use Cases

### For a Product Manager
"What insights do we have about KPMG's preferences for workshops?"
→ Query Entity (KPMG) → traverse to related Insights

### For a Consultant
"What frameworks have we used for AI governance projects?"
→ Query Strategy collection → filter by domain=work, strategy_type=framework

### For a Researcher
"Find all insights related to agentic memory systems"
→ Vector search on Insight collection → semantic match on query

### For Anyone
"What decisions did we make in last month's team meetings?"
→ Query Event collection → filter by event_type=meeting, event_date range → retrieve outcomes

## Design Principles

1. **Atomic Knowledge Units**: Each piece of knowledge stands alone and is self-contained
2. **Explicit Relationships**: Cross-references are intentional, not inferred
3. **Temporal Awareness**: Strategies and insights can be superseded, events are timestamped
4. **Source Attribution**: Every insight tracks its origin (article, conversation, reflection)
5. **Confidence Levels**: Not all knowledge is certain; we track confidence (high/medium/low/hypothesis)

## Architecture Philosophy

### Why Weaviate?
- Native vector search (semantic similarity)
- Structured schema with cross-references
- Filters + vector search in single query
- Scalable and production-ready

### Why External Embeddings (Google Embedding 004)?
- Best-in-class quality (768 dimensions)
- Consistent with other Google AI tools
- Task-specific embeddings (retrieval_document vs retrieval_query)
- Control over embedding pipeline

### Why Manual Vector Injection?
- Embeddings created in Make.com pipeline before ingestion
- Weaviate as pure storage + query engine
- Separation of concerns: embedding logic external, graph logic internal

## Roadmap Vision

### Phase 1: Foundation (✅ Complete - Feb 2026)
- [x] Define schema (5 collections)
- [x] Implement in Weaviate
- [x] Validate with test data
- [x] Document architecture

### Phase 2: Data Ingestion (In Progress)
- [ ] Build Make.com pipeline for embedding generation
- [ ] Create HTTP injection endpoints
- [ ] Migrate existing notes/insights
- [ ] Set up automated ingestion from sources (Readwise, bookmarks, meeting notes)

### Phase 3: Agent Integration (Planned)
- [ ] Build query API for AI agents
- [ ] Create semantic search endpoints
- [ ] Implement context retrieval patterns
- [ ] Test with Claude/GPT integration

### Phase 4: Intelligence Layer (Future)
- [ ] Auto-generate insights from events
- [ ] Suggest cross-references
- [ ] Track knowledge evolution (superseded insights)
- [ ] Personalized knowledge recommendations

## Why Build This?

**Created by**: Franklin, Human-AI Interaction Architect

As someone who works daily with AI agents (Claude, GPT, etc.), I experienced the frustration of:
- Re-explaining context in every conversation
- AI forgetting what matters to me
- Losing valuable insights captured in previous chats
- Wanting AI to "know" my work relationships and strategies

NebulaOS is the system I wish existed: **a memory layer that makes AI agents truly helpful, not just capable.**

## Values

1. **Privacy First**: Self-hosted, you control your data
2. **Open Design**: Architecture and schema documented publicly
3. **AI-Native**: Designed for semantic search and agent consumption, not just human browsing
4. **Pragmatic**: Built with production-ready tools (Weaviate, Google Embeddings), not experimental tech
5. **Evolvable**: Schema supports versioning, superseding, and knowledge evolution

---

**Next Steps**: See `docs/02-architecture.md` for technical design details.
