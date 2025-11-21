import { useState } from "react";
import { Navigate, Route, Routes, useNavigate } from "react-router-dom";

import "./App.css";

import Login from "./pages/Login.jsx";
import Profile from "./pages/Profile.jsx";
import Transactions from "./pages/Transactions.jsx";
import Reminders from "./pages/Reminders.jsx";
import DeviceBinding from "./pages/DeviceBinding.jsx";
import SignInHelp from "./pages/SignInHelp.jsx";
import Beneficiaries from "./pages/Beneficiaries.jsx";
import Chat from "./pages/Chat.jsx";
import { authenticateUser } from "./api/client.js";

const mockProfile = {
  fullName: "Ananya Sharma",
  segment: "Priority",
  branch: {
    name: "Sun National Bank",
    city: "Hyderabad",
  },
  accountSummary: [
    {
      accountNumber: "91HYD001123456",
      type: "Savings PLUS",
      balance: "₹2,43,890.55",
      currency: "INR",
    },
    {
      accountNumber: "91HYD001982201",
      type: "Hello! UPI Wallet",
      balance: "₹18,900.00",
      currency: "INR",
    },
  ],
  lastLogin: "14 November 2025 · 07:42 PM via Voice",
  nextReminder: {
    label: "Electricity bill auto-pay",
    date: "Due in 2 days · ₹1,450",
  },
};

const App = () => {
  const navigate = useNavigate();
  const [session, setSession] = useState({
    authenticated: false,
    user: null,
    accessToken: null,
    expiresAt: null,
    meta: null,
    detail: null,
  });

  const authenticate = async ({
    userId,
    password,
    authMode,
    otp,
    deviceIdentifier,
    deviceFingerprint,
    platform,
    deviceLabel,
    voiceSampleBlob,
    validateOnly = false,
  }) => {
    if (!userId || userId.length < 4) {
      return { success: false, message: "Enter a valid User ID." };
    }

    const loginResult = await authenticateUser({
      userId,
      password: authMode === "password" ? password : "",
      deviceIdentifier,
      deviceFingerprint,
      platform,
      deviceLabel,
      registrationMethod: authMode === "voice" ? "otp+voice" : "password",
      voiceSampleBlob,
      loginMode: authMode,
      otp,
      validateOnly,
    });
    
    // Debug logging for voice login
    if (authMode === "voice") {
      console.log("[Voice Login] Authentication result:", {
        success: loginResult.success,
        hasProfile: !!loginResult.profile,
        hasToken: !!loginResult.accessToken,
        tokenLength: loginResult.accessToken ? loginResult.accessToken.length : 0,
        profileKeys: loginResult.profile ? Object.keys(loginResult.profile) : null,
        validateOnly,
      });
    }
    
    if (!loginResult.success || (!validateOnly && !loginResult.profile)) {
      console.error("[Voice Login] Authentication failed:", {
        success: loginResult.success,
        hasProfile: !!loginResult.profile,
        message: loginResult.message,
        authMode,
        validateOnly,
      });
      return {
        success: false,
        message: loginResult.message || "Invalid user ID or password.",
      };
    }

    if (validateOnly) {
      return { success: true };
    }

    if (!loginResult.profile) {
      console.error("[Voice Login] Profile missing in response:", loginResult);
      return {
        success: false,
        message: "Profile data unavailable from API.",
      };
    }

    if (!loginResult.accessToken) {
      console.error("[Voice Login] Access token missing in response:", loginResult);
      return {
        success: false,
        message: "Access token unavailable from API.",
      };
    }

    const persona = {
      ...mockProfile,
      ...loginResult.profile,
    };
    const expiresAt = loginResult.expiresIn
      ? Date.now() + Number(loginResult.expiresIn) * 1000
      : null;
    
    // Set session state FIRST before navigation
    const sessionData = {
      authenticated: true,
      user: persona,
      accessToken: loginResult.accessToken,
      expiresAt,
      meta: loginResult.meta ?? null,
      detail: loginResult.detail ?? null,
    };
    
    console.log("[Voice Login] Setting session state:", {
      authenticated: sessionData.authenticated,
      hasToken: !!sessionData.accessToken,
      tokenLength: sessionData.accessToken ? sessionData.accessToken.length : 0,
      hasUser: !!sessionData.user,
    });
    
    if (authMode === "voice") {
      try {
        window.localStorage.setItem(`voiceEnrolled:${userId}`, "true");
      } catch (storageError) {
        console.warn("Unable to persist voice enrollment flag", storageError);
      }
    }
    
    // Set session state - this will trigger a re-render
    setSession(sessionData);
    
    // Navigate immediately - React Router will use the updated session state
    // The Profile component will receive the updated accessToken prop on the next render
    console.log("[Voice Login] Navigating to profile page with token:", {
      hasToken: !!sessionData.accessToken,
      tokenLength: sessionData.accessToken ? sessionData.accessToken.length : 0,
    });
    navigate("/profile", { replace: true });
    
    return { success: true };
  };

  const signOut = () => {
    setSession({
      authenticated: false,
      user: null,
      accessToken: null,
      expiresAt: null,
      meta: null,
      detail: null,
    });
    navigate("/", { replace: true });
  };

  return (
    <Routes>
      <Route
        path="/"
        element={
          <Login authenticated={session.authenticated} onAuthenticate={authenticate} />
        }
      />
      <Route
        path="/profile"
        element={
          session.authenticated && session.accessToken ? (
            <Profile
              user={session.user}
              accessToken={session.accessToken}
              sessionDetail={session.detail}
              onSignOut={signOut}
            />
          ) : session.authenticated ? (
            // Authenticated but no token yet - wait for token
            <div>Loading...</div>
          ) : (
            <Navigate to="/" replace />
          )
        }
      />
      <Route
        path="/transactions"
        element={
          session.authenticated ? (
            <Transactions session={session} onSignOut={signOut} />
          ) : (
            <Navigate to="/" replace />
          )
        }
      />
      <Route
        path="/reminders"
        element={
          session.authenticated ? (
            <Reminders session={session} onSignOut={signOut} />
          ) : (
            <Navigate to="/" replace />
          )
        }
      />
      <Route
        path="/beneficiaries"
        element={
          session.authenticated ? (
            <Beneficiaries session={session} onSignOut={signOut} />
          ) : (
            <Navigate to="/" replace />
          )
        }
      />
      <Route
        path="/chat"
        element={
          session.authenticated ? (
            <Chat session={session} onSignOut={signOut} />
          ) : (
            <Navigate to="/" replace />
          )
        }
      />
      <Route
        path="/device-binding"
        element={
          session.authenticated ? (
            <DeviceBinding session={session} onSignOut={signOut} />
          ) : (
            <Navigate to="/" replace />
          )
        }
      />
      <Route
        path="/sign-in-help"
        element={<SignInHelp onBack={() => navigate(-1)} />}
      />
      <Route path="*" element={<Navigate to={session.authenticated ? "/profile" : "/"} replace />} />
    </Routes>
  );
};

export default App;
