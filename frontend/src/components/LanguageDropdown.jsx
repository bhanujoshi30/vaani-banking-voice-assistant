import { useState, useEffect, useRef } from "react";
import PropTypes from "prop-types";
import { getPreferredLanguage, setPreferredLanguage } from "../utils/preferences.js";
import { getLanguageByCode } from "../config/voiceConfig.js";

const SUPPORTED_LANGUAGES = ["en-IN", "hi-IN"];

/**
 * LanguageDropdown Component
 * A dropdown component that allows users to select between Hindi and English
 * 
 * @param {boolean} disabled - Whether the dropdown is disabled
 * @param {string} className - Optional CSS class name
 * @param {function} onSelect - Optional callback function that overrides default behavior
 */
const LanguageDropdown = ({ disabled, className, onSelect }) => {
  const [currentLanguage, setCurrentLanguage] = useState(() => {
    const preferred = getPreferredLanguage();
    return SUPPORTED_LANGUAGES.includes(preferred) ? preferred : "en-IN";
  });
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef(null);

  // Get current language info
  const currentLangInfo = getLanguageByCode(currentLanguage);

  // Handle language selection
  const handleLanguageSelect = (newLang) => {
    if (newLang === currentLanguage) {
      setIsOpen(false);
      return;
    }

    // If custom onSelect handler is provided, call it but don't update state here
    // The state will be updated via languageChanged event or localStorage sync
    if (onSelect) {
      onSelect(newLang);
      setIsOpen(false);
      return;
    }

    // Default behavior: update state and localStorage
    setCurrentLanguage(newLang);
    setPreferredLanguage(newLang);
    // Dispatch custom event to notify other components
    window.dispatchEvent(new CustomEvent("languageChanged", { detail: { language: newLang } }));
    setIsOpen(false);
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

  // Sync with localStorage changes (if changed elsewhere, e.g., from other tabs or components)
  useEffect(() => {
    const handleStorageChange = () => {
      const preferred = getPreferredLanguage();
      if (SUPPORTED_LANGUAGES.includes(preferred)) {
        setCurrentLanguage((prevLang) => {
          // Only update if different to avoid unnecessary re-renders
          return preferred !== prevLang ? preferred : prevLang;
        });
      }
    };

    const handleLanguageChange = (event) => {
      const { language: newLang } = event.detail;
      if (SUPPORTED_LANGUAGES.includes(newLang)) {
        setCurrentLanguage((prevLang) => {
          // Only update if different to avoid unnecessary re-renders
          return newLang !== prevLang ? newLang : prevLang;
        });
      }
    };

    // Listen for storage changes (e.g., from other tabs)
    window.addEventListener("storage", handleStorageChange);
    // Listen for custom language change events (from same tab)
    window.addEventListener("languageChanged", handleLanguageChange);
    
    // Check localStorage on mount to ensure we're in sync
    const preferred = getPreferredLanguage();
    if (SUPPORTED_LANGUAGES.includes(preferred) && preferred !== currentLanguage) {
      setCurrentLanguage(preferred);
    }
    
    return () => {
      window.removeEventListener("storage", handleStorageChange);
      window.removeEventListener("languageChanged", handleLanguageChange);
    };
  }, [currentLanguage]);

  return (
    <div 
      ref={dropdownRef}
      className={className || "language-dropdown"}
      style={{ position: "relative", display: "inline-block" }}
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
            zIndex: 1000,
            overflow: "hidden",
          }}
        >
          {SUPPORTED_LANGUAGES.map((langCode) => {
            const langInfo = getLanguageByCode(langCode);
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
                <span>{langInfo?.flag || "🇮🇳"}</span>
                <span>{langInfo?.nativeName || langInfo?.name || langCode}</span>
                {isSelected && (
                  <span style={{ marginLeft: "auto", color: "#ff8f42" }}>✓</span>
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
};

LanguageDropdown.defaultProps = {
  disabled: false,
  className: null,
  onSelect: null,
};

export default LanguageDropdown;

