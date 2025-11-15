import PropTypes from "prop-types";
import { useEffect, useState } from "react";
import { Navigate, useNavigate } from "react-router-dom";

import SunHeader from "../components/SunHeader.jsx";
import { fetchReminders, updateReminderStatus } from "../api/client.js";

const formatDateTime = (value) => {
  if (!value) return null;
  const date = typeof value === "string" ? new Date(value) : value;
  if (Number.isNaN(date.getTime())) return null;
  return date.toLocaleString("en-IN", {
    dateStyle: "medium",
    timeStyle: "short",
  });
};

const RemindersPage = ({ session }) => {
  const navigate = useNavigate();
  const isAuthenticated = Boolean(session?.authenticated);
  const accessToken = session?.accessToken ?? null;

  const [reminders, setReminders] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!isAuthenticated || !accessToken) {
      return undefined;
    }

    let isMounted = true;

    const loadReminders = async () => {
      setLoading(true);
      setError("");
      try {
        const data = await fetchReminders({ accessToken });
        if (isMounted) {
          setReminders(data);
        }
      } catch (err) {
        if (isMounted) {
          setError(err.message);
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };

    loadReminders();

    return () => {
      isMounted = false;
    };
  }, [isAuthenticated, accessToken]);

  const handleMarkSent = async (reminderId) => {
    if (!accessToken) return;
    try {
      const updated = await updateReminderStatus({
        accessToken,
        reminderId,
        status: "sent",
      });
      setReminders((prev) =>
        prev.map((reminder) => (reminder.id === updated.id ? updated : reminder)),
      );
    } catch (err) {
      setError(err.message);
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
            subtitle="All reminders"
            actionSlot={
              <button type="button" className="ghost-btn" onClick={() => navigate(-1)}>
                Back
              </button>
            }
          />
          <main className="card-surface profile-surface">
            <section className="profile-card profile-card--span">
              <h2>Reminders</h2>
              {error && <div className="form-error">{error}</div>}
              {loading && <p className="profile-hint">Loading reminders…</p>}
              {!loading && reminders.length === 0 && (
                <p className="profile-hint">No reminders found.</p>
              )}
              {!loading && reminders.length > 0 && (
                <ul className="reminders-list">
                  {reminders.map((reminder) => (
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
                          onClick={() => handleMarkSent(reminder.id)}
                        >
                          Mark sent
                        </button>
                      )}
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

RemindersPage.propTypes = {
  session: PropTypes.shape({
    authenticated: PropTypes.bool,
    accessToken: PropTypes.string,
  }).isRequired,
};

export default RemindersPage;
