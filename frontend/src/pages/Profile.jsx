import PropTypes from "prop-types";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { Navigate, useNavigate, useLocation } from "react-router-dom";

import SunHeader from "../components/SunHeader.jsx";
import LanguageDropdown from "../components/LanguageDropdown.jsx";
import AIAssistantLogo from "../components/AIAssistantLogo.jsx";
import "./Chat.css";
import { usePageLanguage } from "../hooks/usePageLanguage.js";
import { getVoicePhrase } from "../config/loginStrings.js";
import {
  fetchAccounts,
  fetchTransactions,
  fetchAccountBalance,
  createInternalTransfer,
  fetchReminders,
  createReminder,
  updateReminderStatus,
  fetchBeneficiaries,
  listDeviceBindings,
  revokeDeviceBinding,
} from "../api/client.js";
import VoiceEnrollmentModal from "../components/VoiceEnrollmentModal.jsx";
import ForceLogoutModal from "../components/ForceLogoutModal.jsx";
import { setPreferredLanguage } from "../utils/preferences.js";

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
    currency,
    minimumFractionDigits: 2,
  }).format(Number(amount));
};

const parseBalanceString = (value) => {
  if (!value) return null;
  const cleaned = value.replace(/[^\d.-]/g, "");
  const amount = Number(cleaned);
  return Number.isNaN(amount) ? null : amount;
};

const PANEL_KEYS = ["balance", "transfer", "transactions", "reminders", "beneficiaries", "deviceBinding"];
const SESSION_EXPIRY_CODES = new Set([
  "session_timeout",
  "session_expired",
  "session_inactive",
  "session_invalid",
]);

