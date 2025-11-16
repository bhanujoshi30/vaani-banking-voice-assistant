import { useCallback, useEffect, useMemo, useState } from "react";
import PropTypes from "prop-types";
import { useNavigate } from "react-router-dom";

import SunHeader from "../components/SunHeader.jsx";
import {
  fetchBeneficiaries,
  createBeneficiary,
  deleteBeneficiary,
} from "../api/client.js";

const SESSION_EXPIRY_CODES = new Set([
  "session_timeout",
  "session_expired",
  "session_inactive",
  "session_invalid",
]);

const Beneficiaries = ({ session, onSignOut }) => {
  const navigate = useNavigate();
  const { accessToken, user } = session;

  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [form, setForm] = useState({
    name: "",
    accountNumber: "",
    bankName: "Sun National Bank",
    ifsc: "",
  });
  const [formError, setFormError] = useState("");
  const [formMessage, setFormMessage] = useState(null);
  const [formSubmitting, setFormSubmitting] = useState(false);

  const handleSessionExpiry = useCallback(
    (err) => {
      if (err?.code && SESSION_EXPIRY_CODES.has(err.code)) {
        onSignOut();
        return true;
      }
      return false;
    },
    [onSignOut],
  );

  const loadBeneficiaries = useCallback(() => {
    if (!accessToken) return;
    setLoading(true);
    setError("");
    fetchBeneficiaries({ accessToken })
      .then((data) => setItems(data))
      .catch((err) => {
        if (handleSessionExpiry(err)) return;
        setError(err.message);
      })
      .finally(() => setLoading(false));
  }, [accessToken, handleSessionExpiry]);

  useEffect(() => {
    loadBeneficiaries();
  }, [loadBeneficiaries]);

  const activeItems = useMemo(
    () => items.filter((item) => item.status !== "blocked"),
    [items],
  );

  const handleInputChange = (event) => {
    const { name, value } = event.target;
    setForm((prev) => ({ ...prev, [name]: value }));
    setFormError("");
    setFormMessage(null);
  };

  const handleAddBeneficiary = async (event) => {
    event.preventDefault();
    if (!accessToken) return;
    if (!form.name.trim() || !form.accountNumber.trim()) {
      setFormError("Please provide a beneficiary name and account number.");
      return;
    }

    setFormSubmitting(true);
    setFormError("");
    setFormMessage(null);
    try {
      const payload = {
        name: form.name.trim(),
        accountNumber: form.accountNumber.trim(),
        bankName: form.bankName.trim() || undefined,
        ifsc: form.ifsc.trim() || undefined,
      };
      const created = await createBeneficiary({ accessToken, payload });
      if (created) {
        setItems((prev) => [created, ...prev]);
        setFormMessage({ type: "success", text: "Beneficiary added successfully." });
        setForm({
          name: "",
          accountNumber: "",
          bankName: form.bankName,
          ifsc: "",
        });
      }
    } catch (err) {
      if (handleSessionExpiry(err)) return;
      setFormError(err.message);
    } finally {
      setFormSubmitting(false);
    }
  };

  const handleRemove = async (beneficiaryId) => {
    if (!accessToken || !beneficiaryId) return;
    const confirmed = window.confirm(
      "This will disable the beneficiary immediately. Do you want to continue?",
    );
    if (!confirmed) return;

    try {
      const removed = await deleteBeneficiary({ accessToken, beneficiaryId });
      if (removed) {
        setItems((prev) =>
          prev.map((item) => (item.id === removed.id ? removed : item)),
        );
      }
    } catch (err) {
      if (handleSessionExpiry(err)) return;
      window.alert(err.message);
    }
  };

  const hasItems = activeItems.length > 0;

  return (
    <div className="app-shell">
      <div className="app-content">
        <div className="app-gradient">
          <SunHeader
            subtitle={`${user?.branch?.name ?? "Sun National Bank"} · RBI compliant`}
            actionSlot={
              <button type="button" className="ghost-btn" onClick={onSignOut}>
                Log out
              </button>
            }
          />
          <main className="card-surface profile-surface">
            <article className="profile-card profile-card--span">
              <button type="button" className="link-btn" onClick={() => navigate(-1)}>
                ← Back to previous page
              </button>
              <h1>Manage beneficiaries</h1>
              <p className="profile-hint">
                RBI mandates a verified beneficiary list before high-value transfers. Add trusted
                recipients here so that future payments are quicker and safer.
              </p>
            </article>

            <article className="profile-card profile-card--span">
              <h2>Add a new beneficiary</h2>
              <form className="form-grid" onSubmit={handleAddBeneficiary}>
                <label htmlFor="beneficiary-name">
                  Beneficiary name
                  <input
                    id="beneficiary-name"
                    name="name"
                    type="text"
                    value={form.name}
                    onChange={handleInputChange}
                    placeholder="e.g., Ramesh Kumar"
                    required
                  />
                </label>
                <label htmlFor="beneficiary-account">
                  Account number
                  <input
                    id="beneficiary-account"
                    name="accountNumber"
                    type="text"
                    value={form.accountNumber}
                    onChange={handleInputChange}
                    placeholder="Enter exact account number"
                    required
                  />
                </label>
                <label htmlFor="beneficiary-bank">
                  Bank name
                  <input
                    id="beneficiary-bank"
                    name="bankName"
                    type="text"
                    value={form.bankName}
                    onChange={handleInputChange}
                    placeholder="Sun National Bank"
                  />
                </label>
                <label htmlFor="beneficiary-ifsc">
                  IFSC (optional)
                  <input
                    id="beneficiary-ifsc"
                    name="ifsc"
                    type="text"
                    value={form.ifsc}
                    onChange={handleInputChange}
                    placeholder="SUNB0001HYD"
                  />
                </label>
                <button
                  type="submit"
                  className="primary-btn primary-btn--compact"
                  disabled={formSubmitting}
                >
                  {formSubmitting ? "Adding…" : "Add beneficiary"}
                </button>
              </form>
              {formError && <div className="form-error">{formError}</div>}
              {formMessage && (
                <div
                  className={formMessage.type === "success" ? "form-success" : "form-error"}
                >
                  {formMessage.text}
                </div>
              )}
              <p className="profile-hint">
                Production deployments will enforce a cooling period and OTP confirmation before a
                beneficiary becomes active.
              </p>
            </article>

            <article className="profile-card profile-card--span">
              <h2>Saved beneficiaries</h2>
              {loading && <p>Loading beneficiaries…</p>}
              {error && <div className="form-error">{error}</div>}
              {!loading && !error && !hasItems && (
                <p className="profile-hint">No beneficiaries added yet.</p>
              )}
              {!loading && !error && hasItems && (
                <ul className="beneficiary-list">
                  {activeItems.map((item) => (
                    <li key={item.id} className="beneficiary-list__item">
                      <div>
                        <p className="beneficiary-list__name">{item.name}</p>
                        <p className="beneficiary-list__account">{item.accountNumber}</p>
                        <p className="beneficiary-list__meta">
                          IFSC {item.ifsc} · Added on {new Date(item.addedAt).toLocaleDateString("en-IN")}
                        </p>
                      </div>
                      <button
                        type="button"
                        className="link-btn link-btn--danger"
                        onClick={() => handleRemove(item.id)}
                      >
                        Remove
                      </button>
                    </li>
                  ))}
                </ul>
              )}
            </article>
          </main>
        </div>
      </div>
    </div>
  );
};

Beneficiaries.propTypes = {
  session: PropTypes.shape({
    accessToken: PropTypes.string,
    user: PropTypes.object,
  }).isRequired,
  onSignOut: PropTypes.func.isRequired,
};

export default Beneficiaries;
