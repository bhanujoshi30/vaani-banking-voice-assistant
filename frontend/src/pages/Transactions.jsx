/* eslint-disable react-hooks/set-state-in-effect */
import PropTypes from "prop-types";
import { useEffect, useMemo, useState } from "react";
import { Navigate, useLocation, useNavigate } from "react-router-dom";

import SunHeader from "../components/SunHeader.jsx";
import { fetchAccounts, fetchTransactions } from "../api/client.js";

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

const TransactionsPage = ({ session }) => {
  const navigate = useNavigate();
  const location = useLocation();

  const isAuthenticated = Boolean(session?.authenticated);
  const accessToken = session?.accessToken ?? "";

  const [accounts, setAccounts] = useState([]);
  const [accountsLoading, setAccountsLoading] = useState(false);
  const [accountsError, setAccountsError] = useState("");
  const [selectedAccountId, setSelectedAccountId] = useState(location.state?.accountId ?? "");
  const [transactions, setTransactions] = useState([]);
  const [transactionsLoading, setTransactionsLoading] = useState(false);
  const [transactionsError, setTransactionsError] = useState("");

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
  }, [isAuthenticated, accessToken]);

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
  }, [isAuthenticated, accessToken, selectedAccountId]);

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

  return (
    <div className="app-shell">
      <div className="app-content">
        <div className="app-gradient">
          <SunHeader
            subtitle="Complete transaction history"
            actionSlot={
              <button type="button" className="ghost-btn" onClick={() => navigate(-1)}>
                Back
              </button>
            }
          />
          <main className="card-surface profile-surface">
            <section className="profile-card profile-card--span">
              <h2>Accounts</h2>
              {accountsError && <div className="form-error">{accountsError}</div>}
              <div className="form-grid">
                <label htmlFor="transactions-account">
                  Select account
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
                  Current balance: {formatCurrency(selectedAccount.balance, selectedAccount.currency)}
                </p>
              )}
            </section>

            <section className="profile-card profile-card--span">
              <h2>Transactions</h2>
              {transactionsError && <div className="form-error">{transactionsError}</div>}
              {transactionsLoading && <p className="profile-hint">Fetching transactions…</p>}
              {!transactionsLoading && transactions.length === 0 && (
                <p className="profile-hint">No transactions found for this account.</p>
              )}
              {!transactionsLoading && transactions.length > 0 && (
                <ul className="transactions-list">
                  {transactions.map((txn) => (
                    <li key={txn.id} className="transaction-row">
                      <div>
                        <p className="profile-label">{txn.type}</p>
                        <p className="profile-value">{txn.description ?? "—"}</p>
                        <p className="profile-hint">
                          {formatDateTime(txn.occurredAt)} · Reference: {txn.referenceId ?? "—"}
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
};

export default TransactionsPage;
/* eslint-enable react-hooks/set-state-in-effect */
