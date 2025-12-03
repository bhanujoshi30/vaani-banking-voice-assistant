const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

const extractErrorInfo = (payload, fallback) => {
  if (!payload) {
    return { message: fallback, code: null };
  }

  const detail = payload?.detail;
  const errorNode = detail?.error ?? payload?.error;
  const messageSources = [
    errorNode?.message,
    payload?.message,
    typeof detail === "string" ? detail : null,
    Array.isArray(detail) && detail.length > 0 ? detail[0]?.msg : null,
    typeof payload === "string" ? payload : null,
  ].filter(Boolean);

  const message = messageSources[0] ?? fallback;
  const code = errorNode?.code ?? detail?.code ?? payload?.code ?? null;
  return { message, code };
};

export async function authenticateUser({
  userId,
  password,
  loginMode,
  deviceIdentifier,
  deviceFingerprint,
  deviceLabel,
  platform,
  voiceSampleBlob,
  registrationMethod,
  otp,
  validateOnly,
}) {
  const formData = new FormData();
  formData.append("userId", userId);
  formData.append("password", password);
  if (loginMode) formData.append("loginMode", loginMode);
  if (deviceIdentifier) formData.append("deviceIdentifier", deviceIdentifier);
  if (deviceFingerprint) formData.append("deviceFingerprint", deviceFingerprint);
  if (deviceLabel) formData.append("deviceLabel", deviceLabel);
  if (platform) formData.append("platform", platform);
  if (registrationMethod) formData.append("registrationMethod", registrationMethod);
  if (voiceSampleBlob) {
    formData.append("voiceSample", voiceSampleBlob, "voice-login.wav");
  }
  if (otp) formData.append("otp", otp);
  if (validateOnly) formData.append("validateOnly", "true");

  const response = await fetch(`${API_BASE_URL}/api/v1/auth/login`, {
    method: "POST",
    body: formData,
  });

  const payload = await response.json().catch(() => ({}));

  if (!response.ok) {
    const { message, code } = extractErrorInfo(payload, "Unable to sign in.");
    return { success: false, message, code };
  }

  const data = payload?.data;
  if (!data) {
    console.error("[Auth Client] Malformed response - no data:", payload);
    return { success: false, message: "Malformed response from server." };
  }

  // Debug logging for voice login
  if (loginMode === "voice") {
    console.log("[Auth Client] Voice login response:", {
      hasData: !!data,
      hasProfile: !!data.profile,
      hasAccessToken: !!data.accessToken,
      profileKeys: data.profile ? Object.keys(data.profile) : null,
      accessTokenLength: data.accessToken ? data.accessToken.length : 0,
    });
  }

  // Ensure profile exists for non-validateOnly requests
  if (!data.profile && !validateOnly) {
    console.error("[Auth Client] Missing profile in response:", {
      data,
      payload,
      loginMode,
    });
    return {
      success: false,
      message: "Profile data missing from server response.",
    };
  }

  return {
    success: true,
    profile: data.profile ?? null,
    accessToken: data.accessToken,
    expiresIn: data.expiresIn,
    meta: payload.meta,
    detail: data.detail ?? null,
  };
}

export async function fetchAccounts({ accessToken }) {
  const response = await fetch(`${API_BASE_URL}/api/v1/accounts`, {
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  });

  const payload = await response.json().catch(() => ({}));

  if (!response.ok) {
    const { message, code } = extractErrorInfo(payload, "Unable to fetch accounts.");
    const error = new Error(message);
    if (code) error.code = code;
    throw error;
  }

  const accounts = payload?.data ?? [];
  // Ensure upiId field is available (handle both camelCase and snake_case)
  return accounts.map(account => ({
    ...account,
    upiId: account.upiId || account.upi_id || null,
  }));
}

export async function fetchTransactions({ accessToken, accountId, from, to, limit }) {
  const params = new URLSearchParams();
  if (from) params.set("from", from);
  if (to) params.set("to", to);
  if (limit) params.set("limit", String(limit));

  const url = `${API_BASE_URL}/api/v1/accounts/${accountId}/transactions${
    params.toString() ? `?${params.toString()}` : ""
  }`;

  const response = await fetch(url, {
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  });

  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    const { message, code } = extractErrorInfo(payload, "Unable to fetch transactions.");
    const error = new Error(message);
    if (code) error.code = code;
    throw error;
  }
  return payload?.data ?? [];
}