const Profile = ({ user, accessToken, onSignOut, sessionDetail }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const { strings, language } = usePageLanguage();
  const s = strings.profile;
  const [isVoiceEnrollmentModalOpen, setIsVoiceEnrollmentModalOpen] = useState(false);
  const [isForceLogoutModalOpen, setIsForceLogoutModalOpen] = useState(false);
  const [hasVoiceBinding, setHasVoiceBinding] = useState(false);
  const [checkingVoiceBinding, setCheckingVoiceBinding] = useState(true);
  
  // Check if current session was logged in with voice
  const loggedInWithVoice = useMemo(() => {
    const detail = sessionDetail ?? {};
    return Boolean(detail.voiceLogin) || detail.loginMode === "voice";
  }, [sessionDetail]);

  // Determine if voice session is secured
  // Voice session is secured if:
  // 1. User logged in with voice, OR
  // 2. User has an active voice binding (even if logged in with password)
  const isVoiceSecured = useMemo(() => {
    return loggedInWithVoice || hasVoiceBinding;
  }, [loggedInWithVoice, hasVoiceBinding]);

  const [panels, setPanels] = useState({
    balance: false,
    transfer: false,
    transactions: false,
    reminders: false,
    beneficiaries: false,
    deviceBinding: false,
  });

  const [accounts, setAccounts] = useState([]);
  const [accountsLoading, setAccountsLoading] = useState(false);
  const [accountsError, setAccountsError] = useState("");
  const [balanceVisibility, setBalanceVisibility] = useState({});

  const [transactions, setTransactions] = useState([]);
  const [transactionsLoading, setTransactionsLoading] = useState(false);
  const [transactionsError, setTransactionsError] = useState("");
  const [selectedTxnAccountId, setSelectedTxnAccountId] = useState("");
  const [selectedTxnAccountNumber, setSelectedTxnAccountNumber] = useState("");

  const [balanceAccountId, setBalanceAccountId] = useState("");
  const [balanceResult, setBalanceResult] = useState(null);
  const [balanceLoading, setBalanceLoading] = useState(false);
  const [balanceError, setBalanceError] = useState("");

  const [transferForm, setTransferForm] = useState({
    sourceAccountId: "",
    destinationAccountNumber: "",
    beneficiaryId: "",
    amount: "",
    remarks: "",
  });
  const [transferLoading, setTransferLoading] = useState(false);
  const [transferStatus, setTransferStatus] = useState(null);

  const [reminders, setReminders] = useState([]);
  const [remindersLoading, setRemindersLoading] = useState(false);
  const [remindersError, setRemindersError] = useState("");
  const [reminderForm, setReminderForm] = useState({
    reminderType: "bill_payment",
    remindAt: "",
    message: "",
    accountId: "",
    channel: "voice",
    recurrenceRule: "",
  });
  const [reminderStatus, setReminderStatus] = useState(null);

  const [beneficiaries, setBeneficiaries] = useState([]);
  const [beneficiariesLoading, setBeneficiariesLoading] = useState(false);
  const [beneficiariesError, setBeneficiariesError] = useState("");

  // device binding panel state
  const [deviceBindings, setDeviceBindings] = useState([]);
  const [deviceLoading, setDeviceLoading] = useState(false);
  const [deviceError, setDeviceError] = useState("");

  const bindingDetail = sessionDetail ?? {};
  const deviceBindingRequired = Boolean(bindingDetail.deviceBindingRequired);
  const voiceEnrollmentRequired = Boolean(bindingDetail.voiceEnrollmentRequired);
  const voiceReverificationRequired = Boolean(bindingDetail.voiceReverificationRequired);
  const voicePhrase = bindingDetail.voicePhrase ?? getVoicePhrase(language);

  const handleSessionExpiry = useCallback(
    (error, setter) => {
    if (error?.code && SESSION_EXPIRY_CODES.has(error.code)) {
      const message = s.sessionExpired || "Your session expired due to inactivity. Please sign in again.";
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

  useEffect(() => {
    if (!accessToken) {
      return;
    }
    let isMounted = true;
    setAccountsLoading(true);
    setAccountsError("");
    fetchAccounts({ accessToken })
      .then((data) => {
        if (!isMounted) return;
        setAccounts(data);
      })
      .catch((error) => {
        if (!isMounted) return;
        if (handleSessionExpiry(error, setAccountsError)) return;
        setAccountsError(error.message);
      })
      .finally(() => {
        if (isMounted) {
          setAccountsLoading(false);
        }
      });
    return () => {
      isMounted = false;
    };
  }, [accessToken, handleSessionExpiry]);

  useEffect(() => {
    if (!accessToken) {
      return;
    }
    let isMounted = true;
    setRemindersLoading(true);
    setRemindersError("");
    fetchReminders({ accessToken })
      .then((data) => {
        if (!isMounted) return;
        setReminders(data);
      })
      .catch((error) => {
        if (!isMounted) return;
        if (handleSessionExpiry(error, setRemindersError)) return;
        setRemindersError(error.message);
      })
      .finally(() => {
        if (isMounted) {
          setRemindersLoading(false);
        }
      });
    return () => {
      isMounted = false;
    };
  }, [accessToken, handleSessionExpiry]);

  useEffect(() => {
    if (!accessToken) {
      return;
    }
    let isMounted = true;
    setBeneficiariesLoading(true);
    setBeneficiariesError("");
    fetchBeneficiaries({ accessToken })
      .then((data) => {
        if (!isMounted) return;
        setBeneficiaries(data);
      })
      .catch((error) => {
        if (!isMounted) return;
        if (handleSessionExpiry(error, setBeneficiariesError)) return;
        setBeneficiariesError(error.message);
      })
      .finally(() => {
        if (isMounted) {
          setBeneficiariesLoading(false);
        }
      });
    return () => {
      isMounted = false;
    };
  }, [accessToken, handleSessionExpiry]);

  const accountsByNumber = useMemo(() => {
    const map = new Map();
    accounts.forEach((account) => {
      map.set(account.accountNumber, account);
    });
    return map;
  }, [accounts]);

  const accountCards = useMemo(() => {
    if (!user) return [];
    return user.accountSummary.map((summary) => {
      const account = accountsByNumber.get(summary.accountNumber);
      const ledgerBalance =
        account?.balance ??
        (typeof summary.availableBalance === "number"
          ? summary.availableBalance
          : parseBalanceString(summary.balance));
      const availableBalance =
        account?.availableBalance ??
        (typeof summary.availableBalance === "number"
          ? summary.availableBalance
          : parseBalanceString(summary.balance));

      return {
        ...summary,
        accountId: account?.id ?? summary.id ?? null,
        status: account?.status ?? summary.status ?? "active",
        ledgerBalance,
        availableBalance,
        currency: account?.currency ?? summary.currency,
        debitCards: account?.debitCards ?? summary.debitCards ?? [],
        creditCards: account?.creditCards ?? summary.creditCards ?? [],
      };
    });
  }, [user, accountsByNumber]);

  const accountOptions = useMemo(
    () =>
      accountCards
        .map((account) => ({
          id: account.accountId,
          number: account.accountNumber,
          currency: account.currency,
        }))
        .filter((option) => Boolean(option.id)),
    [accountCards],
  );

  const beneficiaryOptions = useMemo(
    () =>
      beneficiaries
        .filter((item) => item.status !== "blocked")
        .map((item) => ({
          id: item.id,
          name: item.name,
          accountNumber: item.accountNumber,
        })),
    [beneficiaries],
  );

  useEffect(() => {
    if (!accountOptions.length) return;
    const current =
      accountOptions.find((option) => option.id === selectedTxnAccountId) || accountOptions[0];
    setSelectedTxnAccountNumber(current.number);
    setSelectedTxnAccountId((prev) => prev || current.id);
  }, [accountOptions, selectedTxnAccountId]);

  useEffect(() => {
    if (!accountOptions.length) return;
    const firstAccountId = accountOptions[0].id;
    setBalanceAccountId((prev) => prev || firstAccountId);
    setTransferForm((prev) => ({
      ...prev,
      sourceAccountId: prev.sourceAccountId || firstAccountId,
    }));
    setReminderForm((prev) => ({
      ...prev,
      accountId: prev.accountId || firstAccountId,
    }));
  }, [accountOptions]);

  useEffect(() => {
    if (!accountCards.length) return;
    setBalanceVisibility((prev) => {
      const next = {};
      accountCards.forEach((account) => {
        next[account.accountNumber] = prev[account.accountNumber] ?? false;
      });
      return next;
    });
  }, [accountCards]);

  useEffect(() => {
    if (!transferForm.beneficiaryId) return;
    if (!beneficiaryOptions.some((option) => option.id === transferForm.beneficiaryId)) {
      setTransferForm((prev) => ({ ...prev, beneficiaryId: "" }));
    }
  }, [beneficiaryOptions, transferForm.beneficiaryId]);

  const handlePanelToggle = (panel) => {
    const isOpening = !panels[panel];
    setPanels(
      PANEL_KEYS.reduce(
        (acc, key) => ({ ...acc, [key]: key === panel ? isOpening : false }),
        {},
      ),
    );
    if (isOpening) {
      window.setTimeout(() => {
        const el = document.getElementById(`panel-${panel}`);
        if (el) {
          el.scrollIntoView({ behavior: "smooth", block: "start" });
        }
      }, 150);
    }
  };

  // Function to check voice binding status
  const checkVoiceBindingStatus = useCallback(() => {
    if (!accessToken) {
      setCheckingVoiceBinding(false);
      setHasVoiceBinding(false);
      return;
    }
    let mounted = true;
    setCheckingVoiceBinding(true);
    listDeviceBindings({ accessToken })
      .then((data) => {
        if (!mounted) return;
        // Check if any ACTIVE (non-revoked) device binding has voice signature
        // Only count bindings that are trusted (not revoked) and have voice signature
        const hasVoice = data.some(
          (binding) => 
            binding.voiceSignaturePresent === true && 
            binding.trustLevel !== "revoked"
        );
        setHasVoiceBinding(hasVoice);
      })
      .catch((error) => {
        if (!mounted) return;
        // Don't show error for voice check, just assume no voice
        setHasVoiceBinding(false);
      })
      .finally(() => {
        if (mounted) setCheckingVoiceBinding(false);
      });
    return () => {
      mounted = false;
    };
  }, [accessToken]);

  // Check voice binding status on mount
  useEffect(() => {
    checkVoiceBindingStatus();
  }, [checkVoiceBindingStatus]);

  // Refresh voice binding status when page becomes visible (user returns from device binding page)
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (!document.hidden && accessToken) {
        checkVoiceBindingStatus();
      }
    };
    document.addEventListener("visibilitychange", handleVisibilityChange);
    return () => {
      document.removeEventListener("visibilitychange", handleVisibilityChange);
    };
  }, [accessToken, checkVoiceBindingStatus]);

  // Also refresh when window gains focus (alternative approach)
  useEffect(() => {
    const handleFocus = () => {
      if (accessToken) {
        checkVoiceBindingStatus();
      }
    };
    window.addEventListener("focus", handleFocus);
    return () => {
      window.removeEventListener("focus", handleFocus);
    };
  }, [accessToken, checkVoiceBindingStatus]);

  // Refresh voice binding status when route changes to profile (user navigates back from device binding)
  const prevPathRef = useRef(location.pathname);
  useEffect(() => {
    // Only refresh if we're on profile page and we came from device-binding page
    if (location.pathname === "/profile" && prevPathRef.current === "/device-binding" && accessToken) {
      checkVoiceBindingStatus();
    }
    prevPathRef.current = location.pathname;
  }, [location.pathname, accessToken, checkVoiceBindingStatus]);

  // fetch trusted device bindings when deviceBinding panel opens
  useEffect(() => {
    if (!panels.deviceBinding) return;
    if (!accessToken) {
      setDeviceError("Session expired. Please sign in again.");
      return;
    }
    let mounted = true;
    setDeviceLoading(true);
    setDeviceError("");
    listDeviceBindings({ accessToken })
      .then((data) => {
        if (!mounted) return;
        setDeviceBindings(data);
        // Update voice binding status when device bindings are fetched
        // Only count active (non-revoked) bindings with voice signature
        const hasVoice = data.some(
          (binding) => 
            binding.voiceSignaturePresent === true && 
            binding.trustLevel !== "revoked"
        );
        setHasVoiceBinding(hasVoice);
      })
      .catch((error) => {
        if (!mounted) return;
        if (handleSessionExpiry(error, setDeviceError)) return;
        setDeviceError(error.message);
      })
      .finally(() => {
        if (mounted) setDeviceLoading(false);
      });
    return () => {
      mounted = false;
    };
  }, [panels.deviceBinding, accessToken, handleSessionExpiry]);

  // Refresh voice binding status when device binding panel is closed (user might have made changes)
  useEffect(() => {
    if (!panels.deviceBinding && accessToken) {
      // Small delay to ensure any pending operations complete
      const timeoutId = setTimeout(() => {
        checkVoiceBindingStatus();
      }, 500);
      return () => clearTimeout(timeoutId);
    }
  }, [panels.deviceBinding, accessToken, checkVoiceBindingStatus]);

  // Refresh voice binding status when device bindings are revoked
  const handleDeviceRevoke = async (bindingId) => {
    if (!accessToken) return;
    setDeviceLoading(true);
    setDeviceError("");
    try {
      const updated = await revokeDeviceBinding({ accessToken, bindingId });
      setDeviceBindings((prev) => prev.map((item) => (item.id === updated.id ? updated : item)));
      // Re-check voice binding status after revocation
      // Only count active (non-revoked) bindings with voice signature
      const data = await listDeviceBindings({ accessToken });
      const hasVoice = data.some(
        (binding) => 
          binding.voiceSignaturePresent === true && 
          binding.trustLevel !== "revoked"
      );
      setHasVoiceBinding(hasVoice);
      
      // Show force logout modal when device binding is revoked
      setIsForceLogoutModalOpen(true);
    } catch (error) {
      if (handleSessionExpiry(error, setDeviceError)) return;
      setDeviceError(error.message);
    } finally {
      setDeviceLoading(false);
    }
  };

  const toggleBalanceVisibility = (accountNumber) => {
    setBalanceVisibility((prev) => ({
      ...prev,
      [accountNumber]: !prev[accountNumber],
    }));
  };

  const handleViewTransactions = useCallback(
    async (accountId, accountNumber) => {
      if (!accessToken || !accountId) {
        setTransactionsError("Session expired. Please sign in again.");
        return;
      }
      setTransactionsError("");
      setTransactions([]);
      setTransactionsLoading(true);
      setSelectedTxnAccountNumber(accountNumber ?? "");
      try {
        const data = await fetchTransactions({ accessToken, accountId, limit: 5 });
        setTransactions(data);
      } catch (error) {
        if (handleSessionExpiry(error, setTransactionsError)) {
          return;
        }
        setTransactionsError(error.message);
      } finally {
        setTransactionsLoading(false);
      }
    },
    [accessToken, handleSessionExpiry],
  );

  useEffect(() => {
    if (!panels.transactions) return;
    const selectedOption =
      accountOptions.find((option) => option.id === selectedTxnAccountId) || accountOptions[0];
    if (selectedOption) {
      handleViewTransactions(selectedOption.id, selectedOption.number);
    }
  }, [panels.transactions, selectedTxnAccountId, accountOptions, handleViewTransactions]);

  const handleBalanceSubmit = async (event) => {
    event.preventDefault();
    if (!balanceAccountId || !accessToken) return;
    setBalanceLoading(true);
    setBalanceError("");
    setBalanceResult(null);
    try {
      const data = await fetchAccountBalance({ accessToken, accountId: balanceAccountId });
      setBalanceResult(data);
    } catch (error) {
      if (handleSessionExpiry(error, setBalanceError)) {
        return;
      }
      setBalanceError(error.message);
    } finally {
      setBalanceLoading(false);
    }
  };

  const handleTransferChange = (event) => {
    const { name, value } = event.target;
    if (name === "beneficiaryId") {
      const selected = beneficiaryOptions.find((option) => option.id === value);
      setTransferForm((prev) => ({
        ...prev,
        beneficiaryId: value,
        destinationAccountNumber: selected ? selected.accountNumber : "",
      }));
      return;
    }
    if (name === "destinationAccountNumber") {
      setTransferForm((prev) => ({
        ...prev,
        beneficiaryId: "",
        destinationAccountNumber: value,
      }));
      return;
    }
    setTransferForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleTransferSubmit = async (event) => {
    event.preventDefault();
    if (!accessToken) return;
    if (!transferForm.sourceAccountId) {
      setTransferStatus({ type: "error", message: s.selectSourceAccount });
      return;
    }

    const destinationAccountNumber = transferForm.destinationAccountNumber.trim();
    if (!destinationAccountNumber) {
      setTransferStatus({ type: "error", message: s.enterDestinationAccount });
      return;
    }

    const transferAmount = Number(transferForm.amount);
    if (!Number.isFinite(transferAmount) || transferAmount <= 0) {
      setTransferStatus({ type: "error", message: s.enterValidAmount });
      return;
    }

    const sourceAccount =
      accounts.find((account) => account.id === transferForm.sourceAccountId) ||
      accountCards.find((account) => account.accountId === transferForm.sourceAccountId);
    const currency = sourceAccount?.currency ?? "INR";

    setTransferLoading(true);
    setTransferStatus(null);
    try {
      await createInternalTransfer({
        accessToken,
        payload: {
          sourceAccountId: transferForm.sourceAccountId,
          destinationAccountNumber,
          amount: transferAmount,
          currency,
          remarks: transferForm.remarks || undefined,
        },
      });
      setTransferStatus({ type: "success", message: s.transferInitiated });
      setTransferForm((prev) => ({
        ...prev,
        destinationAccountNumber: "",
        beneficiaryId: "",
        amount: "",
        remarks: "",
      }));
      const accountNumber = sourceAccount?.accountNumber;
      if (accountNumber) {
        handleViewTransactions(transferForm.sourceAccountId, accountNumber);
      }
    } catch (error) {
      if (
        handleSessionExpiry(error, (msg) =>
          setTransferStatus({ type: "error", message: msg }),
        )
      ) {
        return;
      }
      setTransferStatus({ type: "error", message: error.message });
    } finally {
      setTransferLoading(false);
    }
  };

  const handleReminderChange = (event) => {
    const { name, value } = event.target;
    setReminderForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleReminderSubmit = async (event) => {
    event.preventDefault();
    if (!accessToken) return;
    setReminderStatus(null);
    try {
      const payload = {
        reminderType: reminderForm.reminderType,
        remindAt: reminderForm.remindAt,
        message: reminderForm.message,
        accountId: reminderForm.accountId || undefined,
        channel: reminderForm.channel || "voice",
        recurrenceRule: reminderForm.recurrenceRule || undefined,
      };
      const created = await createReminder({ accessToken, payload });
      setReminders((prev) => [created, ...prev]);
      setReminderStatus({ type: "success", message: s.reminderCreated });
      setReminderForm((prev) => ({
        ...prev,
        message: "",
        remindAt: "",
        recurrenceRule: "",
      }));
    } catch (error) {
      if (
        handleSessionExpiry(error, (msg) =>
          setReminderStatus({ type: "error", message: msg }),
        )
      ) {
        return;
      }
      setReminderStatus({ type: "error", message: error.message });
    }
  };

  const handleReminderStatusUpdate = async (reminderId, status) => {
    if (!accessToken) return;
    try {
      const updated = await updateReminderStatus({ accessToken, reminderId, status });
      setReminders((prev) =>
        prev.map((reminder) => (reminder.id === updated.id ? updated : reminder)),
      );
    } catch (error) {
      if (
        handleSessionExpiry(error, (msg) =>
          setReminderStatus({ type: "error", message: msg }),
        )
      ) {
        return;
      }
      setReminderStatus({ type: "error", message: error.message });
    }
  };


  if (!user) {
    return <Navigate to="/" replace />;
  }

  const {
    fullName,
    segment,
    branch,
    lastLogin,
    nextReminder,
    customerId,
  } = user;

  const formattedLastLogin = formatDateTime(lastLogin);
  const formattedReminder = formatDateTime(nextReminder?.date);
  const displayedAccounts = accountCards.slice(0, 5);
  const displayedReminders = reminders.slice(0, 5);
  const displayedBeneficiaries = beneficiaries
    .filter((item) => item.status !== "blocked")
    .slice(0, 5);

  const canPerformActions =
    Boolean(accessToken) && accountOptions.length > 0 && !accountsLoading;

  return (
    <div className="app-shell">
      <div className="app-content">
        <div className="app-gradient">
          <SunHeader
            subtitle={`${branch.name} · ${branch.city}`}
            actionSlot={
              <div style={{ display: "flex", alignItems: "center", gap: "1rem" }}>
                <LanguageDropdown />
                <button type="button" className="ghost-btn" onClick={onSignOut}>
                  {s.logOut}
                </button>
              </div>
            }
          />
          
          {/* Floating Chat Button */}
          <button
            type="button"
            className="floating-chat-button"
            onClick={() => {
              // Use the current page language from the toggle
              setPreferredLanguage(language);
              navigate("/chat");
            }}
            title="Voice assistant"
            aria-label="Open voice assistant"
          >
            <AIAssistantLogo size={166} showAssistant={true} />
          </button>

          <VoiceEnrollmentModal
            isOpen={isVoiceEnrollmentModalOpen}
            onClose={() => setIsVoiceEnrollmentModalOpen(false)}
            onConfirm={() => {
              setIsVoiceEnrollmentModalOpen(false);
              navigate("/device-binding");
            }}
            strings={{
              addVoiceToAccount: s.addVoiceToAccount,
              addVoicePrompt: s.addVoicePrompt,
              addVoicePromptDescription: s.addVoicePromptDescription,
              cancel: s.cancel,
              okay: s.okay,
            }}
          />

          <ForceLogoutModal
            isOpen={isForceLogoutModalOpen}
            onConfirm={() => {
              setIsForceLogoutModalOpen(false);
              onSignOut();
            }}
            strings={{
              forceLogoutTitle: s.forceLogoutTitle,
              forceLogoutMessage: s.forceLogoutMessage,
              forceLogoutDescription: s.forceLogoutDescription,
              okay: s.okay,
            }}
          />

          <main className="card-surface profile-surface">
            {(deviceBindingRequired || voiceEnrollmentRequired || voiceReverificationRequired) && (
              <section className="profile-card profile-card--span">
                <div className="form-error">
                  <p>
                    {deviceBindingRequired
                      ? s.deviceBinding.forSecureBanking
                      : voiceEnrollmentRequired
                        ? s.deviceBinding.completeVoiceEnrollment
                        : s.deviceBinding.refreshVoiceSignature}
                  </p>
                  <p className="profile-hint">
                    {s.deviceBinding.speakPassphraseLabel} <strong>{voicePhrase}</strong>
                  </p>
                  <button
                    type="button"
                    className="link-btn"
                    onClick={() => navigate("/device-binding")}
                  >
                    {s.deviceBinding.manageDeviceBinding}
                  </button>
                </div>
              </section>
            )}

            <section className="profile-hero">
              <div>
                <p className="profile-eyebrow">{s.loggedInAs}</p>
                <h1>{fullName}</h1>
                <p className="profile-segment">{segment} {s.bankingCustomer}</p>
                <p className="profile-hint">{s.customerId} {customerId}</p>
              </div>
              {!checkingVoiceBinding && (
                <div
                  className={`profile-pill ${isVoiceSecured ? "profile-pill--secured" : "profile-pill--unsecured"}`}
                  onClick={!isVoiceSecured ? () => setIsVoiceEnrollmentModalOpen(true) : undefined}
                  style={!isVoiceSecured ? { cursor: "pointer" } : undefined}
                  role={!isVoiceSecured ? "button" : undefined}
                  tabIndex={!isVoiceSecured ? 0 : undefined}
                  onKeyDown={!isVoiceSecured ? (e) => {
                    if (e.key === "Enter" || e.key === " ") {
                      e.preventDefault();
                      setIsVoiceEnrollmentModalOpen(true);
                    }
                  } : undefined}
                >
                  <span className={`status-dot ${isVoiceSecured ? "status-dot--online" : "status-dot--warning"}`} />
                  {isVoiceSecured ? s.voiceSessionSecured : s.voiceSessionUnsecured}
                </div>
              )}
            </section>

            <section className="profile-grid">
              <article className="profile-card">
                <h2>{s.accountSnapshot}</h2>
                {accountsLoading && <p className="profile-hint">{s.loadingAccountDetails}</p>}
                {accountsError && accountOptions.length === 0 && (
                  <div className="form-error">{accountsError}</div>
                )}
                <ul>
                  {displayedAccounts.map((account) => {
                    const isBalanceVisible = balanceVisibility[account.accountNumber] ?? false;
                    const balanceValue =
                      account.ledgerBalance ?? parseBalanceString(account.balance);
                    const balanceDisplay = isBalanceVisible
                      ? formatCurrency(balanceValue, account.currency)
                      : `${account.currency} ••••`;
                    return (
                      <li key={account.accountNumber}>
                        <div>
                          <p className="profile-label">{account.type}</p>
                          <p className="profile-value">{account.accountNumber}</p>
                        </div>
                        <div className="balance-visibility">
                          <div className="profile-amount">
                            <span>{account.currency}</span>
                            <strong>{balanceDisplay}</strong>
                          </div>
                          <button
                            type="button"
                            className="link-btn"
                            onClick={() => toggleBalanceVisibility(account.accountNumber)}
                          >
                            {isBalanceVisible ? s.hide : s.show}
                          </button>
                        </div>
                        {isBalanceVisible && account.availableBalance !== null && (
                          <p className="profile-hint">
                            {s.available} {formatCurrency(account.availableBalance, account.currency)}
                          </p>
                        )}
                        {(account.debitCards.length > 0 || account.creditCards.length > 0) && (
                          <div className="account-card-groups">
                            {account.debitCards.length > 0 && (
                              <div>
                                <p className="profile-label">{s.debitCards}</p>
                                <ul className="cards-list">
                                  {account.debitCards.slice(0, 5).map((card) => (
                                    <li key={card.id} className="card-pill">
                                      <span>{card.maskedNumber}</span>
                                      <span>{card.network}</span>
                                      <span className={`card-status card-status--${card.status}`}>
                                        {card.status}
                                      </span>
                                    </li>
                                  ))}
                                </ul>
                              </div>
                            )}
                            {account.creditCards.length > 0 && (
                              <div>
                                <p className="profile-label">{s.creditCards}</p>
                                <ul className="cards-list">
                                  {account.creditCards.slice(0, 5).map((card) => (
                                    <li key={card.id} className="card-pill">
                                      <span>{card.maskedNumber}</span>
                                      <span>{card.network}</span>
                                      <span className={`card-status card-status--${card.status}`}>
                                        {card.status}
                                      </span>
                                    </li>
                                  ))}
                                </ul>
                              </div>
                            )}
                          </div>
                        )}
                      </li>
                    );
                  })}
                </ul>
                {accountCards.length > 5 && (
                  <p className="profile-hint">{s.showingAccounts} {accountCards.length} {s.accounts}</p>
                )}
              </article>

              <article className="profile-card">
                <h2>{s.sessionInsights}</h2>
                <div className="profile-meta">
                  <div>
                    <p className="profile-label">{s.lastVoiceLogin}</p>
                    <p className="profile-value">
                      {formattedLastLogin ?? s.noRecentLogin}
                    </p>
                  </div>
                  <div>
                    <p className="profile-label">{s.nextReminder}</p>
                    <p className="profile-value">
                      {nextReminder?.label ?? s.noRemindersConfigured}
                    </p>
                    {formattedReminder && <p className="profile-hint">{formattedReminder}</p>}
                  </div>
                </div>
              </article>

              <article className="profile-card profile-card--span">
                <h2>{s.quickActions}</h2>
                <div className="quick-actions">
                  <button
                    type="button"
                    className="secondary-btn"
                    onClick={() => handlePanelToggle("balance")}
                    disabled={!canPerformActions}
                  >
                    {s.checkBalances}
                  </button>
                  <button
                    type="button"
                    className="secondary-btn"
                    onClick={() => handlePanelToggle("transfer")}
                    disabled={!canPerformActions}
                  >
                    {s.makeTransfer}
                  </button>
                  <button
                    type="button"
                    className="secondary-btn"
                    onClick={() => handlePanelToggle("transactions")}
                    disabled={!canPerformActions}
                  >
                    {s.reviewTransactions}
                  </button>
                  <button
                    type="button"
                    className="secondary-btn"
                    onClick={() => handlePanelToggle("reminders")}
                    disabled={!canPerformActions}
                  >
                    {s.manageReminders}
                  </button>
                  <button
                    type="button"
                    className="secondary-btn"
                    onClick={() => handlePanelToggle("beneficiaries")}
                    disabled={!canPerformActions}
                  >
                    {s.beneficiaries}
                  </button>
                  <button
                    type="button"
                    className="secondary-btn"
                    onClick={() => handlePanelToggle("deviceBinding")}
                  >
                    {s.trustedDevices}
                  </button>
                </div>
              </article>

              {panels.balance && (
                <article id="panel-balance" className="profile-card profile-card--span">
                  <h2>{s.balanceEnquiry}</h2>
                  <form className="form-grid" onSubmit={handleBalanceSubmit}>
                    <label htmlFor="balance-account">
                      {s.account}
                      <select
                        id="balance-account"
                        value={balanceAccountId}
                        onChange={(event) => setBalanceAccountId(event.target.value)}
                        required
                      >
                        {accountOptions.map((option) => (
                          <option key={option.id} value={option.id}>
                            {option.number}
                          </option>
                        ))}
                      </select>
                    </label>
                    <button type="submit" className="primary-btn primary-btn--compact" disabled={balanceLoading}>
                      {balanceLoading ? s.checking : s.viewBalance}
                    </button>
                  </form>
                  {balanceError && <div className="form-error">{balanceError}</div>}
                  {balanceResult && (
                    <div className="balance-result">
                      <p>
                        {s.ledgerBalance}{" "}
                        <strong>
                          {formatCurrency(balanceResult.ledgerBalance, balanceResult.currency)}
                        </strong>
                      </p>
                      <p>
                        {s.availableBalance}{" "}
                        <strong>
                          {formatCurrency(balanceResult.availableBalance, balanceResult.currency)}
                        </strong>
                      </p>
                      <p className="profile-hint">{s.status} {balanceResult.status}</p>
                    </div>
                  )}
                </article>
              )}

              {panels.transfer && (
                <article id="panel-transfer" className="profile-card profile-card--span">
                  <h2>{s.internalTransfer}</h2>
                  <form className="form-grid" onSubmit={handleTransferSubmit}>
                    <label htmlFor="transfer-source">
                      {s.fromAccount}
                      <select
                        id="transfer-source"
                        name="sourceAccountId"
                        value={transferForm.sourceAccountId}
                        onChange={handleTransferChange}
                        required
                      >
                        {accountOptions.map((option) => (
                          <option key={option.id} value={option.id}>
                            {option.number}
                          </option>
                        ))}
                      </select>
                    </label>
                    <label htmlFor="transfer-destination">
                      {s.destinationAccountNumber}
                      <input
                        id="transfer-destination"
                        type="text"
                        name="destinationAccountNumber"
                        value={transferForm.destinationAccountNumber}
                        onChange={handleTransferChange}
                        required
                      />
                    </label>
                    {beneficiaryOptions.length > 0 && (
                      <label htmlFor="transfer-beneficiary">
                        {s.savedBeneficiary}
                        <select
                          id="transfer-beneficiary"
                          name="beneficiaryId"
                          value={transferForm.beneficiaryId}
                          onChange={handleTransferChange}
                        >
                          <option value="">{s.selectBeneficiary}</option>
                          {beneficiaryOptions.map((option) => (
                            <option key={option.id} value={option.id}>
                              {option.name} · {option.accountNumber}
                            </option>
                          ))}
                        </select>
                      </label>
                    )}
                    <label htmlFor="transfer-amount">
                      {s.amount}
                      <input
                        id="transfer-amount"
                        type="number"
                        min="1"
                        step="0.01"
                        name="amount"
                        value={transferForm.amount}
                        onChange={handleTransferChange}
                        required
                      />
                    </label>
                    <label htmlFor="transfer-remarks" className="form-grid--span">
                      {s.remarks}
                      <textarea
                        id="transfer-remarks"
                        name="remarks"
                        value={transferForm.remarks}
                        onChange={handleTransferChange}
                        placeholder={s.optionalNarration}
                      />
                    </label>
                    <button type="submit" className="primary-btn primary-btn--compact" disabled={transferLoading}>
                      {transferLoading ? s.processing : s.initiateTransfer}
                    </button>
                  </form>
                  {transferStatus && (
                    <div
                      className={
                        transferStatus.type === "success" ? "form-success" : "form-error"
                      }
                    >
                      {transferStatus.message}
                    </div>
                  )}
                </article>
              )}

              {panels.beneficiaries && (
                <article id="panel-beneficiaries" className="profile-card profile-card--span">
                  <h2>{s.beneficiariesTitle}</h2>
                  {beneficiariesError && <div className="form-error">{beneficiariesError}</div>}
                  {beneficiariesLoading && <p>{s.loadingAccountDetails}</p>}
                  {!beneficiariesLoading && !beneficiariesError && (
                    <>
                      {displayedBeneficiaries.length === 0 ? (
                        <p className="profile-hint">
                          {s.noBeneficiariesYet}
                        </p>
                      ) : (
                        <ul className="beneficiary-mini-list">
                          {displayedBeneficiaries.map((item) => (
                            <li key={item.id} className="beneficiary-mini-list__item">
                              <div>
                                <p className="beneficiary-mini-list__name">{item.name}</p>
                                <p className="beneficiary-mini-list__account">{item.accountNumber}</p>
                                {(() => {
                                  const lastUsed = formatDateTime(item.lastUsedAt);
                                  if (!lastUsed) return null;
                                  return (
                                    <p className="beneficiary-mini-list__meta">{s.lastUsed || "Last used"} {lastUsed}</p>
                                  );
                                })()}
                              </div>
                            </li>
                          ))}
                        </ul>
                      )}
                      <div className="card-form__actions">
                        <button
                          type="button"
                          className="secondary-btn"
                          onClick={() => navigate("/beneficiaries")}
                        >
                          {s.viewAllBeneficiaries}
                        </button>
                      </div>
                    </>
                  )}
                </article>
              )}

              {panels.deviceBinding && (
                <article id="panel-device-binding" className="profile-card profile-card--span">
                  <h2>{s.deviceBinding.title}</h2>
                  {deviceLoading && <p className="profile-hint">{s.deviceBinding.loading}</p>}
                  {deviceError && <div className="form-error">{deviceError}</div>}
                  {!deviceLoading && deviceBindings.length === 0 && (
                    <p className="profile-hint">{s.deviceBinding.noDevices}</p>
                  )}
                  {!deviceLoading && deviceBindings.length > 0 && (
                    <ul className="transactions-list">
                      {deviceBindings.map((binding) => (
                        <li key={binding.id} className="transaction-row">
                          <div>
                            <p className="profile-label">{binding.deviceLabel ?? "Unnamed device"}</p>
                            <p className="profile-value">{binding.platform ?? "unknown"} · Trust {binding.trustLevel}</p>
                            <p className="profile-hint">
                              {s.deviceBinding.lastVerified} {binding.lastVerifiedAt ? new Date(binding.lastVerifiedAt).toLocaleString("en-IN") : s.deviceBinding.never}
                            </p>
                          </div>
                          <div className="profile-account-actions">
                            {binding.trustLevel !== "revoked" ? (
                              <button
                                type="button"
                                className="link-btn"
                                onClick={() => handleDeviceRevoke(binding.id)}
                                disabled={deviceLoading}
                              >
                                {s.deviceBinding.revoke}
                              </button>
                            ) : (
                              <span className="profile-hint">{s.deviceBinding.revoked}</span>
                            )}
                          </div>
                        </li>
                      ))}
                    </ul>
                  )}
                  <div className="transactions-actions">
                    <button
                      type="button"
                      className="link-btn"
                      onClick={() => navigate("/device-binding")}
                    >
                      {s.deviceBinding.manageDeviceBinding}
                    </button>
                  </div>
                </article>
              )}

              {panels.reminders && (
                <article id="panel-reminders" className="profile-card profile-card--span">
                  <h2>{s.reminders}</h2>
                  {remindersError && <div className="form-error">{remindersError}</div>}
                  {reminderStatus && (
                    <div
                      className={
                        reminderStatus.type === "success" ? "form-success" : "form-error"
                      }
                    >
                      {reminderStatus.message}
                    </div>
                  )}
                  <form className="form-grid" onSubmit={handleReminderSubmit}>
                    <label htmlFor="reminder-type">
                      {s.type}
                      <select
                        id="reminder-type"
                        name="reminderType"
                        value={reminderForm.reminderType}
                        onChange={handleReminderChange}
                      >
                        <option value="bill_payment">Bill payment</option>
                        <option value="due_date">Due date</option>
                        <option value="savings">Savings</option>
                        <option value="custom">Custom</option>
                      </select>
                    </label>
                    <label htmlFor="reminder-when">
                      {s.remindAt}
                      <input
                        id="reminder-when"
                        type="datetime-local"
                        name="remindAt"
                        value={reminderForm.remindAt}
                        onChange={handleReminderChange}
                        required
                      />
                    </label>
                    <label htmlFor="reminder-message" className="form-grid--span">
                      {s.message}
                      <textarea
                        id="reminder-message"
                        name="message"
                        value={reminderForm.message}
                        onChange={handleReminderChange}
                        required
                      />
                    </label>
                    <label htmlFor="reminder-account">
                      {s.linkedAccount}
                      <select
                        id="reminder-account"
                        name="accountId"
                        value={reminderForm.accountId}
                        onChange={handleReminderChange}
                      >
                        <option value="">{s.none}</option>
                        {accountOptions.map((option) => (
                          <option key={option.id} value={option.id}>
                            {option.number}
                          </option>
                        ))}
                      </select>
                    </label>
                    <label htmlFor="reminder-channel">
                      {s.channel}
                      <select
                        id="reminder-channel"
                        name="channel"
                        value={reminderForm.channel}
                        onChange={handleReminderChange}
                      >
                        <option value="voice">Voice</option>
                        <option value="sms">SMS</option>
                        <option value="push">Push</option>
                      </select>
                    </label>
                    <label htmlFor="reminder-recurrence">
                      {s.recurrenceRule}
                      <input
                        id="reminder-recurrence"
                        type="text"
                        name="recurrenceRule"
                        value={reminderForm.recurrenceRule}
                        onChange={handleReminderChange}
                        placeholder={s.optionalRrule}
                      />
                    </label>
                    <button type="submit" className="primary-btn primary-btn--compact" disabled={remindersLoading}>
                      {remindersLoading ? s.creating : s.createReminder}
                    </button>
                  </form>
                  <ul className="reminders-list">
                    {displayedReminders.map((reminder) => (
                      <li key={reminder.id} className="reminder-row">
                        <div>
                          <p className="profile-label">{reminder.reminderType}</p>
                          <p className="profile-value">{reminder.message}</p>
                          <p className="profile-hint">
                            {formatDateTime(reminder.remindAt)} · Status: {reminder.status}
                          </p>
                        </div>
                        {reminder.status !== "sent" && (
                          <button
                            type="button"
                            className="link-btn"
                            onClick={() => handleReminderStatusUpdate(reminder.id, "sent")}
                          >
                            {s.markSent}
                          </button>
                        )}
                      </li>
                    ))}
                    {displayedReminders.length === 0 && !remindersLoading && (
                      <li>
                        <p className="profile-hint">{s.noRemindersYet}</p>
                      </li>
                    )}
                  </ul>
                  {reminders.length > 5 && (
                    <div className="transactions-actions">
                      <button
                        type="button"
                        className="link-btn"
                        onClick={() => navigate("/reminders")}
                      >
                        {s.viewAllReminders}
                      </button>
                    </div>
                  )}
                </article>
              )}

              {panels.transactions && (
                <article id="panel-transactions" className="profile-card profile-card--span">
                  <h2>{s.recentTransactions}</h2>
                  <div className="form-grid">
                    <label htmlFor="transactions-account">
                      {s.account}
                      <select
                        id="transactions-account"
                        value={selectedTxnAccountId}
                        onChange={(event) => setSelectedTxnAccountId(event.target.value)}
                      >
                        {accountOptions.map((option) => (
                          <option key={option.id} value={option.id}>
                            {option.number}
                          </option>
                        ))}
                      </select>
                    </label>
                  </div>
                  {selectedTxnAccountNumber && (
                    <p className="profile-hint">{s.account} • {selectedTxnAccountNumber}</p>
                  )}
                  {transactionsError && <div className="form-error">{transactionsError}</div>}
                  {transactionsLoading && <p className="profile-hint">{s.fetchingTransactions}</p>}
                  {!transactionsLoading && transactions.length > 0 && (
                    <ul className="transactions-list">
                      {transactions.map((txn) => (
                        <li key={txn.id} className="transaction-row">
                          <div>
                            <p className="profile-label">{txn.type}</p>
                            <p className="profile-value">{txn.description ?? "—"}</p>
                            <p className="profile-hint">{formatDateTime(txn.occurredAt)}</p>
                          </div>
                          <div className="profile-amount">
                            <span>{txn.currency}</span>
                            <strong>{formatCurrency(txn.amount, txn.currency)}</strong>
                          </div>
                        </li>
                      ))}
                    </ul>
                  )}
                  {!transactionsLoading && !transactionsError && transactions.length === 0 && (
                    <p className="profile-hint">
                      {s.selectAccountToView}
                    </p>
                  )}
                  <div className="transactions-actions">
                    <button
                      type="button"
                      className="link-btn"
                      disabled={!accountOptions.length}
                      onClick={() => {
                        const targetAccountId = selectedTxnAccountId || accountOptions[0]?.id;
                        if (targetAccountId) {
                          navigate("/transactions", {
                            state: { accountId: targetAccountId },
                          });
                        }
                      }}
                    >
                      {s.viewAllTransactions}
                    </button>
                  </div>
                </article>
              )}
            </section>
          </main>
        </div>
      </div>
    </div>
  );
};

Profile.propTypes = {
  user: PropTypes.shape({
    fullName: PropTypes.string.isRequired,
    segment: PropTypes.string.isRequired,
    customerId: PropTypes.string.isRequired,
    branch: PropTypes.shape({
      name: PropTypes.string.isRequired,
      city: PropTypes.string.isRequired,
    }).isRequired,
    accountSummary: PropTypes.arrayOf(
      PropTypes.shape({
        accountNumber: PropTypes.string.isRequired,
        type: PropTypes.string.isRequired,
        balance: PropTypes.string.isRequired,
        currency: PropTypes.string.isRequired,
      }),
    ).isRequired,
    lastLogin: PropTypes.string.isRequired,
    nextReminder: PropTypes.shape({
      label: PropTypes.string.isRequired,
      date: PropTypes.oneOfType([PropTypes.string, PropTypes.instanceOf(Date)]).isRequired,
    }),
  }),
  accessToken: PropTypes.string,
  onSignOut: PropTypes.func.isRequired,
  sessionDetail: PropTypes.shape({
    deviceBindingRequired: PropTypes.bool,
    voiceEnrollmentRequired: PropTypes.bool,
    voiceReverificationRequired: PropTypes.bool,
  }),
};

Profile.defaultProps = {
  user: null,
  accessToken: null,
  sessionDetail: null,
};

export default Profile;

