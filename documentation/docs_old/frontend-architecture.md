# Vaani Frontend Module Architecture

This document describes how the `frontend/` React + Vite application is structured, how data moves between routes, hooks, and API clients, and how the UI collaborates with the backend (FastAPI) and AI (hybrid supervisor) services.

> Diagram source: `documentation/frontend-architecture.mmd`

---

## 1. Purpose and scope

The frontend module is the user-facing surface for Sun National Bank. It delivers:

- **Auth experiences** – password/OTP login plus voice enrollment, OTP verification, and device binding.
- **Banking dashboards** – account cards, transfers, reminders, beneficiaries, and statement tools.
- **Conversational/voice UX** – chat workspace with speech recognition, text-to-speech, QR uploads, and UPI flows.
- **Localization** – runtime language switching (English/Hindi today, more languages staged via `voiceConfig.js`).

Everything is bundled with Vite, rendered through React Router, and talks to two HTTP surfaces:

1. `VITE_API_BASE_URL` (default `http://localhost:8000`) → traditional banking APIs.
2. `VITE_AI_BACKEND_URL` (default `http://localhost:8001`) → AI chat/tts endpoints.

---

## 2. App shell and routing

| Layer | Implementation | Responsibilities |
| --- | --- | --- |
| Entry point | `src/main.jsx` | Mounts `BrowserRouter` and renders `<App />` inside React Strict Mode. |
| Shell | `src/App.jsx` | Owns `session` state (auth token, profile, expiry) and exposes `authenticate()` / `signOut()`. Performs guarded routing (redirects to `/` if unauthenticated, prevents `/profile` without token). |
| Router | `Routes` + `Route` in `App.jsx` | Maps canonical paths to pages: `/`, `/profile`, `/transactions`, `/reminders`, `/beneficiaries`, `/device-binding`, `/chat`, `/sign-in-help`, catch-all redirect. |

The shell centralizes navigation side-effects (e.g., after login it sets session state and calls `navigate("/profile")`), so individual pages stay focused on UI + data fetching.

---

## 3. Page surfaces

### 3.1 Login & Device Binding (`src/pages/Login.jsx`, `DeviceBinding.jsx`)
- Implements dual-mode authentication (password or voice) with OTP gating.
- Handles client-side voice capture, waveform visualization, and WAV encoding before sending the sample to `/api/v1/auth/login`.
- Tracks OTP state, handles `validateOnly` pre-checks, and stores `voiceEnrolled:<userId>` flags in `localStorage`.
- Device Binding page consumes `listDeviceBindings`, `registerDeviceBinding`, and `revokeDeviceBinding` to manage trusted devices and voice signatures.

### 3.2 Profile dashboard (`src/pages/Profile.jsx`)
- Acts as the console for balances, transfers, transactions, reminders, beneficiaries, and device bindings.
- Drives collapsible panels (`PANEL_KEYS`) and defers data fetching to `api/client.js` helpers (balances, reminders, beneficiaries, transfers, statements).
- Maintains derived state (account cards, memoized options, panel toggles) and handles session expiry codes uniformly (logging users out when backend returns `session_timeout` or similar).

### 3.3 Chat and UPI workspace (`src/pages/Chat.jsx`)
- Combines conversational UI with multimodal inputs:
  - `useSpeechRecognition` for speech-to-text.
  - `useTextToSpeech` for assistant narration.
  - `useChatHandler`, `useChatMessages`, `useVoiceMode` for message lifecycle and automatic sending.
  - UPI consent, PIN, and QR upload flows via `UPIConsentModal`, `UPIPinModal`, QR reader (jsQR fallback to backend `/api/qr-code/process`).
- Coordinates `upiMode` state with backend responses (`structured_data.type === 'upi_mode_activation'`) and persists consent per session.
- Calls both API surfaces: banking (`listDeviceBindings`, `/api/v1/upi/verify-pin`) and AI chat (`api/aiClient.js`).

### 3.4 Auxiliary pages
- `Transactions.jsx`, `Reminders.jsx`, `Beneficiaries.jsx` reuse the same API helpers but expose simplified, read-only summaries.
- `SignInHelp.jsx` provides static guidance and links to device binding/voice enrollment instructions.

---

## 4. Shared components

| Component | Purpose |
| --- | --- |
| `SunHeader` | Top-of-screen hero with subtitle + action slot (language picker, logout, breadcrumbs). |
| `LanguageDropdown`, `LanguageToggle`, `LanguagePreferenceModal` | Controls language settings and dispatches `languageChanged` events so pages stay in sync. |
| `VoiceEnrollmentModal`, `UPIConsentModal`, `UPIPinModal`, `ForceLogoutModal` | Reusable overlay modals for security-critical flows. |
| `Chat/*` components (message bubbles, sidebar, typing indicators, voice toggles) | Render assistant/user messages, quick actions, and structured cards produced by the AI backend. |

Components intentionally stay dumb—they render props while hooks own side-effects.

---

## 5. Hooks and voice stack

