#!/usr/bin/env python3
"""
Quick Reference: Common Operations for NebulaOS Weaviate Collections

⚠️ NOTE: This file contains examples using manual vectorization.
With the current text2vec-transformers setup, vectors are auto-generated.
For updated examples using auto-vectorization, see:
- weaviate/example_auto_vectorization.py

This file is kept for reference purposes.
"""

import weaviate
from weaviate.classes.query import Filter, QueryReference
from datetime import datetime, timezone
import os


# ============================================================================
# CONNECTION
# ============================================================================

def connect():
    """Connect to Weaviate with authentication"""
    return weaviate.connect_to_local(
        host="localhost",
        port=8081,
        grpc_port=50051,
        auth_credentials=weaviate.auth.AuthApiKey(os.environ.get("WEAVIATE_API_KEY"))
    )


# ============================================================================
# CREATE OPERATIONS
# ============================================================================

def create_entity_example():
    """Create an entity"""
    from embedding_helpers import prepare_entity_vector
    
    client = connect()
    
    entity_data = {
        "name": "Example Corp",
        "entity_type": "company",
        "domain": "work",
        "description": "Example company description",
        "notes": "Important notes here",
        "status": "active",
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    }
    
    vector = prepare_entity_vector(entity_data)
    
    collection = client.collections.get("Entity")
    uuid = collection.data.insert(properties=entity_data, vector=vector)
    
    client.close()
    return uuid


