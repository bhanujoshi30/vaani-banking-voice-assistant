import PropTypes from "prop-types";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { Navigate, useNavigate } from "react-router-dom";

import SunHeader from "../components/SunHeader.jsx";
import LanguageDropdown from "../components/LanguageDropdown.jsx";
import {
  listDeviceBindings,
  registerDeviceBinding,
  revokeDeviceBinding,
} from "../api/client.js";
import { usePageLanguage } from "../hooks/usePageLanguage.js";
import { getVoicePhrase } from "../config/loginStrings.js";

const SESSION_EXPIRY_CODES = new Set([
  "session_timeout",
  "session_expired",
  "session_inactive",
  "session_invalid",
]);

const MAX_RECORDING_MS = 7000;

const hashText = async (text) => {
  const encoder = new TextEncoder();
  const data = encoder.encode(text);
  if (window.crypto?.subtle) {
    const digest = await window.crypto.subtle.digest("SHA-256", data);
    return Array.from(new Uint8Array(digest))
      .map((b) => b.toString(16).padStart(2, "0"))
      .join("");
  }
  return window.btoa(unescape(encodeURIComponent(text)));
};

const buildFingerprintSource = () => {
  const { userAgent, language, platform } = navigator;
  const screenInfo = window.screen
    ? `${window.screen.width}x${window.screen.height}-${window.devicePixelRatio}`
    : "unknown-screen";
  return `${userAgent}::${language}::${platform}::${screenInfo}`;
};

const inferPlatform = () => {
  const ua = navigator.userAgent.toLowerCase();
  if (ua.includes("android")) return "android";
  if (ua.includes("iphone") || ua.includes("ipad")) return "ios";
  if (ua.includes("windows")) return "windows";
  if (ua.includes("mac os")) return "macos";
  return "web";
};

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

