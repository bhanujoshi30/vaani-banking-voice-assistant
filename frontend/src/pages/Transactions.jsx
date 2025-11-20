import PropTypes from "prop-types";
import { useCallback, useEffect, useMemo, useState } from "react";
import { Navigate, useLocation, useNavigate } from "react-router-dom";

import SunHeader from "../components/SunHeader.jsx";
import LanguageDropdown from "../components/LanguageDropdown.jsx";
import { fetchAccounts, fetchTransactions } from "../api/client.js";
import { usePageLanguage } from "../hooks/usePageLanguage.js";

const STATEMENT_FETCH_LIMIT = 500;
const RBI_MAX_STATEMENT_DAYS = 365;

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

const toIsoRangeBoundary = (dateString, endOfDay = false) => {
  const date = new Date(`${dateString}T00:00:00`);
  if (Number.isNaN(date.getTime())) return null;
  if (endOfDay) {
    date.setHours(23, 59, 59, 999);
  }
  return date;
};

const toIsoStringBoundary = (date, endOfDay = false) => {
  if (!(date instanceof Date)) return null;
  const copy = new Date(date);
  if (endOfDay) {
    copy.setHours(23, 59, 59, 999);
  }
  return copy.toISOString();
};

const formatAmountForCsv = (amount) =>
  new Intl.NumberFormat("en-IN", { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(
    Number(amount ?? 0),
  );

const formatDateForStatement = (value) =>
  new Date(value).toLocaleString("en-IN", {
    timeZone: "Asia/Kolkata",
    dateStyle: "medium",
    timeStyle: "short",
  });

const isDebitTransaction = (type = "") => {
  const lowered = type.toLowerCase();
  return ["withdraw", "debit", "payment", "transfer_out", "upi", "bill"].some((token) =>
    lowered.includes(token),
  );
};

const buildStatementCsv = ({
  bankName,
  account,
  accountHolder,
  fromDate,
  toDate,
  currency,
  closingBalance,
  transactions,
}) => {
  const generatedAt = formatDateForStatement(Date.now());

  const sortedTransactions = [...transactions].sort((a, b) => {
    const aDate = new Date(a.occurredAt).getTime();
    const bDate = new Date(b.occurredAt).getTime();
    return aDate - bDate;
  });

  const totalDelta = sortedTransactions.reduce((acc, txn) => {
    const amount = Number(txn.amount ?? 0);
    return acc + (isDebitTransaction(txn.type) ? -amount : amount);
  }, 0);

  const closing = Number(closingBalance ?? 0);
  const openingBalance = closing - totalDelta;
  let runningBalance = openingBalance;

  const openingDisplay = formatAmountForCsv(openingBalance);
  const closingDisplay = (() => {
    const finalBalance = sortedTransactions.reduce((acc, txn) => {
      const amount = Number(txn.amount ?? 0);
      return acc + (isDebitTransaction(txn.type) ? -amount : amount);
    }, openingBalance);
    return formatAmountForCsv(finalBalance);
  })();

  const headerLines = [
    `"${bankName}","Account Statement"`,
    `"Account Holder","${accountHolder}"`,
    `"Account Number","${account.accountNumber}"`,
    `"Account Type","${account.type.replace(/_/g, " ").toUpperCase()}"`,
    `"Statement Period","${fromDate} to ${toDate}"`,
    `"Opening Balance (${currency})","${openingDisplay}"`,
    `"Closing Balance (${currency})","${closingDisplay}"`,
    `"Generated On","${generatedAt}"`,
    "",
    "Transaction Date,Value Date,Description,Reference No.,Debit (INR),Credit (INR),Balance (INR),Status",
  ];

  const txnLines = sortedTransactions.map((txn) => {
    const amount = Number(txn.amount ?? 0);
    const debit = isDebitTransaction(txn.type) ? formatAmountForCsv(amount) : "";
    const credit = isDebitTransaction(txn.type) ? "" : formatAmountForCsv(amount);
    const occurred = formatDateForStatement(txn.occurredAt ?? Date.now());
    const reference = txn.referenceId ?? "—";
    const description = (txn.description ?? "").replace(/\s+/g, " ").trim() || "—";
    runningBalance += isDebitTransaction(txn.type) ? -amount : amount;
    const balanceFormatted = formatAmountForCsv(runningBalance);

    return [
      occurred,
      occurred,
      description,
      reference,
      debit,
      credit,
      balanceFormatted,
      txn.status ?? "—",
    ]
      .map((value) => `"${String(value ?? "").replace(/"/g, '""')}"`)
      .join(",");
  });

  return [...headerLines, ...txnLines].join("\n");
};

const SESSION_EXPIRY_CODES = new Set([
  "session_timeout",
  "session_expired",
  "session_inactive",
  "session_invalid",
]);

const TransactionsPage = ({ session, onSignOut }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const { strings } = usePageLanguage();
  const s = strings.transactions;

  const isAuthenticated = Boolean(session?.authenticated);
  const accessToken = session?.accessToken ?? "";

  const [accounts, setAccounts] = useState([]);
  const [accountsLoading, setAccountsLoading] = useState(false);
  const [accountsError, setAccountsError] = useState("");
  const [selectedAccountId, setSelectedAccountId] = useState(location.state?.accountId ?? "");
  const [transactions, setTransactions] = useState([]);
  const [transactionsLoading, setTransactionsLoading] = useState(false);
  const [transactionsError, setTransactionsError] = useState("");
  const [statementFrom, setStatementFrom] = useState("");
  const [statementTo, setStatementTo] = useState("");
  const [statementStatus, setStatementStatus] = useState(null);
  const [statementDownloading, setStatementDownloading] = useState(false);

  const handleSessionExpiry = useCallback(
    (error, setter) => {
      if (error?.code && SESSION_EXPIRY_CODES.has(error.code)) {
        const message = s.sessionExpired || "Your session expired due to inactivity. Please sign in again.";
        if (typeof setter === "function") {
          setter(message);
        }
        onSignOut?.();
        return true;
      }
      return false;
    },
    [onSignOut],
  );

  useEffect(() => {
    if (!isAuthenticated || !accessToken) {
      return;
    }
    let isMounted = true;
    setAccountsLoading(true);
    setAccountsError("");
    fetchAccounts({ accessToken })
      .then((data) => {
        if (!isMounted) return;
        setAccounts(data);
        setSelectedAccountId((prev) => prev || (data[0]?.id ?? ""));
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
  }, [isAuthenticated, accessToken, handleSessionExpiry]);

  useEffect(() => {
    if (!isAuthenticated || !accessToken || !selectedAccountId) {
      return;
    }
    let isMounted = true;
    setTransactionsLoading(true);
    setTransactionsError("");
    fetchTransactions({ accessToken, accountId: selectedAccountId })
      .then((data) => {
        if (!isMounted) return;
        setTransactions(data);
      })
      .catch((error) => {
        if (!isMounted) return;
        if (handleSessionExpiry(error, setTransactionsError)) return;
        setTransactionsError(error.message);
      })
      .finally(() => {
        if (isMounted) {
          setTransactionsLoading(false);
        }
      });
    return () => {
      isMounted = false;
    };
  }, [isAuthenticated, accessToken, selectedAccountId, handleSessionExpiry]);

  const accountLookup = useMemo(() => {
    const map = new Map();
    accounts.forEach((account) => {
      map.set(account.id, account);
    });
    return map;
  }, [accounts]);

  if (!isAuthenticated) {
    return <Navigate to="/" replace />;
  }

  const selectedAccount = selectedAccountId ? accountLookup.get(selectedAccountId) : null;

  const handleDownloadStatement = async () => {
    if (!selectedAccountId || !selectedAccount) {
      setStatementStatus({ type: "error", message: s.selectAccountToDownload });
      return;
    }
    if (!statementFrom || !statementTo) {
      setStatementStatus({ type: "error", message: s.chooseBothDates });
      return;
    }
    if (statementFrom > statementTo) {
      setStatementStatus({
        type: "error",
        message: s.startDateBeforeEnd,
      });
      return;
    }

    const fromDateObj = toIsoRangeBoundary(statementFrom, false);
    const toDateObj = toIsoRangeBoundary(statementTo, true);
    if (!fromDateObj || !toDateObj) {
      setStatementStatus({ type: "error", message: s.invalidDateRange });
      return;
    }

    const diffMs = toDateObj.getTime() - fromDateObj.getTime();
    const diffDays = diffMs / (1000 * 60 * 60 * 24);
    if (diffDays > RBI_MAX_STATEMENT_DAYS) {
      setStatementStatus({
        type: "error",
        message: `In compliance with RBI retention norms we can fetch up to ${RBI_MAX_STATEMENT_DAYS} days at once. Please select a shorter period.`,
      });
      return;
    }

    const fromIso = toIsoStringBoundary(fromDateObj, false);
    const toIso = toIsoStringBoundary(toDateObj, true);
    if (!fromIso || !toIso) {
      setStatementStatus({ type: "error", message: s.invalidDateRange });
      return;
    }

    setStatementDownloading(true);
    setStatementStatus(null);
    try {
      const statementTxns = await fetchTransactions({
        accessToken,
        accountId: selectedAccountId,
        from: fromIso,
        to: toIso,
        limit: STATEMENT_FETCH_LIMIT,
      });

      const csv = buildStatementCsv({
        bankName: "Sun National Bank",
        account: selectedAccount,
        accountHolder: session?.user?.fullName ?? "Sun National Bank Customer",
        fromDate: new Date(statementFrom).toLocaleDateString("en-IN"),
        toDate: new Date(statementTo).toLocaleDateString("en-IN"),
        currency: selectedAccount.currency ?? "INR",
        closingBalance: selectedAccount.availableBalance ?? selectedAccount.balance ?? 0,
        transactions: statementTxns,
      });

      const blob = new Blob([csv], { type: "text/csv;charset=utf-8" });
      const url = URL.createObjectURL(blob);
      const filename = `snb_statement_${selectedAccount.accountNumber}_${statementFrom}_to_${statementTo}.csv`;
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = filename;
      document.body.appendChild(anchor);
      anchor.click();
      document.body.removeChild(anchor);
      URL.revokeObjectURL(url);

      setStatementStatus({
        type: "success",
        message:
          statementTxns.length >= STATEMENT_FETCH_LIMIT
            ? `${s.mostRecent} ${STATEMENT_FETCH_LIMIT} ${s.transactionsLimit}`
            : `${s.statementDownloaded} ${statementTxns.length} ${s.transaction}`,
      });
    } catch (error) {
      if (
        handleSessionExpiry(error, (msg) =>
          setStatementStatus({ type: "error", message: msg }),
        )
      ) {
        return;
      }
      const rawMessage = error.message || s.unableToDownload;
      const friendlyMessage = rawMessage.includes("less than or equal to 500")
        ? s.rbiGuidelines
        : rawMessage;
      setStatementStatus({
        type: "error",
        message: friendlyMessage,
      });
    } finally {
      setStatementDownloading(false);
    }
  };

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
              <h2>{s.accounts}</h2>
              {accountsError && <div className="form-error">{accountsError}</div>}
              <div className="form-grid">
                <label htmlFor="transactions-account">
                  {s.selectAccount}
                  <select
                    id="transactions-account"
                    value={selectedAccountId}
                    onChange={(event) => setSelectedAccountId(event.target.value)}
                    disabled={accountsLoading}
                  >
                    {accounts.map((account) => (
                      <option key={account.id} value={account.id}>
                        {account.accountNumber}
                      </option>
                    ))}
                  </select>
                </label>
              </div>
              {selectedAccount && (
                <p className="profile-hint">
                  {s.currentBalance} {formatCurrency(selectedAccount.balance, selectedAccount.currency)}
                </p>
              )}
            </section>

            <section className="profile-card profile-card--span">
              <h2>{s.transactions}</h2>
              {transactionsError && <div className="form-error">{transactionsError}</div>}
              {transactionsLoading && <p className="profile-hint">{s.fetchingTransactions}</p>}
              {!transactionsLoading && transactions.length === 0 && (
                <p className="profile-hint">{s.noTransactionsFound}</p>
              )}
              {!transactionsLoading && transactions.length > 0 && (
                <ul className="transactions-list">
                  {transactions.map((txn) => (
                    <li key={txn.id} className="transaction-row">
                      <div>
                        <p className="profile-label">{txn.type}</p>
                        <p className="profile-value">{txn.description ?? "—"}</p>
                        <p className="profile-hint">
                          {formatDateTime(txn.occurredAt)} · {s.reference} {txn.referenceId ?? "—"}
                        </p>
                      </div>
                      <div className="profile-amount">
                        <span>{txn.currency}</span>
                        <strong>{formatCurrency(txn.amount, txn.currency)}</strong>
                      </div>
                    </li>
                  ))}
                </ul>
              )}

              <div className="statement-controls">
                <h3>{s.downloadStatement}</h3>
                <div className="form-grid">
                  <label htmlFor="statement-from">
                    {s.fromDate}
                    <input
                      id="statement-from"
                      type="date"
                      value={statementFrom}
                      onChange={(event) => setStatementFrom(event.target.value)}
                    />
                  </label>
                  <label htmlFor="statement-to">
                    {s.toDate}
                    <input
                      id="statement-to"
                      type="date"
                      value={statementTo}
                      onChange={(event) => setStatementTo(event.target.value)}
                    />
                  </label>
                </div>
                <button
                  type="button"
                  className="primary-btn primary-btn--compact"
                  onClick={handleDownloadStatement}
                  disabled={statementDownloading}
                >
                  {statementDownloading ? s.preparing : s.downloadStatementButton}
                </button>
                {statementStatus && (
                  <div
                    className={
                      statementStatus.type === "success" ? "form-success" : "form-error"
                    }
                  >
                    {statementStatus.message}
                  </div>
                )}
              </div>
            </section>
          </main>
        </div>
      </div>
    </div>
  );
};

TransactionsPage.propTypes = {
  session: PropTypes.shape({
    authenticated: PropTypes.bool,
    accessToken: PropTypes.string,
  }).isRequired,
  onSignOut: PropTypes.func.isRequired,
};

export default TransactionsPage;
