# NebulaOS Architecture & Design

**Version**: 1.0  
**Date**: February 2026  
**Status**: Implemented and Validated

## System Architecture

### High-Level Overview

```
┌─────────────────┐
│   Data Sources  │ (Readwise, bookmarks, meeting notes, manual input)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Make.com       │ (Embedding generation, data transformation)
│  Pipeline       │ • Generate 768-dim vectors (Google Embedding 004)
└────────┬────────┘ • Format for Weaviate schema
         │          • HTTP POST to Weaviate
         ▼
┌─────────────────┐
│   Weaviate DB   │ (Knowledge graph storage + vector search)
│  (Docker)       │ • 5 collections with cross-references
└────────┬────────┘ • HNSW index for vector similarity
         │          • Property filtering + semantic search
         ▼
┌─────────────────┐
│  AI Agents      │ (Claude, GPT, custom agents)
│  (Query Layer)  │ • Semantic search queries
└─────────────────┘ • Context retrieval for conversations
```

## Collections Design

### 1. Entity (Foundation)

**Purpose**: The "nouns" of your knowledge base - concrete objects that other knowledge references.

**Properties**:
- `name` (TEXT) - Display name (e.g., "KPMG", "NebulaOS")
- `entity_type` (TEXT) - Type: company | team | product | project | conference | community | person
- `domain` (TEXT) - Context: personal | work | both
- `description` (TEXT) - What it is, why it matters
- `notes` (TEXT) - Running observations, preferences, history
- `status` (TEXT) - Lifecycle: active | inactive | archived
- `created_at`, `updated_at` (DATE) - Timestamps

**References**: None (foundation layer)

**Use Cases**:
- "Tell me about KPMG" → Query Entity by name
- "What personal projects am I tracking?" → Filter by entity_type=project, domain=personal
- Context for insights: "This insight relates to [Entity]"

### 2. Insight (Knowledge Units)

**Purpose**: Atomic learnings, observations, ideas, patterns, mental models.

**Properties**:
- `content` (TEXT) - The insight itself, self-contained
- `source_name` (TEXT) - Origin (article title, book, conversation)
- `source_type` (TEXT) - Type: article | video | book | podcast | conversation | reflection | research
- `domain` (TEXT) - personal | work | both
- `tags` (TEXT_ARRAY) - Flexible categorization (e.g., ["ai-agents", "prompt-engineering"])
- `status` (TEXT) - active | superseded | archived
- `superseded_by` (UUID) - Link to newer insight that replaces this
- `confidence` (TEXT) - high | medium | low | hypothesis
- `created_at`, `updated_at` (DATE)

**References**:
- `relatedEntities` → Entity (what/who this relates to)
- `relatedStrategies` → Strategy (what strategy this supports)
- `relatedInsights` → Insight (self-reference for connected insights)

**Use Cases**:
- "What have I learned about prompt engineering?" → Vector search on content
- "Show insights from Anthropic research" → Filter by source_name
- "Find high-confidence insights about AI agents" → Filter by tags + confidence

### 3. Strategy (Goals & Frameworks)

**Purpose**: Goals, frameworks, principles, methodologies, mental models for decision-making.

**Properties**:
- `title` (TEXT) - Strategy name
- `content` (TEXT) - Full description
- `strategy_type` (TEXT) - goal | framework | principle | methodology | guideline
- `domain` (TEXT) - personal | work | both
- `time_horizon` (TEXT) - immediate | short-term | long-term | ongoing
- `valid_from`, `valid_until` (DATE) - Temporal validity
- `status` (TEXT) - active | superseded | archived
- `superseded_by` (UUID) - Link to updated strategy
- `created_at`, `updated_at` (DATE)

**References**:
- `appliesToEntities` → Entity (which entities follow this strategy)
- `relatedStrategies` → Strategy (parent/child or related strategies)

**Use Cases**:
- "What's my current content strategy?" → Query by title, filter status=active
- "Show frameworks for AI governance" → Filter by strategy_type=framework, domain=work
- "What strategies apply to NebulaOS?" → Query Entity → traverse to related Strategies

### 4. Event (Historical Timeline)

**Purpose**: Meetings, decisions, milestones, announcements - timestamped events that generate knowledge.

