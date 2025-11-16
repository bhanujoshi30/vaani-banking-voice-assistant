import { useState, useRef, useEffect, useCallback } from 'react';
import { createVoiceProvider, VOICE_SETTINGS } from '../config/voiceConfig.js';

/**
 * Custom hook for Web Speech API integration
 * Provides voice-to-text functionality with better control over listening duration
 * 
 * @param {Object} options - Configuration options
 * @param {string} options.lang - Language code (default: from voiceConfig)
 * @param {boolean} options.continuous - Whether to listen continuously
 * @param {boolean} options.interimResults - Show interim results
 * @returns {Object} Speech recognition state and controls
 */
export const useSpeechRecognition = (options = {}) => {
  // Get voice provider configuration
  const providerConfig = createVoiceProvider(options.lang);
  
  const {
    lang = providerConfig.config.lang,
    continuous = providerConfig.config.continuous,
    interimResults = providerConfig.config.interimResults,
  } = options;

  const [isListening, setIsListening] = useState(false);
  const [isSpeechSupported, setIsSpeechSupported] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [interimTranscript, setInterimTranscript] = useState('');
  const [error, setError] = useState(null);

  const recognitionRef = useRef(null);
  const isManualStopRef = useRef(false);

  // Initialize Speech Recognition
  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    
    if (!SpeechRecognition) {
      setIsSpeechSupported(false);
      console.warn('Speech Recognition API not supported in this browser');
      return;
    }

    setIsSpeechSupported(true);
    const recognition = new SpeechRecognition();
    
    // Configure recognition
    recognition.continuous = continuous;
    recognition.interimResults = interimResults;
    recognition.lang = lang;
    recognition.maxAlternatives = 1;

    // Handle results
    recognition.onresult = (event) => {
      let finalTranscript = '';
      let interimText = '';

      console.log('Speech result event:', event.results.length, 'results');

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcriptPiece = event.results[i][0].transcript;
        
        console.log(`Result ${i}:`, transcriptPiece, 'isFinal:', event.results[i].isFinal);
        
        if (event.results[i].isFinal) {
          finalTranscript += transcriptPiece + ' ';
        } else {
          interimText += transcriptPiece;
        }
      }

      if (finalTranscript) {
        console.log('Final transcript:', finalTranscript);
        setTranscript((prev) => prev + finalTranscript);
        setInterimTranscript('');
      }
      
      if (interimText) {
        console.log('Interim transcript:', interimText);
        setInterimTranscript(interimText);
      }
    };

    // Handle errors
    recognition.onerror = (event) => {
      console.error('Speech recognition error:', event.error);
      
      let errorMessage = 'Voice input failed. ';
      
      switch (event.error) {
        case 'no-speech':
          errorMessage = 'No speech detected. Please try again.';
          break;
        case 'audio-capture':
          errorMessage = 'Microphone not found or not accessible.';
          break;
        case 'not-allowed':
          errorMessage = 'Microphone permission denied. Please allow microphone access.';
          break;
        case 'network':
          errorMessage = 'Network error occurred. Please check your connection.';
          break;
        case 'aborted':
          // Don't show error if manually stopped
          if (!isManualStopRef.current) {
            errorMessage = 'Voice input was aborted.';
          } else {
            errorMessage = null;
          }
          break;
        default:
          errorMessage = `Error: ${event.error}. Please try again.`;
      }

      if (errorMessage) {
        setError(errorMessage);
      }
      setIsListening(false);
    };

    // Handle end of recognition
    recognition.onend = () => {
      console.log('Speech recognition ended');
      setIsListening(false);
      
      // Auto-restart if continuous and not manually stopped
      if (continuous && !isManualStopRef.current && recognitionRef.current) {
        try {
          console.log('Auto-restarting recognition...');
          recognition.start();
        } catch (err) {
          console.log('Could not auto-restart:', err);
        }
      }
      
      isManualStopRef.current = false;
    };

    // Handle start of recognition
    recognition.onstart = () => {
      console.log('Speech recognition started');
      setIsListening(true);
      setError(null);
    };

    // Handle speech start (when user starts speaking)
    recognition.onspeechstart = () => {
      console.log('🎤 User started speaking');
    };

    // Handle speech end (when user stops speaking)
    recognition.onspeechend = () => {
      console.log('🎤 User stopped speaking');
    };

    // Handle audio start (when audio capture begins)
    recognition.onaudiostart = () => {
      console.log('🔊 Audio capture started - microphone is working!');
    };

    // Handle audio end (when audio capture ends)
    recognition.onaudioend = () => {
      console.log('🔊 Audio capture ended');
    };

    // Handle sound start
    recognition.onsoundstart = () => {
      console.log('🔉 Sound detected');
    };

    // Handle sound end
    recognition.onsoundend = () => {
      console.log('🔇 Sound ended');
    };

    recognitionRef.current = recognition;

    return () => {
      if (recognitionRef.current) {
        try {
          recognitionRef.current.abort();
        } catch (err) {
          console.log('Cleanup error:', err);
        }
      }
    };
  }, [lang, continuous, interimResults]);

  // Start listening
  const startListening = useCallback(() => {
    if (!isSpeechSupported) {
      setError('Voice input is not supported in your browser. Please use Chrome, Edge, or Safari.');
      return false;
    }

    if (!recognitionRef.current) {
      setError('Speech recognition not initialized');
      return false;
    }

    if (isListening) {
      console.log('Already listening');
      return false;
    }

    try {
      isManualStopRef.current = false;
      setTranscript('');
      setInterimTranscript('');
      setError(null);
      recognitionRef.current.start();
      return true;
    } catch (err) {
      console.error('Error starting speech recognition:', err);
      setError('Failed to start voice input. Please try again.');
      return false;
    }
  }, [isSpeechSupported, isListening]);

  // Stop listening
  const stopListening = useCallback(() => {
    if (!recognitionRef.current || !isListening) {
      return;
    }

    try {
      isManualStopRef.current = true;
      recognitionRef.current.stop();
    } catch (err) {
      console.error('Error stopping speech recognition:', err);
    }
  }, [isListening]);

  // Toggle listening
  const toggleListening = useCallback(() => {
    if (isListening) {
      stopListening();
    } else {
      startListening();
    }
  }, [isListening, startListening, stopListening]);

  // Reset transcript
  const resetTranscript = useCallback(() => {
    setTranscript('');
    setInterimTranscript('');
  }, []);

  // Get full transcript (final + interim)
  const fullTranscript = transcript + interimTranscript;

  return {
    isListening,
    isSpeechSupported,
    transcript,
    interimTranscript,
    fullTranscript,
    error,
    startListening,
    stopListening,
    toggleListening,
    resetTranscript,
  };
};

export default useSpeechRecognition;
