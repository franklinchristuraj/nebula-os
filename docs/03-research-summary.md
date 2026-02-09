# NebulaOS: Agentic Memory Research Summary

**Date**: February 2026  
**Purpose**: Research findings that informed NebulaOS architecture  
**Status**: Reference document

## Research Question

**How should we design a memory system that enables AI agents to provide truly personalized, context-aware assistance?**

## Key Findings

### 1. Semantic Memory vs. Episodic Memory

**Episodic Memory** (traditional chat history):
- Sequential record of conversations
- Temporal but not semantic
- Hard to search conceptually
- Limited to "what was said"

**Semantic Memory** (knowledge graphs):
- Structured, interconnected knowledge
- Searchable by meaning (vector embeddings)
- Represents "what is known"
- NebulaOS approach: **Hybrid** - structured collections with semantic vectors

**Decision**: Use semantic memory (vector embeddings) + structured schema for balance of flexibility and queryability.

---

### 2. Vector Databases for Agentic Memory

**Evaluated Options**:

| Database | Pros | Cons | Decision |
|----------|------|------|----------|
| **Pinecone** | Fast, managed, simple | Proprietary, cost at scale | ❌ |
| **Chroma** | Open source, easy setup | Limited cross-references | ❌ |
| **Weaviate** | Open source, schema + vectors, cross-references | Setup complexity | ✅ **Chosen** |
| **Qdrant** | Fast, Rust-based | Less mature ecosystem | ❌ |
| **Milvus** | Scalable, production-ready | Overkill for personal use | ❌ |

**Why Weaviate?**
- Native vector search + structured schema
- Cross-references between collections (graph capabilities)
- Filters + vector search in single query
- Open source + self-hostable
- Production-ready (used by companies at scale)

---

### 3. Embedding Models for Knowledge Retrieval

**Evaluated Models**:

| Model | Dimensions | Quality | Cost | Decision |
|-------|-----------|---------|------|----------|
| OpenAI text-embedding-3-small | 1536 | High | $0.02/1M tokens | ❌ |
| OpenAI text-embedding-3-large | 3072 | Very High | $0.13/1M tokens | ❌ |
| Cohere embed-english-v3 | 1024 | High | $0.10/1M tokens | ❌ |
| **Google text-embedding-004** | 768 | Very High | Free (Gemini API) | ✅ **Chosen** |

**Why Google Embedding 004?**
- **Quality**: State-of-the-art (MTEB benchmark top-tier)
- **Cost**: Free with Gemini API (generous limits)
- **Task Types**: Supports `retrieval_document` vs `retrieval_query` (optimized embeddings)
- **Ecosystem**: Integrates with Google AI studio, consistent with other tools
- **Dimensions**: 768 (sweet spot - not too sparse, not too large)

---

### 4. Schema Design for Agent Memory

**Research Question**: What are the core "types" of knowledge an AI agent needs?

**Cognitive Science Perspective**:
- **Entities**: Objects, people, places (nouns)
- **Events**: Things that happened (temporal)
- **Concepts**: Abstract ideas, principles (semantic)
- **Procedures**: How-tos, workflows (operational)

**Personal Knowledge Management Perspective** (Zettelkasten, PARA):
- **Projects**: Active work (entities in NebulaOS)
- **Areas**: Ongoing responsibilities (strategies)
- **Resources**: Reference material (insights)
- **Archives**: Historical context (events)

**NebulaOS Synthesis**:
1. **Entity** - Concrete objects (nouns)
2. **Insight** - Knowledge units (learnings, observations)
3. **Strategy** - Goals, frameworks, principles
4. **Event** - Historical timeline (meetings, decisions)
5. **Process** - Operational knowledge (how-tos)

**Decision**: 5 collections provide cognitive clarity without over-fragmentation.

---

### 5. Cross-References vs. Pure Vector Search

**Pure Vector Search** (e.g., Pinecone, Chroma):
- Pros: Flexible, no schema constraints
- Cons: Can't explicitly model "Insight X relates to Entity Y"

**Graph Databases** (e.g., Neo4j):
- Pros: Rich relationships, traversal queries
- Cons: No native vector search

**Hybrid: Weaviate** (vector + graph):
- Schema with typed cross-references
- Vector search within collections
- Graph traversal across collections
- **Example**: "Find insights about KPMG that relate to AI governance strategy"
  - Query: Entity (name="KPMG") → related Insights → filter by related Strategy (vector match "AI governance")

**Decision**: Cross-references essential for agent memory - explicit relationships augment semantic search.

---

### 6. Manual vs. Automatic Vectorization