export async function fetchAccountBalance({ accessToken, accountId }) {
  let response;
  try {
    response = await fetch(`${API_BASE_URL}/api/v1/accounts/${accountId}/balance`, {
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    });
  } catch {
    throw new Error("Unable to reach balance service. Please try again.");
  }

  let payload;
  try {
    payload = await response.json();
  } catch {
    payload = {};
  }

  if (!response.ok) {
    const { message, code } = extractErrorInfo(payload, "Unable to fetch balance.");
    const error = new Error(message);
    if (code) error.code = code;
    throw error;
  }
  return payload?.data ?? null;
}

export async function createInternalTransfer({ accessToken, payload }) {
  let response;
  try {
    response = await fetch(`${API_BASE_URL}/api/v1/transfers/internal`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${accessToken}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });
  } catch {
    throw new Error("Unable to reach transfer service. Please try again.");
  }

  let json;
  try {
    json = await response.json();
  } catch {
    json = {};
  }

  if (!response.ok) {
    const { message, code } = extractErrorInfo(json, "Transfer failed.");
    const error = new Error(message);
    if (code) error.code = code;
    throw error;
  }
  return json?.data ?? null;
}

export async function requestStatementDownload({ accessToken, payload }) {
  let response;
  try {
    response = await fetch(`${API_BASE_URL}/api/v1/statements/download`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${accessToken}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });
  } catch {
    throw new Error("Unable to reach statements service. Please try again.");
  }

  const json = await response.json().catch(() => ({}));
  if (!response.ok) {
    const { message, code } = extractErrorInfo(json, "Unable to prepare statement.");
    const error = new Error(message);
    if (code) error.code = code;
    throw error;
  }

  return json?.data ?? null;
}

export async function fetchReminders({ accessToken }) {
  let response;
  try {
    response = await fetch(`${API_BASE_URL}/api/v1/reminders`, {
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    });
  } catch {
    throw new Error("Unable to reach reminder service. Please try again.");
  }

  let payload;
  try {
    payload = await response.json();
  } catch {
    payload = {};
  }

  if (!response.ok) {
    const { message, code } = extractErrorInfo(payload, "Unable to fetch reminders.");
    const error = new Error(message);
    if (code) error.code = code;
    throw error;
  }
  return payload?.data ?? [];
}

export async function createReminder({ accessToken, payload }) {
  let response;
  try {
    response = await fetch(`${API_BASE_URL}/api/v1/reminders`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${accessToken}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });
  } catch {
    throw new Error("Unable to reach reminder service. Please try again.");
  }

  let json;
  try {
    json = await response.json();
  } catch {
    json = {};
  }

  if (!response.ok) {
    const { message, code } = extractErrorInfo(json, "Unable to create reminder.");
    const error = new Error(message);
    if (code) error.code = code;
    throw error;
  }
  return json?.data ?? null;
}