def create_insight_with_refs(entity_uuid, strategy_uuid):
    """Create insight with references"""
    from embedding_helpers import prepare_insight_vector
    
    client = connect()
    
    content = "Your insight content here"
    vector = prepare_insight_vector(content, "Source Name")
    
    collection = client.collections.get("Insight")
    uuid = collection.data.insert(
        properties={
            "content": content,
            "source_name": "Source Name",
            "source_type": "article",
            "domain": "both",
            "tags": ["tag1", "tag2"],
            "status": "active",
            "confidence": "high",
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        vector=vector,
        references={
            "relatedEntities": [entity_uuid],
            "relatedStrategies": [strategy_uuid]
        }
    )
    
    client.close()
    return uuid


# ============================================================================
# QUERY OPERATIONS
# ============================================================================

def query_by_name(name):
    """Find entity by exact name"""
    client = connect()
    
    collection = client.collections.get("Entity")
    response = collection.query.fetch_objects(
        filters=Filter.by_property("name").equal(name),
        limit=1
    )
    
    result = response.objects[0] if response.objects else None
    client.close()
    return result


def semantic_search(query_text, collection_name="Insight", limit=5):
    """Semantic search using vector similarity"""
    from embedding_helpers import generate_query_embedding
    
    client = connect()
    
    query_vector = generate_query_embedding(query_text)
    
    collection = client.collections.get(collection_name)
    response = collection.query.near_vector(
        near_vector=query_vector,
        limit=limit,
        return_metadata=["distance", "certainty"]
    )
    
    results = response.objects
    client.close()
    return results


def query_active_work_entities():
    """Find all active work entities"""
    client = connect()
    
    collection = client.collections.get("Entity")
    response = collection.query.fetch_objects(
        filters=(
            Filter.by_property("domain").equal("work") &
            Filter.by_property("status").equal("active")
        ),
        limit=100
    )
    
    results = response.objects
    client.close()
    return results


def query_with_references(insight_content_pattern):
    """Query insights and return with references"""
    client = connect()
    
    collection = client.collections.get("Insight")
    response = collection.query.fetch_objects(
        filters=Filter.by_property("content").like(f"*{insight_content_pattern}*"),
        return_references=[
            QueryReference(link_on="relatedEntities"),
            QueryReference(link_on="relatedStrategies")
        ],
        limit=10
    )
    
    results = response.objects
    client.close()
    return results


def get_entity_context(entity_name):
    """Get full context for an entity: events, strategies, insights"""
    client = connect()
    
    # Get entity
    entity_collection = client.collections.get("Entity")
    entity_response = entity_collection.query.fetch_objects(
        filters=Filter.by_property("name").equal(entity_name),
        limit=1
    )
    
    if not entity_response.objects:
        client.close()
        return None
    
    entity = entity_response.objects[0]
    entity_uuid = entity.uuid
    
    # Get related events
    event_collection = client.collections.get("Event")
    events = event_collection.query.fetch_objects(
        filters=Filter.by_ref("involvesEntities").by_id().equal(entity_uuid),
        limit=20
    )
    
    # Get related strategies
    strategy_collection = client.collections.get("Strategy")
    strategies = strategy_collection.query.fetch_objects(
        filters=Filter.by_ref("appliesToEntities").by_id().equal(entity_uuid),
        limit=20
    )
    
    # Get related insights
    insight_collection = client.collections.get("Insight")
    insights = insight_collection.query.fetch_objects(
        filters=Filter.by_ref("relatedEntities").by_id().equal(entity_uuid),
        limit=20
    )
    
    context = {
        "entity": entity,
        "events": events.objects,
        "strategies": strategies.objects,
        "insights": insights.objects
    }
    
    client.close()
    return context


# ============================================================================
# UPDATE OPERATIONS
# ============================================================================

def update_entity_status(entity_uuid, new_status):
    """Update entity status"""
    client = connect()
    
    collection = client.collections.get("Entity")
    collection.data.update(
        uuid=entity_uuid,
        properties={
            "status": new_status,
            "updated_at": datetime.now(timezone.utc)
        }
    )
    
    client.close()


def add_reference(from_uuid, from_collection, to_uuid, reference_property):
    """Add a cross-reference between objects"""
    client = connect()
    
    collection = client.collections.get(from_collection)
    collection.data.reference_add(
        from_uuid=from_uuid,
        from_property=reference_property,
        to=to_uuid
    )
    
    client.close()


# ============================================================================
# DELETE OPERATIONS
# ============================================================================

def delete_object(collection_name, uuid):
    """Delete an object by UUID"""
    client = connect()
    
    collection = client.collections.get(collection_name)
    collection.data.delete_by_id(uuid)
    
    client.close()


def archive_insight(insight_uuid, superseded_by_uuid=None):
    """Archive an insight (mark as superseded)"""
    client = connect()
    
    collection = client.collections.get("Insight")
    update_data = {
        "status": "superseded" if superseded_by_uuid else "archived",
        "updated_at": datetime.now(timezone.utc)
    }
    
    if superseded_by_uuid:
        update_data["superseded_by"] = superseded_by_uuid
    
    collection.data.update(uuid=insight_uuid, properties=update_data)
    
    client.close()


# ============================================================================
# BATCH OPERATIONS
# ============================================================================

def batch_insert_entities(entities_data):
    """Insert multiple entities in batch"""
    from embedding_helpers import prepare_entity_vector
    
    client = connect()
    collection = client.collections.get("Entity")
    
    uuids = []
    with collection.batch.dynamic() as batch:
        for entity_data in entities_data:
            vector = prepare_entity_vector(entity_data)
            uuid = batch.add_object(properties=entity_data, vector=vector)
            uuids.append(uuid)
    
    client.close()
    return uuids


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_collection_stats():
    """Get object counts for all collections"""
    client = connect()
    
    stats = {}
    for name in ["Entity", "Insight", "Strategy", "Event", "Process"]:
        collection = client.collections.get(name)
        response = collection.aggregate.over_all(total_count=True)
        stats[name] = response.total_count
    
    client.close()
    return stats


def search_by_tags(tags, collection_name="Insight"):
    """Find insights/content by tags"""
    client = connect()
    
    collection = client.collections.get(collection_name)
    
    # Build filter for tags
    if len(tags) == 1:
        filter_obj = Filter.by_property("tags").contains_any(tags)
    else:
        filter_obj = Filter.by_property("tags").contains_any(tags)
    
    response = collection.query.fetch_objects(
        filters=filter_obj,
        limit=50
    )
    
    results = response.objects
    client.close()
    return results


# ============================================================================
# EXAMPLES
# ============================================================================

if __name__ == "__main__":
    print("Quick Reference - Example Usage\n")
    
    # Example 1: Get stats
    print("Collection Statistics:")
    stats = get_collection_stats()
    for name, count in stats.items():
        print(f"  {name}: {count} objects")
    print()
    
    # Example 2: Search active work entities
    print("Active Work Entities:")
    entities = query_active_work_entities()
    for entity in entities[:5]:
        print(f"  • {entity.properties['name']} ({entity.properties['entity_type']})")
    print()
    
    # Example 3: Semantic search
    print("Semantic Search Example:")
    print("  Query: 'AI agent reliability'")
    results = semantic_search("AI agent reliability", limit=3)
    for i, obj in enumerate(results, 1):
        print(f"  {i}. {obj.properties['content'][:60]}...")
        print(f"     Distance: {obj.metadata.distance:.4f}")
    print()
    
    print("See README.md for more examples!")
