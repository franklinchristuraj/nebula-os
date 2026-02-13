# Quick Reference: Weaviate with Auto-Vectorization

## Setup Summary

### 1. Start the Transformers Service
```bash
cd /home/franklinchris/nebula-os/weaviate
docker-compose -f docker-compose-vectorizer.yml up -d
```

### 2. Update Weaviate Container
Add these environment variables to your Weaviate container:
```
ENABLE_MODULES=text2vec-transformers
DEFAULT_VECTORIZER_MODULE=text2vec-transformers
TRANSFORMERS_INFERENCE_API=http://t2v-transformers:8080
```

### 3. Restart Weaviate
```bash
docker restart weaviate-secure
```

### 4. Create New Schema
```bash
python3 create_schema.py
```

---

## Key Differences: Before vs After

### BEFORE (Manual Vectors)
```python
# You had to provide vectors manually
test_vector = [0.1] * 768  # Generate externally

insight_collection.data.insert(
    properties={...},
    vector=test_vector  # Required!
)
```

### AFTER (Auto-Vectorization)
```python
# Just insert data - vectors generated automatically
insight_collection.data.insert(
    properties={
        "content": "Your insight text here",
        "source_type": "article",
        ...
    }
    # No vector parameter needed!
)
```

---

## Common Operations

### Insert Insight (No Vector Needed)
```python
insight_collection = client.collections.get("Insight")

insight_uuid = insight_collection.data.insert(
    properties={
        "content": "Your insight content",
        "source_name": "Source Name",
        "source_type": "article",
        "domain": "work",
        "tags": ["tag1", "tag2"],
        "status": "active",
        "confidence": "high",
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    }
)
```

### Semantic Search with near_text
```python
# Search using natural language
results = insight_collection.query.near_text(
    query="machine learning best practices",
    limit=10
)

for obj in results.objects:
    print(obj.properties['content'])
```

### Semantic Search + Filters
```python
from weaviate.classes.query import Filter

results = insight_collection.query.near_text(
    query="AI automation",
    filters=(
        Filter.by_property("domain").equal("work") &
        Filter.by_property("confidence").equal("high")
    ),
    limit=5
)
```

### Hybrid Search (Keyword + Semantic)
```python
results = insight_collection.query.hybrid(
    query="weaviate embedding",
    alpha=0.5,  # 0=pure keyword, 1=pure vector
    limit=10
)
```

### Insert with Cross-References
```python
# Create entity first
entity_uuid = entity_collection.data.insert(
    properties={
        "name": "Weaviate",
        "entity_type": "product",
        ...
    }
)

# Create insight linked to entity
insight_uuid = insight_collection.data.insert(
    properties={
        "content": "Insight about Weaviate",
        ...
    },
    references={
        "relatedEntities": [entity_uuid]
    }
)
```

### Query with Cross-References
```python
from weaviate.classes.query import QueryReference

results = insight_collection.query.near_text(
    query="database architecture",
    return_references=[
        QueryReference(link_on="relatedEntities"),
        QueryReference(link_on="relatedStrategies")
    ],
    limit=5
)

for obj in results.objects:
    print(obj.properties['content'])
    if obj.references:
        print("Related entities:", obj.references.get("relatedEntities"))
```

---

## Schema Reference

### Insight Properties
- `content` (TEXT) - **Vectorized** - The insight text
- `source_name` (TEXT) - **Vectorized** - Where it came from
- `source_type` (TEXT) - Not vectorized - article|video|book|podcast|conversation|reflection|research
- `domain` (TEXT) - Not vectorized - personal|work|both
- `tags` (TEXT_ARRAY) - Not vectorized - Flexible categorization
- `status` (TEXT) - Not vectorized - active|superseded|archived
- `superseded_by` (UUID) - Not vectorized - Reference to newer insight
- `confidence` (TEXT) - Not vectorized - high|medium|low|hypothesis
- `created_at` (DATE) - Not vectorized
- `updated_at` (DATE) - Not vectorized

### Insight References
- `relatedStrategies` → Strategy
- `relatedEntities` → Entity
- `relatedInsights` → Insight

---

## Troubleshooting

### Check if vectorizer is working
```python
collection = client.collections.get("Insight")
config = collection.config.get()
print(f"Vectorizer: {config.vectorizer_config.vectorizer}")
# Should print: text2vec-transformers
```

### Check transformers service
```bash
docker logs weaviate-t2v-transformers
```

### Test the API directly
```bash
docker exec weaviate-t2v-transformers curl http://localhost:8080/.well-known/ready
```

### Check Weaviate logs
```bash
docker logs weaviate-secure | grep text2vec
```

---

## Performance Tips

1. **Batch Insert**: Use `data.insert_many()` for bulk operations
2. **Limit Results**: Always use `limit` parameter to control response size
3. **Filter First**: Apply filters before semantic search when possible
4. **Monitor Resources**: The transformers service uses CPU/GPU for inference

---

## Files in This Directory

- `create_schema.py` - **Main schema file (now with auto-vectorization)**
- `create_schema_with_vectorizer.py` - (Deprecated) Duplicate kept for reference
- `test_schema.py` - Schema validation tests
- `docker-compose-vectorizer.yml` - Transformers service config
- `example_auto_vectorization.py` - Usage examples
- `setup_vectorizer.sh` - Automated setup script
- `README_VECTORIZER.md` - Detailed documentation
- `QUICK_REFERENCE.md` - This file
