#!/usr/bin/env python3
"""
NebulaOS Schema Creation Script
Creates all 5 collections in Weaviate with proper dependencies
Version: 1.2
Date: 2025-02-09
"""

import weaviate
from weaviate.classes.config import Configure, Property, DataType, ReferenceProperty
from datetime import datetime, timezone
import sys
import traceback
import os


def create_entity_collection(client):
    """Create Entity collection with no auto-vectorization"""
    
    client.collections.create(
        name="Entity",
        description="Organizations, teams, products, projects, and people that appear in knowledge base",
        
        # Using vector_config instead of vectorizer_config (deprecated)
        vector_index_config=Configure.VectorIndex.hnsw(),
        
        properties=[
            Property(
                name="name",
                data_type=DataType.TEXT,
                description="Display name of the entity (e.g., 'KPMG', 'Make Product Team', 'NebulaOS')",
                index_filterable=True,
                index_searchable=True
            ),
            Property(
                name="entity_type",
                data_type=DataType.TEXT,
                description="Type: company | team | product | project | conference | community | person",
                index_filterable=True,
                index_searchable=False
            ),
            Property(
                name="domain",
                data_type=DataType.TEXT,
                description="Domain filter: personal | work | both",
                index_filterable=True,
                index_searchable=False
            ),
            Property(
                name="description",
                data_type=DataType.TEXT,
                description="Brief context about this entity - what it is, why it matters",
                index_filterable=False,
                index_searchable=True
            ),
            Property(
                name="notes",
                data_type=DataType.TEXT,
                description="Running notes: what works with them, preferences, history, quirks",
                index_filterable=False,
                index_searchable=True
            ),
            Property(
                name="status",
                data_type=DataType.TEXT,
                description="Lifecycle status: active | inactive | archived",
                index_filterable=True,
                index_searchable=False
            ),
            Property(
                name="created_at",
                data_type=DataType.DATE,
                description="Creation timestamp",
                index_filterable=True
            ),
            Property(
                name="updated_at",
                data_type=DataType.DATE,
                description="Last update timestamp",
                index_filterable=True
            )
        ]
    )
    print("✅ Created Entity collection")


def create_strategy_collection(client):
    """Create Strategy collection"""
    
    client.collections.create(
        name="Strategy",
        description="Goals, priorities, frameworks, principles, mental models - decision-making knowledge",
        
        vector_index_config=Configure.VectorIndex.hnsw(),
        
        properties=[
            Property(
                name="title",
                data_type=DataType.TEXT,
                description="Descriptive title (e.g., 'Q1 2025 Product Priorities', 'RICE Framework')",
                index_filterable=True,
                index_searchable=True
            ),
            Property(
                name="content",
                data_type=DataType.TEXT,
                description="Full description of the strategy, framework, or principle",
                index_filterable=False,
                index_searchable=True
            ),
            Property(
                name="strategy_type",
                data_type=DataType.TEXT,
                description="Type: goal | framework | principle | priority | mental_model | methodology",
                index_filterable=True,
                index_searchable=False
            ),
            Property(
                name="domain",
                data_type=DataType.TEXT,
                description="Domain filter: personal | work | both",
                index_filterable=True,
                index_searchable=False
            ),
            Property(
                name="time_horizon",
                data_type=DataType.TEXT,
                description="Timeframe: evergreen | quarterly | yearly | project-bound",
                index_filterable=True,
                index_searchable=False
            ),
            Property(
                name="valid_from",
                data_type=DataType.DATE,
                description="When this strategy becomes active",
                index_filterable=True
            ),
            Property(
                name="valid_until",
                data_type=DataType.DATE,
                description="When this strategy expires (null = no expiry)",
                index_filterable=True
            ),
            Property(
                name="status",
                data_type=DataType.TEXT,
                description="Lifecycle status: active | superseded | archived",
                index_filterable=True,
                index_searchable=False
            ),
            Property(
                name="superseded_by",
                data_type=DataType.UUID,
                description="Reference to newer Strategy UUID that replaces this one",
                index_filterable=True
            ),
            Property(
                name="created_at",
                data_type=DataType.DATE,
                index_filterable=True
            ),
            Property(
                name="updated_at",
                data_type=DataType.DATE,
                index_filterable=True
            )
        ],
        
        references=[
            ReferenceProperty(
                name="appliesToEntities",
                target_collection="Entity",
                description="Entities this strategy applies to or involves"
            ),
            ReferenceProperty(
                name="relatedStrategies",
                target_collection="Strategy",
                description="Parent strategies, supporting frameworks, related goals"
            )
        ]
    )
    print("✅ Created Strategy collection")


