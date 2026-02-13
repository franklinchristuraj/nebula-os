# NebulaOS Weaviate with Local Embedding

This guide explains how to set up Weaviate with automatic local embedding generation using text2vec-transformers.

## Overview

You have two options for embeddings:
1. **Manual embeddings** (current setup) - Generate vectors externally and pass them in
2. **Automatic embeddings** (recommended) - Let Weaviate generate vectors automatically

## Setup: Automatic Embeddings with text2vec-transformers

### Step 1: Update Weaviate Configuration

First, you need to enable the text2vec-transformers module in your main Weaviate container.

Check your current Weaviate container startup command or docker-compose file and add:

```bash
ENABLE_MODULES=text2vec-transformers
DEFAULT_VECTORIZER_MODULE=text2vec-transformers
TRANSFORMERS_INFERENCE_API=http://t2v-transformers:8080
```

If you're using Docker run command, add these environment variables:
```bash
docker run -d \
  --name weaviate-secure \
  -e ENABLE_MODULES=text2vec-transformers \
  -e DEFAULT_VECTORIZER_MODULE=text2vec-transformers \
  -e TRANSFORMERS_INFERENCE_API=http://t2v-transformers:8080 \
  ... (other existing env vars)
```

### Step 2: Start the Transformers Inference Service

The `docker-compose-vectorizer.yml` file is ready. Start it with:

```bash
cd /home/franklinchris/nebula-os/weaviate
docker-compose -f docker-compose-vectorizer.yml up -d
```

This will start a container running the `sentence-transformers/all-MiniLM-L6-v2` model, which:
- Produces 384-dimensional vectors
- Is lightweight and fast
- Works well for general semantic search

### Step 3: Restart Weaviate

After adding the environment variables, restart your Weaviate container:

```bash
docker restart weaviate-secure
```

Wait a few seconds for it to start up.

### Step 4: Delete Old Collections and Create New Schema

**IMPORTANT**: You need to delete your existing collections because you can't change vectorizer settings on existing collections.

```bash
# Back up any important data first!

# Then run the new schema creation script
cd /home/franklinchris/nebula-os/weaviate
python3 create_schema_with_vectorizer.py
```

## Usage Examples

### Adding an Insight (No Vector Needed!)

```python
import weaviate
from datetime import datetime, timezone

client = weaviate.connect_to_local(
    host="localhost",
    port=8081,
    grpc_port=50051
)

insight_collection = client.collections.get("Insight")

# Just insert the data - vector is generated automatically!
insight_uuid = insight_collection.data.insert(
    properties={
        "content": "Weaviate's text2vec-transformers makes embedding easy by handling vectorization automatically",
        "source_name": "Weaviate Documentation",
        "source_type": "article",
        "domain": "work",
        "tags": ["weaviate", "embedding", "automation"],
        "status": "active",
        "confidence": "high",
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    }
    # No vector parameter needed!
)

print(f"Inserted insight: {insight_uuid}")

client.close()
```

### Semantic Search with Near Text

```python
# Search using natural language
results = insight_collection.query.near_text(
    query="how to automate embedding generation",
    limit=5
)

for obj in results.objects:
    print(f"- {obj.properties['content']}")
```

### Hybrid Search (Keyword + Semantic)

```python
from weaviate.classes.query import Filter

results = insight_collection.query.hybrid(
    query="weaviate embedding",
    filters=Filter.by_property("domain").equal("work"),
    limit=10
)
```

## Model Information

**Current model**: `sentence-transformers/all-MiniLM-L6-v2`
- **Dimensions**: 384
- **Speed**: Very fast
- **Quality**: Good for most use cases
- **Size**: ~80MB

### Alternative Models

You can change the model by editing `docker-compose-vectorizer.yml`:

**For better quality** (slower, larger):
```yaml
image: cr.weaviate.io/semitechnologies/transformers-inference:sentence-transformers-all-mpnet-base-v2
# 768 dimensions, ~400MB
```

**For multilingual support**:
```yaml
image: cr.weaviate.io/semitechnologies/transformers-inference:sentence-transformers-paraphrase-multilingual-MiniLM-L12-v2
# 384 dimensions, multilingual
```

## Comparison: Manual vs Automatic Embeddings

| Feature | Manual (Current) | Automatic (text2vec-transformers) |
|---------|-----------------|-----------------------------------|
| Setup Complexity | Simple | Moderate (needs extra container) |
| Insert Code | Must provide vector | No vector needed |
| Flexibility | Use any embedding model | Limited to supported models |
| External API | Yes (Google, OpenAI, etc) | No - runs locally |
| Cost | API costs | Free (uses compute) |
| Privacy | Data sent to API | Data stays local |
| Speed | Network latency | Local speed |

## Troubleshooting

### Connection Error
Make sure both containers are running:
```bash
docker ps | grep -E "weaviate|t2v-transformers"
```

### Module Not Enabled
Check Weaviate logs:
```bash
docker logs weaviate-secure
```

Look for: "text2vec-transformers module enabled"

### Vector Dimensions
The schema expects vectors that match the model's output:
- `all-MiniLM-L6-v2`: 384 dimensions
- `all-mpnet-base-v2`: 768 dimensions

### Network Issues
Ensure both containers are on the same network:
```bash
docker network inspect weaviate_default
```

## Files

- `create_schema.py` - Original schema (manual vectors)
- `create_schema_with_vectorizer.py` - New schema (automatic vectors)
- `docker-compose-vectorizer.yml` - Transformers inference service
- `test_schema.py` - Test existing schema

## Next Steps

1. Back up your current data
2. Follow the setup steps above
3. Run `create_schema_with_vectorizer.py`
4. Start inserting data without worrying about vectors!
5. Use `near_text()` for semantic search
