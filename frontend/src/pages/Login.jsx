import { useEffect, useRef, useState } from "react";
import PropTypes from "prop-types";
import { Link, Navigate } from "react-router-dom";

import SunHeader from "../components/SunHeader.jsx";

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
const VOICE_PHRASE_HINDI = "सन बैंक मेरा साथी, हर कदम सुरक्षित बैंकिंग का वादा";
const VOICE_PHRASE_ENGLISH = "Sun Bank is my companion, a promise of secure banking at every step";
const VOICE_PHRASE = `${VOICE_PHRASE_HINDI} or ${VOICE_PHRASE_ENGLISH}`;
const FIXED_OTP = "12345";

const Login = ({ onAuthenticate, authenticated }) => {
  const [authMode, setAuthMode] = useState("password");
  const [userId, setUserId] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
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
      resetVoiceCapture(enrolled ? 2 : 1);
      requestAnimationFrame(() => {
        if (voiceSectionRef.current) {
          voiceSectionRef.current.scrollIntoView({ behavior: "smooth", block: "center" });
        }
      });
    } else if (authMode !== "voice") {
      resetVoiceCapture(1);
      setIsVoiceEnrolled(false);
    }
    setError("");
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
      setRecordingStatus("Microphone access is not supported on this device.");
      return;
    }

    if (recordingTimerRef.current) {
      clearInterval(recordingTimerRef.current);
      recordingTimerRef.current = null;
    }
    setRecordingProgress(0);

    setRecordingStatus("Requesting microphone access…");
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
          if (voiceCaptureStep === 1) {
            setFirstVoiceSummary(`Sample 1 ready · ${(duration ?? 0).toFixed(1)}s`);
            setRecordingStatus(
              'First sample captured. Please re-record the passphrase to confirm your voice.',
            );
            setVoiceCaptureStep(2);
            setVoiceBlob(null);
            setVoiceSummary("");
          } else {
            setVoiceBlob(wavBlob);
            // make blob reachable from devtools for quick inspection
            try {
              // eslint-disable-next-line no-undef
              window.__lastVoiceBlob = wavBlob;
            } catch {
              // ignore
            }
            const label =
              isFirstVoiceLogin && voiceCaptureStep === 2
                ? `Sample 2 ready · ${(duration ?? 0).toFixed(1)}s`
                : `Sample ready · ${(duration ?? 0).toFixed(1)}s`;
            setVoiceSummary(label);
            setRecordingStatus("Voice sample confirmed. You can proceed to login.");
          }
          setRecordingProgress(1);
        } catch (processingError) {
          setRecordingStatus(
            processingError?.message || "Unable to process the voice sample.",
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
      if (voiceCaptureStep === 1) {
    setRecordingStatus(`Recording… Speak clearly: "${VOICE_PHRASE_HINDI}" or "${VOICE_PHRASE_ENGLISH}"`);
      } else {
        setRecordingStatus("Recording… Speak naturally in your own words.");
      }
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
        permissionError?.message || "Microphone permission denied by the browser.",
      );
    }
  };

  const credentialInputsDisabled = awaitingOtp || isSubmitting;

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError("");
    if (isSubmitting) return;

    if (!awaitingOtp) {
      // debug: show current voice state
      // eslint-disable-next-line no-console
      console.debug("handleSubmit: voiceBlob", { voiceBlob, voiceCaptureStep, recordingState, voiceSummary });
      if (!userId.trim()) {
        setError("Please enter your User ID to continue.");
        return;
      }
      if (authMode === "password") {
        if (!verifyPasswordLocally(password)) {
          setError("Enter a valid password (minimum 4 characters).");
          return;
        }
      } else if (!voiceBlob) {
        setError(
          "Please capture and confirm your voice sample before continuing. (If this is your first time enrolling for voice login, record the passphrase twice.)",
        );
        return;
      }

      const validationPayload = {
        userId: userId.trim(),
        password: authMode === "password" ? password.trim() : "",
        authMode,
      };

      if (authMode === "voice") {
        validationPayload.voiceSampleBlob = voiceBlob;
      }

      const preliminary = await onAuthenticate({
        ...validationPayload,
        validateOnly: true,
      });

      if (!preliminary?.success) {
        setError(preliminary?.message || "Credentials could not be verified. Try again.");
        return;
      }

      setAwaitingOtp(true);
      setOtp("");
      setTimeout(() => otpInputRef.current?.focus(), 150);
      return;
    }

    if (otp.trim() !== FIXED_OTP) {
      setError("The OTP you entered is incorrect. Please try again.");
      return;
    }

    setIsSubmitting(true);

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

      if (!result?.success) {
        setError(result?.message || "We could not verify those credentials. Try again.");
        setAwaitingOtp(false);
      } else if (authMode === "voice" && userId.trim()) {
        setIsVoiceEnrolled(true);
        window.localStorage.setItem(`voiceEnrolled:${userId.trim()}`, "true");
      }
    } catch (authError) {
      setError(
        authError?.message ||
          "Something went wrong while contacting the bank. Please try again.",
      );
      setAwaitingOtp(false);
    } finally {
      setIsSubmitting(false);
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
              <h1>Welcome back.</h1>
              <p>Sign in to continue to your Sun National Bank profile.</p>
            </div>
            <div className="login-mode-switch">
              <button
                type="button"
                className={`mode-chip ${authMode === "password" ? "mode-chip--active" : ""}`}
                onClick={() => !credentialInputsDisabled && setAuthMode("password")}
                disabled={credentialInputsDisabled}
              >
                Password
              </button>
              <button
                type="button"
                className={`mode-chip ${authMode === "voice" ? "mode-chip--active" : ""}`}
                onClick={() => !credentialInputsDisabled && setAuthMode("voice")}
                disabled={credentialInputsDisabled}
              >
                Voice
              </button>
            </div>
            <form className="card-form" onSubmit={handleSubmit} noValidate>
              <label htmlFor="userId">
                User ID
                <input
                  id="userId"
                  name="userId"
                  type="text"
                  autoComplete="username"
                  placeholder="Enter your customer ID"
                  value={userId}
                  onChange={(event) => setUserId(event.target.value)}
                  disabled={credentialInputsDisabled}
                />
              </label>
              {authMode === "password" && (
                <label htmlFor="password" className="input-with-toggle">
                  Password
                  <div className="input-with-toggle__wrapper">
                    <input
                      id="password"
                      name="password"
                      type={showPassword ? "text" : "password"}
                      autoComplete="current-password"
                      placeholder="Enter your password"
                      value={password}
                      onChange={(event) => setPassword(event.target.value)}
                      disabled={credentialInputsDisabled}
                    />
                    <button
                      type="button"
                      className="input-with-toggle__btn"
                      onClick={() => setShowPassword((prev) => !prev)}
                      aria-label={showPassword ? "Hide password" : "Show password"}
                    >
                      {showPassword ? "Hide" : "Show"}
                    </button>
                  </div>
                </label>
              )}
              {authMode === "voice" && (
                <div className="card-form__voice" ref={voiceSectionRef}>
                  {isFirstVoiceLogin ? (
                    <div className="info-banner">
                      First time with voice login? We’ll capture the passphrase
                      <strong> {VOICE_PHRASE_HINDI}</strong> or <strong> {VOICE_PHRASE_ENGLISH}</strong>
                      twice to enroll your voice securely. From the next login you can speak any short phrase.
                    </div>
                  ) : (
                    <p className="profile-hint">
                      Speak in your normal voice—any short phrase works for quick verification.
                    </p>
                  )}
                  <div className="voice-controls">
                    <button
                      className="secondary-btn"
                      type="button"
                      onClick={recordingState === "recording" ? stopRecording : startRecording}
                      disabled={credentialInputsDisabled}
                    >
                      {recordingState === "recording" ? "Stop recording" : "Record voice sample"}
                    </button>
                    {voiceCaptureStep === 2 && !voiceBlob && firstVoiceSummary && (
                      <span className="profile-hint">{firstVoiceSummary}</span>
                    )}
                    {voiceSummary && voiceBlob && (
                      <span className="profile-hint">
                        {voiceSummary}
                      </span>
                    )}
                    {voiceBlob && (
                      <span className="profile-hint">
                        Captured {Math.round(voiceBlob.size / 1024)} KB
                      </span>
                    )}
                  </div>
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
                    Reset voice capture
                  </button>
                </div>
              )}
              {awaitingOtp && (
                <label htmlFor="otp" className="input-with-toggle">
                  Enter OTP
                  <div className="input-with-toggle__wrapper">
                    <input
                      id="otp"
                      name="otp"
                      type={showOtp ? "text" : "password"}
                      placeholder="Enter the 5-digit OTP"
                      value={otp}
                      onChange={(event) => setOtp(event.target.value)}
                      ref={otpInputRef}
                    />
                    <button
                      type="button"
                      className="input-with-toggle__btn"
                      onClick={() => setShowOtp((prev) => !prev)}
                      aria-label={showOtp ? "Hide OTP" : "Show OTP"}
                    >
                      {showOtp ? "Hide" : "Show"}
                    </button>
                  </div>
                </label>
              )}
              {error && <div className="form-error">{error}</div>}
              <div className="card-form__actions">
                <button className="primary-btn" type="submit" disabled={isSubmitting}>
                  {awaitingOtp ? (isSubmitting ? "Verifying…" : "Verify OTP") : "Log in"}
                </button>
                {awaitingOtp && (
                  <button
                    type="button"
                    className="secondary-btn"
                    onClick={handleCancelOtp}
                    disabled={isSubmitting}
                  >
                    Edit details
                  </button>
                )}
              </div>
              {!awaitingOtp && (
                <div className="card-form__meta">
                  <Link className="muted-link" to="/sign-in-help">
                    Need help signing in?
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