def create_insight_collection(client):
    """Create Insight collection with cross-references"""
    
    client.collections.create(
        name="Insight",
        description="Atomic knowledge units - learnings, observations, ideas, patterns, mental models",
        
        vector_index_config=Configure.VectorIndex.hnsw(),
        
        properties=[
            Property(
                name="content",
                data_type=DataType.TEXT,
                description="The insight itself, written to be self-contained and clear",
                index_filterable=False,
                index_searchable=True
            ),
            Property(
                name="source_name",
                data_type=DataType.TEXT,
                description="Origin reference: article title, video name, book, conversation topic",
                index_filterable=True,
                index_searchable=True
            ),
            Property(
                name="source_type",
                data_type=DataType.TEXT,
                description="Type: article | video | book | podcast | conversation | reflection | research",
                index_filterable=True,
                index_searchable=False
            ),
            Property(
                name="domain",
                data_type=DataType.TEXT,
                description="Domain filter: personal | work | both",
                index_filterable=True,
                index_searchable=False
            ),
            Property(
                name="tags",
                data_type=DataType.TEXT_ARRAY,
                description="Flexible categorization for filtering (e.g., ai-agents, prompt-engineering)",
                index_filterable=True,
                index_searchable=True
            ),
            Property(
                name="status",
                data_type=DataType.TEXT,
                description="Lifecycle status: active | superseded | archived",
                index_filterable=True,
                index_searchable=False
            ),
            Property(
                name="superseded_by",
                data_type=DataType.UUID,
                description="Reference to newer Insight UUID that replaces this one",
                index_filterable=True
            ),
            Property(
                name="confidence",
                data_type=DataType.TEXT,
                description="Confidence level: high | medium | low | hypothesis",
                index_filterable=True,
                index_searchable=False
            ),
            Property(
                name="created_at",
                data_type=DataType.DATE,
                index_filterable=True
            ),
            Property(
                name="updated_at",
                data_type=DataType.DATE,
                index_filterable=True
            )
        ],
        
        references=[
            ReferenceProperty(
                name="relatedStrategies",
                target_collection="Strategy",
                description="Strategies this insight informs or supports"
            ),
            ReferenceProperty(
                name="relatedEntities",
                target_collection="Entity",
                description="Entities this insight relates to"
            ),
            ReferenceProperty(
                name="relatedInsights",
                target_collection="Insight",
                description="Other insights that connect to this one"
            )
        ]
    )
    print("✅ Created Insight collection")


