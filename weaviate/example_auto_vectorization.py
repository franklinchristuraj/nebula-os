#!/usr/bin/env python3
"""
Example: Adding insights with automatic vectorization
No need to generate vectors manually!
"""

import weaviate
from datetime import datetime, timezone
import os


def connect():
    """Connect to Weaviate"""
    api_key = os.environ.get("WEAVIATE_API_KEY")
    
    client = weaviate.connect_to_local(
        host="localhost",
        port=8081,
        grpc_port=50051,
        auth_credentials=weaviate.auth.AuthApiKey(api_key) if api_key else None
    )
    
    return client


def add_insight_example(client):
    """
    Example: Add an insight without providing a vector
    Weaviate will automatically generate it!
    """
    
    print("=" * 60)
    print("Example: Adding Insight with Auto-Vectorization")
    print("=" * 60)
    print()
    
    insight_collection = client.collections.get("Insight")
    
    # Just provide the properties - no vector needed!
    insight_data = {
        "content": (
            "When using Weaviate with text2vec-transformers, vectors are "
            "automatically generated from your text content. This eliminates "
            "the need to call external embedding APIs and keeps your data local."
        ),
        "source_name": "Weaviate text2vec-transformers documentation",
        "source_type": "article",
        "domain": "work",
        "tags": ["weaviate", "embedding", "vectorization", "automation"],
        "status": "active",
        "confidence": "high",
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    }
    
    print("Inserting insight...")
    print(f"Content: {insight_data['content'][:80]}...")
    print()
    
    # Insert without vector parameter
    insight_uuid = insight_collection.data.insert(properties=insight_data)
    
    print(f"✅ Successfully inserted insight!")
    print(f"   UUID: {insight_uuid}")
    print(f"   Vector was generated automatically by text2vec-transformers")
    print()
    
    return insight_uuid


def semantic_search_example(client):
    """
    Example: Semantic search using near_text
    """
    
    print("=" * 60)
    print("Example: Semantic Search with near_text")
    print("=" * 60)
    print()
    
    insight_collection = client.collections.get("Insight")
    
    # Search using natural language query
    query = "automatic embedding generation"
    print(f"Searching for: '{query}'")
    print()
    
    results = insight_collection.query.near_text(
        query=query,
        limit=3
    )
    
    print(f"Found {len(results.objects)} results:")
    print()
    
    for i, obj in enumerate(results.objects, 1):
        content = obj.properties['content']
        # Truncate for display
        if len(content) > 150:
            content = content[:150] + "..."
        
        print(f"{i}. {content}")
        print(f"   Tags: {', '.join(obj.properties.get('tags', []))}")
        print(f"   Confidence: {obj.properties.get('confidence', 'N/A')}")
        print()


def add_entity_with_insight_reference(client):
    """
    Example: Add entity and link it to insights
    """
    
    print("=" * 60)
    print("Example: Entity with Cross-References")
    print("=" * 60)
    print()
    
    # First, add an entity
    entity_collection = client.collections.get("Entity")
    
    entity_uuid = entity_collection.data.insert(
        properties={
            "name": "Weaviate",
            "entity_type": "product",
            "domain": "work",
            "description": "Open-source vector database with built-in vectorization capabilities",
            "notes": "Supports multiple vectorizer modules including text2vec-transformers",
            "status": "active",
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
    )
    
    print(f"✅ Created Entity: {entity_uuid}")
    print()
    
    # Now add an insight that references this entity
    insight_collection = client.collections.get("Insight")
    
    insight_uuid = insight_collection.data.insert(
        properties={
            "content": (
                "Weaviate's modular architecture allows you to choose different "
                "vectorizers based on your needs - from lightweight local models "
                "to cloud-based APIs."
            ),
            "source_type": "reflection",
            "domain": "work",
            "tags": ["architecture", "flexibility"],
            "status": "active",
            "confidence": "high",
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        references={
            "relatedEntities": [entity_uuid]
        }
    )
    
    print(f"✅ Created Insight: {insight_uuid}")
    print(f"   Linked to Entity: {entity_uuid}")
    print()
    
    return entity_uuid, insight_uuid


def query_with_filters(client):
    """
    Example: Combined semantic search with filters
    """
    
    print("=" * 60)
    print("Example: Semantic Search + Filters")
    print("=" * 60)
    print()
    
    from weaviate.classes.query import Filter
    
    insight_collection = client.collections.get("Insight")
    
    # Search for insights about automation, but only high confidence ones
    results = insight_collection.query.near_text(
        query="automation and efficiency",
        filters=Filter.by_property("confidence").equal("high"),
        limit=5
    )
    
    print(f"Found {len(results.objects)} high-confidence insights about automation:")
    print()
    
    for obj in results.objects:
        print(f"- {obj.properties['content'][:100]}...")
        print(f"  Confidence: {obj.properties['confidence']}")
        print()


def main():
    """Run all examples"""
    
    print("\n")
    print("=" * 60)
    print("Weaviate Auto-Vectorization Examples")
    print("=" * 60)
    print()
    
    # Connect
    try:
        print("Connecting to Weaviate...")
        client = connect()
        print(f"✅ Connected: {client.is_ready()}")
        print()
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("\nMake sure:")
        print("  1. Weaviate is running")
        print("  2. text2vec-transformers service is running")
        print("  3. Schema was created with create_schema_with_vectorizer.py")
        return 1
    
    try:
        # Example 1: Simple insert
        insight_uuid = add_insight_example(client)
        
        # Example 2: Semantic search
        semantic_search_example(client)
        
        # Example 3: Cross-references
        entity_uuid, insight_uuid2 = add_entity_with_insight_reference(client)
        
        # Example 4: Search with filters
        query_with_filters(client)
        
        # Cleanup examples (optional)
        print("=" * 60)
        print("Cleanup")
        print("=" * 60)
        print()
        print("Example objects remain in database.")
        print("To delete them, run:")
        print(f"  insight_collection.data.delete_by_id('{insight_uuid}')")
        print(f"  insight_collection.data.delete_by_id('{insight_uuid2}')")
        print(f"  entity_collection.data.delete_by_id('{entity_uuid}')")
        print()
        
        print("=" * 60)
        print("✅ All Examples Completed!")
        print("=" * 60)
        print()
        print("Key Takeaways:")
        print("  • No vector parameter needed when inserting")
        print("  • Use near_text() for semantic search")
        print("  • Combine semantic search with filters")
        print("  • Cross-references work the same way")
        print("  • Vectors are generated automatically in the background")
        print()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        client.close()
        print("Connection closed.\n")
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
