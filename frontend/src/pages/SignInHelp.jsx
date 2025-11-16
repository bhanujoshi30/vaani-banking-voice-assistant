import PropTypes from "prop-types";
import { Link } from "react-router-dom";

import SunHeader from "../components/SunHeader.jsx";

const SignInHelp = ({ onBack }) => (
  <div className="app-shell">
    <div className="app-content">
      <div className="app-gradient">
        <SunHeader subtitle="Voice-first banking, made human." />
        <main className="card-surface">
          <div className="card-hero">
            <h1>Need help signing in?</h1>
            <p>
              Follow these quick steps to access your Sun National Bank profile using either your
              password or voice with the audio OTP safeguard.
            </p>
          </div>

          <section className="help-section">
            <h2>Password + OTP</h2>
            <ol>
              <li>Enter your customer User ID exactly as issued by the bank.</li>
              <li>Type your password and press <strong>Log in</strong>.</li>
              <li>
                The system validates your credentials and then prompts for the one-time password.
              </li>
              <li>
                Enter the prototype OTP <strong>12345</strong> (production will use SMS/email/WhatsApp).
              </li>
              <li>Submit to finish signing in. Incorrect entries reset the OTP step for security.</li>
            </ol>
          </section>

          <section className="help-section">
            <h2>Voice login + OTP</h2>
            <ol>
              <li>Select the <strong>Voice</strong> tab on the login screen.</li>
              <li>
                For first-time users, record the passphrase “Sun Bank mera saathi, har kadam surakshit
                banking ka vaada” twice to enrol your voice signature.
              </li>
              <li>
                Returning users can speak any clear phrase. Watch the audio meter to stay within the
                7-second capture window.
              </li>
              <li>
                After the voice check passes, enter the OTP <strong>12345</strong> to complete login.
              </li>
            </ol>
            <p className="help-note">
              Tip: Record from a quiet space and keep the microphone 10–15&nbsp;cm away for best
              matching accuracy.
            </p>
          </section>

          <section className="help-section">
            <h2>Still can’t sign in?</h2>
            <ul>
              <li>Use the password mode if your voice sample is unavailable.</li>
              <li>Clear your browser cache or retry in a private window to refresh device bindings.</li>
              <li>Ensure your microphone permissions are enabled for this site.</li>
              <li>Contact branch support to reset your password or revoke suspicious device bindings.</li>
            </ul>
          </section>

          <div className="card-form__actions help-actions">
            <button
              type="button"
              className="secondary-btn"
              onClick={() => {
                if (onBack) onBack();
              }}
            >
              Go back
            </button>
            <Link to="/" className="link-btn">
              Return to login
            </Link>
          </div>
        </main>
      </div>
    </div>
  </div>
);

SignInHelp.propTypes = {
  onBack: PropTypes.func,
};

SignInHelp.defaultProps = {
  onBack: undefined,
};

export default SignInHelp;


