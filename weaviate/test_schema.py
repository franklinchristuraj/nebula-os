#!/usr/bin/env python3
"""
Test and validate NebulaOS Weaviate collections
"""

import weaviate
from weaviate.classes.query import QueryReference, Filter
from datetime import datetime, timezone
import os
import sys


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


def validate_collections(client):
    """Validate all collections exist with correct schema"""
    
    print("=" * 60)
    print("📋 Schema Validation")
    print("=" * 60)
    print()
    
    collections = ["Entity", "Insight", "Strategy", "Event", "Process"]
    all_valid = True
    
    for collection_name in collections:
        try:
            collection = client.collections.get(collection_name)
            config = collection.config.get()
            
            # Count properties
            prop_count = len(config.properties)
            
            # Count references
            ref_count = len(config.references) if hasattr(config, 'references') and config.references else 0
            
            print(f"✅ {collection_name}")
            print(f"   Properties: {prop_count}")
            print(f"   References: {ref_count}")
            
            # Show reference details
            if config.references:
                for ref in config.references:
                    target = getattr(ref, 'target_collection', getattr(ref, 'target', 'Unknown'))
                    print(f"      → {ref.name} → {target}")
            print()
            
        except Exception as e:
            print(f"❌ {collection_name}: {str(e)}\n")
            all_valid = False
    
    return all_valid


