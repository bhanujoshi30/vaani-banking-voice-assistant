import PropTypes from "prop-types";
import { useCallback, useEffect, useMemo, useState } from "react";
import { Navigate, useNavigate } from "react-router-dom";

import SunHeader from "../components/SunHeader.jsx";
import "./Chat.css";
import {
  fetchAccounts,
  fetchTransactions,
  fetchAccountBalance,
  createInternalTransfer,
  fetchReminders,
  createReminder,
  updateReminderStatus,
  fetchBeneficiaries,
} from "../api/client.js";

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

const PANEL_KEYS = ["balance", "transfer", "transactions", "reminders", "beneficiaries"];
const SESSION_EXPIRY_CODES = new Set([
  "session_timeout",
  "session_expired",
  "session_inactive",
  "session_invalid",
]);

const Profile = ({ user, accessToken, onSignOut, sessionDetail }) => {
  const navigate = useNavigate();

  const [panels, setPanels] = useState({
    balance: false,
    transfer: false,
    transactions: false,
    reminders: false,
    beneficiaries: false,
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

  const bindingDetail = sessionDetail ?? {};
  const deviceBindingRequired = Boolean(bindingDetail.deviceBindingRequired);
  const voiceEnrollmentRequired = Boolean(bindingDetail.voiceEnrollmentRequired);
  const voiceReverificationRequired = Boolean(bindingDetail.voiceReverificationRequired);
  const voicePhrase = bindingDetail.voicePhrase ?? "Sun Bank hai mera saathi";

  const handleSessionExpiry = useCallback(
    (error, setter) => {
    if (error?.code && SESSION_EXPIRY_CODES.has(error.code)) {
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
      setTransferStatus({ type: "error", message: "Select a source account." });
      return;
    }

    const destinationAccountNumber = transferForm.destinationAccountNumber.trim();
    if (!destinationAccountNumber) {
      setTransferStatus({ type: "error", message: "Enter a destination account number." });
      return;
    }

    const transferAmount = Number(transferForm.amount);
    if (!Number.isFinite(transferAmount) || transferAmount <= 0) {
      setTransferStatus({ type: "error", message: "Enter a valid transfer amount." });
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
      setTransferStatus({ type: "success", message: "Transfer initiated successfully." });
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
      setReminderStatus({ type: "success", message: "Reminder created successfully." });
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
              <button type="button" className="ghost-btn" onClick={onSignOut}>
                Log out
              </button>
            }
          />
          
          {/* Floating Chat Button */}
          <button
            type="button"
            className="floating-chat-button"
            onClick={() => navigate("/chat")}
            title="Chat with Vaani"
          >
            <svg
              width="28"
              height="28"
              viewBox="0 0 24 24"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                d="M21 15C21 15.5304 20.7893 16.0391 20.4142 16.4142C20.0391 16.7893 19.5304 17 19 17H7L3 21V5C3 4.46957 3.21071 3.96086 3.58579 3.58579C3.96086 3.21071 4.46957 3 5 3H19C19.5304 3 20.0391 3.21071 20.4142 3.58579C20.7893 3.96086 21 4.46957 21 5V15Z"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                fill="white"
              />
            </svg>
          </button>

          <main className="card-surface profile-surface">
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

            <section className="profile-hero">
              <div>
                <p className="profile-eyebrow">Logged in as</p>
                <h1>{fullName}</h1>
                <p className="profile-segment">{segment} banking customer</p>
                <p className="profile-hint">Customer ID: {customerId}</p>
              </div>
              <div className="profile-pill">
                <span className="status-dot status-dot--online" />
                Voice session secured
              </div>
            </section>

            <section className="profile-grid">
              <article className="profile-card">
                <h2>Account snapshot</h2>
                {accountsLoading && <p className="profile-hint">Loading account details…</p>}
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
                            {isBalanceVisible ? "Hide" : "Show"}
                          </button>
                        </div>
                        {isBalanceVisible && account.availableBalance !== null && (
                          <p className="profile-hint">
                            Available {formatCurrency(account.availableBalance, account.currency)}
                          </p>
                        )}
                        {(account.debitCards.length > 0 || account.creditCards.length > 0) && (
                          <div className="account-card-groups">
                            {account.debitCards.length > 0 && (
                              <div>
                                <p className="profile-label">Debit cards</p>
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
                                <p className="profile-label">Credit cards</p>
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
                  <p className="profile-hint">Showing 5 of {accountCards.length} accounts.</p>
                )}
              </article>

              <article className="profile-card">
                <h2>Session insights</h2>
                <div className="profile-meta">
                  <div>
                    <p className="profile-label">Last voice login</p>
                    <p className="profile-value">
                      {formattedLastLogin ?? "No recent login recorded"}
                    </p>
                  </div>
                  <div>
                    <p className="profile-label">Next reminder</p>
                    <p className="profile-value">
                      {nextReminder?.label ?? "No reminders configured"}
                    </p>
                    {formattedReminder && <p className="profile-hint">{formattedReminder}</p>}
                  </div>
                </div>
              </article>

              <article className="profile-card profile-card--span">
                <h2>Quick actions</h2>
                <div className="quick-actions">
                  <button
                    type="button"
                    className="secondary-btn"
                    onClick={() => handlePanelToggle("balance")}
                    disabled={!canPerformActions}
                  >
                    Check balances
                  </button>
                  <button
                    type="button"
                    className="secondary-btn"
                    onClick={() => handlePanelToggle("transfer")}
                    disabled={!canPerformActions}
                  >
                    Make a transfer
                  </button>
                  <button
                    type="button"
                    className="secondary-btn"
                    onClick={() => handlePanelToggle("transactions")}
                    disabled={!canPerformActions}
                  >
                    Review transactions
                  </button>
                  <button
                    type="button"
                    className="secondary-btn"
                    onClick={() => handlePanelToggle("reminders")}
                    disabled={!canPerformActions}
                  >
                    Manage reminders
                  </button>
                  <button
                    type="button"
                    className="secondary-btn"
                    onClick={() => handlePanelToggle("beneficiaries")}
                    disabled={!canPerformActions}
                  >
                    Beneficiaries
                  </button>
                  <button
                    type="button"
                    className="secondary-btn"
                    onClick={() => navigate("/device-binding")}
                  >
                    Trusted devices
                  </button>
                </div>
              </article>

              {panels.balance && (
                <article id="panel-balance" className="profile-card profile-card--span">
                  <h2>Balance enquiry</h2>
                  <form className="form-grid" onSubmit={handleBalanceSubmit}>
                    <label htmlFor="balance-account">
                      Account
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
                      {balanceLoading ? "Checking…" : "View balance"}
                    </button>
                  </form>
                  {balanceError && <div className="form-error">{balanceError}</div>}
                  {balanceResult && (
                    <div className="balance-result">
                      <p>
                        Ledger balance: {" "}
                        <strong>
                          {formatCurrency(balanceResult.ledgerBalance, balanceResult.currency)}
                        </strong>
                      </p>
                      <p>
                        Available balance: {" "}
                        <strong>
                          {formatCurrency(balanceResult.availableBalance, balanceResult.currency)}
                        </strong>
                      </p>
                      <p className="profile-hint">Status: {balanceResult.status}</p>
                    </div>
                  )}
                </article>
              )}

              {panels.transfer && (
                <article id="panel-transfer" className="profile-card profile-card--span">
                  <h2>Internal transfer</h2>
                  <form className="form-grid" onSubmit={handleTransferSubmit}>
                    <label htmlFor="transfer-source">
                      From account
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
                      Destination account number
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
                        Saved beneficiary (optional)
                        <select
                          id="transfer-beneficiary"
                          name="beneficiaryId"
                          value={transferForm.beneficiaryId}
                          onChange={handleTransferChange}
                        >
                          <option value="">Select beneficiary</option>
                          {beneficiaryOptions.map((option) => (
                            <option key={option.id} value={option.id}>
                              {option.name} · {option.accountNumber}
                            </option>
                          ))}
                        </select>
                      </label>
                    )}
                    <label htmlFor="transfer-amount">
                      Amount (INR)
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
                      Remarks
                      <textarea
                        id="transfer-remarks"
                        name="remarks"
                        value={transferForm.remarks}
                        onChange={handleTransferChange}
                        placeholder="Optional narration"
                      />
                    </label>
                    <button type="submit" className="primary-btn primary-btn--compact" disabled={transferLoading}>
                      {transferLoading ? "Processing…" : "Initiate transfer"}
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
                  <h2>Beneficiaries</h2>
                  {beneficiariesError && <div className="form-error">{beneficiariesError}</div>}
                  {beneficiariesLoading && <p>Loading beneficiaries…</p>}
                  {!beneficiariesLoading && !beneficiariesError && (
                    <>
                      {displayedBeneficiaries.length === 0 ? (
                        <p className="profile-hint">
                          No beneficiaries added yet. Add one to speed up transfers.
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
                                    <p className="beneficiary-mini-list__meta">Last used {lastUsed}</p>
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
                          View all beneficiaries
                        </button>
                      </div>
                    </>
                  )}
                </article>
              )}

              {panels.reminders && (
                <article id="panel-reminders" className="profile-card profile-card--span">
                  <h2>Reminders</h2>
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
                      Type
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
                      Remind at
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
                      Message
                      <textarea
                        id="reminder-message"
                        name="message"
                        value={reminderForm.message}
                        onChange={handleReminderChange}
                        required
                      />
                    </label>
                    <label htmlFor="reminder-account">
                      Linked account
                      <select
                        id="reminder-account"
                        name="accountId"
                        value={reminderForm.accountId}
                        onChange={handleReminderChange}
                      >
                        <option value="">None</option>
                        {accountOptions.map((option) => (
                          <option key={option.id} value={option.id}>
                            {option.number}
                          </option>
                        ))}
                      </select>
                    </label>
                    <label htmlFor="reminder-channel">
                      Channel
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
                      Recurrence rule
                      <input
                        id="reminder-recurrence"
                        type="text"
                        name="recurrenceRule"
                        value={reminderForm.recurrenceRule}
                        onChange={handleReminderChange}
                        placeholder="Optional RFC 5545 RRULE"
                      />
                    </label>
                    <button type="submit" className="primary-btn primary-btn--compact" disabled={remindersLoading}>
                      {remindersLoading ? "Creating…" : "Create reminder"}
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
                            Mark sent
                          </button>
                        )}
                      </li>
                    ))}
                    {displayedReminders.length === 0 && !remindersLoading && (
                      <li>
                        <p className="profile-hint">No reminders configured yet.</p>
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
                        View all reminders
                      </button>
                    </div>
                  )}
                </article>
              )}

              {panels.transactions && (
                <article id="panel-transactions" className="profile-card profile-card--span">
                  <h2>Recent transactions</h2>
                  <div className="form-grid">
                    <label htmlFor="transactions-account">
                      Account
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
                    <p className="profile-hint">Account • {selectedTxnAccountNumber}</p>
                  )}
                  {transactionsError && <div className="form-error">{transactionsError}</div>}
                  {transactionsLoading && <p className="profile-hint">Fetching transactions…</p>}
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
                      Select an account above to view the latest five transactions.
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
                      View all transactions
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

