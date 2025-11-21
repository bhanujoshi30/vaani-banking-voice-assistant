import { useState, useRef, useEffect, useCallback } from 'react';
import { createVoiceProvider, VOICE_SETTINGS } from '../config/voiceConfig.js';
import { normalizeTranscript } from '../config/vocabularyConfig.js';

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
  const isManuallyStoppedRef = useRef(false); // Track if user manually stopped (prevents auto-restart)
  const maxRecordingTimeoutRef = useRef(null); // Maximum recording time (30 seconds)
  const inactivityTimeoutRef = useRef(null); // Inactivity timeout (5 seconds)
  
  // Maximum recording duration: 30 seconds
  const MAX_RECORDING_DURATION_MS = 30000;
  // Inactivity threshold: 5 seconds (stop if no speech detected)
  const INACTIVITY_THRESHOLD_MS = 5000;

  // Helper function to reset inactivity timer
  const resetInactivityTimer = useCallback(() => {
    // Clear existing inactivity timeout
    if (inactivityTimeoutRef.current) {
      clearTimeout(inactivityTimeoutRef.current);
    }
    
    // Set new inactivity timeout (5 seconds)
    inactivityTimeoutRef.current = setTimeout(() => {
      console.log('⏱️ Inactivity threshold (5s) reached - no speech detected, auto-stopping...');
      if (recognitionRef.current) {
        // Check if still listening using a closure-safe check
        const currentRecognition = recognitionRef.current;
        isManualStopRef.current = true;
        try {
          currentRecognition.stop();
        } catch (err) {
          console.log('Error auto-stopping due to inactivity:', err);
        }
      }
    }, INACTIVITY_THRESHOLD_MS);
  }, []);
  
  // Helper function to clear all timeouts
  const clearAllTimeouts = useCallback(() => {
    if (maxRecordingTimeoutRef.current) {
      clearTimeout(maxRecordingTimeoutRef.current);
      maxRecordingTimeoutRef.current = null;
    }
    if (inactivityTimeoutRef.current) {
      clearTimeout(inactivityTimeoutRef.current);
      inactivityTimeoutRef.current = null;
    }
  }, []);

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
        const rawTranscriptPiece = event.results[i][0].transcript;
        
        // Normalize transcript using vocabulary and accent mappings
        const transcriptPiece = normalizeTranscript(rawTranscriptPiece, lang);
        
        console.log(`Result ${i}:`, {
          raw: rawTranscriptPiece,
          normalized: transcriptPiece,
          isFinal: event.results[i].isFinal
        });
        
        if (event.results[i].isFinal) {
          finalTranscript += transcriptPiece + ' ';
        } else {
          interimText += transcriptPiece;
        }
      }

      if (finalTranscript) {
        // Normalize final transcript one more time (in case of multi-word phrases)
        const normalizedFinal = normalizeTranscript(finalTranscript.trim(), lang);
        console.log('Final transcript (normalized):', normalizedFinal);
        setTranscript((prev) => prev + normalizedFinal + ' ');
        setInterimTranscript('');
      }
      
      if (interimText) {
        // Normalize interim transcript
        const normalizedInterim = normalizeTranscript(interimText, lang);
        console.log('Interim transcript (normalized):', normalizedInterim);
        setInterimTranscript(normalizedInterim);
      }
      
      // Reset inactivity timer when speech is detected
      resetInactivityTimer();
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
      
      // Clear all timeouts
      clearAllTimeouts();
      
      // Auto-restart ONLY if:
      // 1. Continuous mode is enabled
      // 2. It wasn't manually stopped by user
      // 3. Recognition object still exists
      // Note: Auto-restart is mainly for voice mode, but we check manual stop to prevent unwanted restarts
      if (continuous && !isManualStopRef.current && !isManuallyStoppedRef.current && recognitionRef.current) {
        try {
          console.log('Auto-restarting recognition (continuous mode)...');
          recognition.start();
        } catch (err) {
          console.log('Could not auto-restart:', err);
        }
      } else if (isManualStopRef.current || isManuallyStoppedRef.current) {
        console.log('🛑 Recording was manually stopped - preventing auto-restart');
      }
      
      // Reset manual stop flag (but keep isManuallyStoppedRef for voice mode)
      isManualStopRef.current = false;
    };

    // Handle start of recognition
    recognition.onstart = () => {
      console.log('Speech recognition started');
      setIsListening(true);
      setError(null);
      
      // Clear any existing timeouts
      clearAllTimeouts();
      
      // Set maximum recording timeout (30 seconds)
      maxRecordingTimeoutRef.current = setTimeout(() => {
        console.log('⏱️ Maximum recording duration (30s) reached, auto-stopping...');
        if (recognitionRef.current) {
          isManualStopRef.current = true;
          try {
            recognitionRef.current.stop();
          } catch (err) {
            console.log('Error auto-stopping due to max duration:', err);
          }
        }
      }, MAX_RECORDING_DURATION_MS);
      
      // Start inactivity timer
      resetInactivityTimer();
    };

    // Handle speech start (when user starts speaking)
    recognition.onspeechstart = () => {
      console.log('🎤 User started speaking');
      // Reset inactivity timer when speech starts
      resetInactivityTimer();
    };

    // Handle speech end (when user stops speaking)
    recognition.onspeechend = () => {
      console.log('🎤 User stopped speaking');
      // Start inactivity timer when speech ends
      resetInactivityTimer();
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
      // Reset inactivity timer when sound is detected
      resetInactivityTimer();
    };

    // Handle sound end
    recognition.onsoundend = () => {
      console.log('🔇 Sound ended');
    };

    recognitionRef.current = recognition;

    return () => {
      // Clear all timeouts on cleanup
      if (maxRecordingTimeoutRef.current) {
        clearTimeout(maxRecordingTimeoutRef.current);
        maxRecordingTimeoutRef.current = null;
      }
      if (inactivityTimeoutRef.current) {
        clearTimeout(inactivityTimeoutRef.current);
        inactivityTimeoutRef.current = null;
      }
      
      if (recognitionRef.current) {
        try {
          recognitionRef.current.abort();
        } catch (err) {
          console.log('Cleanup error:', err);
        }
      }
    };
  }, [lang, continuous, interimResults, resetInactivityTimer, clearAllTimeouts]);

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
      isManuallyStoppedRef.current = false; // Reset manual stop flag when starting
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
      console.log('Cannot stop: not listening or recognition not initialized');
      return;
    }

    try {
      console.log('🛑 Manually stopping speech recognition...');
      isManualStopRef.current = true;
      isManuallyStoppedRef.current = true; // Mark as manually stopped to prevent auto-restart
      
      // Clear all timeouts
      if (maxRecordingTimeoutRef.current) {
        clearTimeout(maxRecordingTimeoutRef.current);
        maxRecordingTimeoutRef.current = null;
      }
      if (inactivityTimeoutRef.current) {
        clearTimeout(inactivityTimeoutRef.current);
        inactivityTimeoutRef.current = null;
      }
      
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
