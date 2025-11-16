import { useState } from "react";
import { Navigate, Route, Routes, useNavigate } from "react-router-dom";

import "./App.css";

import Login from "./pages/Login.jsx";
import Profile from "./pages/Profile.jsx";
import Transactions from "./pages/Transactions.jsx";
import Reminders from "./pages/Reminders.jsx";
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
  });

  const authenticate = async ({ userId, password }) => {
    if (!userId || userId.length < 4) {
      return { success: false, message: "Enter a valid User ID." };
    }

    const loginResult = await authenticateUser({ userId, password });
    if (!loginResult.success || !loginResult.profile) {
      return {
        success: false,
        message: loginResult.message || "Invalid user ID or password.",
      };
    }

    if (!loginResult.profile) {
      return {
        success: false,
        message: "Profile data unavailable from API.",
      };
    }

    const persona = {
      ...mockProfile,
      ...loginResult.profile,
    };
    const expiresAt = loginResult.expiresIn
      ? Date.now() + Number(loginResult.expiresIn) * 1000
      : null;
    setSession({
      authenticated: true,
      user: persona,
      accessToken: loginResult.accessToken ?? null,
      expiresAt,
      meta: loginResult.meta ?? null,
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
          session.authenticated ? (
            <Profile
              user={session.user}
              accessToken={session.accessToken}
              onSignOut={signOut}
            />
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
        path="/chat"
        element={
          session.authenticated ? (
            <Chat session={session} onSignOut={signOut} />
          ) : (
            <Navigate to="/" replace />
          )
        }
      />
      <Route path="*" element={<Navigate to={session.authenticated ? "/profile" : "/"} replace />} />
    </Routes>
  );
};

export default App;
