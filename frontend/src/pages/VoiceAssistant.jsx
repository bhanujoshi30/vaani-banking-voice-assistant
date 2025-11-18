import PropTypes from "prop-types";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";

import SunHeader from "../components/SunHeader.jsx";
import {
  fetchAccounts,
  fetchBeneficiaries,
  fetchAccountBalance,
  fetchTransactions,
  fetchReminders,
  createInternalTransfer,
  createReminder,
  interpretVoiceUtterance,
  fetchLoanKnowledge,
  submitVoiceFeedback,
  translateUtterance,
} from "../api/client.js";

const SESSION_EXPIRY_CODES = new Set([
  "session_expired",
  "session_invalid",
  "device_verification_required",
  "token_invalid",
]);

const QUICK_SUGGESTIONS = [
  {
    label: "Check savings balance",
    utterance: "What is the balance in my savings account?",
  },
  {
    label: "Recent transactions",
    utterance: "Show the latest transactions on my account ending 3456.",
  },
  {
    label: "Transfer to beneficiary",
    utterance: "Transfer 1000 rupees to my mother.",
  },
  {
    label: "Set bill reminder",
    utterance: "Remind me to pay the electricity bill tomorrow.",
  },
  {
    label: "Investment options",
    utterance: "Tell me about government bonds.",
  },
];

const CONFIDENCE_THRESHOLD = 0.55;

const REMINDER_SAMPLES = [
  {
    label: "Rent reminder (tomorrow)",
    utterance: "Remind me to pay the house rent tomorrow.",
  },
  {
    label: "SIP reminder (5th)",
    utterance: "Set a reminder on the 5th of every month for my SIP.",
  },
  {
    label: "Bill reminder (15th)",
    utterance: "Remind me on the 15th to pay the electricity bill.",
  },
];

const createMessageId = () => {
  if (typeof crypto !== "undefined" && typeof crypto.randomUUID === "function") {
    return crypto.randomUUID();
  }
  return `msg_${Math.random().toString(36).slice(2, 10)}`;
};

const formatDateTime = (value) => {
  if (!value) return null;
  const date = typeof value === "string" ? new Date(value) : value;
  if (Number.isNaN(date.getTime())) return null;
  return date.toLocaleString("en-IN", {
    dateStyle: "medium",
    timeStyle: "short",
  });
};

const formatCurrency = (amount, currency) => {
  if (amount === undefined || amount === null) return "—";
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: currency || "INR",
    minimumFractionDigits: 2,
  }).format(Number(amount));
};

const maskAccount = (value) => {
  if (!value) return "";
  return value.length > 4 ? `ending ${value.slice(-4)}` : value;
};

const parseReminderDueDate = (value) => {
  if (!value) {
    return null;
  }
  const normalized = value.toString().trim().toLowerCase();
  const now = new Date();
  const base = new Date(now.getTime());
  base.setHours(9, 0, 0, 0);

  if (normalized === "today") {
    return base;
  }
  if (normalized === "tomorrow") {
    base.setDate(base.getDate() + 1);
    return base;
  }
  if (normalized === "day after" || normalized === "day after tomorrow") {
    base.setDate(base.getDate() + 2);
    return base;
  }

  const parsed = new Date(value);
  if (!Number.isNaN(parsed.getTime())) {
    return parsed;
  }

  const appended = new Date(`${value} ${now.getFullYear()}`);
  if (!Number.isNaN(appended.getTime())) {
    return appended;
  }

  return null;
};

