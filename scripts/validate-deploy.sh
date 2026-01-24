#!/bin/bash
# Post-deploy validation script for Render backend
# Run this after your Render deployment is complete

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}🔍 PreciosRegulados.uy - Backend Health Check${NC}"
echo "============================================"

# Get the backend URL from user
if [ -z "$1" ]; then
  echo -e "${RED}❌ Usage: ./scripts/validate-deploy.sh <backend-url>${NC}"
  echo "   Example: ./scripts/validate-deploy.sh https://preciosregulados-api.onrender.com"
  exit 1
fi

BACKEND_URL="$1"
TIMEOUT=10

# Function to check endpoint
check_endpoint() {
  local endpoint=$1
  local name=$2
  
  echo -n "Checking $name ... "
  
  if curl -s -m $TIMEOUT "$BACKEND_URL$endpoint" > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC}"
    return 0
  else
    echo -e "${RED}✗${NC}"
    return 1
  fi
}

# Health checks
echo ""
echo "Testing endpoints:"
echo "-----------------"

ERRORS=0

check_endpoint "/docs" "API Documentation" || ((ERRORS++))
check_endpoint "/api/v1/productos" "Productos endpoint" || ((ERRORS++))
check_endpoint "/api/v1/etl/status" "ETL Status" || ((ERRORS++))

echo ""

if [ $ERRORS -eq 0 ]; then
  echo -e "${GREEN}✅ All checks passed!${NC}"
  echo ""
  echo "Backend URL: $BACKEND_URL"
  echo "API Docs: $BACKEND_URL/docs"
  echo ""
  echo "Next steps:"
  echo "1. Use this URL in Cloudflare Pages as VITE_API_URL"
  echo "2. Update CORS_ORIGINS in Render environment if needed"
  exit 0
else
  echo -e "${RED}❌ Some checks failed${NC}"
  echo "Backend might still be starting. Wait a few minutes and try again."
  exit 1
fi