**Automatic Vectorization** (Weaviate's built-in):
- Pros: Convenient, one-step ingestion
- Cons: Vendor lock-in, less control, API key exposure

**Manual Vectorization** (external pipeline):
- Pros: Full control, model flexibility, debuggable
- Cons: More complex ingestion pipeline

**NebulaOS Decision**:
- **Manual vectorization** in Make.com pipeline
- Embeddings generated before Weaviate ingestion
- Weaviate configured with `vectorizer: none`
- **Rationale**: Separates concerns (embedding logic vs. graph storage), easier to change models

---

### 7. Agent Query Patterns

**Research**: How will AI agents actually query this memory?

**Identified Patterns**:
1. **Semantic Lookup**: "What do I know about X?"
   - Vector search on content
2. **Entity-Centric**: "Tell me about KPMG"
   - Query Entity → traverse to related Insights/Events
3. **Temporal**: "What happened in Q1 2026?"
   - Filter Event by event_date range
4. **Hybrid**: "Work-related insights about prompt engineering"
   - Vector search + filters (domain=work, tags contains "prompt-engineering")
5. **Graph Traversal**: "What strategies apply to NebulaOS?"
   - Query Entity → Strategy.appliesToEntities

**Decision**: Schema must support all 5 patterns efficiently.

---

### 8. Knowledge Evolution & Versioning

**Research Question**: How to handle knowledge that changes over time?

**Approaches Considered**:

1. **Versioning** (v1, v2, v3):
   - ❌ Clutters search results
   - ❌ Requires version filtering in every query

2. **Soft Delete** (mark as deleted):
   - ❌ Still in search results unless filtered
   - ❌ No pointer to "what replaced this"

3. **`superseded_by` + `status`** (chosen):
   - ✅ Filter by `status=active` for current knowledge
   - ✅ `superseded_by` UUID points to newer version
   - ✅ Audit trail preserved (can query historical if needed)
   - ✅ Clean search results (exclude `status=superseded`)

**Decision**: Insight, Strategy, Process collections have `superseded_by` + `status`.

---

### 9. Privacy & Self-Hosting

**Research**: Should this be cloud-hosted or self-hosted?

**Cloud Options** (Pinecone, Weaviate Cloud):
- Pros: No infrastructure management
- Cons: Data leaves your control, ongoing costs, vendor lock-in

**Self-Hosted** (Docker):
- Pros: Full data control, no ongoing costs, privacy
- Cons: Requires setup, maintenance

**NebulaOS Decision**: **Self-hosted Weaviate in Docker**
- Personal knowledge = sensitive data
- Self-hosting aligns with exocortex philosophy (your brain, your control)
- Docker makes it portable (run anywhere)

---

### 10. Agent Integration Layer

**Research**: How should AI agents (Claude, GPT, etc.) access this memory?

**Options**:

1. **Direct Weaviate Queries** (Python/GraphQL):
   - Pros: Full query power
   - Cons: Agents need to know schema, write complex queries

2. **Semantic Search API** (abstraction layer):
   - Pros: Simple interface ("query(text, filters)")
   - Cons: Hides graph traversal power

3. **Hybrid: Query Templates + Direct Access** (chosen):
   - Provide templates for common patterns
   - Allow direct GraphQL for complex queries
   - **Example**: `query_entity_context(name)` → returns Entity + related Insights + Events

**Decision**: Build thin API layer with templates, expose GraphQL for power users.

---

## Research References

### Academic Papers
1. **"MemGPT: Towards LLMs as Operating Systems"** (Park et al., 2023)
   - Insight: LLMs need explicit memory management (like OS paging)
2. **"Generative Agents"** (Park et al., 2023)
   - Insight: Memory stream + reflection for agent coherence
3. **"Retrieval-Augmented Generation"** (Lewis et al., 2020)
   - Insight: External knowledge retrieval improves LLM accuracy

### Industry Implementations
1. **Notion AI**: Workspace-wide semantic search
2. **Mem.ai**: Personal knowledge graph with AI
3. **Rewind**: Local-first, screenshot-based memory
4. **Anthropic's Extended Context**: Up to 1M tokens (but not persistent)

### Personal Knowledge Management
1. **Zettelkasten**: Atomic notes + connections
2. **PARA Method**: Projects, Areas, Resources, Archives
3. **Building a Second Brain** (Tiago Forte): Capture, organize, distill, express

---

## Key Insights Applied to NebulaOS

1. **Structured + Semantic**: Schema for queryability + vectors for semantic search
2. **Entity-Centric**: Ground knowledge in concrete objects
3. **Cross-References**: Explicit relationships augment vector search
4. **Manual Embeddings**: Control + flexibility
5. **Self-Hosted**: Privacy-first design
6. **5 Collections**: Cognitive clarity without fragmentation
7. **Superseding**: Clean knowledge evolution
8. **Domain Separation**: Personal vs. work context
9. **Graph Traversal**: Rich context retrieval
10. **Agent-Native**: Designed for AI consumption, not just human browsing

---

## Open Research Questions

1. **Auto-Insight Generation**: Can agents auto-generate insights from events?
2. **Confidence Decay**: Should confidence degrade over time for hypotheses?
3. **Cross-Domain Insights**: When do personal insights inform work (and vice versa)?
4. **Memory Pruning**: At what scale should we archive/prune old knowledge?
5. **Multi-Agent Memory**: Can multiple agents share/contribute to the same memory?

---

**Next Steps**: See `docs/02-architecture.md` for how these research findings translated into technical design.
