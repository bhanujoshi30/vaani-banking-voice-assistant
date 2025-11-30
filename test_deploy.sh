#!/bin/bash
# Test script - run after deployment

if [ -z "$1" ]; then
    echo "Usage: $0 <deployment-url>"
    echo "Example: $0 https://your-backend.vercel.app"
    exit 1
fi

URL="$1"
echo "Testing: $URL"
echo ""

# Health check
echo -n "1. Health check... "
HEALTH=$(curl -s -o /dev/null -w "%{http_code}" "${URL}/health" 2>/dev/null || echo "000")
[ "$HEALTH" = "200" ] && echo "✅ ($HEALTH)" || echo "❌ ($HEALTH)"

# Root
echo -n "2. Root endpoint... "
ROOT=$(curl -s -o /dev/null -w "%{http_code}" "${URL}/" 2>/dev/null || echo "000")
[ "$ROOT" = "200" ] && echo "✅ ($ROOT)" || echo "❌ ($ROOT)"

# Login
echo -n "3. Login endpoint... "
LOGIN_RESPONSE=$(curl -s -w "\n%{http_code}" \
    -X POST \
    -H "Content-Type: application/json" \
    -d '{"email":"john.doe@example.com","password":"SecurePass123!"}' \
    "${URL}/api/v1/auth/login" 2>/dev/null || echo -e "\n000")
LOGIN_CODE=$(echo "$LOGIN_RESPONSE" | tail -1)
LOGIN_BODY=$(echo "$LOGIN_RESPONSE" | head -n -1)

if [ "$LOGIN_CODE" = "200" ]; then
    echo "✅ ($LOGIN_CODE)"
    TOKEN=$(echo "$LOGIN_BODY" | grep -oE '"access_token"[[:space:]]*:[[:space:]]*"[^"]*"' | cut -d'"' -f4 || echo "")
    if [ -n "$TOKEN" ]; then
        echo "   ✅ Token received: ${TOKEN:0:30}..."
    fi
else
    echo "❌ ($LOGIN_CODE)"
    echo "   Response: $(echo "$LOGIN_BODY" | head -c 200)"
fi

echo ""
echo "Done!"
