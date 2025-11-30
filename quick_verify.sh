#!/bin/bash
# Quick verification script - tests deployment immediately after build
# Fast alternative to waiting for production logs

set -e

URL="$1"
if [ -z "$URL" ]; then
    echo "Usage: $0 <deployment-url>"
    exit 1
fi

echo "Quick verification: $URL"
echo ""

# Quick health check with timeout
echo -n "Health check... "
RESPONSE=$(curl -s --max-time 5 "${URL}/health" 2>&1 || echo "ERROR")
if echo "$RESPONSE" | grep -q "healthy\|status"; then
    echo "✅ Working"
elif echo "$RESPONSE" | grep -q "401\|Authentication"; then
    echo "⚠️  Password protected (function may be working)"
elif echo "$RESPONSE" | grep -q "500\|FUNCTION_INVOCATION_FAILED"; then
    echo "❌ Function crashed"
else
    echo "❓ Unknown response: $(echo "$RESPONSE" | head -c 50)"
fi

echo ""
echo "For detailed logs, check Vercel dashboard or run:"
echo "  vercel logs $URL"

