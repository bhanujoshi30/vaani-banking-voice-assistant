import { useCallback, useEffect, useMemo, useState } from "react";
import PropTypes from "prop-types";
import { useNavigate } from "react-router-dom";

import SunHeader from "../components/SunHeader.jsx";
import LanguageDropdown from "../components/LanguageDropdown.jsx";
import {
  fetchBeneficiaries,
  createBeneficiary,
  deleteBeneficiary,
} from "../api/client.js";
import { usePageLanguage } from "../hooks/usePageLanguage.js";

const SESSION_EXPIRY_CODES = new Set([
  "session_timeout",
  "session_expired",
  "session_inactive",
  "session_invalid",
]);

const Beneficiaries = ({ session, onSignOut }) => {
  const navigate = useNavigate();
  const { strings } = usePageLanguage();
  const s = strings.beneficiaries;
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
      setFormError(s.provideNameAndAccount);
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
        setFormMessage({ type: "success", text: s.beneficiaryAdded });
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
    const confirmed = window.confirm(s.removeConfirm);
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
              <div style={{ display: "flex", alignItems: "center", gap: "1rem" }}>
                <LanguageDropdown />
                <button type="button" className="ghost-btn" onClick={onSignOut}>
                  {s.logOut}
                </button>
              </div>
            }
          />
          <main className="card-surface profile-surface">
            <article className="profile-card profile-card--span">
              <button type="button" className="link-btn" onClick={() => navigate(-1)}>
                {s.backToPrevious}
              </button>
              <h1>{s.title}</h1>
              <p className="profile-hint">
                {s.subtitle}
              </p>
            </article>

            <article className="profile-card profile-card--span">
              <h2>{s.addNewBeneficiary}</h2>
              <form className="form-grid" onSubmit={handleAddBeneficiary}>
                <label htmlFor="beneficiary-name">
                  {s.beneficiaryName}
                  <input
                    id="beneficiary-name"
                    name="name"
                    type="text"
                    value={form.name}
                    onChange={handleInputChange}
                    placeholder={s.beneficiaryNamePlaceholder}
                    required
                  />
                </label>
                <label htmlFor="beneficiary-account">
                  {s.accountNumber}
                  <input
                    id="beneficiary-account"
                    name="accountNumber"
                    type="text"
                    value={form.accountNumber}
                    onChange={handleInputChange}
                    placeholder={s.accountNumberPlaceholder}
                    required
                  />
                </label>
                <label htmlFor="beneficiary-bank">
                  {s.bankName}
                  <input
                    id="beneficiary-bank"
                    name="bankName"
                    type="text"
                    value={form.bankName}
                    onChange={handleInputChange}
                    placeholder={s.bankNamePlaceholder}
                  />
                </label>
                <label htmlFor="beneficiary-ifsc">
                  {s.ifsc}
                  <input
                    id="beneficiary-ifsc"
                    name="ifsc"
                    type="text"
                    value={form.ifsc}
                    onChange={handleInputChange}
                    placeholder={s.ifscPlaceholder}
                  />
                </label>
                <button
                  type="submit"
                  className="primary-btn primary-btn--compact"
                  disabled={formSubmitting}
                >
                  {formSubmitting ? s.adding : s.addBeneficiary}
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
                {s.productionNote}
              </p>
            </article>

            <article className="profile-card profile-card--span">
              <h2>{s.savedBeneficiaries}</h2>
              {loading && <p>{s.loading}</p>}
              {error && <div className="form-error">{error}</div>}
              {!loading && !error && !hasItems && (
                <p className="profile-hint">{s.noBeneficiariesYet}</p>
              )}
              {!loading && !error && hasItems && (
                <ul className="beneficiary-list">
                  {activeItems.map((item) => (
                    <li key={item.id} className="beneficiary-list__item">
                      <div>
                        <p className="beneficiary-list__name">{item.name}</p>
                        <p className="beneficiary-list__account">{item.accountNumber}</p>
                        <p className="beneficiary-list__meta">
                          IFSC {item.ifsc} · {s.addedOn} {new Date(item.addedAt).toLocaleDateString("en-IN")}
                        </p>
                      </div>
                      <button
                        type="button"
                        className="link-btn link-btn--danger"
                        onClick={() => handleRemove(item.id)}
                      >
                        {s.remove}
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
