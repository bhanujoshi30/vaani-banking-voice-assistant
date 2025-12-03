import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router-dom";

import "./index.css";
import App from "./App.jsx";

// iOS Native Bridge Setup
// Detect if running inside native iOS app (WKWebView)
const isNativeIOS = window.webkit?.messageHandlers?.nativeHandler !== undefined;

if (isNativeIOS) {
  console.log('📱 Native iOS bridge detected - setting up communication');
  
  // Notify native app that React is ready
  window.webkit.messageHandlers.nativeHandler.postMessage({
    type: 'ready',
    timestamp: new Date().toISOString()
  });
  
  // Expose function for native app to send messages
  window.sendAutoMessage = (message) => {
    console.log('📱 Received auto-send message from native app:', message);
    
    // Dispatch custom event that Chat component will listen to
    const event = new CustomEvent('nativeAutoSend', { 
      detail: { 
        message,
        timestamp: new Date().toISOString()
      } 
    });
    window.dispatchEvent(event);
  };
  
  console.log('✅ iOS bridge initialized - window.sendAutoMessage available');
} else {
  console.log('🌐 Running in web browser (not native iOS app)');
}

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </StrictMode>,
);