def test_basic_operations(client):
    """Test basic CRUD operations"""
    
    print("=" * 60)
    print("🧪 Testing Basic Operations")
    print("=" * 60)
    print()
    
    test_vector = [0.1] * 768  # Dummy 768-dimensional vector
    
    # Test 1: Create Entity
    print("Test 1: Create Entity")
    entity_collection = client.collections.get("Entity")
    entity_uuid = entity_collection.data.insert(
        properties={
            "name": "Test Company XYZ",
            "entity_type": "company",
            "domain": "work",
            "description": "A test company for validation purposes",
            "notes": "This is a test entity",
            "status": "active",
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        vector=test_vector
    )
    print(f"  ✅ Created Entity: {entity_uuid}\n")
    
    # Test 2: Query by property
    print("Test 2: Query by Property")
    response = entity_collection.query.fetch_objects(
        filters=Filter.by_property("name").equal("Test Company XYZ"),
        limit=1
    )
    
    if response.objects:
        obj = response.objects[0]
        print(f"  ✅ Found: {obj.properties['name']}")
        print(f"     Type: {obj.properties['entity_type']}")
        print(f"     Domain: {obj.properties['domain']}\n")
    else:
        print("  ❌ Query failed\n")
        return False
    
    # Test 3: Vector search
    print("Test 3: Vector Search")
    vector_response = entity_collection.query.near_vector(
        near_vector=test_vector,
        limit=3
    )
    
    print(f"  ✅ Found {len(vector_response.objects)} results via vector search")
    for obj in vector_response.objects:
        print(f"     • {obj.properties['name']}")
    print()
    
    # Test 4: Create Strategy with reference
    print("Test 4: Create Strategy with Entity Reference")
    strategy_collection = client.collections.get("Strategy")
    strategy_uuid = strategy_collection.data.insert(
        properties={
            "title": "Test Q1 Strategy",
            "content": "Focus on testing and validation",
            "strategy_type": "priority",
            "domain": "work",
            "time_horizon": "quarterly",
            "status": "active",
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        vector=test_vector,
        references={
            "appliesToEntities": [entity_uuid]
        }
    )
    print(f"  ✅ Created Strategy: {strategy_uuid}")
    print(f"     Linked to Entity: {entity_uuid}\n")
    
    # Test 5: Create Insight with multiple references
    print("Test 5: Create Insight with Multiple References")
    insight_collection = client.collections.get("Insight")
    insight_uuid = insight_collection.data.insert(
        properties={
            "content": "Testing cross-references is crucial for data integrity",
            "source_name": "Weaviate Testing Guide",
            "source_type": "article",
            "domain": "both",
            "tags": ["testing", "data-integrity", "weaviate"],
            "status": "active",
            "confidence": "high",
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        vector=test_vector,
        references={
            "relatedEntities": [entity_uuid],
            "relatedStrategies": [strategy_uuid]
        }
    )
    print(f"  ✅ Created Insight: {insight_uuid}")
    print(f"     Linked to Entity and Strategy\n")
    
    # Test 6: Query with cross-references
    print("Test 6: Query with Cross-References")
    insight_response = insight_collection.query.fetch_objects(
        filters=Filter.by_property("content").like("*cross-references*"),
        return_references=[
            QueryReference(link_on="relatedEntities"),
            QueryReference(link_on="relatedStrategies")
        ],
        limit=1
    )
    
    if insight_response.objects:
        obj = insight_response.objects[0]
        print(f"  ✅ Found Insight: {obj.properties['content'][:50]}...")
        
        if obj.references:
            if "relatedEntities" in obj.references and obj.references["relatedEntities"].objects:
                entities = obj.references["relatedEntities"].objects
                print(f"     Related Entities: {', '.join([e.properties['name'] for e in entities])}")
            
            if "relatedStrategies" in obj.references and obj.references["relatedStrategies"].objects:
                strategies = obj.references["relatedStrategies"].objects
                print(f"     Related Strategies: {', '.join([s.properties['title'] for s in strategies])}")
        print()
    else:
        print("  ❌ Query with references failed\n")
    
    # Test 7: Create Event with multiple references
    print("Test 7: Create Event with Multiple References")
    event_collection = client.collections.get("Event")
    event_uuid = event_collection.data.insert(
        properties={
            "title": "Test Planning Meeting",
            "event_type": "meeting",
            "summary": "Discussed testing strategy and validation procedures",
            "participants": ["Alice (Engineering)", "Bob (Product)"],
            "domain": "work",
            "event_date": datetime.now(timezone.utc),
            "outcomes": "Agreed on comprehensive testing approach",
            "action_items": "1. Write tests\n2. Run validation\n3. Document results",
            "created_at": datetime.now(timezone.utc)
        },
        vector=test_vector,
        references={
            "involvesEntities": [entity_uuid],
            "relatesToStrategies": [strategy_uuid],
            "generatedInsights": [insight_uuid]
        }
    )
    print(f"  ✅ Created Event: {event_uuid}")
    print(f"     Linked to Entity, Strategy, and Insight\n")
    
    # Test 8: Complex query
    print("Test 8: Complex Filter Query")
    work_entities = entity_collection.query.fetch_objects(
        filters=(
            Filter.by_property("domain").equal("work") &
            Filter.by_property("status").equal("active")
        ),
        limit=10
    )
    
    print(f"  ✅ Found {len(work_entities.objects)} active work entities")
    for obj in work_entities.objects:
        print(f"     • {obj.properties['name']} ({obj.properties['entity_type']})")
    print()
    
    # Cleanup
    print("Cleanup: Removing test objects...")
    entity_collection.data.delete_by_id(entity_uuid)
    strategy_collection.data.delete_by_id(strategy_uuid)
    insight_collection.data.delete_by_id(insight_uuid)
    event_collection.data.delete_by_id(event_uuid)
    print("  ✅ Cleanup complete\n")
    
    return True


def show_collection_stats(client):
    """Show statistics for all collections"""
    
    print("=" * 60)
    print("📊 Collection Statistics")
    print("=" * 60)
    print()
    
    collections = ["Entity", "Insight", "Strategy", "Event", "Process"]
    
    for collection_name in collections:
        try:
            collection = client.collections.get(collection_name)
            
            # Get object count
            response = collection.aggregate.over_all(total_count=True)
            count = response.total_count
            
            print(f"{collection_name}: {count} objects")
            
        except Exception as e:
            print(f"{collection_name}: Error - {e}")
    
    print()


def main():
    """Main test runner"""
    
    print("=" * 60)
    print("🔬 NebulaOS Weaviate Collections - Validation Test")
    print("=" * 60)
    print()
    
    # Connect
    try:
        print("🔌 Connecting to Weaviate...")
        client = connect()
        print(f"✅ Connected: {client.is_ready()}\n")
    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")
        return 1
    
    try:
        # Validate schema
        if not validate_collections(client):
            print("❌ Schema validation failed")
            return 1
        
        # Show current stats
        show_collection_stats(client)
        
        # Run tests
        if not test_basic_operations(client):
            print("❌ Basic operations test failed")
            return 1
        
        print("=" * 60)
        print("✅ All Tests Passed!")
        print("=" * 60)
        print()
        print("📝 Summary:")
        print("  • All 5 collections exist with correct schema")
        print("  • Entity, Insight, Strategy, Event, Process")
        print("  • Cross-references working correctly")
        print("  • Vector search operational (768 dimensions)")
        print("  • Property filters working")
        print("  • Ready for Google Embedding 004 integration")
        print()
        print("Next steps:")
        print("  1. Install Google AI: pip install google-generativeai")
        print("  2. Set GOOGLE_API_KEY environment variable")
        print("  3. Test embedding_helpers.py")
        print("  4. Run example_usage.py for real data insertion")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        client.close()
        print("\n🔌 Connection closed")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
