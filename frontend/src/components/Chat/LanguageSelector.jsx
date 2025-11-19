import { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import { getEnabledLanguages } from '../../config/voiceConfig.js';
import './LanguageSelector.css';

/**
 * LanguageSelector Component
 * Allows users to select their preferred language for voice input
 */
const LanguageSelector = ({ selectedLanguage, onLanguageChange, disabled }) => {
  const [isOpen, setIsOpen] = useState(false);
  const languages = getEnabledLanguages();
  const currentLang = languages.find(lang => lang.code === selectedLanguage);

  const handleSelect = (languageCode) => {
    onLanguageChange(languageCode);
    setIsOpen(false);
  };

  useEffect(() => {
    if (disabled && isOpen) {
      setIsOpen(false);
    }
  }, [disabled, isOpen]);

  const tooltip = disabled
    ? 'Enable Voice Mode to change the assistant language'
    : 'Select language for voice input';

  return (
    <div className="language-selector">
      <button
        type="button"
        className={`language-selector__button ${isOpen ? 'language-selector__button--open' : ''}`}
        onClick={() => setIsOpen(!isOpen)}
        disabled={disabled}
        title={tooltip}
      >
        <span className="language-selector__flag">{currentLang?.flag}</span>
        <span className="language-selector__name">{currentLang?.name}</span>
        <svg
          width="16"
          height="16"
          viewBox="0 0 24 24"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          className="language-selector__arrow"
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

      {isOpen && (
        <>
          <div
            className="language-selector__backdrop"
            onClick={() => setIsOpen(false)}
          />
          <div className="language-selector__dropdown">
            <div className="language-selector__header">
              🎤 Select Voice Language
            </div>
            {languages.map((lang) => (
              <button
                key={lang.code}
                type="button"
                className={`language-selector__option ${
                  lang.code === selectedLanguage ? 'language-selector__option--active' : ''
                }`}
                onClick={() => handleSelect(lang.code)}
              >
                <span className="language-selector__option-flag">{lang.flag}</span>
                <div className="language-selector__option-text">
                  <span className="language-selector__option-name">{lang.name}</span>
                  <span className="language-selector__option-native">{lang.nativeName}</span>
                </div>
                {lang.code === selectedLanguage && (
                  <svg
                    width="20"
                    height="20"
                    viewBox="0 0 24 24"
                    fill="none"
                    xmlns="http://www.w3.org/2000/svg"
                    className="language-selector__check"
                  >
                    <path
                      d="M20 6L9 17L4 12"
                      stroke="currentColor"
                      strokeWidth="2"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    />
                  </svg>
                )}
              </button>
            ))}
          </div>
        </>
      )}
    </div>
  );
};

LanguageSelector.propTypes = {
  selectedLanguage: PropTypes.string.isRequired,
  onLanguageChange: PropTypes.func.isRequired,
  disabled: PropTypes.bool,
};

LanguageSelector.defaultProps = {
  disabled: false,
};

export default LanguageSelector;
