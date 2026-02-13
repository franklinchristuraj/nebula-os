# Migration to Auto-Vectorization - Summary

## Overview

NebulaOS has been migrated from manual embedding generation (using Google Gemini embedding-004) to Weaviate's built-in text2vec-transformers for automatic vectorization.

## What Changed

### Architecture
- **Before**: External API calls to Google for 768-dimensional embeddings
- **After**: Local text2vec-transformers service generating 384-dimensional embeddings
- **Model**: sentence-transformers/all-MiniLM-L6-v2 (fast, lightweight, local)

### Data Flow
```
BEFORE: Data → Make.com → Google API (embed) → Weaviate → AI Agents
AFTER:  Data → Make.com → Weaviate (auto-embed) → AI Agents
```

### Benefits
✅ **Privacy**: All data stays local, no external API calls
✅ **Cost**: No API usage costs for embeddings
✅ **Simplicity**: No manual vector management
✅ **Speed**: Local inference, no network latency
✅ **Reliability**: No dependency on external services

## Files Updated

### Core Schema
- ✅ `weaviate/create_schema.py` - Updated to use text2vec-transformers
  - Added `vectorizer_config` to all collections
  - Added `skip_vectorization` flags to properties
  - Removed manual vector insertion from tests
  - Updated to use `near_text()` instead of `near_vector()`

### Configuration
- ✅ `CLAUDE.md` - Updated project overview and architecture docs
- ✅ `.env.example` - Marked Google API key as optional
- ✅ `requirements.txt` - Marked google-generativeai as optional

### Documentation
- ✅ `weaviate/QUICK_REFERENCE.md` - Updated to reference new schema
- ✅ `weaviate/README_VECTORIZER.md` - Detailed vectorizer setup guide (already existed)

### Deprecated Files (Kept for Reference)
- ⚠️ `scripts/embedding_helpers.py` - Manual embedding generation (no longer needed)
- ⚠️ `scripts/quick_reference.py` - Examples with manual vectors
- ⚠️ `scripts/example_usage.py` - Examples with manual vectors
- ⚠️ `weaviate/create_schema_with_vectorizer.py` - Duplicate of updated create_schema.py

## New Files (Already Created)
- ✅ `weaviate/docker-compose-vectorizer.yml` - Transformers service
- ✅ `weaviate/setup_vectorizer.sh` - Automated setup script
- ✅ `weaviate/example_auto_vectorization.py` - Usage examples

## Key Code Changes

### BEFORE: Manual Vectorization
```python
from embedding_helpers import prepare_insight_vector

# Generate vector manually
vector = prepare_insight_vector(content, source_name)

# Must provide vector on insert
insight_collection.data.insert(
    properties={
        "content": content,
        ...
    },
    vector=vector  # Required!
)

# Search with manual query embedding
query_vector = generate_query_embedding("search term")
results = collection.query.near_vector(
    near_vector=query_vector,
    limit=10
)
```

### AFTER: Auto-Vectorization
```python
# No imports needed for vectors!

# Just insert data - vector auto-generated
insight_collection.data.insert(
    properties={
        "content": content,
        ...
    }
    # No vector parameter!
)

# Search with natural language
results = collection.query.near_text(
    query="search term",
    limit=10
)
```

## Property Vectorization Rules

### Vectorized Properties (included in embedding)
- Entity: `name`, `description`, `notes`
- Insight: `content`, `source_name`
- Strategy: `title`, `content`
- Event: `title`, `summary`, `outcomes`, `action_items`, `open_questions`
- Process: `title`, `content`, `triggers`

### Not Vectorized (metadata/filters)
- All `_type` fields (entity_type, source_type, etc.)
- All `domain` fields
- All `status` fields
- All date fields (created_at, updated_at, etc.)
- All UUID references (superseded_by)
- Tags arrays

## Migration Steps (If You Have Existing Data)

### 1. Backup Current Data
```bash
# Export existing data before migration
# (Custom export script needed)
```

### 2. Setup Transformers Service
```bash
cd weaviate
bash setup_vectorizer.sh
```

Or manually:
```bash
# Start transformers service
docker-compose -f docker-compose-vectorizer.yml up -d

# Update Weaviate container with modules
# Add these env vars and restart:
#   ENABLE_MODULES=text2vec-transformers
#   DEFAULT_VECTORIZER_MODULE=text2vec-transformers
#   TRANSFORMERS_INFERENCE_API=http://t2v-transformers:8080
```

### 3. Delete Old Collections
```python
import weaviate
client = weaviate.connect_to_local(port=8081, grpc_port=50051)

# Delete old collections (they can't be updated)
for name in ['Entity', 'Insight', 'Strategy', 'Event', 'Process']:
    client.collections.delete(name)

client.close()
```

### 4. Create New Schema
```bash
python3 weaviate/create_schema.py
```

### 5. Import Data (If Applicable)
- Re-import from backup
- Vectors will be auto-generated on insert
- No need to provide vector parameter

## Testing Auto-Vectorization

```bash
# Run the example script
python3 weaviate/example_auto_vectorization.py

# Or run validation tests
python3 weaviate/create_schema.py  # Includes validation
```

## Troubleshooting

### Check Vectorizer Status
```python
collection = client.collections.get("Insight")
config = collection.config.get()
print(f"Vectorizer: {config.vectorizer_config.vectorizer}")
# Should print: text2vec-transformers
```

### Check Services
```bash
# Check transformers service
docker ps | grep t2v-transformers
docker logs weaviate-t2v-transformers

# Check Weaviate modules
docker logs weaviate-secure | grep "text2vec-transformers"
```

### Common Issues

**"No vectorizer configured"**
- Make sure transformers service is running
- Check Weaviate has ENABLE_MODULES env var set
- Restart Weaviate after adding modules

**"Dimension mismatch"**
- Old data had 768 dims (Google Embedding 004)
- New data has 384 dims (all-MiniLM-L6-v2)
- Cannot mix - must recreate schema

**"Slow insertion"**
- Transformers service generates embeddings on-the-fly
- For bulk imports, consider batch operations
- Monitor CPU/GPU usage on transformers container

## Next Steps

1. ✅ Schema updated to use auto-vectorization
2. ⏳ Update Make.com pipelines to remove manual embedding calls
3. ⏳ Start using new insertion patterns (no vector parameter)
4. ⏳ Migrate existing data if applicable
5. ⏳ Remove Google API key from environment (optional)

## References

- `weaviate/README_VECTORIZER.md` - Detailed setup guide
- `weaviate/QUICK_REFERENCE.md` - Common operations
- `weaviate/example_auto_vectorization.py` - Working examples
- https://weaviate.io/developers/weaviate/modules/retriever-vectorizer-modules/text2vec-transformers

---

**Migration Date**: 2025-02-13
**Updated By**: Claude Code (Opus 4.6)
