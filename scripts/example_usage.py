"""
NebulaOS Example Usage
Demonstrates how to insert and query data with manual vectors
"""

import weaviate
from weaviate.classes.query import Filter
from datetime import datetime, timezone
from embedding_helpers import (
    prepare_entity_vector,
    prepare_insight_vector,
    prepare_strategy_vector,
    prepare_event_vector,
    prepare_process_vector,
    generate_query_embedding
)


def example_create_entity(client):
    """Example: Create an entity with Google Embedding"""
    
    print("📝 Creating Entity: KPMG\n")
    
    entity_data = {
        "name": "KPMG",
        "entity_type": "company",
        "domain": "work",
        "description": "Big 4 consulting firm. Key partner for AI Governance workshops.",
        "notes": "Prefer structured agendas. Jean is primary contact - responsive on email.",
        "status": "active",
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    }
    
    # Generate embedding from entity data
    entity_vector = prepare_entity_vector(entity_data)
    
    entity_collection = client.collections.get("Entity")
    entity_uuid = entity_collection.data.insert(
        properties=entity_data,
        vector=entity_vector
    )
    
    print(f"✅ Created Entity with UUID: {entity_uuid}\n")
    return entity_uuid


def example_create_insight_with_references(client, entity_uuid):
    """Example: Create insight and link to entity"""
    
    print("📝 Creating Insight with cross-reference\n")
    
    insight_content = "Prompt chaining with explicit handoff context reduces hallucination rates by 40%"
    
    # Generate embedding for the insight
    insight_vector = prepare_insight_vector(
        insight_content,
        source_name="Building Effective Agents - Anthropic Blog"
    )
    
    insight_collection = client.collections.get("Insight")
    insight_uuid = insight_collection.data.insert(
        properties={
            "content": insight_content,
            "source_name": "Building Effective Agents - Anthropic Blog",
            "source_type": "article",
            "domain": "both",
            "tags": ["ai-agents", "prompt-engineering", "reliability"],
            "status": "active",
            "confidence": "high",
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        vector=insight_vector,
        references={
            "relatedEntities": [entity_uuid]  # Link to KPMG entity
        }
    )
    
    print(f"✅ Created Insight with UUID: {insight_uuid}")
    print(f"   Linked to Entity: {entity_uuid}\n")
    return insight_uuid


def example_create_strategy(client, entity_uuid):
    """Example: Create a strategy"""
    
    print("📝 Creating Strategy\n")
    
    strategy_data = {
        "title": "Q1 2025 Product Priorities",
        "content": "Focus on AI agent reliability, user feedback loops, and enterprise integration features.",
        "strategy_type": "priority",
        "domain": "work",
        "time_horizon": "quarterly",
        "valid_from": datetime.now(timezone.utc),
        "status": "active",
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    }
    
    strategy_vector = prepare_strategy_vector(strategy_data)
    
    strategy_collection = client.collections.get("Strategy")
    strategy_uuid = strategy_collection.data.insert(
        properties=strategy_data,
        vector=strategy_vector,
        references={
            "appliesToEntities": [entity_uuid]
        }
    )
    
    print(f"✅ Created Strategy with UUID: {strategy_uuid}\n")
    return strategy_uuid


def example_create_event(client, entity_uuid, insight_uuid, strategy_uuid):
    """Example: Create an event with multiple references"""
    
    print("📝 Creating Event\n")
    
    event_data = {
        "title": "KPMG Workshop Planning",
        "event_type": "meeting",
        "summary": "Discussed AI governance framework and workshop structure for March delivery.",
        "participants": ["Jean (KPMG Lead)", "Marie (Product)", "Alex (Technical)"],
        "domain": "work",
        "event_date": datetime.now(timezone.utc),
        "outcomes": "Agreed on 3-day workshop format with hands-on sessions.",
        "action_items": "1. Draft agenda by Friday\n2. Prepare case studies\n3. Book venue",
        "open_questions": "Budget approval timeline? Participant capacity?",
        "created_at": datetime.now(timezone.utc)
    }
    
    event_vector = prepare_event_vector(event_data)
    
    event_collection = client.collections.get("Event")
    event_uuid = event_collection.data.insert(
        properties=event_data,
        vector=event_vector,
        references={
            "involvesEntities": [entity_uuid],
            "generatedInsights": [insight_uuid],
            "relatesToStrategies": [strategy_uuid]
        }
    )
    
    print(f"✅ Created Event with UUID: {event_uuid}")
    print(f"   Linked to Entity, Insight, and Strategy\n")
    return event_uuid


def example_create_process(client, entity_uuid, strategy_uuid):
    """Example: Create a process"""
    
    print("📝 Creating Process\n")
    
    process_data = {
        "title": "Stakeholder Update Cadence",
        "content": """Weekly stakeholder updates following this structure:
1. Progress since last update
2. Blockers and risks
3. Upcoming milestones
4. Questions for stakeholders

Keep updates concise (max 5 minutes). Use Slack for async updates, meetings for decisions only.""",
        "domain": "work",
        "triggers": "Every Friday EOD, or when major milestone reached, or when blocker needs escalation",
        "status": "active",
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    }
    
    process_vector = prepare_process_vector(process_data)
    
    process_collection = client.collections.get("Process")
    process_uuid = process_collection.data.insert(
        properties=process_data,
        vector=process_vector,
        references={
            "appliesToEntities": [entity_uuid],
            "relatedStrategies": [strategy_uuid]
        }
    )
    
    print(f"✅ Created Process with UUID: {process_uuid}\n")
    return process_uuid


def example_semantic_search(client):
    """Example: Semantic search for insights"""
    
    print("🔍 Semantic Search: Finding insights about AI agents\n")
    
    # Generate query embedding
    query = "How to make AI agents more reliable?"
    query_vector = generate_query_embedding(query)
    
    insight_collection = client.collections.get("Insight")
    
    response = insight_collection.query.near_vector(
        near_vector=query_vector,
        limit=3,
        return_metadata=["distance", "certainty"],
        return_references=["relatedEntities"]
    )
    
    print(f"Query: '{query}'")
    print(f"Found {len(response.objects)} results:\n")
    
    for i, obj in enumerate(response.objects, 1):
        print(f"{i}. {obj.properties['content']}")
        print(f"   Source: {obj.properties['source_name']}")
        print(f"   Confidence: {obj.properties['confidence']}")
        print(f"   Distance: {obj.metadata.distance:.4f}")
        
        # Show related entities
        if obj.references and "relatedEntities" in obj.references:
            entities = obj.references["relatedEntities"].objects
            if entities:
                entity_names = [e.properties['name'] for e in entities]
                print(f"   Related to: {', '.join(entity_names)}")
        print()


def example_filter_query(client):
    """Example: Query with filters"""
    
    print("🔍 Filter Query: Active work entities\n")
    
    entity_collection = client.collections.get("Entity")
    
    response = entity_collection.query.fetch_objects(
        filters=(
            Filter.by_property("domain").equal("work") &
            Filter.by_property("status").equal("active")
        ),
        limit=10
    )
    
    print(f"Found {len(response.objects)} active work entities:\n")
    
    for obj in response.objects:
        print(f"• {obj.properties['name']} ({obj.properties['entity_type']})")
        print(f"  {obj.properties['description']}")
        print()


def example_meeting_prep(client, entity_name: str):
    """Example: Complex query for meeting preparation"""
    
    print(f"📋 Meeting Prep Query for: {entity_name}\n")
    
    # 1. Get entity details
    entity_collection = client.collections.get("Entity")
    entity_response = entity_collection.query.fetch_objects(
        filters=Filter.by_property("name").equal(entity_name),
        limit=1
    )
    
    if not entity_response.objects:
        print(f"❌ Entity '{entity_name}' not found")
        return
    
    entity = entity_response.objects[0]
    entity_uuid = entity.uuid
    
    print(f"📌 {entity.properties['name']} ({entity.properties['entity_type']})")
    print(f"Description: {entity.properties['description']}")
    print(f"Notes: {entity.properties['notes']}\n")
    
    # 2. Get recent events
    print("Recent Events:")
    event_collection = client.collections.get("Event")
    event_response = event_collection.query.fetch_objects(
        filters=Filter.by_ref("involvesEntities").by_id().equal(entity_uuid),
        limit=5
    )
    
    if event_response.objects:
        for event in event_response.objects:
            print(f"\n  • {event.properties['title']}")
            print(f"    Date: {event.properties.get('event_date', 'N/A')}")
            print(f"    Type: {event.properties['event_type']}")
            if event.properties.get('outcomes'):
                print(f"    Outcomes: {event.properties['outcomes']}")
            if event.properties.get('open_questions'):
                print(f"    Open Questions: {event.properties['open_questions']}")
    else:
        print("  No recent events found")
    
    # 3. Get related strategies
    print("\n\nActive Strategies:")
    strategy_collection = client.collections.get("Strategy")
    strategy_response = strategy_collection.query.fetch_objects(
        filters=(
            Filter.by_ref("appliesToEntities").by_id().equal(entity_uuid) &
            Filter.by_property("status").equal("active")
        ),
        limit=5
    )
    
    if strategy_response.objects:
        for strategy in strategy_response.objects:
            print(f"\n  • {strategy.properties['title']}")
            print(f"    Type: {strategy.properties['strategy_type']}")
            print(f"    Content: {strategy.properties['content'][:150]}...")
    else:
        print("  No active strategies found")


def main():
    """Run all examples"""
    
    print("=" * 60)
    print("🎯 NebulaOS Example Usage")
    print("=" * 60)
    print()
    
    # Connect to Weaviate
    client = weaviate.connect_to_local()
    
    try:
        if not client.is_ready():
            print("❌ Weaviate connection failed")
            return 1
        
        print("✅ Connected to Weaviate\n")
        print("=" * 60)
        print()
        
        # Create example data
        entity_uuid = example_create_entity(client)
        insight_uuid = example_create_insight_with_references(client, entity_uuid)
        strategy_uuid = example_create_strategy(client, entity_uuid)
        event_uuid = example_create_event(client, entity_uuid, insight_uuid, strategy_uuid)
        process_uuid = example_create_process(client, entity_uuid, strategy_uuid)
        
        print("=" * 60)
        print()
        
        # Query examples
        example_semantic_search(client)
        
        print("=" * 60)
        print()
        
        example_filter_query(client)
        
        print("=" * 60)
        print()
        
        example_meeting_prep(client, "KPMG")
        
        print()
        print("=" * 60)
        print("✅ Examples completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        client.close()
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
