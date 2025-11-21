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
          
          // Select voice based on current language
          if (lang === 'hi-IN') {
            // For Hindi, prioritize Hindi voices
            const hindiVoicePreferences = [
              { name: 'Google हिन्दी', lang: 'hi-IN' },
              { name: 'Google हिंदी', lang: 'hi-IN' },
              { name: 'Google भारत', lang: 'hi-IN' },
              { name: 'Microsoft Swara Online (Natural) - Hindi (India)', lang: 'hi-IN' },
              { name: 'Microsoft Swara - Hindi (India)', lang: 'hi-IN' },
              { name: 'Swara', lang: 'hi-IN' },
            ];
            
            // Try exact name matches for Hindi voices
            for (const pref of hindiVoicePreferences) {
              voice = voices.find(v => v.name.includes(pref.name));
              if (voice) {
                console.log('✅ Found preferred Hindi voice:', voice.name, voice.lang);
                break;
              }
            }
            
            // Try any Hindi voice
            if (!voice) {
              voice = voices.find(v => v.lang.startsWith('hi-IN') || v.lang.startsWith('hi'));
              if (voice) console.log('✅ Found Hindi voice:', voice.name, voice.lang);
            }
          } else {
            // For English, prioritize Indian English voices
            const englishVoicePreferences = [
              { name: 'Microsoft Heera Online (Natural) - English (India)', lang: 'en-IN' },
              { name: 'Microsoft Heera - English (India)', lang: 'en-IN' },
              { name: 'Heera', lang: 'en-IN' },
              { name: 'Google UK English Female', lang: 'en-GB' },
              { name: 'Google US English Female', lang: 'en-US' },
            ];
            
            // Try exact name matches for Indian English voices
            for (const pref of englishVoicePreferences) {
              voice = voices.find(v => v.name.includes(pref.name));
              if (voice) {
                console.log('✅ Found preferred English voice:', voice.name, voice.lang);
                break;
              }
            }
            
            // Try any Indian English voice
            if (!voice) {
              voice = voices.find(v => v.lang.startsWith('en-IN'));
              if (voice) console.log('✅ Found Indian English voice:', voice.name);
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
    const normalizedText = normalizeForTTS(text, lang);
    
    console.log('🔊 Starting TTS:', {
      language: lang,
      original: text.substring(0, 100) + '...',
      normalized: normalizedText.substring(0, 100) + '...',
      hasHindiChars: /[\u0900-\u097F]/.test(text),
      hasPercentages: /(\d+\.?\d*)\s*%/.test(text)
    });

    const utterance = new SpeechSynthesisUtterance(normalizedText);
    
    // Use selected Indian female voice if available
    if (selectedVoice) {
      utterance.voice = selectedVoice;
      console.log('🎤 Using voice:', selectedVoice.name, 'Language:', selectedVoice.lang);
    }
    
    // Ensure utterance language matches the selected language
    utterance.lang = lang;
    console.log('🎤 TTS utterance language set to:', utterance.lang);
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
