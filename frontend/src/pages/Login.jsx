import { useState } from "react";
import PropTypes from "prop-types";
import { Navigate } from "react-router-dom";

import SunHeader from "../components/SunHeader.jsx";

const Login = ({ onAuthenticate, authenticated }) => {
  const [userId, setUserId] = useState("");
  const [password, setPassword] = useState("");
  const [rememberDevice, setRememberDevice] = useState(true);
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (authenticated) {
    return <Navigate to="/profile" replace />;
  }

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError("");

    if (!userId.trim() || !password.trim()) {
      setError("Please enter both User ID and Password to continue.");
      return;
    }

    setIsSubmitting(true);

    try {
      const result = await onAuthenticate({
        userId: userId.trim(),
        password: password.trim(),
        rememberDevice,
      });

      if (!result?.success) {
        setError(result?.message || "We could not verify those credentials. Try again.");
      }
    } catch (authError) {
      setError(
        authError?.message ||
          "Something went wrong while contacting the bank. Please try again.",
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="app-shell">
      <div className="app-content">
        <div className="app-gradient">
          <SunHeader subtitle="Voice-first banking, made human." />
          <main className="card-surface">
            <div className="card-hero">
              <h1>Welcome back.</h1>
              <p>Sign in to continue to your Sun National Bank profile.</p>
            </div>
            <form className="card-form" onSubmit={handleSubmit} noValidate>
              <label htmlFor="userId">
                User ID
                <input
                  id="userId"
                  name="userId"
                  type="text"
                  autoComplete="username"
                  placeholder="Enter your customer ID"
                  value={userId}
                  onChange={(event) => setUserId(event.target.value)}
                />
              </label>
              <label htmlFor="password">
                Password
                <input
                  id="password"
                  name="password"
                  type="password"
                  autoComplete="current-password"
                  placeholder="Enter your password"
                  value={password}
                  onChange={(event) => setPassword(event.target.value)}
                />
              </label>
              <div className="card-form__meta">
                <label className="checkbox">
                  <input
                    type="checkbox"
                    checked={rememberDevice}
                    onChange={(event) => setRememberDevice(event.target.checked)}
                  />
                  Trust this device for quick voice authentication
                </label>
                <a className="muted-link" href="#help">
                  Need help signing in?
                </a>
              </div>
              {error && <div className="form-error">{error}</div>}
              <button className="primary-btn" type="submit" disabled={isSubmitting}>
                {isSubmitting ? "Verifying…" : "Log in"}
              </button>
            </form>
            <div className="card-footer">
              <p>
                Prefer the conversation experience?{" "}
                <a href="#voice">Use voice + device binding</a>
              </p>
            </div>
          </main>
        </div>
      </div>
      <footer className="app-footer">
        © {new Date().getFullYear()} Sun National Bank · RBI compliant · Made for Bharat
      </footer>
    </div>
  );
};

Login.propTypes = {
  onAuthenticate: PropTypes.func.isRequired,
  authenticated: PropTypes.bool,
};

Login.defaultProps = {
  authenticated: false,
};

export default Login;


