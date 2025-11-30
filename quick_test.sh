#!/bin/bash
# Quick test script for backend API
# Tests the last deployed URL or a custom URL

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Get URL from argument or last deployment
if [ -n "$1" ]; then
    TEST_URL="$1"
elif [ -f ".last_deployment_url.txt" ]; then
    TEST_URL=$(cat .last_deployment_url.txt)
    echo -e "${BLUE}Using last deployment URL: ${TEST_URL}${NC}"
else
    echo -e "${RED}❌ No URL provided and no .last_deployment_url.txt found${NC}"
    echo "Usage: $0 [URL]"
    echo "Example: $0 https://api.sunnationalbank.online"
    exit 1
fi

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Quick API Test${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "Testing: ${YELLOW}${TEST_URL}${NC}"
echo ""

# Test 1: Health
echo -n "1. Health check... "
HEALTH=$(curl -s -o /dev/null -w "%{http_code}" "${TEST_URL}/health" 2>/dev/null || echo "000")
if [ "$HEALTH" = "200" ]; then
    echo -e "${GREEN}✅${NC}"
else
    echo -e "${RED}❌ (${HEALTH})${NC}"
fi

# Test 2: Root
echo -n "2. Root endpoint... "
ROOT=$(curl -s -o /dev/null -w "%{http_code}" "${TEST_URL}/" 2>/dev/null || echo "000")
if [ "$ROOT" = "200" ]; then
    echo -e "${GREEN}✅${NC}"
else
    echo -e "${RED}❌ (${ROOT})${NC}"
fi

# Test 3: Login
echo -n "3. Login endpoint... "
LOGIN_RESPONSE=$(curl -s -w "\n%{http_code}" \
    -X POST \
    -H "Content-Type: application/json" \
    -d '{"email":"john.doe@example.com","password":"SecurePass123!"}' \
    "${TEST_URL}/api/v1/auth/login" 2>/dev/null || echo -e "\n000")
LOGIN_CODE=$(echo "$LOGIN_RESPONSE" | tail -1)

if [ "$LOGIN_CODE" = "200" ]; then
    echo -e "${GREEN}✅${NC}"
    LOGIN_BODY=$(echo "$LOGIN_RESPONSE" | head -n -1)
    TOKEN=$(echo "$LOGIN_BODY" | grep -oP '"access_token":\s*"[^"]*"' | cut -d'"' -f4 || echo "")
    if [ -n "$TOKEN" ]; then
        echo -e "   ${GREEN}✅ Login successful! Token: ${TOKEN:0:20}...${NC}"
    fi
else
    echo -e "${RED}❌ (${LOGIN_CODE})${NC}"
    LOGIN_BODY=$(echo "$LOGIN_RESPONSE" | head -n -1)
    echo "   Response: $(echo "$LOGIN_BODY" | head -c 100)"
fi

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "Results: Health=$([ "$HEALTH" = "200" ] && echo "✅" || echo "❌") | Root=$([ "$ROOT" = "200" ] && echo "✅" || echo "❌") | Login=$([ "$LOGIN_CODE" = "200" ] && echo "✅" || echo "❌")"
echo -e "${BLUE}========================================${NC}"