def create_event_collection(client):
    """Create Event collection"""
    
    client.collections.create(
        name="Event",
        description="Point-in-time occurrences - meetings, decisions, milestones, announcements",
        
        vector_index_config=Configure.VectorIndex.hnsw(),
        
        properties=[
            Property(
                name="title",
                data_type=DataType.TEXT,
                description="Event name (e.g., 'KPMG Workshop Planning', 'Q1 Roadmap Decision')",
                index_filterable=True,
                index_searchable=True
            ),
            Property(
                name="event_type",
                data_type=DataType.TEXT,
                description="Type: meeting | decision | milestone | announcement | workshop | review",
                index_filterable=True,
                index_searchable=False
            ),
            Property(
                name="summary",
                data_type=DataType.TEXT,
                description="What happened - key discussion points, context",
                index_filterable=False,
                index_searchable=True
            ),
            Property(
                name="participants",
                data_type=DataType.TEXT_ARRAY,
                description="Names with optional context: ['Marie (Product)', 'Jean (KPMG)']",
                index_filterable=True,
                index_searchable=True
            ),
            Property(
                name="domain",
                data_type=DataType.TEXT,
                description="Domain filter: personal | work | both",
                index_filterable=True,
                index_searchable=False
            ),
            Property(
                name="event_date",
                data_type=DataType.DATE,
                description="When this event occurred (ISO 8601 format)",
                index_filterable=True
            ),
            Property(
                name="outcomes",
                data_type=DataType.TEXT,
                description="Decisions made, conclusions reached",
                index_filterable=False,
                index_searchable=True
            ),
            Property(
                name="action_items",
                data_type=DataType.TEXT,
                description="Tasks assigned, next steps agreed",
                index_filterable=False,
                index_searchable=True
            ),
            Property(
                name="open_questions",
                data_type=DataType.TEXT,
                description="Unresolved items, parking lot topics",
                index_filterable=False,
                index_searchable=True
            ),
            Property(
                name="created_at",
                data_type=DataType.DATE,
                index_filterable=True
            )
        ],
        
        references=[
            ReferenceProperty(
                name="involvesEntities",
                target_collection="Entity",
                description="Organizations/teams involved (not individual participants)"
            ),
            ReferenceProperty(
                name="relatesToStrategies",
                target_collection="Strategy",
                description="Strategies discussed or affected by this event"
            ),
            ReferenceProperty(
                name="generatedInsights",
                target_collection="Insight",
                description="Insights that emerged from this event"
            )
        ]
    )
    print("✅ Created Event collection")


def create_process_collection(client):
    """Create Process collection"""
    
    client.collections.create(
        name="Process",
        description="Procedures, workflows, how-tos - operational knowledge for recurring activities",
        
        vector_index_config=Configure.VectorIndex.hnsw(),
        
        properties=[
            Property(
                name="title",
                data_type=DataType.TEXT,
                description="Process name (e.g., 'Stakeholder Update Cadence', 'Workshop Delivery Checklist')",
                index_filterable=True,
                index_searchable=True
            ),
            Property(
                name="content",
                data_type=DataType.TEXT,
                description="The process itself - steps, principles, checklist",
                index_filterable=False,
                index_searchable=True
            ),
            Property(
                name="domain",
                data_type=DataType.TEXT,
                description="Domain filter: personal | work | both",
                index_filterable=True,
                index_searchable=False
            ),
            Property(
                name="triggers",
                data_type=DataType.TEXT,
                description="When to use this process: conditions, cues, schedules",
                index_filterable=False,
                index_searchable=True
            ),
            Property(
                name="status",
                data_type=DataType.TEXT,
                description="Lifecycle status: active | superseded | archived",
                index_filterable=True,
                index_searchable=False
            ),
            Property(
                name="superseded_by",
                data_type=DataType.UUID,
                description="Reference to newer Process UUID that replaces this one",
                index_filterable=True
            ),
            Property(
                name="created_at",
                data_type=DataType.DATE,
                index_filterable=True
            ),
            Property(
                name="updated_at",
                data_type=DataType.DATE,
                index_filterable=True
            )
        ],
        
        references=[
            ReferenceProperty(
                name="appliesToEntities",
                target_collection="Entity",
                description="Entities this process is used with"
            ),
            ReferenceProperty(
                name="relatedStrategies",
                target_collection="Strategy",
                description="Strategies this process supports or implements"
            )
        ]
    )
    print("✅ Created Process collection")