**Properties**:
- `title` (TEXT) - Event name
- `event_type` (TEXT) - meeting | decision | milestone | announcement | release
- `summary` (TEXT) - What happened
- `participants` (TEXT_ARRAY) - Who was involved
- `domain` (TEXT) - personal | work | both
- `event_date` (DATE) - When it occurred
- `outcomes` (TEXT) - Results, deliverables
- `action_items` (TEXT) - Next steps
- `open_questions` (TEXT) - Unresolved items
- `created_at` (DATE)

**References**:
- `involvesEntities` → Entity (who/what was involved)
- `relatesToStrategies` → Strategy (which strategies were discussed)
- `generatedInsights` → Insight (insights that came from this event)

**Use Cases**:
- "What decisions did we make about AI strategy?" → Filter by event_type=decision, vector search on summary
- "Show Q1 team meetings" → Filter by event_type=meeting, event_date range
- "What insights came from the KPMG workshop?" → Query Event → traverse to generatedInsights

### 5. Process (Operational Knowledge)

**Purpose**: Procedures, workflows, how-tos, operational playbooks.

**Properties**:
- `title` (TEXT) - Process name
- `content` (TEXT) - Step-by-step description
- `domain` (TEXT) - personal | work | both
- `triggers` (TEXT) - When/why to use this process
- `status` (TEXT) - active | superseded | archived
- `superseded_by` (UUID) - Link to updated process
- `created_at`, `updated_at` (DATE)

**References**:
- `appliesToEntities` → Entity (which teams/products use this)
- `relatedStrategies` → Strategy (which strategies this process supports)

**Use Cases**:
- "How do I prepare for client workshops?" → Vector search on content
- "Show active processes for NebulaOS" → Filter by domain, traverse from Entity
- "What's the updated version of this workflow?" → Query superseded_by

## Cross-Reference Graph

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

**Key Design Decisions**:
1. **Entity as Foundation**: No references to other collections, only referenced by others
2. **Insight as Connector**: Most cross-referenced (to Entity, Strategy, and self)
3. **Event as Integrator**: References all other collections (captures full context)
4. **Strategy as Structure**: Self-referencing for hierarchical goals/frameworks
5. **Process as Operational**: Connects execution (Process) to intent (Strategy)

## Vector Search Configuration

### Embedding Model
- **Model**: Google text-embedding-004
- **Dimensions**: 768
- **Task Types**:
  - `retrieval_document` for storing objects
  - `retrieval_query` for search queries
- **Why**: Best-in-class quality, consistent with Google AI ecosystem

### Weaviate Configuration
- **Vectorizer**: None (manual injection)
- **Index Type**: HNSW (Hierarchical Navigable Small World)
- **Distance Metric**: Cosine similarity
- **Why Manual Vectorization**:
  - Embeddings generated in Make.com before ingestion
  - Weaviate as pure storage + query engine
  - Flexibility to change embedding models without schema changes

### Query Patterns

**1. Pure Semantic Search**
```
Query: "How to make AI agents more reliable?"
→ Generate query vector (768-dim, retrieval_query task)
→ Search Insight collection with near_vector
→ Return top 5 by cosine similarity
```

**2. Hybrid Search (Filters + Vectors)**
```
Query: "Work-related insights about prompt engineering"
→ Generate query vector
→ Search Insight with:
  - near_vector (semantic match)
  - filters: domain="work", tags contains "prompt-engineering"
→ Return filtered + ranked results
```

**3. Graph Traversal**
```
Query: "What strategies apply to KPMG?"
→ Query Entity by name="KPMG"
→ Traverse references: Strategy.appliesToEntities → this Entity
→ Return all connected Strategies
```

**4. Complex Multi-Collection Query**
```
Query: "Find events involving KPMG that generated insights about AI governance"
→ Query Event:
  - involvesEntities → Entity (name="KPMG")
  - generatedInsights → Insight (vector match on "AI governance")
→ Return Events with traversed Insights
```

## Data Flow

### Ingestion Pipeline

```
1. Source Data
   ↓
2. Make.com Scenario:
   a. Parse/extract content
   b. Determine collection + properties
   c. Generate embedding:
      - POST to Google AI API
      - Task: "retrieval_document"
      - Return 768-dim vector
   ↓
3. HTTP POST to Weaviate:
   - Endpoint: http://localhost:8081/v1/objects
   - Headers: X-Api-Key, Content-Type
   - Body: {class, properties, vector, references}
   ↓
4. Weaviate:
   - Validate schema
   - Store object + vector
   - Build HNSW index
   - Update cross-references
```

