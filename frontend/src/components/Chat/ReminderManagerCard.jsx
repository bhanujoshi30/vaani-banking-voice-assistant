import { useCallback, useEffect, useMemo, useState } from 'react';
import PropTypes from 'prop-types';
import {
  fetchAccounts,
  fetchReminders,
  createReminder,
  updateReminderStatus,
} from '../../api/client.js';
import ReminderCard from './ReminderCard.jsx';
import './ReminderManagerCard.css';

const dateTimeLocal = (date) => new Date(date).toISOString().slice(0, 16);

const ReminderManagerCard = ({
  session,
  language = 'en-IN',
  intent = 'create',
  accounts: hintedAccounts = [],
  prefilled = {},
  onSuccess,
}) => {
  const [accounts, setAccounts] = useState([]);
  const [accountsError, setAccountsError] = useState('');
  const [reminders, setReminders] = useState([]);
  const [loadingReminders, setLoadingReminders] = useState(true);
  const [statusMessage, setStatusMessage] = useState(null);
  const [formLoading, setFormLoading] = useState(false);

  const defaultReminderDate = useMemo(
    () => dateTimeLocal(Date.now() + 24 * 60 * 60 * 1000),
    []
  );

  // Initialize form with prefilled data if available
  const getInitialForm = useCallback(() => {
    return {
      reminderType: 'bill_payment',
      remindAt: prefilled.remindAt || dateTimeLocal(Date.now() + 24 * 60 * 60 * 1000),
      message: prefilled.message || '',
      accountId: prefilled.accountId || '',
      channel: prefilled.channel || 'voice',
    };
  }, [prefilled]);

  const [form, setForm] = useState(getInitialForm);

  // Update form when prefilled data changes or accounts are loaded
  useEffect(() => {
    if (prefilled && Object.keys(prefilled).length > 0) {
      setForm((prev) => {
        const updates = {};
        
        if (prefilled.message) {
          updates.message = prefilled.message;
        }
        if (prefilled.remindAt) {
          updates.remindAt = prefilled.remindAt;
        }
        if (prefilled.accountId) {
          // Verify accountId exists in loaded accounts
          const accountExists = accounts.some(
            (acc) => (acc.id || acc.accountId) === prefilled.accountId
          );
          if (accountExists) {
            updates.accountId = prefilled.accountId;
          }
        }
        if (prefilled.channel) {
          updates.channel = prefilled.channel;
        }
        
        return { ...prev, ...updates };
      });
    }
  }, [prefilled, accounts]);

  const loadAccounts = useCallback(async () => {
    try {
      const data = await fetchAccounts({ accessToken: session.accessToken });
      setAccounts(data ?? []);
    } catch (error) {
      setAccountsError(error.message);
      setAccounts([]);
    }
  }, [session.accessToken, hintedAccounts]);

  const loadReminders = useCallback(async () => {
    setLoadingReminders(true);
    try {
      const data = await fetchReminders({ accessToken: session.accessToken });
      setReminders(data ?? []);
    } catch (error) {
      setStatusMessage({
        type: 'error',
        message: error.message || (language === 'hi-IN' ? 'अनुस्मारक लोड नहीं हो पाए।' : 'Unable to load reminders.'),
      });
    } finally {
      setLoadingReminders(false);
    }
  }, [session.accessToken, language]);

  useEffect(() => {
    loadAccounts();
    loadReminders();
  }, [loadAccounts, loadReminders]);

  const accountMap = useMemo(() => {
    const map = {};
    accounts.forEach((account) => {
      const id = account.id;
      if (!id) return;
      map[id] = account.accountNumber || account.account_number || account.number || '';
    });
    return map;
  }, [accounts]);

  const handleFormChange = (event) => {
    const { name, value } = event.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleCreateReminder = async (event) => {
    event.preventDefault();
    setStatusMessage(null);

    if (!form.message?.trim()) {
      setStatusMessage({
        type: 'error',
        message: language === 'hi-IN' ? 'कृपया संदेश दर्ज करें।' : 'Please enter a reminder message.',
      });
      return;
    }

    setFormLoading(true);
    try {
      const payload = {
        reminderType: form.reminderType,
        remindAt: new Date(form.remindAt).toISOString(),
        message: form.message.trim(),
        accountId: form.accountId || undefined,
        channel: form.channel,
      };
      const created = await createReminder({ accessToken: session.accessToken, payload });
      setReminders((prev) => [created, ...prev]);
      
      const successMessage = language === 'hi-IN' 
        ? `अनुस्मारक सफलतापूर्वक बना दिया गया है: "${form.message.trim()}"`
        : `Reminder created successfully: "${form.message.trim()}"`;
      
      setStatusMessage({
        type: 'success',
        message: language === 'hi-IN' ? 'अनुस्मारक बना दिया गया।' : 'Reminder created successfully.',
      });
      
      // Add success message to chat
      if (onSuccess) {
        onSuccess(successMessage);
      }
      setForm({
        reminderType: 'bill_payment',
        remindAt: defaultReminderDate,
        message: '',
        accountId: '',
        channel: 'voice',
      });
    } catch (error) {
      setStatusMessage({
        type: 'error',
        message: error.message || (language === 'hi-IN' ? 'अनुस्मारक नहीं बन पाया।' : 'Unable to create reminder.'),
      });
    } finally {
      setFormLoading(false);
    }
  };

  const handleReminderStatus = async (reminderId, status) => {
    setStatusMessage(null);
    try {
      const updated = await updateReminderStatus({
        accessToken: session.accessToken,
        reminderId,
        payload: { status },
      });
      setReminders((prev) => prev.map((item) => (item.id === updated.id ? updated : item)));
      setStatusMessage({
        type: 'success',
        message:
          language === 'hi-IN'
            ? 'अनुस्मारक अपडेट कर दिया गया।'
            : 'Reminder updated successfully.',
      });
    } catch (error) {
      setStatusMessage({
        type: 'error',
        message: error.message || (language === 'hi-IN' ? 'अपडेट विफल रहा।' : 'Failed to update reminder.'),
      });
    }
  };

  const normalizedReminders = reminders.map((reminder) => ({
    ...reminder,
    remind_at: reminder.remindAt || reminder.remind_at,
    account_number:
      reminder.account_number ||
      reminder.accountNumber ||
      (reminder.accountId ? accountMap[reminder.accountId] : undefined),
  }));

  const showCreateForm = intent !== 'view';

  return (
    <div className="reminder-manager">
      <div className="reminder-manager__header">
        <div>
          <h3>
            {language === 'hi-IN'
              ? showCreateForm
                ? 'अनुस्मारक सेट करें'
                : 'अनुस्मारक देखें'
              : showCreateForm
              ? 'Set a reminder'
              : 'View reminders'}
          </h3>
          <p>
            {language === 'hi-IN'
              ? 'भुगतान के लिए रिमाइंडर बनाएँ और उन्हें अपडेट/हटाएँ।'
              : 'Create payment reminders and manage existing ones.'}
          </p>
        </div>
      </div>

      {showCreateForm && (
        <form className="reminder-manager__form" onSubmit={handleCreateReminder}>
          <label>
            {language === 'hi-IN' ? 'अनुस्मारक प्रकार' : 'Reminder type'}
            <select name="reminderType" value={form.reminderType} onChange={handleFormChange}>
              <option value="bill_payment">{language === 'hi-IN' ? 'बिल भुगतान' : 'Bill payment'}</option>
              <option value="due_date">{language === 'hi-IN' ? 'देय तिथि' : 'Due date'}</option>
              <option value="savings">{language === 'hi-IN' ? 'बचत' : 'Savings'}</option>
              <option value="custom">{language === 'hi-IN' ? 'कस्टम' : 'Custom'}</option>
            </select>
          </label>

          <label>
            {language === 'hi-IN' ? 'संदेश' : 'Message'}
            <textarea
              name="message"
              value={form.message}
              onChange={handleFormChange}
              placeholder={language === 'hi-IN' ? 'जैसे बिजली का बिल याद दिलाना है' : 'e.g. Pay electricity bill'}
              required
            />
          </label>

          <label>
            {language === 'hi-IN' ? 'कब याद दिलाना है' : 'Remind me on'}
            <input
              type="datetime-local"
              name="remindAt"
              value={form.remindAt}
              onChange={handleFormChange}
              min={dateTimeLocal(Date.now())}
              required
            />
          </label>

          <label>
            {language === 'hi-IN' ? 'लिंक्ड खाता (वैकल्पिक)' : 'Linked account (optional)'}
            <select
              name="accountId"
              value={form.accountId}
              onChange={handleFormChange}
              disabled={accounts.length === 0}
            >
              <option value="">{language === 'hi-IN' ? 'कोई नहीं' : 'None'}</option>
              {accounts.map((account) => (
                <option key={account.id} value={account.id}>
                  {account.accountNumber}
                </option>
              ))}
            </select>
            {accountsError && (
              <small className="reminder-manager__hint">{accountsError}</small>
            )}
          </label>

          <label>
            {language === 'hi-IN' ? 'चैनल' : 'Channel'}
            <select name="channel" value={form.channel} onChange={handleFormChange}>
              <option value="voice">{language === 'hi-IN' ? 'वॉइस' : 'Voice'}</option>
              <option value="sms">SMS</option>
              <option value="push">Push</option>
            </select>
          </label>

          <button type="submit" disabled={formLoading} className="reminder-manager__primary-btn">
            {formLoading
              ? language === 'hi-IN'
                ? 'बना रहे हैं…'
                : 'Creating…'
              : language === 'hi-IN'
              ? 'अनुस्मारक बनाएं'
              : 'Create reminder'}
          </button>
        </form>
      )}

      {statusMessage && (
        <div
          className={
            statusMessage.type === 'success'
              ? 'reminder-manager__status reminder-manager__status--success'
              : 'reminder-manager__status reminder-manager__status--error'
          }
        >
          {statusMessage.message}
        </div>
      )}

      <div className="reminder-manager__list">
        <div className="reminder-manager__list-header">
          <h4>{language === 'hi-IN' ? 'अनुस्मारक सूची' : 'Your reminders'}</h4>
          <button type="button" className="link-btn" onClick={loadReminders} disabled={loadingReminders}>
            {loadingReminders
              ? language === 'hi-IN'
                ? 'रीफ्रेश हो रहा है…'
                : 'Refreshing…'
              : language === 'hi-IN'
              ? 'रीफ्रेश'
              : 'Refresh'}
          </button>
        </div>

        {loadingReminders ? (
          <p className="reminder-manager__hint">
            {language === 'hi-IN' ? 'अनुस्मारक लोड हो रहे हैं…' : 'Loading reminders…'}
          </p>
        ) : normalizedReminders.length === 0 ? (
          <p className="reminder-manager__hint">
            {language === 'hi-IN'
              ? 'अभी कोई अनुस्मारक सेट नहीं है।'
              : 'No reminders yet.'}
          </p>
        ) : (
          <ul className="reminder-manager__items">
            {normalizedReminders.map((reminder) => (
              <li key={reminder.id} className="reminder-manager__item">
                <ReminderCard reminder={reminder} language={language} />
                <div className="reminder-manager__item-actions">
                  {reminder.status !== 'sent' && (
                    <button
                      type="button"
                      onClick={() => handleReminderStatus(reminder.id, 'sent')}
                      className="reminder-manager__secondary-btn"
                    >
                      {language === 'hi-IN' ? 'पूर्ण चिह्नित करें' : 'Mark done'}
                    </button>
                  )}
                  {reminder.status !== 'cancelled' && (
                    <button
                      type="button"
                      onClick={() => handleReminderStatus(reminder.id, 'cancelled')}
                      className="reminder-manager__secondary-btn reminder-manager__secondary-btn--danger"
                    >
                      {language === 'hi-IN' ? 'हटाएँ' : 'Delete'}
                    </button>
                  )}
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
};

ReminderManagerCard.propTypes = {
  session: PropTypes.shape({
    accessToken: PropTypes.string,
  }).isRequired,
  language: PropTypes.string,
  intent: PropTypes.oneOf(['create', 'view']),
  accounts: PropTypes.arrayOf(PropTypes.object),
  prefilled: PropTypes.shape({
    message: PropTypes.string,
    remindAt: PropTypes.string,
    accountId: PropTypes.string,
    channel: PropTypes.oneOf(['voice', 'sms', 'push']),
  }),
  onSuccess: PropTypes.func,
};

export default ReminderManagerCard;

