# Frontend Architecture Documentation

This document outlines the architecture of the React-based frontend for the Vaani Banking Voice Assistant. The application is designed with a clear separation of concerns between routing, page logic, state management (hooks), UI presentation, and API services.

## High-Level Overview

The frontend is a Single Page Application (SPA) built with **React** and **Vite**. It serves as the primary interface for users to interact with the banking assistant via text or voice.

### Key Architectural Layers

1.  **Page Layer**: Top-level route components.
2.  **Chat Module**: The core feature, handling the conversational interface.
3.  **Hooks Layer**: Custom React hooks encapsulating business logic and state.
4.  **Component Layer**: Reusable UI elements and specialized "Cards" for structured data.
5.  **Service Layer**: API communication wrappers.

---

## 1. Chat Module Architecture

The `Chat.jsx` page is the heart of the application. It orchestrates several subsystems to provide a seamless voice and text experience.

### Core Components

*   **Chat.jsx**: The container component. It initializes the chat state and layout.
*   **ChatSidebar.jsx**: Displays conversation history or navigation options.
*   **ChatInput.jsx**: Handles user input (text typing) and contains the microphone trigger.
*   **ChatMessage.jsx**: A smart component that renders different content based on the message type (text, structured data, interactive flows).

### Interactive Cards (Structured Responses)

Instead of just displaying text, the assistant returns structured data which the frontend renders as interactive "Cards". This allows for rich UI elements within the chat stream.

*   **AccountBalanceCards**: Displays account details in a carousel or grid.
*   **TransferFlow**: A multi-step wizard for fund transfers embedded in the chat.
*   **UPIPaymentFlow**: Specialized UI for UPI transactions (PIN entry, confirmation).
*   **TransactionTable**: Tabular view of recent transactions.

---

## 2. State Management & Logic (Hooks)

We use **Custom Hooks** to separate logic from UI rendering. This makes the components cleaner and the logic testable.

### `useChatHandler`
*   **Responsibility**: Manages the overall chat session.
*   **Actions**: Handles sending messages, receiving responses, and updating the message list.
*   **Integration**: Connects `chatService` with the UI state.

### `useVoiceMode`
*   **Responsibility**: Manages the "Voice Mode" state (Active/Inactive).
*   **Integration**: Orchestrates `useSpeechRecognition` and `useTextToSpeech`.
*   **Logic**: Automatically triggers listening after speaking (turn-taking) if voice mode is active.

### `useSpeechRecognition` & `useTextToSpeech`
*   **Responsibility**: Wrappers around the browser's native **Web Speech API**.
*   **Features**: Handles browser compatibility, permission errors, and event callbacks (onStart, onEnd).

---

## 3. Service Layer

The service layer handles all HTTP communication with the Python backend.

*   **client.js**: The base Axios instance with default configuration (base URL, headers, interceptors for auth).
*   **aiClient.js**: Specialized methods for AI endpoints (sending prompts, handling streams if applicable).
*   **chatService.js**: High-level business methods used by the UI (e.g., `sendMessage`, `getHistory`).

---

## 4. Data Flow Example: "Check Balance"

1.  **User Action**: User clicks the microphone in `ChatInput` and says "Check my balance".
2.  **Voice Layer**: `useSpeechRecognition` captures audio, converts to text, and passes it to `useChatHandler`.
3.  **Logic Layer**: `useChatHandler` calls `chatService.sendMessage("Check my balance")`.
4.  **Service Layer**: `chatService` POSTs to the backend.
5.  **Backend Processing**: (AI Agent processes request).
6.  **Response**: Backend returns a JSON payload with `type: "balance_inquiry"` and account data.
7.  **Rendering**:
    *   `useChatHandler` updates the message list state.
    *   `ChatMessage` sees the `type` is `balance_inquiry`.
    *   It dynamically imports and renders `<AccountBalanceCards data={...} />`.
8.  **TTS**: If Voice Mode is on, `useTextToSpeech` reads the accompanying text response aloud.

---

## Directory Structure Mapping

| Directory | Role | Key Files |
| :--- | :--- | :--- |
| `src/pages` | Route destinations | `Chat.jsx`, `Login.jsx` |
| `src/components/Chat` | Chat-specific UI | `ChatInput.jsx`, `ChatMessage.jsx` |
| `src/hooks` | Logic & State | `useChatHandler.js`, `useVoiceMode.js` |
| `src/services` | API Calls | `chatService.js`, `client.js` |
| `src/api` | Low-level HTTP | `client.js` |
