import { useState, useEffect, useRef } from "react";
import PropTypes from "prop-types";
import { getPreferredLanguage, setPreferredLanguage } from "../utils/preferences.js";
import { getLanguageByCode } from "../config/voiceConfig.js";
import "./LanguageDropdown.css";

const SUPPORTED_LANGUAGES = ["en-IN", "hi-IN"];

/**
 * LanguageDropdown Component
 * A dropdown component that allows users to select between Hindi and English
 * 
 * @param {boolean} disabled - Whether the dropdown is disabled
 * @param {string} className - Optional CSS class name
 * @param {function} onSelect - Optional callback function that overrides default behavior
 * @param {string} value - Optional current language value to sync with parent component
 */
const LanguageDropdown = ({ disabled, className, onSelect, value }) => {
  const [currentLanguage, setCurrentLanguage] = useState(() => {
    // If value prop is provided, use it; otherwise use localStorage
    if (value && SUPPORTED_LANGUAGES.includes(value)) {
      return value;
    }
    const preferred = getPreferredLanguage();
    return SUPPORTED_LANGUAGES.includes(preferred) ? preferred : "en-IN";
  });
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef(null);

  // Get current language info
  const currentLangInfo = getLanguageByCode(currentLanguage);

  // Handle language selection
  const handleLanguageSelect = (newLang) => {
    // Validate language code
    if (!newLang || !SUPPORTED_LANGUAGES.includes(newLang)) {
      console.warn('LanguageDropdown: Invalid language code:', newLang);
      setIsOpen(false);
      return;
    }

    // If same language selected, just close dropdown
    if (newLang === currentLanguage) {
      setIsOpen(false);
      return;
    }

    console.log('LanguageDropdown: User selected language:', newLang, '(current:', currentLanguage, ')');

    // Close dropdown immediately for better UX
    setIsOpen(false);

    // If custom onSelect handler is provided, call it FIRST
    // The handler will update localStorage, state, and dispatch events
    // We'll update our internal state via the value prop sync or event listener
    if (onSelect) {
      console.log('LanguageDropdown: Calling onSelect handler with:', newLang);
      onSelect(newLang);
      // Don't update state here - let the parent's handler and value prop handle it
      // This ensures single source of truth
      return;
    }

    // Default behavior (when no onSelect handler): update state and localStorage
    setCurrentLanguage(newLang);
    setPreferredLanguage(newLang);
    // Dispatch custom event to notify other components
    window.dispatchEvent(new CustomEvent("languageChanged", { detail: { language: newLang } }));
  };

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener("mousedown", handleClickOutside);
    }

    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [isOpen]);

  // Sync with parent's language value prop if provided
  // This ensures dropdown stays in sync with parent component's language state
  // This is critical when onSelect handler is provided - the dropdown must sync with parent's state
  useEffect(() => {
    if (value && SUPPORTED_LANGUAGES.includes(value)) {
      // Always sync with parent's value prop when it changes
      // This handles cases where language is changed via AI command or manual dropdown selection
      if (value !== currentLanguage) {
        console.log('LanguageDropdown: Syncing with parent value prop:', value, '(current:', currentLanguage, ')');
        setCurrentLanguage(value);
      }
    }
  }, [value, currentLanguage]); // Include currentLanguage to detect when sync is needed

  // Sync with localStorage changes (if changed elsewhere, e.g., from other tabs or components)
  useEffect(() => {
    const handleStorageChange = () => {
      const preferred = getPreferredLanguage();
      if (SUPPORTED_LANGUAGES.includes(preferred)) {
        setCurrentLanguage((prevLang) => {
          // Only update if different to avoid unnecessary re-renders
          // But respect value prop if provided
          if (value && value !== preferred) {
            return prevLang; // Don't update if value prop takes precedence
          }
          return preferred !== prevLang ? preferred : prevLang;
        });
      }
    };

    const handleLanguageChange = (event) => {
      const { language: newLang } = event.detail;
      if (SUPPORTED_LANGUAGES.includes(newLang)) {
        setCurrentLanguage((prevLang) => {
          // Only update if different to avoid unnecessary re-renders
          // But respect value prop if provided
          if (value && value !== newLang) {
            return prevLang; // Don't update if value prop takes precedence
          }
          return newLang !== prevLang ? newLang : prevLang;
        });
      }
    };

    // Listen for storage changes (e.g., from other tabs)
    window.addEventListener("storage", handleStorageChange);
    // Listen for custom language change events (from same tab)
    window.addEventListener("languageChanged", handleLanguageChange);
    
    // Check localStorage on mount to ensure we're in sync (only if value prop not provided)
    if (!value) {
      const preferred = getPreferredLanguage();
      if (SUPPORTED_LANGUAGES.includes(preferred) && preferred !== currentLanguage) {
        setCurrentLanguage(preferred);
      }
    }
    
    return () => {
      window.removeEventListener("storage", handleStorageChange);
      window.removeEventListener("languageChanged", handleLanguageChange);
    };
  }, [currentLanguage, value]);

  return (
    <div 
      ref={dropdownRef}
      className={className || "language-dropdown"}
      style={{ position: "relative", display: "inline-block", zIndex: 10003 }}
    >
      <button
        type="button"
        className="language-dropdown__button"
        onClick={() => !disabled && setIsOpen(!isOpen)}
        disabled={disabled}
        aria-label={`Current language: ${currentLangInfo?.nativeName || currentLangInfo?.name}`}
        aria-expanded={isOpen}
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          gap: "0.5rem",
          padding: "0.6rem 1.2rem",
          border: "1px solid rgba(15, 27, 42, 0.12)",
          borderRadius: "999px",
          background: "rgba(255, 255, 255, 0.6)",
          color: "rgba(15, 27, 42, 0.8)",
          cursor: disabled ? "not-allowed" : "pointer",
          fontSize: "0.9rem",
          fontWeight: 600,
          minWidth: "140px",
          width: "140px",
          opacity: disabled ? 0.5 : 1,
          transition: "transform 0.18s ease, box-shadow 0.2s ease",
        }}
        onMouseEnter={(e) => {
          if (!disabled) {
            e.currentTarget.style.transform = "translateY(-1px)";
            e.currentTarget.style.boxShadow = "0 10px 24px -18px rgba(15, 27, 42, 0.25)";
          }
        }}
        onMouseLeave={(e) => {
          if (!disabled) {
            e.currentTarget.style.transform = "none";
            e.currentTarget.style.boxShadow = "none";
          }
        }}
      >
        <span style={{ display: "flex", alignItems: "center", gap: "0.5rem", flex: 1 }}>
          <span>{currentLangInfo?.flag || "🇮🇳"}</span>
          <span style={{ whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
            {currentLangInfo?.nativeName || currentLangInfo?.name || "English"}
          </span>
        </span>
        <svg
          width="12"
          height="12"
          viewBox="0 0 24 24"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          style={{
            flexShrink: 0,
            transform: isOpen ? "rotate(180deg)" : "rotate(0deg)",
            transition: "transform 0.2s",
          }}
        >
          <path
            d="M6 9L12 15L18 9"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
      </button>

      {isOpen && !disabled && (
        <div
          className="language-dropdown__menu"
          style={{
            position: "absolute",
            top: "100%",
            right: 0,
            marginTop: "0.25rem",
            background: "white",
            borderRadius: "0.375rem",
            boxShadow: "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)",
            minWidth: "150px",
            width: "max-content",
            maxWidth: "100%",
            zIndex: 10002,
            overflow: "visible",
            display: "flex",
            flexDirection: "column",
            minHeight: "fit-content",
          }}
        >
          {SUPPORTED_LANGUAGES.map((langCode) => {
            const langInfo = getLanguageByCode(langCode);
            if (!langInfo) {
              console.warn(`Language info not found for code: ${langCode}`);
              return null;
            }
            const isSelected = langCode === currentLanguage;
            return (
              <button
                key={langCode}
                type="button"
                onClick={() => handleLanguageSelect(langCode)}
                style={{
                  width: "100%",
                  display: "flex",
                  alignItems: "center",
                  gap: "0.5rem",
                  padding: "0.75rem 1rem",
                  border: "none",
                  background: isSelected ? "rgba(255, 143, 66, 0.1)" : "transparent",
                  color: isSelected ? "#ff8f42" : "#1f2937",
                  cursor: "pointer",
                  fontSize: "0.875rem",
                  textAlign: "left",
                  transition: "background-color 0.15s",
                  whiteSpace: "nowrap",
                  flexShrink: 0,
                }}
                onMouseEnter={(e) => {
                  if (!isSelected) {
                    e.currentTarget.style.backgroundColor = "rgba(0, 0, 0, 0.05)";
                  }
                }}
                onMouseLeave={(e) => {
                  if (!isSelected) {
                    e.currentTarget.style.backgroundColor = "transparent";
                  }
                }}
              >
                <span style={{ flexShrink: 0 }}>{langInfo?.flag || "🇮🇳"}</span>
                <span style={{ flex: 1, minWidth: 0 }}>{langInfo?.nativeName || langInfo?.name || langCode}</span>
                {isSelected && (
                  <span style={{ marginLeft: "auto", color: "#ff8f42", flexShrink: 0 }}>✓</span>
                )}
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
};

LanguageDropdown.propTypes = {
  disabled: PropTypes.bool,
  className: PropTypes.string,
  onSelect: PropTypes.func,
  value: PropTypes.string,
};

LanguageDropdown.defaultProps = {
  disabled: false,
  className: null,
  onSelect: null,
  value: null,
};

export default LanguageDropdown;

