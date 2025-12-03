# Dokku AI Proxy Setup

This document explains how to keep the Dokku nginx include that proxies `/api/chat` to the `backend.ai` container up-to-date. The AI process runs in a separate container (port `8001`) and its container IP changes after each deploy; we regenerate an nginx include and restart the app after deploys.

Prerequisites (on Dokku host):
- `docker` and `dokku` commands available
- `sudo` privileges to write `/home/dokku/<app>/nginx.conf.d`

Files created by the automation:
- `/home/dokku/backend/nginx.conf.d/ai-proxy.conf` — nginx include with `location /api/chat` and `location /api/chat/stream` forwarding to the AI container.
- `/home/dokku/backend/postdeploy.d/99_update_ai_proxy` — Dokku postdeploy hook that regenerates the include after deploys.

Repository artifacts (added):
- `scripts/update_ai_proxy.sh` — helper that detects the `backend.ai` container IP and writes `ai-proxy.conf`. Run this on the Dokku host to regenerate the include manually.

How it works:
1. `scripts/update_ai_proxy.sh` discovers the running `backend.ai` container with `docker ps --filter "name=backend.ai"` and extracts its container IP via `docker inspect`.
2. It writes `/home/dokku/backend/nginx.conf.d/ai-proxy.conf` with `proxy_pass http://<AI_IP>:8001` for `/api/chat` and `/api/chat/stream`.
3. The script also creates `/home/dokku/backend/postdeploy.d/99_update_ai_proxy` which runs on Dokku after each deploy to re-generate the include and restart the app.

Manual steps (if you prefer to run manually):
1. Copy `scripts/update_ai_proxy.sh` to the Dokku host (e.g. via `scp`).
2. On the Dokku host, run:

```bash
sudo bash update_ai_proxy.sh backend
```

This will write `/home/dokku/backend/nginx.conf.d/ai-proxy.conf` and restart the Dokku app.

Post-deploy hook notes:
- Dokku executes `postdeploy.d` scripts after deployment. The script created by `update_ai_proxy.sh` regenerates the include and restarts the app so the new ai container IP is used.
- If you have a CI pipeline, ensure the Dokku deploy user has permission to execute the hook or run the update script as a final step.

Troubleshooting:
- If `/api/chat` still returns `404` externally but works when curling the AI container directly, check that the `ai-proxy.conf` exists and contains the correct `proxy_pass` IP and port.
- Confirm docker container name via `docker ps | grep backend.ai`.
- Check Dokku logs: `dokku logs backend` and system nginx config.

Security considerations:
- The include proxies only the `/api/chat` and `/api/chat/stream` paths. If additional endpoints need exposure, add them explicitly.
- Limiting access to the AI endpoints via authentication or firewall rules is recommended if they should not be public.

Alternatives:
- Expose the `ai` process directly as the web process (change `Procfile`) so Dokku's upstream points at the AI container — this can simplify routing but may impact other web endpoints.
- Use a stable service discovery mechanism (e.g., docker labels + reverse proxy) that avoids IP-based includes.

If you want, I can also:
- Add a small systemd unit to run the update script periodically, or
- Modify the `postdeploy.d` hook to use `dokku ps:report` or other Dokku APIs for discovery.
