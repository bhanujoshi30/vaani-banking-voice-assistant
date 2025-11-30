#!/bin/bash
# Robust Backend Deployment Script with Integrated Testing
# Based on Vercel Build Output API best practices

set -uo pipefail  # Removed -e temporarily to handle errors manually

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Logging functions
log_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }
log_warn() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_step() { echo -e "${CYAN}▶️  $1${NC}"; }

# Error handler - only show if we haven't already shown an error
cleanup() {
    local exit_code=$?
    if [ $exit_code -ne 0 ] && [ -z "${ERROR_SHOWN:-}" ]; then
        log_error "Script failed with exit code $exit_code"
        log_info "Check the output above for details"
    fi
}
trap cleanup EXIT

echo ""
echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Backend Deployment & Test Suite      ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
echo ""

# Step 1: Verify prerequisites
log_step "Step 1: Verifying prerequisites..."

if ! command -v vercel &> /dev/null; then
    log_error "Vercel CLI not found. Install with: npm install -g vercel"
    exit 1
fi
log_success "Vercel CLI found"

# Check login status more robustly
log_info "Checking Vercel login status..."
VERCEL_WHOAMI_OUTPUT=$(vercel whoami 2>&1) || true
VERCEL_WHOAMI_EXIT=$?

# Check for error messages in output (even if exit code is 0)
if echo "$VERCEL_WHOAMI_OUTPUT" | grep -qiE "No existing credentials|not valid|Error.*credentials"; then
    log_error "Not logged in to Vercel"
    log_warn "It seems credentials aren't persisting. Trying to fix..."
    echo ""
    log_info "Please run this command to login:"
    echo "  vercel login"
    echo ""
    log_info "If you just logged in, the credentials might not be saved."
    log_info "Try logging in again in this terminal session."
    exit 1
fi

# If exit code is non-zero, also fail
if [ $VERCEL_WHOAMI_EXIT -ne 0 ]; then
    log_error "Not logged in to Vercel. Run: vercel login"
    exit 1
fi

# Extract username (skip "Vercel CLI" line)
VERCEL_USER=$(echo "$VERCEL_WHOAMI_OUTPUT" | grep -v "Vercel CLI" | grep -v "^$" | head -1 || echo "authenticated")
if [ -z "$VERCEL_USER" ] || [ "$VERCEL_USER" = "authenticated" ]; then
    VERCEL_USER="authenticated"
fi
log_success "Logged in to Vercel"

if [ ! -f "vercel-build.sh" ]; then
    log_error "vercel-build.sh not found in current directory"
    log_info "Current directory: $(pwd)"
    exit 1
fi
log_success "Build script found"

log_success "Prerequisites verified"
echo ""

# Step 2: Build locally
log_step "Step 2: Building locally..."

set +e  # Temporarily disable exit on error to capture build output
bash vercel-build.sh
BUILD_EXIT=$?
set -e  # Re-enable exit on error

if [ $BUILD_EXIT -ne 0 ]; then
    log_error "Local build failed with exit code $BUILD_EXIT"
    exit 1
fi

if [ ! -d ".vercel/output" ]; then
    log_error "Build output directory not found"
    exit 1
fi

log_success "Local build completed"
echo ""

# Step 3: Deploy to Vercel
log_step "Step 3: Deploying to Vercel..."
log_info "This may take 1-2 minutes..."
echo ""

# Deploy and capture output
DEPLOY_LOG="/tmp/vercel_deploy_$$.log"
if ! vercel --prod --yes > "$DEPLOY_LOG" 2>&1; then
    log_error "Deployment failed"
    echo ""
    log_info "Last 30 lines of deployment output:"
    tail -30 "$DEPLOY_LOG"
    rm -f "$DEPLOY_LOG"
    exit 1
fi

# Extract deployment URL (try multiple methods)
DEPLOY_OUTPUT=$(cat "$DEPLOY_LOG")
DEPLOY_URL=""

# Method 1: Look for production URL pattern
DEPLOY_URL=$(echo "$DEPLOY_OUTPUT" | grep -oE 'https://[a-zA-Z0-9-]+\.vercel\.app' | head -1)

# Method 2: Look for "production" or "deployed" lines
if [ -z "$DEPLOY_URL" ]; then
    DEPLOY_URL=$(echo "$DEPLOY_OUTPUT" | grep -i "production\|deployed\|ready" | grep -oE 'https://[a-zA-Z0-9-]+\.vercel\.app' | head -1)
fi

# Method 3: Get from vercel ls
if [ -z "$DEPLOY_URL" ]; then
    log_info "Trying to get URL from vercel ls..."
    DEPLOY_URL=$(vercel ls --limit 1 2>/dev/null | grep -oE 'https://[a-zA-Z0-9-]+\.vercel\.app' | head -1)
fi

rm -f "$DEPLOY_LOG"

if [ -z "$DEPLOY_URL" ]; then
    log_error "Could not extract deployment URL"
    log_info "Deployment output:"
    echo "$DEPLOY_OUTPUT" | tail -30
    exit 1
