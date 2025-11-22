import { useState, useRef, useCallback, useEffect } from 'react';
import { normalizeForTTS } from '../config/vocabularyConfig.js';

/**
 * Custom hook for Text-to-Speech functionality
 * Uses Web Speech API SpeechSynthesis
 * 
 * @param {Object} options - Configuration options
 * @param {string} options.lang - Language code (default: 'en-IN')
 * @param {number} options.rate - Speech rate (default: 1.0)
 * @param {number} options.pitch - Speech pitch (default: 1.0)
 * @param {number} options.volume - Speech volume (default: 1.0)
 * @returns {Object} Text-to-speech state and controls
 */
export const useTextToSpeech = (options = {}) => {
  const {
    lang = 'en-IN',
    rate = 1.0,
    pitch = 1.0,
    volume = 1.0,
  } = options;

  const [isSpeaking, setIsSpeaking] = useState(false);
  const [isTTSSupported, setIsTTSSupported] = useState(false);
  const [currentText, setCurrentText] = useState('');
  const [selectedVoice, setSelectedVoice] = useState(null);
  const utteranceRef = useRef(null);

  // Check TTS support and find Indian female voice
  useEffect(() => {
    const supported = 'speechSynthesis' in window;
    setIsTTSSupported(supported);
    
    if (supported) {
      console.log('✅ Text-to-Speech is supported');
      
      // Load voices and select appropriate voice based on language
      const loadVoices = () => {
        const voices = window.speechSynthesis.getVoices();
        
        if (voices.length > 0) {
          console.log('🔍 Available voices:', voices.length);
          
          let voice = null;
          
          // Use Hindi voice (Swara) for both Hindi and English languages
          // This ensures consistent voice quality across languages
          const hindiVoicePreferences = [
            { name: 'Microsoft Swara Online (Natural) - Hindi (India)', lang: 'hi-IN' },
            { name: 'Microsoft Swara - Hindi (India)', lang: 'hi-IN' },
            { name: 'Swara', lang: 'hi-IN' },
            { name: 'Google हिन्दी', lang: 'hi-IN' },
            { name: 'Google हिंदी', lang: 'hi-IN' },
            { name: 'Google भारत', lang: 'hi-IN' },
          ];
          
          // Try exact name matches for Hindi voices (preferred for both languages)
          for (const pref of hindiVoicePreferences) {
            voice = voices.find(v => v.name.includes(pref.name));
            if (voice) {
              console.log('✅ Found preferred Hindi voice (using for both languages):', voice.name, voice.lang);
              break;
            }
          }
          
          // Try any Hindi voice
          if (!voice) {
            voice = voices.find(v => v.lang.startsWith('hi-IN') || v.lang.startsWith('hi'));
            if (voice) console.log('✅ Found Hindi voice (using for both languages):', voice.name, voice.lang);
          }
          
          // Fallback: If no Hindi voice found, try Indian English voices
          if (!voice) {
            const englishVoicePreferences = [
              { name: 'Microsoft Heera Online (Natural) - English (India)', lang: 'en-IN' },
              { name: 'Microsoft Heera - English (India)', lang: 'en-IN' },
              { name: 'Heera', lang: 'en-IN' },
            ];
            
            for (const pref of englishVoicePreferences) {
              voice = voices.find(v => v.name.includes(pref.name));
              if (voice) {
                console.log('⚠️ Using fallback English voice:', voice.name, voice.lang);
                break;
              }
            }
          }
          
          // Fallback: Try any female-sounding voice
          if (!voice) {
            const femaleKeywords = ['female', 'woman', 'heera', 'swara', 'nisha', 'priya'];
            voice = voices.find(v => 
              femaleKeywords.some(keyword => v.name.toLowerCase().includes(keyword))
            );
            if (voice) console.log('✅ Found female voice:', voice.name);
          }
          
          // Last resort: Use first available voice
          if (!voice && voices.length > 0) {
            voice = voices[0];
            console.log('⚠️ Using default voice:', voice.name);
          }
          
          setSelectedVoice(voice);
          
          if (voice) {
            console.log('🎤 Selected TTS voice:', {
              name: voice.name,
              lang: voice.lang,
              requestedLang: lang,
              localService: voice.localService,
              default: voice.default
            });
          }
        }
      };
      
      // Load voices (some browsers need this event)
      loadVoices();
      
      if (window.speechSynthesis.onvoiceschanged !== undefined) {
        window.speechSynthesis.onvoiceschanged = loadVoices;
      }
    } else {
      console.warn('❌ Text-to-Speech is not supported in this browser');
    }
  }, [lang]); // Re-select voice when language changes

  /**
   * Speak the given text
   */
  const speak = useCallback((text, onComplete) => {
    if (!isTTSSupported) {
      console.warn('Text-to-Speech not supported');
      onComplete?.();
      return;
    }

    // Cancel any ongoing speech
    window.speechSynthesis.cancel();

    if (!text || text.trim() === '') {
      onComplete?.();
      return;
    }

    // Normalize text for TTS pronunciation (e.g., "UPI" → "U P I")
    // CRITICAL: Detect actual text language - if text is English, use English normalization
    // even if lang parameter is 'hi-IN' (user might be in Hindi mode but response is in English)
    const hasHindiChars = /[\u0900-\u097F]/.test(text);
    const textLanguage = hasHindiChars ? 'hi-IN' : 'en-IN';
    
    // Use detected text language for normalization, not the lang parameter
    // This ensures English text gets English number pronunciation even if user is in Hindi mode
    const normalizedText = normalizeForTTS(text, textLanguage);
    
    console.log('🔊 Starting TTS:', {
      language: lang,
      original: text.substring(0, 100) + '...',
      normalized: normalizedText.substring(0, 100) + '...',
      hasHindiChars: /[\u0900-\u097F]/.test(text),
      hasPercentages: /(\d+\.?\d*)\s*%/.test(text),
      voiceName: selectedVoice?.name,
      voiceLang: selectedVoice?.lang
    });

    const utterance = new SpeechSynthesisUtterance(normalizedText);
    
    // Use selected Hindi voice (Swara) for both Hindi and English
    // CRITICAL: Use detected text language for utterance.lang
    // If text contains Hindi Devanagari characters, set utterance.lang to 'hi-IN'
    // Otherwise, use 'en-IN' for English text (even if user is in Hindi mode)
    
    if (selectedVoice) {
      utterance.voice = selectedVoice;
      
      // Use detected text language (hasHindiChars already detected above)
      utterance.lang = textLanguage;
      console.log('🎤 Using Hindi voice with text language:', selectedVoice.name, 'Text Language:', textLanguage, 'Has Hindi Chars:', hasHindiChars);
    } else {
      // No voice selected, use detected text language
      utterance.lang = textLanguage;
      console.log('⚠️ No voice selected, using text language:', textLanguage);
    }
    
    console.log('🎤 TTS utterance final settings:', {
      voice: selectedVoice?.name || 'none',
      voiceLang: selectedVoice?.lang || 'none',
      utteranceLang: utterance.lang,
      textLang: lang,
      hasHindiChars: hasHindiChars,
      textPreview: text.substring(0, 50)
    });
    utterance.rate = rate;
    utterance.pitch = pitch;
    utterance.volume = volume;

    utterance.onstart = () => {
      console.log('🎤 TTS started');
      setIsSpeaking(true);
      setCurrentText(text);
    };

    utterance.onend = () => {
      console.log('✅ TTS completed');
      setIsSpeaking(false);
      setCurrentText('');
      onComplete?.();
    };

    utterance.onerror = (event) => {
      console.error('❌ TTS error:', event.error);
      setIsSpeaking(false);
      setCurrentText('');
      onComplete?.();
    };

    utteranceRef.current = utterance;
    window.speechSynthesis.speak(utterance);
  }, [isTTSSupported, selectedVoice, lang, rate, pitch, volume]);

  /**
   * Stop speaking
   */
  const stop = useCallback(() => {
    if (isTTSSupported) {
      console.log('🛑 Stopping TTS');
      window.speechSynthesis.cancel();
      setIsSpeaking(false);
      setCurrentText('');
    }
  }, [isTTSSupported]);

  /**
   * Pause speaking
   */
  const pause = useCallback(() => {
    if (isTTSSupported && isSpeaking) {
      console.log('⏸️ Pausing TTS');
      window.speechSynthesis.pause();
    }
  }, [isTTSSupported, isSpeaking]);

  /**
   * Resume speaking
   */
  const resume = useCallback(() => {
    if (isTTSSupported) {
      console.log('▶️ Resuming TTS');
      window.speechSynthesis.resume();
    }
  }, [isTTSSupported]);

  /**
   * Get available voices
   */
  const getVoices = useCallback(() => {
    if (isTTSSupported) {
      return window.speechSynthesis.getVoices();
    }
    return [];
  }, [isTTSSupported]);

  return {
    isSpeaking,
    isTTSSupported,
    currentText,
    selectedVoice,
    speak,
    stop,
    pause,
    resume,
    getVoices,
  };
};

export default useTextToSpeech;