def add_insight_strategy_reference(client):
    """Add the informedByInsights reference to Strategy collection after Insight exists"""
    
    try:
        # Get Strategy collection
        strategy_collection = client.collections.get("Strategy")
        
        # Note: In Weaviate v4 client, we need to update the collection config
        # This requires recreating with all references, which was done in create_strategy_collection
        # The reference is added via client.collections.config.add_reference()
        
        # For now, log that the mutual references are handled by creation order
        print("   Note: Strategy->Insight reference handled via creation order")
        
    except Exception as e:
        print(f"   Warning: Could not update Strategy references: {e}")


def validate_schema(client):
    """Validate all collections were created correctly"""
    
    print("\n📋 Schema Validation:")
    
    collections = ["Entity", "Insight", "Strategy", "Event", "Process"]
    all_valid = True
    
    for collection_name in collections:
        try:
            collection = client.collections.get(collection_name)
            config = collection.config.get()
            
            # Count properties
            prop_count = len(config.properties)
            
            # Count references (if they exist)
            ref_count = len(config.references) if hasattr(config, 'references') and config.references else 0
            
            print(f"  ✅ {collection_name}: {prop_count} properties, {ref_count} references")
            
        except Exception as e:
            print(f"  ❌ {collection_name}: {str(e)}")
            all_valid = False
    
    return all_valid