### Query Pipeline

```
1. AI Agent Query (natural language)
   ↓
2. Query Generation:
   a. Determine collection(s) to search
   b. Extract filters (domain, type, dates)
   c. Generate query vector (task: "retrieval_query")
   ↓
3. Weaviate Query:
   - GraphQL or Python client
   - Combine filters + vector search
   - Traverse references if needed
   ↓
4. Results:
   - Objects with properties
   - Similarity scores (distance/certainty)
   - Referenced objects (if requested)
   ↓
5. AI Agent:
   - Synthesize results
   - Generate response with context
```

## Schema Decisions & Rationale

### Why 5 Collections (Not More/Fewer)?

**Too Few** (e.g., single "Knowledge" collection):
- Loss of structure and queryability
- Unclear relationships
- Difficult to filter by type

**Too Many** (e.g., separate for companies, teams, products):
- Fragmentation
- Complex cross-referencing
- Harder to query "all entities"

**5 Collections** (Entity, Insight, Strategy, Event, Process):
- Natural cognitive categories
- Clear separation of concerns
- Balanced queryability + structure

### Why Manual Vectorization?

**Alternatives Considered**:
1. **Weaviate's built-in vectorizers** (text2vec-transformers, cohere, openai)
   - ❌ Less control over embedding model
   - ❌ Harder to switch models
   - ❌ Vendor lock-in

2. **Auto-vectorization in Weaviate**
   - ❌ Requires exposing API keys to Weaviate
   - ❌ Less visibility into embedding process
   - ❌ Harder to debug

3. **Manual vectorization** (chosen)
   - ✅ Full control over embedding model
   - ✅ Can use Google Embedding 004 (best quality)
   - ✅ Embeddings generated in Make.com pipeline (visible, debuggable)
   - ✅ Easy to change models without schema migration

### Why Cross-References (Not Just Vector Search)?

**Vector search alone**:
- ❌ Can't explicitly filter "insights about KPMG"
- ❌ Semantic similarity may miss exact relationships
- ❌ No way to traverse "all events involving this entity"

**Cross-references + vector search**:
- ✅ Explicit relationships (Entity → Insights)
- ✅ Efficient filtering ("only active strategies")
- ✅ Graph traversal (Event → Entity → related Strategies)
- ✅ Hybrid queries (semantic match + relationship filter)

### Why `superseded_by` Instead of Versioning?

**Versioning** (e.g., v1, v2, v3):
- ❌ Clutters search results with old versions
- ❌ Requires version filtering in every query
- ❌ Unclear which is "current"

**`superseded_by` + `status`**:
- ✅ Single query for "active" knowledge
- ✅ Clear pointer to "what replaced this"
- ✅ Audit trail (can traverse history)
- ✅ Archived insights still searchable if needed

## Performance Considerations

### Expected Scale (Year 1)
- Entities: ~500 (companies, teams, products, people)
- Insights: ~5,000 (daily capture, 15/day average)
- Strategies: ~100 (stable, infrequently updated)
- Events: ~1,000 (meetings, milestones)
- Processes: ~50 (operational playbooks)

**Total**: ~6,650 objects with 768-dim vectors

### Performance Benchmarks (Local Docker)
- Object insertion: ~10-20ms per object with vector
- Property query: <50ms
- Vector search (top 5): <100ms
- Cross-reference query: <150ms
- Complex hybrid query: <200ms

**Bottlenecks**:
- Vector indexing (HNSW rebuild on batch inserts)
- Cross-reference traversal depth (limit to 2-3 hops)

**Optimizations**:
- Batch inserts for initial migration
- Lazy loading of references (only fetch when needed)
- Filter first, then vector search (reduce search space)

## Security & Privacy

### Data Control
- **Self-hosted**: Weaviate runs in Docker on your infrastructure
- **No external calls**: Vectors generated externally, Weaviate only stores/queries
- **API key protection**: Weaviate requires authentication

### Sensitive Data
- **No PII in vectors**: Embeddings are semantic representations, not raw text
- **Domain separation**: Personal vs work knowledge isolated via filters
- **Audit trail**: `created_at`, `updated_at` on all objects

## Next Steps

See `docs/04-implementation-summary.md` for technical implementation details and validation results.
