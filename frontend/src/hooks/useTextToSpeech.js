import { useState, useRef, useCallback, useEffect } from 'react';

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
      
      // Load voices and select Indian female voice
      const loadVoices = () => {
        const voices = window.speechSynthesis.getVoices();
        
        if (voices.length > 0) {
          console.log('🔍 Available voices:', voices.length);
          
          // Preference order for Indian female voices
          const voicePreferences = [
            // Google voices (best quality)
            { name: 'Google हिन्दी', lang: 'hi-IN', female: true },
            { name: 'Google हिंदी', lang: 'hi-IN', female: true },
            { name: 'Google भारत', lang: 'hi-IN', female: true },
            // Microsoft voices
            { name: 'Microsoft Swara Online (Natural) - Hindi (India)', lang: 'hi-IN', female: true },
            { name: 'Microsoft Swara - Hindi (India)', lang: 'hi-IN', female: true },
            { name: 'Swara', lang: 'hi-IN', female: true },
            // Generic Indian English female voices
            { name: 'Google UK English Female', lang: 'en-GB', female: true },
            { name: 'Google US English Female', lang: 'en-US', female: true },
            { name: 'Microsoft Heera Online (Natural) - English (India)', lang: 'en-IN', female: true },
            { name: 'Microsoft Heera - English (India)', lang: 'en-IN', female: true },
            { name: 'Heera', lang: 'en-IN', female: true },
          ];
          
          // Try to find preferred Indian female voice
          let voice = null;
          
          // First: Try exact name matches for Indian voices
          for (const pref of voicePreferences) {
            voice = voices.find(v => 
              v.name.includes(pref.name) || 
              (v.lang.startsWith(pref.lang) && v.name.toLowerCase().includes('female'))
            );
            if (voice) {
              console.log('✅ Found preferred voice:', voice.name, voice.lang);
              break;
            }
          }
          
          // Second: Try any Hindi voice
          if (!voice) {
            voice = voices.find(v => v.lang.startsWith('hi-IN'));
            if (voice) console.log('✅ Found Hindi voice:', voice.name);
          }
          
          // Third: Try any Indian English voice
          if (!voice) {
            voice = voices.find(v => v.lang.startsWith('en-IN'));
            if (voice) console.log('✅ Found Indian English voice:', voice.name);
          }
          
          // Fourth: Try any female-sounding voice
          if (!voice) {
            const femaleKeywords = ['female', 'woman', 'heera', 'swara', 'nisha', 'priya'];
            voice = voices.find(v => 
              femaleKeywords.some(keyword => v.name.toLowerCase().includes(keyword))
            );
            if (voice) console.log('✅ Found female voice:', voice.name);
          }
          
          // Fifth: Use first available voice
          if (!voice && voices.length > 0) {
            voice = voices[0];
            console.log('⚠️ Using default voice:', voice.name);
          }
          
          setSelectedVoice(voice);
          
          if (voice) {
            console.log('🎤 Selected TTS voice:', {
              name: voice.name,
              lang: voice.lang,
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
  }, []);

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

    console.log('🔊 Starting TTS:', text.substring(0, 50) + '...');

    const utterance = new SpeechSynthesisUtterance(text);
    
    // Use selected Indian female voice if available
    if (selectedVoice) {
      utterance.voice = selectedVoice;
      console.log('🎤 Using voice:', selectedVoice.name);
    }
    
    utterance.lang = lang;
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
