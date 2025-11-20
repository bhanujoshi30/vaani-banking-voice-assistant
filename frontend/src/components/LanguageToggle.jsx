import { useState, useEffect } from "react";
import PropTypes from "prop-types";
import { getLoginStrings } from "../config/loginStrings.js";
import { getPreferredLanguage, setPreferredLanguage } from "../utils/preferences.js";

const SUPPORTED_LANGUAGES = ["en-IN", "hi-IN"];

/**
 * LanguageToggle Component
 * A reusable language toggle button that switches between Hindi and English
 * Similar to the one used on the login page
 * 
 * @param {boolean} disabled - Whether the toggle is disabled
 * @param {string} className - Optional CSS class name
 * @param {function} onToggle - Optional callback function that overrides default toggle behavior
 */
const LanguageToggle = ({ disabled, className, onToggle }) => {
  const [currentLanguage, setCurrentLanguage] = useState(() => {
    const preferred = getPreferredLanguage();
    return SUPPORTED_LANGUAGES.includes(preferred) ? preferred : "en-IN";
  });

  // Get localized strings for current language
  const strings = getLoginStrings(currentLanguage);

  // Toggle language between Hindi and English
  const toggleLanguage = () => {
    const newLanguage = currentLanguage === "en-IN" ? "hi-IN" : "en-IN";
    
    // If custom onToggle handler is provided, use it instead
    if (onToggle) {
      onToggle(newLanguage);
      return;
    }
    
    // Default behavior: update state and localStorage
    setCurrentLanguage(newLanguage);
    setPreferredLanguage(newLanguage);
    // Dispatch custom event to notify other components
    window.dispatchEvent(new CustomEvent("languageChanged", { detail: { language: newLanguage } }));
  };

  // Sync with localStorage changes (if changed elsewhere, e.g., from other tabs or components)
  useEffect(() => {
    const handleStorageChange = () => {
      const preferred = getPreferredLanguage();
      if (SUPPORTED_LANGUAGES.includes(preferred) && preferred !== currentLanguage) {
        setCurrentLanguage(preferred);
      }
    };

    const handleLanguageChange = (event) => {
      const { language } = event.detail;
      if (SUPPORTED_LANGUAGES.includes(language) && language !== currentLanguage) {
        setCurrentLanguage(language);
      }
    };

    // Listen for storage changes (e.g., from other tabs)
    window.addEventListener("storage", handleStorageChange);
    // Listen for custom language change events (from same tab)
    window.addEventListener("languageChanged", handleLanguageChange);
    return () => {
      window.removeEventListener("storage", handleStorageChange);
      window.removeEventListener("languageChanged", handleLanguageChange);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className={className || "login-language-toggle"}>
      <button
        type="button"
        className="language-toggle-btn"
        onClick={toggleLanguage}
        disabled={disabled}
        aria-label={strings.languageToggle.ariaLabel}
      >
        <span className="language-toggle-btn__flag">
          🇮🇳
        </span>
        <span className="language-toggle-btn__text">
          {strings.languageToggle.targetLanguage}
        </span>
        <span className="language-toggle-btn__arrow">⇄</span>
      </button>
    </div>
  );
};

LanguageToggle.propTypes = {
  disabled: PropTypes.bool,
  className: PropTypes.string,
  onToggle: PropTypes.func,
};

LanguageToggle.defaultProps = {
  disabled: false,
  className: null,
  onToggle: null,
};

export default LanguageToggle;