export async function updateReminderStatus({ accessToken, reminderId, payload }) {
  let response;
  try {
    response = await fetch(`${API_BASE_URL}/api/v1/reminders/${reminderId}`, {
      method: "PATCH",
      headers: {
        Authorization: `Bearer ${accessToken}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });
  } catch {
    throw new Error("Unable to reach reminder service. Please try again.");
  }

  let json;
  try {
    json = await response.json();
  } catch {
    json = {};
  }

  if (!response.ok) {
    const { message, code } = extractErrorInfo(json, "Unable to update reminder.");
    const error = new Error(message);
    if (code) error.code = code;
    throw error;
  }
  return json?.data ?? null;
}

export async function fetchBeneficiaries({ accessToken }) {
  let response;
  try {
    response = await fetch(`${API_BASE_URL}/api/v1/beneficiaries`, {
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    });
  } catch {
    throw new Error("Unable to reach beneficiary service. Please try again.");
  }

  let payload;
  try {
    payload = await response.json();
  } catch {
    payload = {};
  }

  if (!response.ok) {
    const { message, code } = extractErrorInfo(payload, "Unable to fetch beneficiaries.");
    const error = new Error(message);
    if (code) error.code = code;
    throw error;
  }
  return payload?.data ?? [];
}

export async function createBeneficiary({ accessToken, payload }) {
  let response;
  try {
    response = await fetch(`${API_BASE_URL}/api/v1/beneficiaries`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${accessToken}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });
  } catch {
    throw new Error("Unable to reach beneficiary service. Please try again.");
  }

  let json;
  try {
    json = await response.json();
  } catch {
    json = {};
  }

  if (!response.ok) {
    const { message, code } = extractErrorInfo(json, "Unable to add beneficiary.");
    const error = new Error(message);
    if (code) error.code = code;
    throw error;
  }
  return json?.data ?? null;
}

export async function deleteBeneficiary({ accessToken, beneficiaryId }) {
  let response;
  try {
    response = await fetch(`${API_BASE_URL}/api/v1/beneficiaries/${beneficiaryId}`, {
      method: "DELETE",
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    });
  } catch {
    throw new Error("Unable to reach beneficiary service. Please try again.");
  }

  let json;
  try {
    json = await response.json();
  } catch {
    json = {};
  }

  if (!response.ok) {
    const { message, code } = extractErrorInfo(json, "Unable to remove beneficiary.");
    const error = new Error(message);
    if (code) error.code = code;
    throw error;
  }
  return json?.data ?? null;
}

export async function listDeviceBindings({ accessToken }) {
  const response = await fetch(`${API_BASE_URL}/api/v1/auth/device-bindings`, {
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    const { message, code } = extractErrorInfo(payload, "Unable to load device bindings.");
    const error = new Error(message);
    if (code) error.code = code;
    throw error;
  }
  return payload?.data ?? [];
}

export async function registerDeviceBinding({
  accessToken,
  deviceIdentifier,
  fingerprintHash,
  platform,
  deviceLabel,
  registrationMethod,
  voiceSampleBlob,
}) {
  const formData = new FormData();
  formData.append("deviceIdentifier", deviceIdentifier);
  formData.append("fingerprintHash", fingerprintHash);
  if (platform) formData.append("platform", platform);
  if (deviceLabel) formData.append("deviceLabel", deviceLabel);
  if (registrationMethod) formData.append("registrationMethod", registrationMethod);
  if (voiceSampleBlob) {
    formData.append("voiceSample", voiceSampleBlob, "device-binding.wav");
  }
  const response = await fetch(`${API_BASE_URL}/api/v1/auth/device-bindings`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
    body: formData,
  });
  const json = await response.json().catch(() => ({}));
  if (!response.ok) {
    const { message, code } = extractErrorInfo(json, "Unable to register device binding.");
    const error = new Error(message);
    if (code) error.code = code;
    throw error;
  }
  return json?.data ?? null;
}

export async function revokeDeviceBinding({ accessToken, bindingId }) {
  const response = await fetch(`${API_BASE_URL}/api/v1/auth/device-bindings/${bindingId}`, {
    method: "DELETE",
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  });
  const json = await response.json().catch(() => ({}));
  if (!response.ok) {
    const { message, code } = extractErrorInfo(json, "Unable to revoke device binding.");
    const error = new Error(message);
    if (code) error.code = code;
    throw error;
  }
  return json?.data ?? null;
}

const AI_API_BASE_URL = import.meta.env.VITE_AI_API_BASE_URL ?? "http://localhost:8001";

export async function processQRCode({ imageBase64, language = "en-IN" }) {
  let response;
  try {
    response = await fetch(`${AI_API_BASE_URL}/api/qr-code/process`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        image_base64: imageBase64,
        language,
      }),
    });
  } catch {
    throw new Error("Unable to reach QR code processing service. Please try again.");
  }

  let json;
  try {
    json = await response.json();
  } catch {
    json = {};
  }

  if (!response.ok) {
    const { message, code } = extractErrorInfo(json, "Unable to process QR code.");
    const error = new Error(message);
    if (code) error.code = code;
    throw error;
  }
  return json ?? null;
}

export default {
  authenticateUser,
  fetchAccounts,
  fetchTransactions,
  fetchAccountBalance,
  createInternalTransfer,
  fetchReminders,
  createReminder,
  updateReminderStatus,
  listDeviceBindings,
  registerDeviceBinding,
  revokeDeviceBinding,
  processQRCode,
};


