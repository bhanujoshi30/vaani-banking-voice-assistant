const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

const extractErrorMessage = (payload, fallback) => {
  if (!payload) return fallback;
  if (typeof payload === "string") return payload;
  const detail = payload.detail;
  if (typeof payload.message === "string") return payload.message;
  if (detail) {
    if (Array.isArray(detail) && detail.length > 0) {
      return detail[0]?.msg || fallback;
    }
    if (typeof detail === "string") {
      return detail;
    }
    if (typeof detail === "object") {
      if (typeof detail.error?.message === "string") {
        return detail.error.message;
      }
      if (typeof detail.message === "string") {
        return detail.message;
      }
    }
  }
  if (typeof payload.error?.message === "string") {
    return payload.error.message;
  }
  return fallback;
};

export async function authenticateUser({ userId, password }) {
  const response = await fetch(`${API_BASE_URL}/api/v1/auth/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ userId, password }),
  });

  const payload = await response.json().catch(() => ({}));

  if (!response.ok) {
    const message = extractErrorMessage(payload, "Unable to sign in.");
    return { success: false, message };
  }

  const data = payload?.data;
  if (!data) {
    return { success: false, message: "Malformed response from server." };
  }

  return {
    success: true,
    profile: data.profile ?? null,
    accessToken: data.accessToken,
    expiresIn: data.expiresIn,
    meta: payload.meta,
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
    const message = extractErrorMessage(payload, "Unable to fetch accounts.");
    throw new Error(message);
  }

  return payload?.data ?? [];
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
    const message = extractErrorMessage(payload, "Unable to fetch transactions.");
    throw new Error(message);
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
    const message = extractErrorMessage(payload, "Unable to fetch balance.");
    throw new Error(message);
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
    const message = extractErrorMessage(json, "Transfer failed.");
    throw new Error(message);
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
    const message = extractErrorMessage(payload, "Unable to load reminders.");
    throw new Error(message);
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
    const message = extractErrorMessage(json, "Unable to create reminder.");
    throw new Error(message);
  }
  return json?.data ?? null;
}

export async function updateReminderStatus({ accessToken, reminderId, status }) {
  let response;
  try {
    response = await fetch(`${API_BASE_URL}/api/v1/reminders/${reminderId}`, {
      method: "PATCH",
      headers: {
        Authorization: `Bearer ${accessToken}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ status }),
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
    const message = extractErrorMessage(json, "Unable to update reminder.");
    throw new Error(message);
  }
  return json?.data ?? null;
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
};