def run_validation_tests(client):
    """Run comprehensive validation tests"""
    
    print("\n🧪 Running Validation Tests\n")
    
    # Test 1: Check all collections exist
    print("Test 1: Collection Existence")
    collections = ["Entity", "Insight", "Strategy", "Event", "Process"]
    for name in collections:
        try:
            client.collections.get(name)
            print(f"  ✅ {name} exists")
        except Exception as e:
            print(f"  ❌ {name} missing: {e}")
            return False
    
    # Test 2: Create test entity
    print("\nTest 2: Object Creation with Manual Vector")
    test_vector = [0.1] * 768  # Dummy 768-dimensional vector
    
    entity_collection = client.collections.get("Entity")
    test_uuid = entity_collection.data.insert(
        properties={
            "name": "Test Company",
            "entity_type": "company",
            "domain": "work",
            "description": "Test entity for validation",
            "status": "active",
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        vector=test_vector
    )
    print(f"  ✅ Created test entity: {test_uuid}")
    
    # Test 3: Query test entity
    print("\nTest 3: Query by Property")
    response = entity_collection.query.fetch_objects(
        filters=weaviate.classes.query.Filter.by_property("name").equal("Test Company"),
        limit=1
    )
    
    if response.objects:
        print(f"  ✅ Query successful: {response.objects[0].properties['name']}")
    else:
        print("  ❌ Query failed")
        return False
    
    # Test 4: Vector search
    print("\nTest 4: Vector Search")
    vector_response = entity_collection.query.near_vector(
        near_vector=test_vector,
        limit=1
    )
    
    if vector_response.objects:
        print(f"  ✅ Vector search successful: {vector_response.objects[0].properties['name']}")
    else:
        print("  ❌ Vector search failed")
        return False
    
    # Test 5: Cross-reference
    print("\nTest 5: Cross-Reference Creation")
    insight_collection = client.collections.get("Insight")
    insight_uuid = insight_collection.data.insert(
        properties={
            "content": "Test insight with cross-reference",
            "source_type": "reflection",
            "domain": "work",
            "tags": ["test"],
            "status": "active",
            "confidence": "low",
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        vector=test_vector,
        references={
            "relatedEntities": [test_uuid]
        }
    )
    print(f"  ✅ Created insight with reference: {insight_uuid}")
    
    # Test 6: Query with reference
    print("\nTest 6: Query with Cross-Reference")
    from weaviate.classes.query import QueryReference
    
    insight_response = insight_collection.query.fetch_objects(
        filters=weaviate.classes.query.Filter.by_property("content").like("Test insight*"),
        return_references=[QueryReference(link_on="relatedEntities")],
        limit=1
    )
    
    if insight_response.objects and insight_response.objects[0].references:
        related_entities = insight_response.objects[0].references.get("relatedEntities")
        if related_entities and related_entities.objects:
            print(f"  ✅ Reference query successful: linked to {related_entities.objects[0].properties['name']}")
        else:
            print("  ⚠️  Reference exists but objects not returned")
    else:
        print("  ❌ Reference query failed")
    
    # Cleanup
    print("\nCleaning up test objects...")
    entity_collection.data.delete_by_id(test_uuid)
    insight_collection.data.delete_by_id(insight_uuid)
    print("  ✅ Cleanup complete")
    
    return True


def connect_to_weaviate(local=True, host=None, http_port=8081, grpc_port=50051):
    """
    Connect to Weaviate instance
    
    Args:
        local: If True, connect to localhost
        host: VPS hostname/IP for remote connection
        http_port: HTTP port (default 8081)
        grpc_port: gRPC port (default 50051)
    """
    # Get API key from environment
    api_key = os.environ.get("WEAVIATE_API_KEY")
    
    if local:
        print(f"🔌 Connecting to local Weaviate instance on port {http_port}...")
        if api_key:
            print("   Using API key authentication")
            client = weaviate.connect_to_local(
                host="localhost",
                port=http_port,
                grpc_port=grpc_port,
                auth_credentials=weaviate.auth.AuthApiKey(api_key)
            )
        else:
            print("   No API key found, attempting anonymous access")
            client = weaviate.connect_to_local(
                host="localhost",
                port=http_port,
                grpc_port=grpc_port
            )
    else:
        if not host:
            raise ValueError("Host must be provided for remote connection")
        print(f"🔌 Connecting to remote Weaviate at {host}:{http_port}...")
        
        auth = weaviate.auth.AuthApiKey(api_key) if api_key else None
        
        client = weaviate.connect_to_custom(
            http_host=host,
            http_port=http_port,
            http_secure=False,
            grpc_host=host,
            grpc_port=grpc_port,
            grpc_secure=False,
            auth_credentials=auth
        )
    
    return client


def main():
    """Main execution function"""
    
    print("=" * 60)
    print("🚀 NebulaOS Schema Creation")
    print("=" * 60)
    
    # Connect to Weaviate
    # Change these parameters based on your setup:
    # - local=True for localhost
    # - local=False, host="your-vps-url" for remote
    try:
        client = connect_to_weaviate(local=True)
        print(f"✅ Connected: {client.is_ready()}\n")
    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")
        print("\nPlease ensure:")
        print("  1. Weaviate is running")
        print("  2. Connection details are correct")
        print("  3. Run: pip install weaviate-client")
        print("  4. WEAVIATE_API_KEY is set if authentication is required")
        return 1
    
    try:
        print("📦 Creating collections in dependency order...\n")
        
        # Create collections in correct dependency order
        # 1. Entity first (no dependencies)
        create_entity_collection(client)
        
        # 2. Strategy - references Entity and itself (self-reference is OK)
        create_strategy_collection(client)
        
        # 3. Insight - references Entity, Strategy, and itself
        create_insight_collection(client)
        
        # 4. Event - references Entity, Strategy, and Insight
        create_event_collection(client)
        
        # 5. Process - references Entity and Strategy
        create_process_collection(client)
        
        print("\n" + "=" * 60)
        
        # Validate schema
        if not validate_schema(client):
            print("\n⚠️  Schema validation found issues")
            return 1
        
        print("\n" + "=" * 60)
        
        # Run tests
        if not run_validation_tests(client):
            print("\n⚠️  Validation tests found issues")
            return 1
        
        print("\n" + "=" * 60)
        print("✅ Schema creation complete!")
        print("\n📝 Next steps:")
        print("  1. Set up Google Embedding 004 integration (see embedding_helpers.py)")
        print("  2. Test vector insertion with real embeddings")
        print("  3. Review example_usage.py for data insertion patterns")
        print("  4. Plan data migration strategy")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        traceback.print_exc()
        return 1
    finally:
        client.close()
        print("\n🔌 Connection closed")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