const VoiceAssistant = ({ user, accessToken, sessionDetail, onSignOut }) => {
  const navigate = useNavigate();
  const [messages, setMessages] = useState(() => []);
  const [input, setInput] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [error, setError] = useState("");
  const [accounts, setAccounts] = useState([]);
  const [beneficiaries, setBeneficiaries] = useState([]);
  const [, setReminders] = useState([]);
  const [sessionId, setSessionId] = useState(null);

  const recognitionRef = useRef(null);

  const handleSessionExpiry = useCallback(
    (apiError, setter) => {
      if (apiError?.code && SESSION_EXPIRY_CODES.has(apiError.code)) {
        const message = "Your session expired due to inactivity. Please sign in again.";
        if (typeof setter === "function") {
          setter(message);
        }
        onSignOut();
        return true;
      }
      return false;
    },
    [onSignOut],
  );

  const speakResponse = useCallback((text) => {
    if (typeof window === "undefined" || !text) {
      return;
    }
    const synth = window.speechSynthesis;
    if (!synth) {
      return;
    }
    try {
      synth.cancel();
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = "en-IN";
      utterance.rate = 1;
      synth.speak(utterance);
    } catch (speechError) {
      console.warn("Speech synthesis failed", speechError);
    }
  }, []);

  const normalizeUtterance = useCallback(
    async (rawUtterance) => {
      const trimmed = (rawUtterance ?? "").trim();
      if (!trimmed) {
        return { normalized: "", display: "" };
      }
      const hasLatin = /[A-Za-z]/.test(trimmed);
      if (hasLatin) {
        return { normalized: trimmed, display: trimmed };
      }
      try {
        const translated = await translateUtterance({ text: trimmed, targetLang: "en" });
        const cleaned = translated && translated.trim() ? translated.trim() : trimmed;
        return { normalized: cleaned, display: cleaned };
      } catch (translationError) {
        return { normalized: trimmed, display: trimmed };
      }
    },
    [translateUtterance],
  );

  const resolveAccount = useCallback(
    (identifier) => {
      if (!accounts.length) {
        return { account: null, reason: "no_accounts" };
      }
      if (!identifier) {
        return { account: accounts[0], reason: "default" };
      }
      const value = identifier.toString().trim();
      const normalized = value.toLowerCase();
      const digits = value.replace(/\D/g, "");
      const cleanse = (input) => input?.toString().replace(/\s+/g, "").toLowerCase() ?? "";

      if (digits.length >= 4) {
        const matchEnding = accounts.find((account) =>
          cleanse(account.accountNumber).endsWith(digits),
        );
        if (matchEnding) {
          return { account: matchEnding, reason: "number" };
        }
      }

      const byType = accounts.find(
        (account) => account.type && account.type.toLowerCase().includes(normalized),
      );
      if (byType) {
        return { account: byType, reason: "type" };
      }

      const exact = accounts.find((account) => cleanse(account.accountNumber) === cleanse(value));
      if (exact) {
        return { account: exact, reason: "number" };
      }

      return { account: accounts[0], reason: "default" };
    },
    [accounts],
  );

  const resolveBeneficiary = useCallback(
    (identifier) => {
      if (!beneficiaries.length) {
        return { beneficiary: null, reason: "no_beneficiaries" };
      }
      if (!identifier) {
        return { beneficiary: null, reason: "missing" };
      }
      const value = identifier.toString().trim().toLowerCase();
      const digits = value.replace(/\D/g, "");
      if (digits.length >= 6) {
        const byNumber = beneficiaries.find((item) =>
          item.accountNumber.replace(/\D/g, "").endsWith(digits),
        );
        if (byNumber) {
          return { beneficiary: byNumber, reason: "number" };
        }
      }
      const byName = beneficiaries.find((item) => item.name.toLowerCase().includes(value));
      if (byName) {
        return { beneficiary: byName, reason: "name" };
      }
      return { beneficiary: null, reason: "not_found" };
    },
    [beneficiaries],
  );

  useEffect(() => {
    if (!accessToken) {
      return;
    }
    let cancelled = false;
    const loadAccounts = async () => {
      try {
        const data = await fetchAccounts({ accessToken });
        if (!cancelled) {
          setAccounts(data);
        }
      } catch (accountError) {
        if (!cancelled) {
          handleSessionExpiry(accountError, setError);
        }
      } finally {
        // no-op
      }
    };
    loadAccounts();
    return () => {
      cancelled = true;
    };
  }, [accessToken, handleSessionExpiry]);

  useEffect(() => {
    if (!accessToken) {
      return;
    }
    let cancelled = false;
    const loadBeneficiaries = async () => {
      try {
        const data = await fetchBeneficiaries({ accessToken });
        if (!cancelled) {
          setBeneficiaries(data);
        }
      } catch (beneficiaryError) {
        if (!cancelled) {
          handleSessionExpiry(beneficiaryError, setError);
        }
      } finally {
        // no-op
      }
    };
    loadBeneficiaries();
    return () => {
      cancelled = true;
    };
  }, [accessToken, handleSessionExpiry]);

  const defaultSuggestions = useMemo(() => QUICK_SUGGESTIONS, []);

  const appendMessage = useCallback((message) => {
    setMessages((prev) => [...prev, message]);
  }, []);

  const buildAccountSuggestions = useCallback(
    (purpose) => {
      if (!accounts.length) {
        return [];
      }
      const limit = Math.min(accounts.length, 4);
      const defaultBeneficiary = beneficiaries[0]?.name ?? "my beneficiary";
      return accounts.slice(0, limit).map((account) => {
        const ending = account.accountNumber?.slice(-4) ?? "";
        let utterance = `Use account ending ${ending}.`;
        switch (purpose) {
          case "balance":
            utterance = `What is the balance in account ending ${ending}?`;
            break;
          case "transactions":
            utterance = `Show the latest transactions for account ending ${ending}.`;
            break;
          case "transfer":
            utterance = `Transfer 1000 rupees from account ending ${ending} to ${defaultBeneficiary}.`;
            break;
          default:
            break;
        }
        return {
          label: `${account.type || "Account"} ${maskAccount(account.accountNumber)}`,
          utterance,
        };
      });
    },
    [accounts, beneficiaries],
  );

  const buildBeneficiarySuggestions = useCallback(() => {
    if (!beneficiaries.length) {
      return [];
    }
    const limit = Math.min(beneficiaries.length, 4);
    return beneficiaries.slice(0, limit).map((beneficiary) => ({
      label: `Transfer to ${beneficiary.name}`,
      utterance: `Transfer 1000 rupees to ${beneficiary.name}.`,
    }));
  }, [beneficiaries]);

  const executeAction = useCallback(
    async ({ intent, confidence, slots, sessionId: incomingSessionId }, utterance) => {
      const normalizedSlots = slots ?? {};
      const outcome = {
        text: "",
        intent,
        confidence,
        slots: normalizedSlots,
        data: null,
        suggestions: [],
        feedbackContext: null,
      };

      if (incomingSessionId) {
        setSessionId(incomingSessionId);
      }

      const respond = (text, extra = {}) => {
        outcome.text = text;
        if (extra.data) {
          outcome.data = extra.data;
        }
        if (extra.suggestions) {
          outcome.suggestions = extra.suggestions;
        }
        if (extra.feedbackContext) {
          outcome.feedbackContext = extra.feedbackContext;
        }
        return outcome;
      };

      try {
        switch (intent) {
          case "balance_check": {
            const { account, reason } = resolveAccount(normalizedSlots.account);
            if (!account || !account.id) {
              const chips = buildAccountSuggestions("balance");
              return respond(
                "I could not determine which account to check. Please mention the account type or the last digits of the account number.",
                {
                  suggestions: chips.length > 0 ? chips : defaultSuggestions,
                },
              );
            }
            const data = await fetchAccountBalance({ accessToken, accountId: account.id });
            const clarificationSuggestions =
              reason === "default" && normalizedSlots.account
                ? buildAccountSuggestions("balance")
                : [];
            return respond(
              `The available balance in your account ${maskAccount(account.accountNumber)} is ${formatCurrency(
                data.availableBalance,
                data.currency,
              )}.`,
              {
                data: {
                  type: "balance",
                  payload: {
                    accountNumber: account.accountNumber,
                    ledgerBalance: data.ledgerBalance,
                    availableBalance: data.availableBalance,
                    currency: data.currency,
                    status: data.status,
                  },
                },
                feedbackContext: {
                  action: "balance_check",
                  accountNumber: account.accountNumber,
                  reason,
                },
                suggestions:
                  clarificationSuggestions.length > 0 ? clarificationSuggestions : undefined,
              },
            );
          }
          case "transaction_history": {
            const { account, reason } = resolveAccount(normalizedSlots.account);
            if (!account || !account.id) {
              const chips = buildAccountSuggestions("transactions");
              return respond(
                "Please specify which account the transactions should come from.",
                {
                  suggestions: chips.length > 0 ? chips : defaultSuggestions,
                },
              );
            }
            const data = await fetchTransactions({
              accessToken,
              accountId: account.id,
              limit: 5,
            });
            const clarificationSuggestions =
              reason === "default" && normalizedSlots.account
                ? buildAccountSuggestions("transactions")
                : [];
            return respond(
              data.length
                ? `Here ${data.length === 1 ? "is" : "are"} the latest ${data.length} transaction${
                    data.length > 1 ? "s" : ""
                  } on your account ${maskAccount(account.accountNumber)}.`
                : `I could not find any recent transactions on account ${maskAccount(account.accountNumber)}.`,
              {
                data: { type: "transactions", payload: data },
                feedbackContext: {
                  action: "transaction_history",
                  accountNumber: account.accountNumber,
                  reason,
                },
                suggestions:
                  clarificationSuggestions.length > 0 ? clarificationSuggestions : undefined,
              },
            );
          }
          case "transfer_funds": {
            const amountValue = normalizedSlots.amount
              ? Number(normalizedSlots.amount.toString().replace(/,/g, ""))
              : NaN;
            if (!Number.isFinite(amountValue) || amountValue <= 0) {
              return respond("How much should I transfer?", {
                suggestions: defaultSuggestions,
              });
            }
            const { beneficiary } = resolveBeneficiary(normalizedSlots.destination);
            if (!beneficiary) {
              const chips = buildBeneficiarySuggestions();
              return respond(
                "I could not match that beneficiary. Please mention the beneficiary name or account number.",
                {
                  suggestions: chips.length > 0 ? chips : defaultSuggestions,
                },
              );
            }
            const { account: sourceAccount } = resolveAccount(normalizedSlots.source);
            if (!sourceAccount || !sourceAccount.id) {
              const chips = buildAccountSuggestions("transfer");
              return respond(
                "Which account should I transfer from? Please specify the source account.",
                {
                  suggestions: chips.length > 0 ? chips : defaultSuggestions,
                },
              );
            }
            const receipt = await createInternalTransfer({
              accessToken,
              payload: {
                sourceAccountId: sourceAccount.id,
                destinationAccountNumber: beneficiary.accountNumber,
                amount: amountValue,
                currency: sourceAccount.currency || "INR",
                remarks: normalizedSlots.remarks || undefined,
              },
            });
            return respond(
              `Transfer reference ${receipt.referenceId} confirmed. I sent ${formatCurrency(
                receipt.debit.amount,
                receipt.debit.currency,
              )} from account ${maskAccount(sourceAccount.accountNumber)} to ${beneficiary.name}.`,
              {
                data: {
                  type: "transfer",
                  payload: {
                    referenceId: receipt.referenceId,
                    amount: receipt.debit.amount,
                    currency: receipt.debit.currency,
                    sourceAccount: sourceAccount.accountNumber,
                    beneficiary: beneficiary.name,
                  },
                },
                feedbackContext: {
                  action: "transfer_funds",
                  accountNumber: sourceAccount.accountNumber,
                  beneficiary: beneficiary.name,
                  amount: amountValue,
                },
              },
            );
          }
          case "set_reminder": {
            const isListRequest =
              !normalizedSlots.due_date &&
              /show|list|get|what|view/.test((utterance ?? "").toLowerCase());
            if (isListRequest) {
              const data = await fetchReminders({ accessToken });
              setReminders(data);
              return respond(
                data.length
                  ? `You currently have ${data.length} reminder${data.length > 1 ? "s" : ""}.`
                  : "You do not have any reminders yet.",
                {
                  data: { type: "reminders", payload: data },
                  feedbackContext: { action: "list_reminders", reminderCount: data.length },
                },
              );
            }
            const reminderMessage =
              normalizedSlots.message || "Reminder from Vaani to follow up.";
            const dueDate = parseReminderDueDate(normalizedSlots.due_date);
            if (!dueDate) {
              return respond(
                "When should I schedule the reminder? Please include a date such as tomorrow or 12 January.",
                {
                  suggestions: REMINDER_SAMPLES,
                },
              );
            }
            let reminderType = "custom";
            const lowerMessage = reminderMessage.toLowerCase();
            if (lowerMessage.includes("bill") || lowerMessage.includes("electricity")) {
              reminderType = "bill_payment";
            } else if (lowerMessage.includes("rent") || lowerMessage.includes("due")) {
              reminderType = "due_date";
            } else if (lowerMessage.includes("save") || lowerMessage.includes("savings")) {
              reminderType = "savings";
            }
            let accountIdForReminder;
            if (normalizedSlots.account) {
              const { account } = resolveAccount(normalizedSlots.account);
              accountIdForReminder = account?.id;
            }
            const created = await createReminder({
              accessToken,
              payload: {
                reminderType,
                remindAt: dueDate.toISOString(),
                message: reminderMessage,
                accountId: accountIdForReminder,
                channel: "voice",
              },
            });
            setReminders((prev) => [created, ...prev]);
            return respond(
              `Reminder scheduled for ${formatDateTime(created.remindAt)} with the message "${created.message}".`,
              {
                data: { type: "reminder", payload: created },
                feedbackContext: { action: "set_reminder", reminderId: created.id },
              },
            );
          }
          case "loan_info": {
            const knowledge = await fetchLoanKnowledge({ accessToken, query: utterance });
            if (!knowledge) {
              return respond(
                "I could not find detailed information for that request. Try asking about personal loans, gold bonds, or pension schemes.",
                { suggestions: defaultSuggestions },
              );
            }
            return respond(
              `${knowledge.title}: ${knowledge.description}`,
              {
                data: {
                  type: "knowledge",
                  payload: knowledge,
                },
                feedbackContext: { action: "knowledge", knowledgeId: knowledge.id },
              },
            );
          }
          default:
            return respond(
              "I’m not sure I understood that. Try asking about balances, transfers, reminders, or financial products.",
              { suggestions: defaultSuggestions },
            );
        }
      } catch (actionError) {
        if (handleSessionExpiry(actionError, setError)) {
          return respond("Your session expired. Please sign in again.");
        }
        return respond(actionError?.message ?? "I ran into an issue handling that instruction.");
      }
    },
    [
      accessToken,
      handleSessionExpiry,
      resolveAccount,
      resolveBeneficiary,
      buildAccountSuggestions,
      buildBeneficiarySuggestions,
      defaultSuggestions,
      fetchAccountBalance,
      fetchTransactions,
      fetchReminders,
      createInternalTransfer,
      createReminder,
      fetchLoanKnowledge,
      setReminders,
    ],
  );

  const handleFeedback = useCallback(
    async (messageId, feedback, context) => {
      if (!accessToken || !context || !sessionId) {
        return;
      }
      try {
        await submitVoiceFeedback({
          accessToken,
          payload: {
            sessionId,
            correct: feedback === "positive",
            intent: context.action,
            utterance: context.utterance,
            context,
          },
        });
        setMessages((prev) =>
          prev.map((message) =>
            message.id === messageId ? { ...message, feedback } : message,
          ),
        );
      } catch (feedbackError) {
        console.warn("Unable to submit feedback", feedbackError);
        setMessages((prev) =>
          prev.map((message) =>
            message.id === messageId ? { ...message, feedback: "error" } : message,
          ),
        );
      }
    },
    [accessToken, sessionId],
  );

  const handleSend = useCallback(
    async (rawUtterance, source = "text") => {
      if (isSubmitting) {
        return;
      }
      const utterance = (rawUtterance ?? "").trim();
      if (!utterance || !accessToken) {
        return;
      }
      const messageId = createMessageId();
      appendMessage({
        id: messageId,
        role: "user",
        source,
        text: utterance,
        timestamp: Date.now(),
      });
      setIsSubmitting(true);
      setError("");
      try {
        const { normalized, display } = await normalizeUtterance(utterance);
        const shownText = display || utterance;
        if (shownText !== utterance) {
          setMessages((prev) => {
            if (prev.length === 0) return prev;
            const copy = [...prev];
            copy[copy.length - 1] = { ...copy[copy.length - 1], text: shownText };
            return copy;
          });
        }
        const response = await interpretVoiceUtterance({
          accessToken,
          utterance: normalized || utterance,
          sessionId,
        });
        const outcome = await executeAction(response, normalized || utterance);
        const needsSuggestions =
          !outcome.text ||
          response.intent === "clarify" ||
          (typeof response.confidence === "number" &&
            response.confidence < CONFIDENCE_THRESHOLD);
        const resolvedSuggestions =
          outcome.suggestions && outcome.suggestions.length > 0
            ? outcome.suggestions
            : needsSuggestions
              ? defaultSuggestions
              : [];
        const assistantMessage = {
          id: createMessageId(),
          role: "assistant",
          text:
            outcome.text ||
            "I’m not sure how to help with that—try one of the quick suggestions below.",
          intent: response.intent,
          confidence: response.confidence,
          slots: outcome.slots,
          data: outcome.data,
          suggestions: resolvedSuggestions,
          timestamp: Date.now(),
          feedbackContext: outcome.feedbackContext
            ? {
                ...outcome.feedbackContext,
                utterance: normalized || utterance,
              }
            : null,
          feedback: null,
        };
        appendMessage(assistantMessage);
        if (assistantMessage.text) {
          speakResponse(assistantMessage.text);
        }
      } catch (sendError) {
        if (!handleSessionExpiry(sendError, setError)) {
          appendMessage({
            id: createMessageId(),
            role: "assistant",
            text: sendError?.message ?? "I couldn’t process that request.",
            timestamp: Date.now(),
          });
        }
      } finally {
        setIsSubmitting(false);
        setInput("");
      }
    },
    [
      accessToken,
      appendMessage,
      executeAction,
      handleSessionExpiry,
      isSubmitting,
      normalizeUtterance,
      sessionId,
      speakResponse,
      defaultSuggestions,
    ],
  );

  const stopListening = useCallback(() => {
    if (recognitionRef.current) {
      recognitionRef.current.onresult = null;
      recognitionRef.current.onerror = null;
      recognitionRef.current.onend = null;
      try {
        recognitionRef.current.stop();
      } catch (stopError) {
        console.warn("Error stopping recognition", stopError);
      }
      recognitionRef.current = null;
    }
    setIsListening(false);
  }, []);

  const startListening = useCallback(() => {
    if (typeof window === "undefined") return;
    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition || null;
    if (!SpeechRecognition) {
      setError("Voice recognition is not supported in this browser.");
      return;
    }
    try {
      const recognition = new SpeechRecognition();
      recognition.lang = "en-IN";
      recognition.interimResults = false;
      recognition.maxAlternatives = 1;
      recognition.onresult = (event) => {
        const transcript = event.results?.[0]?.[0]?.transcript ?? "";
        stopListening();
        if (transcript) {
          handleSend(transcript, "voice");
        }
      };
      recognition.onerror = (event) => {
        stopListening();
        setError(event?.error ? `Voice recognition error: ${event.error}` : "Voice recognition aborted.");
      };
      recognition.onend = () => {
        stopListening();
      };
      recognitionRef.current = recognition;
      recognition.start();
      setIsListening(true);
      setError("");
    } catch (listenError) {
      stopListening();
      setError(listenError?.message ?? "Unable to start voice recognition.");
    }
  }, [handleSend, stopListening]);

  useEffect(() => {
    return () => {
      stopListening();
    };
  }, [stopListening]);

  const handleSuggestion = (utterance) => {
    handleSend(utterance, "suggestion");
  };

  const deviceBindingRequired = Boolean(sessionDetail?.deviceBindingRequired);
  const voiceEnrollmentRequired = Boolean(sessionDetail?.voiceEnrollmentRequired);
  const voiceReverificationRequired = Boolean(sessionDetail?.voiceReverificationRequired);
  const voicePhrase = sessionDetail?.voicePhrase ?? "Sun Bank mera saathi, har kadam surakshit banking ka vaada";

  return (
    <div className="app-shell">
      <div className="app-content app-content--stretch">
        <div className="app-gradient voice-gradient">
          <SunHeader
            subtitle={`${user?.branch?.name ?? "Sun National Bank"} · ${
              user?.branch?.city ?? "Hyderabad"
            }`}
            actionSlot={
              <button type="button" className="ghost-btn" onClick={() => navigate("/profile")}>
                Back to dashboard
              </button>
            }
          />
          <main className="card-surface voice-surface">
            {(deviceBindingRequired || voiceEnrollmentRequired || voiceReverificationRequired) && (
              <section className="profile-card profile-card--span">
                <div className="form-error">
                  <p>
                    {deviceBindingRequired
                      ? "For secure banking, please bind this device and verify your voice."
                      : voiceEnrollmentRequired
                        ? "Complete voice signature enrollment to finish device binding."
                        : "Please refresh your voice signature to keep this device trusted."}
                  </p>
                  <p className="profile-hint">
                    Speak the passphrase: <strong>{voicePhrase}</strong>
                  </p>
                  <button
                    type="button"
                    className="link-btn"
                    onClick={() => navigate("/device-binding")}
                  >
                    Manage device & voice binding
                  </button>
                </div>
              </section>
            )}

            <section className="voice-assistant">
              <div className="voice-assistant__header">
                <h2>Voice assistant</h2>
                <p>
                  Speak in clear English or type your request. I can help with balances, transfers,
                  reminders, and information on loans or investment schemes.
                </p>
              </div>

              <div className="voice-assistant__controls">
                <button
                  type="button"
                  className="primary-btn primary-btn--compact"
                  onClick={isListening ? stopListening : startListening}
                >
                  {isListening ? "Stop listening" : "Start talking"}
                </button>
                <button
                  type="button"
                  className="secondary-btn"
                  onClick={() => setMessages([])}
                  disabled={messages.length === 0}
                >
                  Clear conversation
                </button>
                {error && <div className="form-error">{error}</div>}
              </div>

              <div className="voice-assistant__log">
                {messages.length === 0 ? (
                  <div className="voice-assistant__empty">
                    <p>Try asking “Check my savings balance” or “Tell me about government bonds”.</p>
                    <div className="voice-assistant__suggestions">
                      {defaultSuggestions.map((item) => (
                        <button
                          key={item.utterance}
                          type="button"
                          className="chip-btn"
                          onClick={() => handleSuggestion(item.utterance)}
                        >
                          {item.label}
                        </button>
                      ))}
                    </div>
                  </div>
                ) : (
                  <ul>
                    {messages.map((message) => (
                      <li key={message.id} className={`voice-message voice-message--${message.role}`}>
                        <span className="voice-message__role">
                          {message.role === "user" ? "You" : "Assistant"}
                        </span>
                        <p className="voice-message__text">{message.text}</p>
                        {message.data && message.data.type === "balance" && (
                          <div className="voice-card">
                            <p>
                              Available balance:{" "}
                              <strong>
                                {formatCurrency(
                                  message.data.payload.availableBalance,
                                  message.data.payload.currency,
                                )}
                              </strong>
                            </p>
                            <p className="profile-hint">
                              Ledger balance:{" "}
                              {formatCurrency(
                                message.data.payload.ledgerBalance,
                                message.data.payload.currency,
                              )}{" "}
                              · Status: {message.data.payload.status}
                            </p>
                          </div>
                        )}
                        {message.data && message.data.type === "transactions" && (
                          <div className="voice-card">
                            <ul className="transaction-list">
                              {message.data.payload.map((txn) => (
                                <li key={txn.id}>
                                  <span>
                                    {txn.type.replace("_", " ").toLowerCase()} ·{" "}
                                    {formatCurrency(txn.amount, txn.currency)}
                                  </span>
                                  <span className="profile-hint">
                                    {formatDateTime(txn.occurredAt)} · Ref {txn.referenceId ?? "-"}
                                  </span>
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}
                        {message.data && message.data.type === "transfer" && (
                          <div className="voice-card">
                            <p>
                              Reference {message.data.payload.referenceId} ·{" "}
                              {formatCurrency(message.data.payload.amount, message.data.payload.currency)}
                            </p>
                            <p className="profile-hint">
                              From {maskAccount(message.data.payload.sourceAccount)} to{" "}
                              {message.data.payload.beneficiary}
                            </p>
                          </div>
                        )}
                        {message.data && message.data.type === "reminders" && (
                          <div className="voice-card">
                            <ul className="reminder-list">
                              {message.data.payload.map((item) => (
                                <li key={item.id}>
                                  <span>{item.message}</span>
                                  <span className="profile-hint">
                                    {formatDateTime(item.remindAt)} · {item.reminderType}
                                  </span>
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}
                        {message.data && message.data.type === "reminder" && (
                          <div className="voice-card">
                            <p>{message.data.payload.message}</p>
                            <p className="profile-hint">
                              Scheduled for {formatDateTime(message.data.payload.remindAt)}
                            </p>
                          </div>
                        )}
                        {message.data && message.data.type === "knowledge" && (
                          <div className="voice-card">
                            <p>
                              <strong>{message.data.payload.title}</strong>
                            </p>
                            {message.data.payload.rate && <p>Rate: {message.data.payload.rate}</p>}
                            {message.data.payload.maxAmount && (
                              <p>Maximum amount: {message.data.payload.maxAmount}</p>
                            )}
                            {message.data.payload.tenure && (
                              <p>Tenure: {message.data.payload.tenure}</p>
                            )}
                          </div>
                        )}
                        {message.intent && (
                          <span className="voice-message__meta">
                            Intent: {message.intent}
                            {typeof message.confidence === "number" && (
                              <> · Confidence: {(message.confidence * 100).toFixed(1)}%</>
                            )}
                          </span>
                        )}
                        {message.suggestions && message.suggestions.length > 0 && (
                          <div className="voice-assistant__suggestions">
                            {message.suggestions.map((item) => (
                              <button
                                key={`${message.id}-${item.utterance}`}
                                type="button"
                                className="chip-btn"
                                onClick={() => handleSuggestion(item.utterance)}
                              >
                                {item.label}
                              </button>
                            ))}
                          </div>
                        )}
                        {message.role === "assistant" &&
                          message.feedbackContext &&
                          message.feedback !== "positive" &&
                          message.feedback !== "negative" && (
                            <div className="voice-feedback">
                              <span>Was this helpful?</span>
                              <button
                                type="button"
                                className="chip-btn chip-btn--success"
                                onClick={() => handleFeedback(message.id, "positive", message.feedbackContext)}
                              >
                                👍 Yes
                              </button>
                              <button
                                type="button"
                                className="chip-btn chip-btn--danger"
                                onClick={() => handleFeedback(message.id, "negative", message.feedbackContext)}
                              >
                                👎 Needs correction
                              </button>
                            </div>
                          )}
                        {message.feedback === "positive" && (
                          <p className="profile-hint">Thanks! Marked as correct.</p>
                        )}
                        {message.feedback === "negative" && (
                          <p className="profile-hint">Thanks for the feedback. We’ll review this.</p>
                        )}
                        {message.feedback === "error" && (
                          <p className="form-error">Unable to submit feedback right now.</p>
                        )}
                      </li>
                    ))}
                  </ul>
                )}
              </div>

              <form
                className="voice-assistant__form"
                onSubmit={(event) => {
                  event.preventDefault();
                  if (!input.trim()) return;
                  handleSend(input, "text");
                }}
              >
                <input
                  type="text"
                  value={input}
                  onChange={(event) => setInput(event.target.value)}
                  placeholder="Type a request, e.g. Transfer 500 to my mother"
                  disabled={isSubmitting}
                />
                <button type="submit" className="primary-btn primary-btn--compact" disabled={isSubmitting}>
                  Send
                </button>
              </form>
            </section>
          </main>
        </div>
      </div>
    </div>
  );
};

VoiceAssistant.propTypes = {
  user: PropTypes.object,
  accessToken: PropTypes.string,
  sessionDetail: PropTypes.object,
  onSignOut: PropTypes.func.isRequired,
};

export default VoiceAssistant;

