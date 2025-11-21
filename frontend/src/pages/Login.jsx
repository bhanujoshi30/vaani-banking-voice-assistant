import { useEffect, useRef, useState } from "react";
import PropTypes from "prop-types";
import { Link, Navigate } from "react-router-dom";

import SunHeader from "../components/SunHeader.jsx";
import LanguageDropdown from "../components/LanguageDropdown.jsx";
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
  
  const [authMode, setAuthMode] = useState("password");
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
      <div className="app-content">
        <div className="app-gradient">
          <SunHeader subtitle="Voice-first banking, made human." />
          <main className="card-surface">
            <div className="card-hero">
              <div className="card-hero__header">
                <h1>{strings.general.welcomeTitle}</h1>
                <LanguageDropdown
                  disabled={credentialInputsDisabled || recordingState === "recording"}
                  onSelect={handleLanguageChange}
                />
              </div>
              <p>{strings.general.welcomeSubtitle}</p>
            </div>
            <div className="login-mode-switch">
              <button
                type="button"
                className={`mode-chip ${authMode === "password" ? "mode-chip--active" : ""}`}
                onClick={() => !credentialInputsDisabled && setAuthMode("password")}
                disabled={credentialInputsDisabled}
              >
                {strings.general.passwordLabel}
              </button>
              <button
                type="button"
                className={`mode-chip ${authMode === "voice" ? "mode-chip--active" : ""}`}
                onClick={() => !credentialInputsDisabled && setAuthMode("voice")}
                disabled={credentialInputsDisabled}
              >
                {strings.general.voiceLabel}
              </button>
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
                      disabled={credentialInputsDisabled}
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
      </div>
      <footer className="app-footer">
        © {new Date().getFullYear()} Sun National Bank · RBI compliant · Made for Bharat
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


