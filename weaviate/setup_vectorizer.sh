#!/bin/bash
# Setup script for Weaviate with text2vec-transformers

set -e

echo "=========================================="
echo "NebulaOS Weaviate Vectorizer Setup"
echo "=========================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Weaviate is running
echo "Step 1: Checking Weaviate container..."
if docker ps | grep -q "weaviate-secure"; then
    echo -e "${GREEN}✓${NC} Weaviate container is running"
else
    echo -e "${RED}✗${NC} Weaviate container is not running"
    echo "Please start Weaviate first"
    exit 1
fi

# Get current Weaviate configuration
echo ""
echo "Step 2: Checking current Weaviate configuration..."
CURRENT_MODULES=$(docker inspect weaviate-secure --format '{{range .Config.Env}}{{println .}}{{end}}' | grep ENABLE_MODULES || echo "")

if [[ $CURRENT_MODULES == *"text2vec-transformers"* ]]; then
    echo -e "${GREEN}✓${NC} text2vec-transformers module is already enabled"
    NEEDS_RESTART=false
else
    echo -e "${YELLOW}!${NC} text2vec-transformers module is NOT enabled"
    echo ""
    echo "You need to add these environment variables to your Weaviate container:"
    echo ""
    echo "  ENABLE_MODULES=text2vec-transformers"
    echo "  DEFAULT_VECTORIZER_MODULE=text2vec-transformers"
    echo "  TRANSFORMERS_INFERENCE_API=http://t2v-transformers:8080"
    echo ""
    echo -e "${YELLOW}Note:${NC} You'll need to recreate your Weaviate container with these settings."
    NEEDS_RESTART=true
fi

# Check if transformers inference service is running
echo ""
echo "Step 3: Checking transformers inference service..."
if docker ps | grep -q "weaviate-t2v-transformers"; then
    echo -e "${GREEN}✓${NC} Transformers inference service is running"
else
    echo -e "${YELLOW}!${NC} Transformers inference service is not running"
    echo ""
    read -p "Would you like to start it now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Starting transformers inference service..."
        docker-compose -f docker-compose-vectorizer.yml up -d
        echo -e "${GREEN}✓${NC} Started transformers inference service"
        echo "Waiting for service to be ready (15 seconds)..."
        sleep 15
    else
        echo "Please start it manually with:"
        echo "  docker-compose -f docker-compose-vectorizer.yml up -d"
        exit 1
    fi
fi

# Check if we need to restart Weaviate
if [ "$NEEDS_RESTART" = true ]; then
    echo ""
    echo -e "${YELLOW}=========================================="
    echo "ACTION REQUIRED"
    echo -e "==========================================${NC}"
    echo ""
    echo "You need to update your Weaviate container configuration."
    echo ""
    echo "If you're using docker run, stop and restart with these additional flags:"
    echo ""
    echo "  -e ENABLE_MODULES=text2vec-transformers \\"
    echo "  -e DEFAULT_VECTORIZER_MODULE=text2vec-transformers \\"
    echo "  -e TRANSFORMERS_INFERENCE_API=http://t2v-transformers:8080"
    echo ""
    echo "If you're using docker-compose, add these to the environment section"
    echo "and run: docker-compose up -d"
    echo ""
    echo "After updating, run this script again."
    exit 1
fi

# Test the connection
echo ""
echo "Step 4: Testing transformers inference API..."
if docker exec weaviate-t2v-transformers curl -s http://localhost:8080/.well-known/ready > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Transformers inference API is ready"
else
    echo -e "${RED}✗${NC} Transformers inference API is not responding"
    echo "Try restarting the service:"
    echo "  docker-compose -f docker-compose-vectorizer.yml restart"
    exit 1
fi

# Check Python dependencies
echo ""
echo "Step 5: Checking Python dependencies..."
if python3 -c "import weaviate" 2>/dev/null; then
    echo -e "${GREEN}✓${NC} weaviate-client is installed"
else
    echo -e "${YELLOW}!${NC} weaviate-client is not installed"
    read -p "Would you like to install it now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        pip3 install weaviate-client
    else
        echo "Please install it with: pip3 install weaviate-client"
        exit 1
    fi
fi

# All checks passed
echo ""
echo -e "${GREEN}=========================================="
echo "Setup Complete!"
echo -e "==========================================${NC}"
echo ""
echo "Next steps:"
echo ""
echo "1. Back up any important data (if you have existing collections)"
echo ""
echo "2. Delete existing collections (they were created without vectorizer):"
echo "   python3 -c \"import weaviate; c = weaviate.connect_to_local(port=8081, grpc_port=50051); \\"
echo "   [c.collections.delete(name) for name in ['Entity','Insight','Strategy','Event','Process']]; c.close()\""
echo ""
echo "3. Create new schema with auto-vectorization:"
echo "   python3 create_schema_with_vectorizer.py"
echo ""
echo "4. Start inserting data without providing vectors!"
echo ""
echo "See README_VECTORIZER.md for detailed usage examples."