fi

log_success "Deployment successful!"
log_info "URL: $DEPLOY_URL"
echo "$DEPLOY_URL" > .last_deployment_url.txt
echo ""

# Step 4: Wait for deployment to be ready and verify build
log_step "Step 4: Verifying deployment..."
sleep 3

# Check build logs from Vercel to see if function initialized correctly
log_info "Checking deployment build logs..."
BUILD_LOG=$(vercel inspect "$DEPLOY_URL" 2>&1 | grep -i "build\|error\|ready" | head -10 || echo "")
if echo "$BUILD_LOG" | grep -qi "error\|fail"; then
    log_warn "Build logs show potential issues"
else
    log_success "Build completed successfully"
fi
echo ""

# Step 5: Test endpoints
log_step "Step 5: Testing endpoints..."
echo ""

TEST_RESULTS=0

# Test 1: Health check (with timeout to avoid hanging)
echo -n "  Testing /health... "
HEALTH_RESPONSE=$(curl -s --max-time 10 -w "\n%{http_code}" "${DEPLOY_URL}/health" 2>/dev/null || echo -e "\n000")
HEALTH_CODE=$(echo "$HEALTH_RESPONSE" | tail -1)
HEALTH_BODY=$(echo "$HEALTH_RESPONSE" | sed '$d')

if [ "$HEALTH_CODE" = "200" ]; then
    log_success "($HEALTH_CODE)"
    echo "    Response: $HEALTH_BODY" | head -c 100
    echo ""
else
    log_error "($HEALTH_CODE)"
    echo "    Response: $(echo "$HEALTH_BODY" | head -c 100)"
    TEST_RESULTS=1
fi

# Test 2: Root endpoint (with timeout)
echo -n "  Testing /... "
ROOT_RESPONSE=$(curl -s --max-time 10 -w "\n%{http_code}" "${DEPLOY_URL}/" 2>/dev/null || echo -e "\n000")
ROOT_CODE=$(echo "$ROOT_RESPONSE" | tail -1)
ROOT_BODY=$(echo "$ROOT_RESPONSE" | sed '$d')

if [ "$ROOT_CODE" = "200" ]; then
    log_success "($ROOT_CODE)"
    echo "    Response: $ROOT_BODY" | head -c 100
    echo ""
else
    log_error "($ROOT_CODE)"
    echo "    Response: $(echo "$ROOT_BODY" | head -c 100)"
    TEST_RESULTS=1
fi

# Test 3: Login endpoint (with timeout)
echo -n "  Testing /api/v1/auth/login... "
LOGIN_RESPONSE=$(curl -s --max-time 15 -w "\n%{http_code}" \
    -X POST \
    -H "Content-Type: application/json" \
    -d '{"email":"john.doe@example.com","password":"SecurePass123!"}' \
    "${DEPLOY_URL}/api/v1/auth/login" 2>/dev/null || echo -e "\n000")
LOGIN_CODE=$(echo "$LOGIN_RESPONSE" | tail -1)
LOGIN_BODY=$(echo "$LOGIN_RESPONSE" | sed '$d')

if [ "$LOGIN_CODE" = "200" ]; then
    log_success "($LOGIN_CODE)"
    TOKEN=$(echo "$LOGIN_BODY" | grep -oE '"access_token"[[:space:]]*:[[:space:]]*"[^"]*"' | cut -d'"' -f4 || echo "")
    if [ -n "$TOKEN" ]; then
        echo "    ✅ Token received: ${TOKEN:0:30}..."
    else
        echo "    Response: $(echo "$LOGIN_BODY" | head -c 100)"
    fi
else
    log_error "($LOGIN_CODE)"
    echo "    Response: $(echo "$LOGIN_BODY" | head -c 200)"
    TEST_RESULTS=1
fi

echo ""

# Summary
echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Deployment Summary                   ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
echo ""
echo "  Deployment URL: $DEPLOY_URL"
echo ""
echo "  Test Results:"
echo "    Health Check: $([ "$HEALTH_CODE" = "200" ] && echo -e "${GREEN}✅${NC}" || echo -e "${RED}❌${NC}")"
echo "    Root Endpoint: $([ "$ROOT_CODE" = "200" ] && echo -e "${GREEN}✅${NC}" || echo -e "${RED}❌${NC}")"
echo "    Login Endpoint: $([ "$LOGIN_CODE" = "200" ] && echo -e "${GREEN}✅${NC}" || echo -e "${RED}❌${NC}")"
echo ""

if [ $TEST_RESULTS -eq 0 ]; then
    log_success "All tests passed! 🎉"
    echo ""
    log_info "You can test the deployment with:"
    echo "  ./test_deploy.sh $DEPLOY_URL"
    echo ""
    exit 0
else
    log_warn "Some tests failed. Check the output above."
    echo ""
    log_info "You can retry tests with:"
    echo "  ./test_deploy.sh $DEPLOY_URL"
    echo ""
    exit 1
fi

