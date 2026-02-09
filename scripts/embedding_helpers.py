"""
NebulaOS Embedding Generation Helpers
Handles vector generation using Google Embedding 004
"""

from typing import Dict, List, Optional
import os


def prepare_entity_vector(entity_data: Dict) -> List[float]:
    """
    Combine entity fields and generate embedding
    
    Args:
        entity_data: Dictionary with name, description, notes
    
    Returns:
        768-dimensional vector from Google Embedding 004
    """
    # Combine relevant text fields
    text_parts = []
    
    if entity_data.get('name'):
        text_parts.append(f"Entity: {entity_data['name']}")
    if entity_data.get('entity_type'):
        text_parts.append(f"Type: {entity_data['entity_type']}")
    if entity_data.get('description'):
        text_parts.append(entity_data['description'])
    if entity_data.get('notes'):
        text_parts.append(f"Notes: {entity_data['notes']}")
    
    combined_text = " | ".join(text_parts)
    
    return generate_google_embedding(combined_text)


def prepare_insight_vector(insight_content: str, source_name: Optional[str] = None) -> List[float]:
    """
    Generate embedding for insight content
    
    Args:
        insight_content: The insight text
        source_name: Optional source for additional context
    """
    if source_name:
        combined_text = f"{insight_content} | Source: {source_name}"
    else:
        combined_text = insight_content
    
    return generate_google_embedding(combined_text)


def prepare_strategy_vector(strategy_data: Dict) -> List[float]:
    """
    Combine strategy fields and generate embedding
    
    Args:
        strategy_data: Dictionary with title, content, strategy_type
    """
    text_parts = [
        f"Strategy: {strategy_data['title']}",
        f"Type: {strategy_data.get('strategy_type', 'unknown')}",
        strategy_data['content']
    ]
    combined_text = " | ".join(text_parts)
    
    return generate_google_embedding(combined_text)


def prepare_event_vector(event_data: Dict) -> List[float]:
    """
    Combine event fields and generate embedding
    
    Args:
        event_data: Dictionary with title, summary, outcomes
    """
    text_parts = [f"Event: {event_data.get('title', '')}"]
    
    if event_data.get('event_type'):
        text_parts.append(f"Type: {event_data['event_type']}")
    if event_data.get('summary'):
        text_parts.append(event_data['summary'])
    if event_data.get('outcomes'):
        text_parts.append(f"Outcomes: {event_data['outcomes']}")
    
    combined_text = " | ".join(filter(None, text_parts))
    
    return generate_google_embedding(combined_text)


def prepare_process_vector(process_data: Dict) -> List[float]:
    """
    Combine process fields and generate embedding
    
    Args:
        process_data: Dictionary with title, content, triggers
    """
    text_parts = [
        f"Process: {process_data['title']}",
        process_data['content']
    ]
    
    if process_data.get('triggers'):
        text_parts.append(f"When to use: {process_data['triggers']}")
    
    combined_text = " | ".join(text_parts)
    
    return generate_google_embedding(combined_text)


def generate_google_embedding(text: str) -> List[float]:
    """
    Generate embedding using Google Embedding 004
    
    Args:
        text: Text to embed
    
    Returns:
        768-dimensional vector
    """
    try:
        import google.generativeai as genai
        
        # Check for API key
        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError(
                "GOOGLE_API_KEY not found in environment variables. "
                "Set it with: export GOOGLE_API_KEY='your-api-key'"
            )
        
        genai.configure(api_key=api_key)
        
        # Generate embedding
        result = genai.embed_content(
            model="models/text-embedding-004",
            content=text,
            task_type="retrieval_document"  # For storing in vector database
        )
        
        embedding = result['embedding']
        
        # Validate dimension
        if len(embedding) != 768:
            raise ValueError(f"Expected 768 dimensions, got {len(embedding)}")
        
        return embedding
        
    except ImportError:
        raise ImportError(
            "google-generativeai not installed. "
            "Install with: pip install google-generativeai"
        )
    except Exception as e:
        raise RuntimeError(f"Failed to generate embedding: {str(e)}")


def generate_query_embedding(query_text: str) -> List[float]:
    """
    Generate embedding for search queries
    
    Args:
        query_text: The search query
    
    Returns:
        768-dimensional vector optimized for retrieval
    """
    try:
        import google.generativeai as genai
        
        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        
        # Use retrieval_query task type for searches
        result = genai.embed_content(
            model="models/text-embedding-004",
            content=query_text,
            task_type="retrieval_query"  # For searching
        )
        
        return result['embedding']
        
    except ImportError:
        raise ImportError("google-generativeai not installed")
    except Exception as e:
        raise RuntimeError(f"Failed to generate query embedding: {str(e)}")


def batch_generate_embeddings(texts: List[str]) -> List[List[float]]:
    """
    Generate embeddings for multiple texts in batch
    
    Args:
        texts: List of texts to embed
    
    Returns:
        List of 768-dimensional vectors
    """
    try:
        import google.generativeai as genai
        
        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        
        embeddings = []
        
        # Google API supports batch processing
        for text in texts:
            result = genai.embed_content(
                model="models/text-embedding-004",
                content=text,
                task_type="retrieval_document"
            )
            embeddings.append(result['embedding'])
        
        return embeddings
        
    except ImportError:
        raise ImportError("google-generativeai not installed")
    except Exception as e:
        raise RuntimeError(f"Failed to generate batch embeddings: {str(e)}")


# Test function
def test_embedding_setup():
    """Test that embedding generation is working"""
    print("🧪 Testing Google Embedding 004 setup...\n")
    
    try:
        # Test simple embedding
        test_text = "This is a test sentence for embedding generation."
        print(f"Generating embedding for: '{test_text}'")
        
        embedding = generate_google_embedding(test_text)
        
        print(f"✅ Success!")
        print(f"   Dimensions: {len(embedding)}")
        print(f"   First 5 values: {embedding[:5]}")
        print(f"   Vector range: [{min(embedding):.4f}, {max(embedding):.4f}]")
        
        # Test query embedding
        print("\nTesting query embedding...")
        query = "How to implement AI agents?"
        query_embedding = generate_query_embedding(query)
        print(f"✅ Query embedding generated ({len(query_embedding)} dims)")
        
        print("\n✅ Embedding setup is working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print("\nSetup instructions:")
        print("  1. Install: pip install google-generativeai")
        print("  2. Get API key from: https://makersuite.google.com/app/apikey")
        print("  3. Set environment variable: export GOOGLE_API_KEY='your-key'")
        return False


if __name__ == "__main__":
    test_embedding_setup()