const DeviceBindingPage = ({ session, onSignOut }) => {
  const navigate = useNavigate();
  const { strings, language } = usePageLanguage();
  const s = strings.deviceBinding;
  const voicePhrase = getVoicePhrase(language);
  const isAuthenticated = Boolean(session?.authenticated);
  const accessToken = session?.accessToken ?? null;

  const [bindings, setBindings] = useState([]);
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState({ type: null, message: "" });
  const [form, setForm] = useState({
    deviceLabel: "",
  });
  const [fingerprint, setFingerprint] = useState("");
  const [voiceBlob, setVoiceBlob] = useState(null);
  const [voiceHash, setVoiceHash] = useState("");
  const [voiceSummary, setVoiceSummary] = useState("");
  const [recordingState, setRecordingState] = useState("idle");
  const [recordingStatus, setRecordingStatus] = useState("");
  const platform = useMemo(() => inferPlatform(), []);
  const mediaRecorderRef = useRef(null);
  const chunksRef = useRef([]);

  const handleSessionExpiry = useCallback(
    (error) => {
      if (error?.code && SESSION_EXPIRY_CODES.has(error.code)) {
        setStatus({
          type: "error",
          message: s.sessionExpired || "Your session expired. Please sign in again to manage trusted devices.",
        });
        onSignOut?.();
        return true;
      }
      return false;
    },
    [onSignOut],
  );

  useEffect(() => {
    let mounted = true;
    const computeFingerprint = async () => {
      const source = buildFingerprintSource();
      const hash = await hashText(source);
      if (mounted) {
        setFingerprint(hash);
        setForm((prev) => ({
          ...prev,
          deviceLabel: prev.deviceLabel || "This device",
        }));
      }
    };
    computeFingerprint();
    return () => {
      mounted = false;
    };
  }, []);

  useEffect(() => {
    if (!isAuthenticated || !accessToken) {
      return undefined;
    }
    let mounted = true;

    const fetchBindings = async () => {
      setLoading(true);
      setStatus({ type: null, message: "" });
      try {
        const data = await listDeviceBindings({ accessToken });
        if (mounted) {
          setBindings(data);
        }
      } catch (error) {
        if (!mounted) return;
        if (handleSessionExpiry(error)) return;
        setStatus({ type: "error", message: error.message });
      } finally {
        if (mounted) {
          setLoading(false);
        }
      }
    };

    fetchBindings();
    return () => {
      mounted = false;
    };
  }, [accessToken, handleSessionExpiry, isAuthenticated]);

  useEffect(
    () => () => {
      const recorder = mediaRecorderRef.current;
      if (recorder && recorder.state !== "inactive") {
        recorder.stop();
      }
    },
    [],
  );

  const handleInputChange = (event) => {
    const { name, value } = event.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const hashArrayBuffer = async (arrayBuffer) => {
    if (window.crypto?.subtle) {
      const digest = await window.crypto.subtle.digest("SHA-256", arrayBuffer);
      return Array.from(new Uint8Array(digest))
        .map((b) => b.toString(16).padStart(2, "0"))
        .join("");
    }
    const binary = String.fromCharCode(...new Uint8Array(arrayBuffer));
    return window.btoa(binary);
  };

  const stopRecording = () => {
    const recorder = mediaRecorderRef.current;
    if (recorder && recorder.state !== "inactive") {
      recorder.stop();
    }
  };

  const startRecording = async () => {
    if (!navigator.mediaDevices?.getUserMedia) {
      setRecordingStatus("Microphone access is not supported on this device.");
      return;
    }

    setRecordingStatus("Requesting microphone access…");
    setVoiceBlob(null);
    setVoiceHash("");
    setVoiceSummary("");
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
        try {
          const blob = new Blob(chunksRef.current, { type: "audio/webm" });
          const { wavBlob, duration } = await convertBlobToWav(blob);
          const wavBuffer = await wavBlob.arrayBuffer();
          const hash = await hashArrayBuffer(wavBuffer);
          setVoiceBlob(wavBlob);
          setVoiceHash(hash);
          setVoiceSummary(`Sample ready · ${(duration ?? 0).toFixed(1)}s`);
          setRecordingStatus("Voice sample captured and secured.");
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
      const currentPhrase = getVoicePhrase(language);
      setRecordingStatus(`Recording… Speak clearly: "${currentPhrase}"`);
      setTimeout(() => {
        if (mediaRecorderRef.current === recorder && recorder.state === "recording") {
          stopRecording();
        }
      }, MAX_RECORDING_MS);
    } catch (permissionError) {
      setRecordingState("idle");
      setRecordingStatus(
        permissionError?.message || "Microphone permission denied by the browser.",
      );
    }
  };

  const handleRegister = async (event) => {
    event.preventDefault();
    if (!accessToken) return;
    if (!voiceBlob) {
      const currentPhrase = getVoicePhrase(language);
      setStatus({
        type: "error",
        message: `${s.pleaseRecord} "${currentPhrase}" ${s.beforeBinding}`,
      });
      return;
    }

    setLoading(true);
    setStatus({ type: null, message: "" });
    try {
      const binding = await registerDeviceBinding({
        accessToken,
        deviceIdentifier: fingerprint,
        fingerprintHash: fingerprint,
        deviceLabel: form.deviceLabel || "This device",
        platform,
        registrationMethod: "otp+voice",
        voiceSampleBlob: voiceBlob,
      });
      setBindings((prev) => {
        const filtered = prev.filter((item) => item.id !== binding.id);
        return [binding, ...filtered];
      });
      setStatus({
        type: "success",
        message: s.deviceBound,
      });
    } catch (error) {
      if (handleSessionExpiry(error)) return;
      setStatus({ type: "error", message: error.message });
    } finally {
      setLoading(false);
    }
  };

  const handleRevoke = async (bindingId) => {
    if (!accessToken) return;
    setLoading(true);
    setStatus({ type: null, message: "" });
    try {
      const binding = await revokeDeviceBinding({ accessToken, bindingId });
      setBindings((prev) => prev.map((item) => (item.id === binding.id ? binding : item)));
      setStatus({
        type: "success",
        message: s.deviceRevoked,
      });
    } catch (error) {
      if (handleSessionExpiry(error)) return;
      setStatus({ type: "error", message: error.message });
    } finally {
      setLoading(false);
    }
  };

  if (!isAuthenticated) {
    return <Navigate to="/" replace />;
  }

  return (
    <div className="app-shell">
      <div className="app-content">
        <div className="app-gradient">
          <SunHeader
            subtitle={s.title}
            actionSlot={
              <div style={{ display: "flex", alignItems: "center", gap: "1rem" }}>
                <LanguageDropdown />
                <button type="button" className="ghost-btn" onClick={() => navigate(-1)}>
                  {s.back}
                </button>
              </div>
            }
          />
          <main className="card-surface profile-surface">
            <section className="profile-card profile-card--span">
              <h2>{s.trustedDevices}</h2>
              {loading && <p className="profile-hint">{s.loading}</p>}
              {status.type && (
                <div className={status.type === "success" ? "form-success" : "form-error"}>
                  {status.message}
                </div>
              )}
              {!loading && bindings.length === 0 && (
                <p className="profile-hint">
                  {s.noDevices}
                </p>
              )}
              {!loading && bindings.length > 0 && (
                <ul className="transactions-list">
                  {bindings.map((binding) => (
                    <li key={binding.id} className="transaction-row">
                      <div>
                        <p className="profile-label">{binding.deviceLabel ?? "Unnamed device"}</p>
                        <p className="profile-value">
                          {binding.platform ?? "unknown"} · Trust {binding.trustLevel}
                        </p>
                        <p className="profile-hint">
                          {s.lastVerified}{" "}
                          {binding.lastVerifiedAt
                            ? new Date(binding.lastVerifiedAt).toLocaleString("en-IN")
                            : s.never}
                        </p>
                      </div>
                      <div className="profile-account-actions">
                        {binding.trustLevel !== "revoked" ? (
                          <button
                            type="button"
                            className="link-btn"
                            onClick={() => handleRevoke(binding.id)}
                            disabled={loading}
                          >
                            {s.revoke}
                          </button>
                        ) : (
                          <span className="profile-hint">{s.revoked}</span>
                        )}
                      </div>
                    </li>
                  ))}
                </ul>
              )}
            </section>

            <section className="profile-card profile-card--span">
              <h2>{s.bindDevice}</h2>
              <p className="profile-hint">
                {s.description}
              </p>

              <form className="form-grid" onSubmit={handleRegister}>
                <label htmlFor="device-label">
                  {s.deviceLabel}
                  <input
                    id="device-label"
                    name="deviceLabel"
                    type="text"
                    value={form.deviceLabel}
                    onChange={handleInputChange}
                    placeholder={s.deviceLabelPlaceholder}
                  />
                </label>
                <div className="form-grid--span profile-voice-block">
                  <p className="profile-label">{s.voicePassphrase}</p>
                  <p className="profile-hint">
                    {s.speakPassphrase}&nbsp;
                    <strong>{voicePhrase}</strong>
                  </p>
                  <div className="voice-controls">
                    <button
                      type="button"
                      className="secondary-btn"
                      onClick={recordingState === "recording" ? stopRecording : startRecording}
                    >
                      {recordingState === "recording"
                        ? s.stopRecording
                        : s.recordVoiceSample}
                    </button>
                    {voiceSummary && (
                      <span className="profile-hint">
                        {voiceSummary}
                        {voiceHash && (
                          <>
                            {" "}
                            · Hash: <code>{voiceHash.slice(0, 12)}…</code>
                          </>
                        )}
                      </span>
                    )}
                  </div>
                  {recordingStatus && <p className="profile-hint">{recordingStatus}</p>}
                </div>
                <p className="profile-hint form-grid--span">
                  {s.deviceFingerprint} <code>{fingerprint.slice(0, 24)}…</code>
                </p>
                <button
                  type="submit"
                  className="primary-btn primary-btn--compact"
                  disabled={loading || !fingerprint}
                >
                  {loading ? s.bindingDevice : s.bindDevice}
                </button>
              </form>
            </section>
          </main>
        </div>
      </div>
    </div>
  );
};

DeviceBindingPage.propTypes = {
  session: PropTypes.shape({
    authenticated: PropTypes.bool,
    accessToken: PropTypes.string,
  }).isRequired,
  onSignOut: PropTypes.func.isRequired,
};

export default DeviceBindingPage;