- **`useSpeechRecognition`**: Wraps the Web Speech API with guardrails (30s max duration, 5s inactivity auto-stop, manual stop tracking). Centralizes browser capability checks per language.
- **`useTextToSpeech`**: Manages Web Speech synthesis voices, play/stop controls, and exposes `speak()` for assistant answers.
- **`useChatMessages`**: Maintains the chat log (`messages`, `addUserMessage`, `addAssistantMessage`) and handles structured card cleanup.
- **`useChatHandler`**: Orchestrates message sending (stop listening if needed, call AI backend via `services/chatService`, gate UPI flows until consent). Accepts the current `upiMode` and `session` so API calls stay deterministic.
- **`useVoiceMode`**: Higher-level state machine that coordinates speech recognition, text-to-speech, and auto-send rules while voice mode is active.
- **`usePageLanguage`**: Observes `languageChanged` events, returns localized copy (`config/pageStrings.js`), and informs modals/pages.

Together, these hooks decouple device APIs from UI components, making it easy to add new pages that reuse speech or chat behaviors.

---

## 6. Client services and API clients

| Module | Description |
| --- | --- |
| `api/client.js` | Thin REST wrapper over the backend FastAPI routes: login, accounts, reminders, beneficiaries, transfers, statements, device bindings, QR processing. Handles `FormData` payloads for voice samples and file uploads, extracts structured errors, and always returns `{ data, meta }` or throws `Error` with `code`. |
| `api/aiClient.js` | Targets the AI FastAPI surface. Provides `sendChatMessage`, `streamChatMessage` (SSE), `getTextToSpeech`, `checkHealth`, and `playAudioBlob`. Keeps message payload and language handling consistent with the AI supervisor. |
| `services/chatService.js` | Convenience service that formats message history, builds user context, calls `api/aiClient.sendChatMessage`, and falls back to `simulateAIResponse()` if AI is offline. |
| `utils/preferences.js`, `config/voiceConfig.js`, `config/chatCopy.js`, `config/loginStrings.js`, `config/upiStrings.js` | Centralize localization, supported languages, prompt copy, and persistent user preferences.

All outbound calls go through these modules, keeping components testable and preventing duplicated HTTP logic.

---

## 7. Data and control flow (see diagram)

1. The **customer** interacts with the UI via touch, keyboard, or voice.
2. `main.jsx` mounts the app; `App.jsx` loads routing and session guards.
3. Pages (Login/Profile/Chat/etc.) render via React Router and rely on shared components for headers, modals, and cards.
4. Pages call hooks for complex behaviors (voice recording, chat orchestration, TTS, quick actions).
5. Hooks dispatch actions through `services/chatService.js` or `api/client.js`:
   - Banking/UPI REST calls → `backend/` FastAPI service on port 8000.
   - Conversational/TTS calls → AI FastAPI (`ai/` module) on port 8001.
6. Responses propagate back through services → hooks → components → DOM, ensuring structured data (cards, statements, PIN prompts) render consistently.

---

## 8. Voice & UPI safeguards

- **Consent gating**: `useChatHandler` and `Chat.jsx` coordinate `upiConsentGiven` so UPI cards/pin prompts never render until the user accepts `UPIConsentModal` (per RBI guidelines).
- **Voice enrollment checks**: `Chat.jsx` and `Profile.jsx` call `listDeviceBindings` to verify an active voice signature before enabling hands-free or UPI operations.
- **QR uploads**: Client attempts local decoding via `jsQR`; on failure it proxies the image to `/api/qr-code/process`. All flows sanitize UPI IDs and amounts before showing the PIN modal.

---

## 9. Extending the frontend

1. **Add a page** – create a component under `src/pages/`, import it in `App.jsx`, and add a `<Route>`. Reuse hooks and API helpers instead of new fetch logic.
2. **Add API calls** – extend `api/client.js` or `api/aiClient.js`, then call them from services/hooks so error handling stays centralized.
3. **Add languages** – update `config/voiceConfig.js`, `config/*Strings.js`, and ensure `LanguageDropdown` surfaces the new entry. Hooks automatically react to `languageChanged` events.
4. **New chat cards** – make the AI module emit `structured_data.type`, then add a renderer under `components/Chat` to visualize it. The frontend already passes `structuredData` down to `ChatMessage`.
5. **Testing** – component-level logic can be unit-tested by mocking hooks/services; integration tests can hit the FastAPI+AI pair via `run_services.py`.

---

## 10. Interaction with other modules

- **Backend**: All banking data and auth tokens originate from `backend/` FastAPI. The frontend never touches SQLite directly; it depends entirely on REST endpoints.
- **AI module**: Chat, UPI flow automation, language generation, and TTS all depend on the AI FastAPI service. Frontend toggles `upiMode` and voice settings, while the AI returns structured cards that the frontend renders.
- **Docs & tooling**: Use this document plus `frontend-architecture.mmd` when onboarding engineers, recording architectural decisions, or planning new features so changes stay consistent with the existing flows.
