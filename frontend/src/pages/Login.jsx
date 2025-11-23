import { useEffect, useRef, useState } from "react";
import PropTypes from "prop-types";
import { Link, Navigate } from "react-router-dom";

import SunHeader from "../components/SunHeader.jsx";
import LanguageDropdown from "../components/LanguageDropdown.jsx";
import AIAssistantLogo from "../components/AIAssistantLogo.jsx";
import { getLoginStrings, getVoicePhrase } from "../config/loginStrings.js";
import { getPreferredLanguage, setPreferredLanguage } from "../utils/preferences.js";

const verifyPasswordLocally = (inputPassword) => inputPassword.trim().length >= 4;

const mixToMono = (audioBuffer) => {
  if (audioBuffer.numberOfChannels === 1) {
    return audioBuffer.getChannelData(0);
  }
  const length = audioBuffer.length;
  const result = new Float32Array(length);
  for (let channel = 0; channel < audioBuffer.numberOfChannels; channel += 1) {
    const data = audioBuffer.getChannelData(channel);
    for (let i = 0; i < length; i += 1) {
      result[i] += data[i];
    }
  }
  for (let i = 0; i < length; i += 1) {
    result[i] /= audioBuffer.numberOfChannels;
  }
  return result;
};

const writeString = (view, offset, string) => {
  for (let i = 0; i < string.length; i += 1) {
    view.setUint8(offset + i, string.charCodeAt(i));
  }
};

const floatTo16BitPCM = (view, offset, input) => {
  for (let i = 0; i < input.length; i += 1, offset += 2) {
    const sample = Math.max(-1, Math.min(1, input[i]));
    view.setInt16(offset, sample < 0 ? sample * 0x8000 : sample * 0x7fff, true);
  }
};

const encodeWavBuffer = (samples, sampleRate) => {
  const buffer = new ArrayBuffer(44 + samples.length * 2);
  const view = new DataView(buffer);

  writeString(view, 0, "RIFF");
  view.setUint32(4, 36 + samples.length * 2, true);
  writeString(view, 8, "WAVE");
  writeString(view, 12, "fmt ");
  view.setUint32(16, 16, true);
  view.setUint16(20, 1, true);
  view.setUint16(22, 1, true);
  view.setUint32(24, sampleRate, true);
  view.setUint32(28, sampleRate * 2, true);
  view.setUint16(32, 2, true);
  view.setUint16(34, 16, true);
  writeString(view, 36, "data");
  view.setUint32(40, samples.length * 2, true);
  floatTo16BitPCM(view, 44, samples);

  return buffer;
};

const convertBlobToWav = async (blob) => {
  const AudioContextCtor = window.AudioContext || window.webkitAudioContext;
  const audioContext = new AudioContextCtor();
  const arrayBuffer = await blob.arrayBuffer();
  const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);
  const monoSamples = mixToMono(audioBuffer);
  const wavBuffer = encodeWavBuffer(monoSamples, audioBuffer.sampleRate);
  await audioContext.close();
  return { wavBlob: new Blob([wavBuffer], { type: "audio/wav" }), duration: audioBuffer.duration };
};

const MAX_RECORDING_MS = 7000;
const FIXED_OTP = "12345";
const SUPPORTED_LOGIN_LANGUAGES = ["en-IN", "hi-IN"];

