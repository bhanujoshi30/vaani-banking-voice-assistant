import PropTypes from "prop-types";
import { Link } from "react-router-dom";

import SunHeader from "../components/SunHeader.jsx";
import LanguageDropdown from "../components/LanguageDropdown.jsx";
import { usePageLanguage } from "../hooks/usePageLanguage.js";

const SignInHelp = ({ onBack }) => {
  const { strings } = usePageLanguage();
  const s = strings.signInHelp;

  return (
  <div className="app-shell">
    <div className="app-content">
      <div className="app-gradient">
        <SunHeader 
          subtitle="Voice-first banking, made human."
          actionSlot={<LanguageDropdown />}
        />
        <main className="card-surface">
          <div className="card-hero">
            <h1>{s.title}</h1>
            <p>{s.subtitle}</p>
          </div>

          <section className="help-section">
            <h2>{s.passwordOtp}</h2>
            <ol>
              <li>{s.step1}</li>
              <li>{s.step2} <strong>{s.logIn}</strong>.</li>
              <li>{s.step3}</li>
              <li>
                {s.step4} <strong>12345</strong> {s.step4Note}
              </li>
              <li>{s.step5}</li>
            </ol>
          </section>

          <section className="help-section">
            <h2>{s.voiceLoginOtp}</h2>
            <ol>
              <li>{s.voiceStep1} <strong>{s.voiceStep1Bold}</strong> {s.voiceStep1End}</li>
              <li>{s.voiceStep2}</li>
              <li>{s.voiceStep3}</li>
              <li>
                {s.voiceStep4} <strong>12345</strong> {s.voiceStep4End}
              </li>
            </ol>
            <p className="help-note">
              {s.voiceTip}
            </p>
          </section>

          <section className="help-section">
            <h2>{s.stillCantSignIn}</h2>
            <ul>
              <li>{s.usePasswordMode}</li>
              <li>{s.clearBrowserCache}</li>
              <li>{s.enableMicrophone}</li>
              <li>{s.contactSupport}</li>
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
              {s.goBack}
            </button>
            <Link to="/" className="link-btn">
              {s.returnToLogin}
            </Link>
          </div>
        </main>
      </div>
    </div>
  </div>
  );
};

SignInHelp.propTypes = {
  onBack: PropTypes.func,
};

SignInHelp.defaultProps = {
  onBack: undefined,
};

export default SignInHelp;


