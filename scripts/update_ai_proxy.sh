#!/usr/bin/env bash
set -euo pipefail

# update_ai_proxy.sh
# Detect current backend.ai Docker container IP and write Dokku nginx include.
# Also fixes the main nginx.conf to ensure the include is loaded in the correct order.
# Intended to run on the Dokku host (requires sudo/root privileges).

APP_NAME=${1:-backend}
MAIN_NGINX_CONF="/home/dokku/${APP_NAME}/nginx.conf"
NGINX_CONF_DIR="/home/dokku/${APP_NAME}/nginx.conf.d"
POSTDEPLOY_DIR="/home/dokku/${APP_NAME}/postdeploy.d"
PROXY_CONF_FILE="${NGINX_CONF_DIR}/ai-proxy.conf"
POSTDEPLOY_HOOK="${POSTDEPLOY_DIR}/99_update_ai_proxy"

echo "[update_ai_proxy] app=${APP_NAME}"

# Find the AI container for this app
AI_ID=$(docker ps --filter "name=${APP_NAME}.ai" --format '{{.ID}}' | head -n1)
if [ -z "${AI_ID}" ]; then
  echo "[update_ai_proxy] No running container found for ${APP_NAME}.ai"
  exit 1
fi

AI_IP=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' "${AI_ID}")
if [ -z "${AI_IP}" ]; then
  echo "[update_ai_proxy] Could not determine IP for container ${AI_ID}"
  exit 1
fi

echo "[update_ai_proxy] AI container=${AI_ID} IP=${AI_IP}"

# 1. Create the AI proxy include file
sudo mkdir -p "${NGINX_CONF_DIR}"
sudo tee "${PROXY_CONF_FILE}" > /dev/null <<NGINX
# filepath: ${PROXY_CONF_FILE}
location ^~ /api/chat {
    proxy_pass http://${AI_IP}:8001;
    proxy_set_header Host \$host;
    proxy_set_header X-Real-IP \$remote_addr;
    proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto \$scheme;
    proxy_http_version 1.1;
    proxy_set_header Connection "";
    proxy_read_timeout 300s;
    proxy_send_timeout 300s;
    proxy_connect_timeout 60s;
    proxy_buffering off;
}

location ^~ /api/chat/stream {
    proxy_pass http://${AI_IP}:8001;
    proxy_set_header Host \$host;
    proxy_set_header X-Real-IP \$remote_addr;
    proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto \$scheme;
    proxy_http_version 1.1;
    proxy_set_header Connection "keep-alive";
    proxy_read_timeout 3600s;
    proxy_send_timeout 3600s;
    proxy_connect_timeout 60s;
    proxy_buffering off;
}
NGINX

sudo chmod 644 "${PROXY_CONF_FILE}"
echo "[update_ai_proxy] wrote ${PROXY_CONF_FILE}"


# 2. Fix the main nginx.conf to ensure includes are loaded before the generic location block
INCLUDE_LINE="include /home/dokku/${APP_NAME}/nginx.conf.d/*.conf;"
ANCHOR_LINE="underscores_in_headers off;"

# Check if the include line already exists after the anchor
if ! sudo grep -A 1 "${ANCHOR_LINE}" "${MAIN_NGINX_CONF}" | grep -q "${INCLUDE_LINE}"; then
    echo "[update_ai_proxy] Correcting include order in ${MAIN_NGINX_CONF}"
    # Use a temp file for safety
    TMP_CONF=$(mktemp)
    sudo cp "${MAIN_NGINX_CONF}" "${TMP_CONF}"

    # Remove any existing include lines to avoid duplicates
    sudo sed -i '/include \/home\/dokku\/${APP_NAME}\/nginx.conf.d\/\*.conf;/d' "${TMP_CONF}"
    # Add the include line after the anchor
    sudo sed -i "/${ANCHOR_LINE}/a ${INCLUDE_LINE}" "${TMP_CONF}"
    
    # Overwrite the original with the fixed version
    sudo cp "${TMP_CONF}" "${MAIN_NGINX_CONF}"
    rm "${TMP_CONF}"
    echo "[update_ai_proxy] Nginx include order corrected"
else
    echo "[update_ai_proxy] Nginx include order is already correct"
fi


# 3. Create a postdeploy hook on Dokku host to regenerate after deploy
# This hook will contain the same logic to fix the main nginx file as well.
sudo mkdir -p "${POSTDEPLOY_DIR}"
sudo tee "${POSTDEPLOY_HOOK}" > /dev/null <<'HOOK'
#!/usr/bin/env bash
set -euo pipefail
# Regenerate ai-proxy.conf for the app and fix main nginx.conf (dokku host)
APP_NAME="backend"
MAIN_NGINX_CONF="/home/dokku/${APP_NAME}/nginx.conf"
NGINX_CONF_DIR="/home/dokku/${APP_NAME}/nginx.conf.d"
PROXY_CONF_FILE="${NGINX_CONF_DIR}/ai-proxy.conf"

# Update AI proxy IP
AI_ID=$(docker ps --filter "name=${APP_NAME}.ai" --format '{{.ID}}' | head -n1)
if [ -n "${AI_ID}" ]; then
    AI_IP=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' "${AI_ID}")
    mkdir -p "${NGINX_CONF_DIR}"
    cat > "${PROXY_CONF_FILE}" <<NGINX
location ^~ /api/chat {
    proxy_pass http://${AI_IP}:8001;
    proxy_set_header Host \$host;
    proxy_set_header X-Real-IP \$remote_addr;
    proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto \$scheme;
    proxy_http_version 1.1;
    proxy_set_header Connection "";
}
location ^~ /api/chat/stream {
    proxy_pass http://${AI_IP}:8001;
    proxy_set_header Host \$host;
    proxy_set_header X-Real-IP \$remote_addr;
    proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto \$scheme;
    proxy_http_version 1.1;
    proxy_set_header Connection "keep-alive";
}
NGINX
    chmod 644 "${PROXY_CONF_FILE}"
fi

# Fix main nginx.conf include order
INCLUDE_LINE="include /home/dokku/${APP_NAME}/nginx.conf.d/*.conf;"
ANCHOR_LINE="underscores_in_headers off;"
if ! grep -A 1 "${ANCHOR_LINE}" "${MAIN_NGINX_CONF}" | grep -q "${INCLUDE_LINE}"; then
    TMP_CONF=$(mktemp)
    cp "${MAIN_NGINX_CONF}" "${TMP_CONF}"
    sed -i '/include \/home\/dokku\/${APP_NAME}\/nginx.conf.d\/\*.conf;/d' "${TMP_CONF}"
    sed -i "/${ANCHOR_LINE}/a ${INCLUDE_LINE}" "${TMP_CONF}"
    cp "${TMP_CONF}" "${MAIN_NGINX_CONF}"
    rm "${TMP_CONF}"
fi

dokku ps:restart ${APP_NAME}
HOOK

sudo chmod +x "${POSTDEPLOY_HOOK}"
echo "[update_ai_proxy] created postdeploy hook ${POSTDEPLOY_HOOK}"

# 4. Restart the app to apply all changes
echo "[update_ai_proxy] restarting dokku app ${APP_NAME} to apply changes"
sudo dokku ps:restart "${APP_NAME}" || true
echo "[update_ai_proxy] done"