const Login = ({ onAuthenticate, authenticated }) => {
  // Language state - default to user's preferred language or English
  const [loginLanguage, setLoginLanguage] = useState(() => {
    const preferred = getPreferredLanguage();
    return SUPPORTED_LOGIN_LANGUAGES.includes(preferred) ? preferred : "en-IN";
  });
  
  // Get localized strings for current language
  const strings = getLoginStrings(loginLanguage);
  const voicePhrase = getVoicePhrase(loginLanguage);
  
  const [authMode, setAuthMode] = useState("voice");
  const [userId, setUserId] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isVerifyingVoice, setIsVerifyingVoice] = useState(false);
  const [awaitingOtp, setAwaitingOtp] = useState(false);
  const [otp, setOtp] = useState("");
  const [showOtp, setShowOtp] = useState(false);
  const [isVoiceEnrolled, setIsVoiceEnrolled] = useState(false);
  const [voiceBlob, setVoiceBlob] = useState(null);
  const [voiceSummary, setVoiceSummary] = useState("");
  const [recordingState, setRecordingState] = useState("idle");
  const [recordingStatus, setRecordingStatus] = useState("");
  const [voiceCaptureStep, setVoiceCaptureStep] = useState(1);
  const [firstVoiceSummary, setFirstVoiceSummary] = useState("");
  const [recordingProgress, setRecordingProgress] = useState(0);
  const mediaRecorderRef = useRef(null);
  const chunksRef = useRef([]);
  const voiceSectionRef = useRef(null);
  const otpInputRef = useRef(null);
  const recordingTimerRef = useRef(null);
  const recordingStartRef = useRef(null);
  const isFirstVoiceLogin = authMode === "voice" && userId.trim() && !isVoiceEnrolled;
  const [showScrollHint, setShowScrollHint] = useState(true);
  const loginFormRef = useRef(null);
  
  // Toggle language between Hindi and English
  const handleLanguageChange = (newLanguage) => {
    setLoginLanguage(newLanguage);
    setPreferredLanguage(newLanguage);
    // Dispatch event to notify other components
    window.dispatchEvent(new CustomEvent("languageChanged", { detail: { language: newLanguage } }));
  };

  useEffect(
    () => () => {
      const recorder = mediaRecorderRef.current;
      if (recorder && recorder.state !== "inactive") {
        recorder.stop();
      }
      if (recordingTimerRef.current) {
        clearInterval(recordingTimerRef.current);
        recordingTimerRef.current = null;
      }
    },
    [],
  );

  useEffect(() => {
    if (!awaitingOtp) {
      setOtp("");
      setShowOtp(false);
    }
  }, [awaitingOtp]);

  // Handle scroll visibility for scroll hint with graceful fade
  useEffect(() => {
    let timeoutId = null;
    
    const handleScroll = () => {
      // Hide scroll hint when user scrolls down significantly
      // Show it again if they scroll back to top
      const scrollPosition = window.scrollY || window.pageYOffset;
      const windowHeight = window.innerHeight;
      
      // Clear any pending timeout
      if (timeoutId) {
        clearTimeout(timeoutId);
      }
      
      // Hide if scrolled past first viewport, show if back near top
      if (scrollPosition > windowHeight * 0.3) {
        // Add delay to allow graceful fade-out
        timeoutId = setTimeout(() => {
          setShowScrollHint(false);
        }, 100);
      } else {
        // Show immediately when scrolling back up
        setShowScrollHint(true);
      }
    };

    // Check initial scroll position
    handleScroll();
    
    window.addEventListener("scroll", handleScroll, { passive: true });
    return () => {
      window.removeEventListener("scroll", handleScroll);
      if (timeoutId) {
        clearTimeout(timeoutId);
      }
    };
  }, []);

  const scrollToHero = () => {
    const heroSection = document.querySelector(".login-hero-section");
    if (heroSection) {
      heroSection.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  };

  useEffect(() => {
    if (authMode === "voice" && userId.trim()) {
      let enrolled = false;
      try {
        enrolled =
          window.localStorage.getItem(`voiceEnrolled:${userId.trim()}`) === "true";
      } catch {
        enrolled = false;
      }
      setIsVoiceEnrolled(enrolled);
      resetVoiceCapture(1); // Always use step 1 - no double recording needed
      requestAnimationFrame(() => {
        if (voiceSectionRef.current) {
          voiceSectionRef.current.scrollIntoView({ behavior: "smooth", block: "center" });
        }
      });
    } else if (authMode !== "voice") {
      resetVoiceCapture(1);
      setIsVoiceEnrolled(false);
      // Clear any voice-related errors when switching to password mode
      if (error && error.toLowerCase().includes("voice")) {
        setError("");
      }
    }
    // Only clear error if switching modes, not on every userId change
    if (authMode === "password" && error && error.toLowerCase().includes("voice")) {
      setError("");
    }
  }, [authMode, userId]);

  const resetVoiceCapture = (nextStep, flushEnrollment = false) => {
    setVoiceBlob(null);
    setVoiceSummary("");
    setRecordingStatus("");
    setRecordingState("idle");
    setFirstVoiceSummary("");
    setRecordingProgress(0);
    if (authMode === "voice") {
      setError("");
    }
    setVoiceCaptureStep(
      typeof nextStep === "number" ? nextStep : isVoiceEnrolled ? 2 : 1,
    );
    if (flushEnrollment) {
      setIsVoiceEnrolled(false);
      if (userId.trim()) {
        try {
          window.localStorage.removeItem(`voiceEnrolled:${userId.trim()}`);
        } catch {
          /* ignore storage */
        }
      }
    }
  };

  if (authenticated) {
    return <Navigate to="/profile" replace />;
  }

  const stopRecording = () => {
    const recorder = mediaRecorderRef.current;
    if (recorder && recorder.state !== "inactive") {
      recorder.stop();
    }
    if (recordingTimerRef.current) {
      clearInterval(recordingTimerRef.current);
      recordingTimerRef.current = null;
    }
  };

  const startRecording = async () => {
    if (authMode === "voice") {
      setError("");
    }
    if (!navigator.mediaDevices?.getUserMedia) {
      setRecordingStatus(strings.voiceLogin.recording.statusNotSupported);
      return;
    }

    if (recordingTimerRef.current) {
      clearInterval(recordingTimerRef.current);
      recordingTimerRef.current = null;
    }
    setRecordingProgress(0);

    setRecordingStatus(strings.voiceLogin.recording.statusRequesting);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      chunksRef.current = [];
      recorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunksRef.current.push(event.data);
        }
      };
      recorder.onstop = async () => {
        if (recordingTimerRef.current) {
          clearInterval(recordingTimerRef.current);
          recordingTimerRef.current = null;
        }
        try {
          const blob = new Blob(chunksRef.current, { type: "audio/webm" });
          // debug: log raw blob info
          // eslint-disable-next-line no-console
          console.debug("recorder.onstop: rawBlob", { size: blob.size, type: blob.type });
          const { wavBlob, duration } = await convertBlobToWav(blob);
          // debug: log wavBlob info
          // eslint-disable-next-line no-console
          console.debug("recorder.onstop: wavBlob", { size: wavBlob.size, type: wavBlob.type, duration });
          // Always use the first recording - no double recording needed
          setVoiceBlob(wavBlob);
          // make blob reachable from devtools for quick inspection
          try {
            // eslint-disable-next-line no-undef
            window.__lastVoiceBlob = wavBlob;
          } catch {
            // ignore
          }
          const label = `${strings.voiceLogin.controls.sampleReady} · ${(duration ?? 0).toFixed(1)}s`;
          setVoiceSummary(label);
          setRecordingStatus(""); // Clear status - don't show "confirmed" until login is clicked
          setRecordingProgress(1);
        } catch (processingError) {
          setRecordingStatus(
            processingError?.message || strings.voiceLogin.recording.statusError,
          );
        } finally {
          stream.getTracks().forEach((track) => track.stop());
          setRecordingState("captured");
        }
      };
      recorder.start();
      mediaRecorderRef.current = recorder;
      setRecordingState("recording");
      recordingStartRef.current = Date.now();
      recordingTimerRef.current = setInterval(() => {
        const elapsed = Date.now() - recordingStartRef.current;
        setRecordingProgress(Math.min(elapsed / MAX_RECORDING_MS, 1));
      }, 60);
      setRecordingStatus(strings.voiceLogin.recording.statusNormal);
      setTimeout(() => {
        if (mediaRecorderRef.current === recorder && recorder.state === "recording") {
          stopRecording();
        }
      }, MAX_RECORDING_MS);
    } catch (permissionError) {
      setRecordingState("idle");
      if (recordingTimerRef.current) {
        clearInterval(recordingTimerRef.current);
        recordingTimerRef.current = null;
      }
      setRecordingStatus(
        permissionError?.message || strings.voiceLogin.recording.statusPermissionDenied,
      );
    }
  };

  const credentialInputsDisabled = awaitingOtp || isSubmitting || isVerifyingVoice;
  const otpToggleDisabled = isSubmitting || isVerifyingVoice;

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError("");
    if (isSubmitting) return;

    if (!awaitingOtp) {
      // debug: show current voice state
      // eslint-disable-next-line no-console
      console.debug("handleSubmit: voiceBlob", { voiceBlob, voiceCaptureStep, recordingState, voiceSummary });
      if (!userId.trim()) {
        setError(strings.errors.noUserId);
        return;
      }
      if (authMode === "password") {
        if (!verifyPasswordLocally(password)) {
          setError(strings.errors.invalidPassword);
          return;
        }
      } else if (!voiceBlob) {
        setError(strings.voiceLogin.errors.noVoiceSample);
        return;
      }

      const validationPayload = {
        userId: userId.trim(),
        password: authMode === "password" ? password.trim() : "",
        authMode,
      };

      if (authMode === "voice") {
        validationPayload.voiceSampleBlob = voiceBlob;
        setIsVerifyingVoice(true);
        setRecordingStatus(strings.voiceLogin.recording.statusConfirmed); // Show confirmation message when verification starts
      }

      try {
        const preliminary = await onAuthenticate({
          ...validationPayload,
          validateOnly: true,
        });

        if (!preliminary?.success) {
          // Filter out voice-related errors when in password mode
          let errorMessage = preliminary?.message || strings.errors.credentialsError;
          if (authMode === "password" && errorMessage.toLowerCase().includes("voice")) {
            errorMessage = strings.errors.credentialsError;
          }
          setError(errorMessage);
          setRecordingStatus(""); // Clear status on error
          return;
        }
      } finally {
        if (authMode === "voice") {
          setIsVerifyingVoice(false);
        }
      }

      setAwaitingOtp(true);
      setOtp("");
      setTimeout(() => otpInputRef.current?.focus(), 150);
      return;
    }

    if (otp.trim() !== FIXED_OTP) {
      setError(strings.errors.invalidOtp);
      return;
    }

    setIsSubmitting(true);
    // Don't show "verifying voice" during OTP submission - voice was already verified in preliminary step
    // Only show it if we're doing voice verification (not in OTP step)
    if (authMode === "voice" && !awaitingOtp) {
      setIsVerifyingVoice(true);
    }

    try {
      const authPayload = {
        userId: userId.trim(),
        password: authMode === "password" ? password.trim() : "",
        authMode,
        otp: otp.trim(),
      };

      if (authMode === "voice") {
        authPayload.voiceSampleBlob = voiceBlob;
      }

      const result = await onAuthenticate(authPayload);

      // Debug logging for voice login OTP submission
      if (authMode === "voice") {
        console.log("[Voice Login] OTP submission result:", {
          success: result?.success,
          hasMessage: !!result?.message,
          message: result?.message,
          awaitingOtp,
        });
      }

      if (!result?.success) {
        // Filter out voice-related errors when in password mode
        let errorMessage = result?.message || strings.errors.authError;
        if (authMode === "password" && errorMessage.toLowerCase().includes("voice")) {
          errorMessage = strings.errors.authError;
        }
        console.error("[Voice Login] Authentication failed:", {
          authMode,
          errorMessage,
          result,
        });
        setError(errorMessage);
        setAwaitingOtp(false);
        // Don't reset authMode - keep it as voice so user can try again
        return;
      }
      
      // Success - for voice login, the App component will handle navigation
      if (authMode === "voice" && userId.trim()) {
        console.log("[Voice Login] Authentication successful, setting enrolled flag");
        setIsVoiceEnrolled(true);
        try {
          window.localStorage.setItem(`voiceEnrolled:${userId.trim()}`, "true");
        } catch (storageError) {
          console.warn("[Voice Login] Failed to save enrollment flag:", storageError);
        }
      }
      
      // Don't reset awaitingOtp on success - let App component handle navigation
      // The App component will navigate to /profile, which will unmount this component
    } catch (authError) {
      setError(
        authError?.message || strings.errors.serverError,
      );
      setAwaitingOtp(false);
    } finally {
      setIsSubmitting(false);
      // Only reset voice verification state if it was set
      if (authMode === "voice" && !awaitingOtp) {
        setIsVerifyingVoice(false);
      }
    }
  };

  const handleCancelOtp = () => {
    setAwaitingOtp(false);
    setOtp("");
    setError("");
  };

  return (
    <div className="app-shell">
      {/* Login Form Section - Moved to Top */}
      <div className="app-content app-content--login-first" ref={loginFormRef}>
        <div className="app-gradient">
          <SunHeader subtitle={strings.general.sunHeaderSubtitle} />
          <main className="card-surface">
            <div className="card-hero">
              <div className="card-hero__header">
                <h1>{strings.general.welcomeTitle}</h1>
                <LanguageDropdown
                  disabled={credentialInputsDisabled || recordingState === "recording"}
                  onSelect={handleLanguageChange}
                />
              </div>
              <p className="card-hero__subtitle">{strings.general.welcomeSubtitle}</p>
            </div>
            <div className="login-mode-switch-wrapper">
              <div className="login-mode-switch">
                <button
                  type="button"
                  className={`mode-chip ${authMode === "voice" ? "mode-chip--active" : ""}`}
                  onClick={() => !credentialInputsDisabled && setAuthMode("voice")}
                  disabled={credentialInputsDisabled}
                >
                  {strings.general.voiceLabel}
                </button>
                <button
                  type="button"
                  className={`mode-chip ${authMode === "password" ? "mode-chip--active" : ""}`}
                  onClick={() => !credentialInputsDisabled && setAuthMode("password")}
                  disabled={credentialInputsDisabled}
                >
                  {strings.general.passwordLabel}
                </button>
              </div>
            </div>
            <form className="card-form" onSubmit={handleSubmit} noValidate>
              <label htmlFor="userId">
                {strings.general.userIdLabel}
                <input
                  id="userId"
                  name="userId"
                  type="text"
                  autoComplete="username"
                  placeholder={strings.general.userIdPlaceholder}
                  value={userId}
                  onChange={(event) => setUserId(event.target.value)}
                  disabled={credentialInputsDisabled}
                />
              </label>
              {authMode === "password" && (
                <label htmlFor="password" className="input-with-toggle">
                  {strings.general.passwordLabel}
                  <div className="input-with-toggle__wrapper">
                    <input
                      id="password"
                      name="password"
                      type={showPassword ? "text" : "password"}
                      autoComplete="current-password"
                      placeholder={strings.general.passwordPlaceholder}
                      value={password}
                      onChange={(event) => setPassword(event.target.value)}
                      disabled={credentialInputsDisabled}
                    />
                    <button
                      type="button"
                      className="input-with-toggle__btn"
                      onClick={() => setShowPassword((prev) => !prev)}
                      aria-label={showPassword ? strings.general.hidePassword : strings.general.showPassword}
                    >
                      {showPassword ? strings.general.hidePassword : strings.general.showPassword}
                    </button>
                  </div>
                </label>
              )}
              {authMode === "voice" && (
                <div className="card-form__voice" ref={voiceSectionRef}>
                  <div className="voice-reference-box">
                    <p className="voice-reference-box__header">
                      {strings.voiceLogin.referenceBox.header}
                    </p>
                    <div className="voice-reference-box__line">
                      <span className="voice-reference-box__label">
                        {strings.voiceLogin.referenceBox.languageLabel}
                      </span>
                      <span className="voice-reference-box__phrase">{voicePhrase}</span>
                    </div>
                  </div>
                  <div className="voice-controls">
                    <button
                      className="secondary-btn"
                      type="button"
                      onClick={recordingState === "recording" ? stopRecording : startRecording}
                      disabled={credentialInputsDisabled || isVerifyingVoice}
                    >
                      {recordingState === "recording" 
                        ? strings.voiceLogin.controls.stopButton 
                        : strings.voiceLogin.controls.recordButton}
                    </button>
                    {voiceSummary && voiceBlob && (
                      <span className="profile-hint">
                        {voiceSummary}
                      </span>
                    )}
                    {voiceBlob && (
                      <span className="profile-hint">
                        {strings.voiceLogin.controls.captured} {Math.round(voiceBlob.size / 1024)} KB
                      </span>
                    )}
                  </div>
                  {isVerifyingVoice && !awaitingOtp && (
                    <div className="voice-verification-loader">
                      <div className="loader-spinner"></div>
                      <p className="voice-verification-message">
                        {strings.general.verifyingVoice}
                      </p>
                    </div>
                  )}
                  {recordingState === "recording" && (
                    <div className="voice-meter">
                      <div className="voice-meter__wave" aria-hidden="true" />
                      <div className="voice-meter__bar">
                        <div
                          className="voice-meter__progress"
                          style={{ width: `${Math.min(recordingProgress * 100, 100)}%` }}
                        />
                      </div>
                      <span className="voice-meter__time">
                        {Math.min(
                          Math.round((recordingProgress * MAX_RECORDING_MS) / 1000),
                          MAX_RECORDING_MS / 1000,
                        )}
                        s / {MAX_RECORDING_MS / 1000}s
                      </span>
                    </div>
                  )}
                  {recordingStatus && <p className="profile-hint">{recordingStatus}</p>}
                  <button
                    type="button"
                    className="link-btn"
                    onClick={() => resetVoiceCapture(1, true)}
                    disabled={credentialInputsDisabled}
                  >
                    {strings.voiceLogin.controls.resetButton}
                  </button>
                </div>
              )}
              {awaitingOtp && (
                <label htmlFor="otp" className="input-with-toggle">
                  {strings.general.otpLabel}
                  <div className="input-with-toggle__wrapper">
                    <input
                      id="otp"
                      name="otp"
                      type={showOtp ? "text" : "password"}
                      placeholder={strings.general.otpPlaceholder}
                      value={otp}
                      onChange={(event) => setOtp(event.target.value)}
                      ref={otpInputRef}
                    />
                    <button
                      type="button"
                      className="input-with-toggle__btn"
                      onClick={() => setShowOtp((prev) => !prev)}
                      aria-label={showOtp ? strings.general.hideOtp : strings.general.showOtp}
                      disabled={otpToggleDisabled}
                    >
                      {showOtp ? strings.general.hideOtp : strings.general.showOtp}
                    </button>
                  </div>
                </label>
              )}
              {error && <div className="form-error">{error}</div>}
              <div className="card-form__actions">
                <button className="primary-btn" type="submit" disabled={isSubmitting || isVerifyingVoice}>
                  {isVerifyingVoice 
                    ? strings.general.verifyingVoice
                    : awaitingOtp 
                      ? (isSubmitting ? strings.general.verifying : strings.general.verifyOtpButton) 
                      : strings.general.loginButton}
                </button>
                {awaitingOtp && (
                  <button
                    type="button"
                    className="secondary-btn"
                    onClick={handleCancelOtp}
                    disabled={isSubmitting}
                  >
                    {strings.general.editDetails}
                  </button>
                )}
              </div>
              {!awaitingOtp && (
                <div className="card-form__meta">
                  <Link className="muted-link" to="/sign-in-help">
                    {strings.general.needHelp}
                  </Link>
                </div>
              )}
            </form>
          </main>
        </div>
        
        {/* Scroll Indicator - Positioned below login card */}
        <div className={`scroll-indicator-wrapper ${!showScrollHint ? 'fade-out' : ''}`}>
          <div className="scroll-indicator">
            <button 
              type="button"
              className="scroll-indicator__button"
              onClick={scrollToHero}
              aria-label={strings.general.scrollDown}
            >
              <span className="scroll-indicator__text">{strings.general.scrollHint}</span>
              <svg 
                className="scroll-indicator__arrow" 
                width="20" 
                height="20" 
                viewBox="0 0 24 24" 
                fill="none"
                aria-hidden="true"
              >
                <path 
                  d="M7 10l5 5 5-5" 
                  stroke="currentColor" 
                  strokeWidth="2" 
                  strokeLinecap="round" 
                  strokeLinejoin="round"
                />
              </svg>
            </button>
            <div className="scroll-indicator__pulse"></div>
          </div>
        </div>
      </div>

      {/* Hero Section with Image - Moved Below Login Form */}
      <div className="login-hero-section login-hero-section--below">
        <div className="login-hero-image">
          <div className="login-hero-overlay"></div>
        </div>
        <div className="login-hero-content">
          <h1 className="login-hero-title">
            <span className="login-hero-title__english">{strings.hero.titleEnglish}</span>
            <span className="login-hero-title__hindi">{strings.hero.titleHindi}</span>
          </h1>
          <div className="login-hero-languages">
            <span className="language-tag language-tag--primary">{strings.hero.languageTagEnglish}</span>
            <span className="language-tag language-tag--primary">{strings.hero.languageTagHindi}</span>
            <span className="language-tag language-tag--extendable">{strings.hero.languageTagMore}</span>
          </div>
          <p className="login-hero-subtitle">
            <span className="login-hero-subtitle__text">{strings.hero.subtitleText}</span>
            <span className="login-hero-subtitle__hint">{strings.hero.subtitleHint}</span>
          </p>
          <p className="login-hero-tagline">{strings.hero.tagline}</p>
        </div>
      </div>
      
      {/* Products and Services Sections */}
      <div className="products-services-container">
        {/* Vaani AI Assistant Highlight Section */}
        <section className="feature-section vaani-highlight">
          <div className="feature-section__content">
            <div className="feature-section__text">
              <span className="feature-section__badge">{strings.vaani.badge}</span>
              <h2 className="feature-section__title">{strings.vaani.title}</h2>
              <p className="feature-section__description">
                {strings.vaani.description}
              </p>
              <ul className="feature-section__features">
                <li>
                  <svg className="feature-icon" width="20" height="20" viewBox="0 0 24 24" fill="none">
                    <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z" fill="#ff8f42"/>
                  </svg>
                  {strings.vaani.feature1}
                </li>
                <li>
                  <svg className="feature-icon" width="20" height="20" viewBox="0 0 24 24" fill="none">
                    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z" fill="#ff8f42"/>
                  </svg>
                  {strings.vaani.feature2}
                </li>
                <li>
                  <svg className="feature-icon" width="20" height="20" viewBox="0 0 24 24" fill="none">
                    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.94-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z" fill="#ff8f42"/>
                  </svg>
                  {strings.vaani.feature3}
                </li>
                <li>
                  <svg className="feature-icon" width="20" height="20" viewBox="0 0 24 24" fill="none">
                    <path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm-2 12H6l-2 2V4h16v10z" fill="#ff8f42"/>
                  </svg>
                  {strings.vaani.feature4}
                </li>
              </ul>
            </div>
            <div className="feature-section__visual">
              <div className="vaani-visual-card">
                <AIAssistantLogo size={120} showAssistant={true} />
              </div>
            </div>
          </div>
        </section>

        {/* Loan Products Section */}
        <section className="products-section">
          <div className="products-section__header">
            <h2 className="products-section__title">{strings.loans.title}</h2>
            <p className="products-section__subtitle">{strings.loans.subtitle}</p>
          </div>
          <div className="products-grid">
            <div className="product-card">
              <div className="product-card__icon">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none">
                  <path d="M10 20v-6h4v6h5v-8h3L12 3 2 12h3v8z" fill="#ff8f42"/>
                </svg>
              </div>
              <h3 className="product-card__title">{strings.loans.homeLoan.title}</h3>
              <p className="product-card__rate">{strings.loans.homeLoan.rate}</p>
              <p className="product-card__description">{strings.loans.homeLoan.description}</p>
            </div>
            <div className="product-card">
              <div className="product-card__icon">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none">
                  <path d="M18.92 6.01C18.72 5.42 18.16 5 17.5 5h-11c-.66 0-1.21.42-1.42 1.01L3 12v8c0 .55.45 1 1 1h1c.55 0 1-.45 1-1v-1h12v1c0 .55.45 1 1 1h1c.55 0 1-.45 1-1v-8l-2.08-5.99zM6.5 16c-.83 0-1.5-.67-1.5-1.5S5.67 13 6.5 13s1.5.67 1.5 1.5S7.33 16 6.5 16zm11 0c-.83 0-1.5-.67-1.5-1.5s.67-1.5 1.5-1.5 1.5.67 1.5 1.5-.67 1.5-1.5 1.5zM5 11l1.5-4.5h11L19 11H5z" fill="#ff8f42"/>
                </svg>
              </div>
              <h3 className="product-card__title">{strings.loans.autoLoan.title}</h3>
              <p className="product-card__rate">{strings.loans.autoLoan.rate}</p>
              <p className="product-card__description">{strings.loans.autoLoan.description}</p>
            </div>
            <div className="product-card">
              <div className="product-card__icon">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none">
                  <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z" fill="#ff8f42"/>
                </svg>
              </div>
              <h3 className="product-card__title">{strings.loans.personalLoan.title}</h3>
              <p className="product-card__rate">{strings.loans.personalLoan.rate}</p>
              <p className="product-card__description">{strings.loans.personalLoan.description}</p>
            </div>
            <div className="product-card">
              <div className="product-card__icon">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none">
                  <path d="M5 13.18v4L12 21l7-3.82v-4L12 17l-7-3.82zM12 3L1 9l11 6 9-4.91V17h2V9L12 3z" fill="#ff8f42"/>
                </svg>
              </div>
              <h3 className="product-card__title">{strings.loans.educationLoan.title}</h3>
              <p className="product-card__rate">{strings.loans.educationLoan.rate}</p>
              <p className="product-card__description">{strings.loans.educationLoan.description}</p>
            </div>
            <div className="product-card">
              <div className="product-card__icon">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none">
                  {/* Shop/Store building */}
                  <path d="M5 8h14v13H5V8z" fill="#ff8f42" opacity="0.2"/>
                  <path d="M5 8h14v13H5V8z" stroke="#ff8f42" strokeWidth="1.5" fill="none"/>
                  {/* Roof */}
                  <path d="M3 8l9-4 9 4v2H3V8z" fill="#ff8f42"/>
                  {/* Door */}
                  <rect x="10" y="14" width="4" height="7" rx="0.5" fill="#ff8f42"/>
                  {/* Windows */}
                  <rect x="6" y="10" width="2.5" height="2.5" rx="0.3" fill="#ff8f42" opacity="0.6"/>
                  <rect x="15.5" y="10" width="2.5" height="2.5" rx="0.3" fill="#ff8f42" opacity="0.6"/>
                  {/* Sign board */}
                  <rect x="8" y="6" width="8" height="2" rx="0.5" fill="#ff8f42" opacity="0.8"/>
                </svg>
              </div>
              <h3 className="product-card__title">{strings.loans.businessLoan.title}</h3>
              <p className="product-card__rate">{strings.loans.businessLoan.rate}</p>
              <p className="product-card__description">{strings.loans.businessLoan.description}</p>
            </div>
            <div className="product-card">
              <div className="product-card__icon">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none">
                  {/* Gold coin/ornament */}
                  <circle cx="12" cy="12" r="8" fill="#ff8f42" opacity="0.3"/>
                  <circle cx="12" cy="12" r="6.5" fill="#ff8f42"/>
                  {/* Decorative pattern - Indian style */}
                  <circle cx="12" cy="12" r="4" fill="none" stroke="#ffffff" strokeWidth="1.5" opacity="0.8"/>
                  <circle cx="12" cy="12" r="2.5" fill="#ffffff" opacity="0.9"/>
                  {/* Small decorative dots */}
                  <circle cx="12" cy="7" r="0.8" fill="#ffffff" opacity="0.8"/>
                  <circle cx="12" cy="17" r="0.8" fill="#ffffff" opacity="0.8"/>
                  <circle cx="7" cy="12" r="0.8" fill="#ffffff" opacity="0.8"/>
                  <circle cx="17" cy="12" r="0.8" fill="#ffffff" opacity="0.8"/>
                </svg>
              </div>
              <h3 className="product-card__title">{strings.loans.goldLoan.title}</h3>
              <p className="product-card__rate">{strings.loans.goldLoan.rate}</p>
              <p className="product-card__description">{strings.loans.goldLoan.description}</p>
            </div>
            <div className="product-card">
              <div className="product-card__icon">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none">
                  <path d="M12 7V3H2v18h20V7H12zM6 19H4v-2h2v2zm0-4H4v-2h2v2zm0-4H4V9h2v2zm0-4H4V5h2v2zm4 12H8v-2h2v2zm0-4H8v-2h2v2zm0-4H8V9h2v2zm0-4H8V5h2v2zm10 12h-8v-2h2v-2h-2v-2h2v-2h-2V9h8v10zm-2-8h-2v2h2v-2zm0 4h-2v2h2v-2z" fill="#ff8f42"/>
                </svg>
              </div>
              <h3 className="product-card__title">{strings.loans.loanAgainstProperty.title}</h3>
              <p className="product-card__rate">{strings.loans.loanAgainstProperty.rate}</p>
              <p className="product-card__description">{strings.loans.loanAgainstProperty.description}</p>
            </div>
          </div>
        </section>

        {/* Investment Schemes Section */}
        <section className="products-section investment-section">
          <div className="products-section__header">
            <h2 className="products-section__title">{strings.investments.title}</h2>
            <p className="products-section__subtitle">{strings.investments.subtitle}</p>
          </div>
          <div className="products-grid">
            <div className="product-card investment-card">
              <div className="product-card__icon">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none">
                  {/* Piggy bank / Savings jar */}
                  <path d="M8 4h8c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H8c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z" fill="#ff8f42" opacity="0.2"/>
                  <path d="M8 4h8c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H8c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z" stroke="#ff8f42" strokeWidth="1.5" fill="none"/>
                  {/* Top opening */}
                  <ellipse cx="12" cy="6" rx="3" ry="1.5" fill="#ff8f42" opacity="0.4"/>
                  {/* Coin slot */}
                  <rect x="11" y="3" width="2" height="4" rx="1" fill="#ff8f42"/>
                  {/* Coins inside */}
                  <circle cx="10" cy="11" r="1.5" fill="#ff8f42" opacity="0.6"/>
                  <circle cx="14" cy="13" r="1.5" fill="#ff8f42" opacity="0.6"/>
                  <circle cx="12" cy="16" r="1.5" fill="#ff8f42" opacity="0.6"/>
                  {/* Base */}
                  <ellipse cx="12" cy="20" rx="4" ry="1" fill="#ff8f42" opacity="0.3"/>
                </svg>
              </div>
              <h3 className="product-card__title">{strings.investments.ppf.title}</h3>
              <p className="product-card__rate">{strings.investments.ppf.rate}</p>
              <p className="product-card__description">{strings.investments.ppf.description}</p>
            </div>
            <div className="product-card investment-card">
              <div className="product-card__icon">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none">
                  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z" fill="#ff8f42"/>
                  <circle cx="12" cy="12" r="10" stroke="#ff8f42" strokeWidth="2" fill="none"/>
                </svg>
              </div>
              <h3 className="product-card__title">{strings.investments.nps.title}</h3>
              <p className="product-card__rate">{strings.investments.nps.rate}</p>
              <p className="product-card__description">{strings.investments.nps.description}</p>
            </div>
            <div className="product-card investment-card">
              <div className="product-card__icon">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none">
                  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 3c1.66 0 3 1.34 3 3s-1.34 3-3 3-3-1.34-3-3 1.34-3 3-3zm0 14.2c-2.5 0-4.71-1.28-6-3.22.03-1.99 4-3.08 6-3.08 1.99 0 5.97 1.09 6 3.08-1.29 1.94-3.5 3.22-6 3.22z" fill="#ff8f42"/>
                </svg>
              </div>
              <h3 className="product-card__title">{strings.investments.ssy.title}</h3>
              <p className="product-card__rate">{strings.investments.ssy.rate}</p>
              <p className="product-card__description">{strings.investments.ssy.description}</p>
            </div>
            <div className="product-card investment-card">
              <div className="product-card__icon">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none">
                  <path d="M16 6l2.29 2.29-4.88 4.88-4-4L2 16.59 3.41 18l6-6 4 4 6.3-6.29L22 12V6z" fill="#ff8f42"/>
                </svg>
              </div>
              <h3 className="product-card__title">{strings.investments.elss.title}</h3>
              <p className="product-card__rate">{strings.investments.elss.rate}</p>
              <p className="product-card__description">{strings.investments.elss.description}</p>
            </div>
            <div className="product-card investment-card">
              <div className="product-card__icon">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none">
                  <path d="M20 4H4c-1.11 0-1.99.89-1.99 2L2 18c0 1.11.89 2 2 2h16c1.11 0 2-.89 2-2V6c0-1.11-.89-2-2-2zm0 14H4v-6h16v6zm0-10H4V6h16v2z" fill="#ff8f42"/>
                </svg>
              </div>
              <h3 className="product-card__title">{strings.investments.fixedDeposit.title}</h3>
              <p className="product-card__rate">{strings.investments.fixedDeposit.rate}</p>
              <p className="product-card__description">{strings.investments.fixedDeposit.description}</p>
            </div>
            <div className="product-card investment-card">
              <div className="product-card__icon">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none">
                  <path d="M19 3h-1V1h-2v2H8V1H6v2H5c-1.11 0-1.99.9-1.99 2L3 19c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V8h14v11zM7 10h5v5H7z" fill="#ff8f42"/>
                </svg>
              </div>
              <h3 className="product-card__title">{strings.investments.recurringDeposit.title}</h3>
              <p className="product-card__rate">{strings.investments.recurringDeposit.rate}</p>
              <p className="product-card__description">{strings.investments.recurringDeposit.description}</p>
            </div>
            <div className="product-card investment-card">
              <div className="product-card__icon">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none">
                  <path d="M12 7V3H2v18h20V7H12zM6 19H4v-2h2v2zm0-4H4v-2h2v2zm0-4H4V9h2v2zm4 12H8v-2h2v2zm0-4H8v-2h2v2zm0-4H8V9h2v2zm0-4H8V5h2v2zm10 12h-8v-2h2v-2h-2v-2h2v-2h-2V9h8v10zm-2-8h-2v2h2v-2zm0 4h-2v2h2v-2z" fill="#ff8f42"/>
                </svg>
              </div>
              <h3 className="product-card__title">{strings.investments.nsc.title}</h3>
              <p className="product-card__rate">{strings.investments.nsc.rate}</p>
              <p className="product-card__description">{strings.investments.nsc.description}</p>
            </div>
          </div>
        </section>
      </div>

      <footer className="app-footer">
        {strings.footer.text.replace("{year}", new Date().getFullYear().toString())}
      </footer>
    </div>
  );
};

Login.propTypes = {
  onAuthenticate: PropTypes.func.isRequired,
  authenticated: PropTypes.bool,
};

Login.defaultProps = {
  authenticated: false,
};

export default Login;


