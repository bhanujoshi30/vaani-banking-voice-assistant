import PropTypes from 'prop-types';
import './ReminderCard.css';

/**
 * ReminderCard component - Displays reminder information in card format
 */
const ReminderCard = ({ reminder, language = 'en-IN' }) => {
  if (!reminder) {
    return null;
  }

  const remindAt = reminder.remind_at || reminder.remindAt;
  const accountNumber = reminder.account_number || reminder.accountNumber;
  const message =
    reminder.message ||
    reminder.label ||
    reminder.description ||
    (language === 'hi-IN' ? 'भुगतान अनुस्मारक' : 'Payment Reminder');

  const formatDate = (dateString) => {
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString(language === 'hi-IN' ? 'hi-IN' : 'en-IN', {
        day: '2-digit',
        month: 'short',
        year: 'numeric',
      });
    } catch {
      return dateString;
    }
  };

  const formatAmount = (amount) => {
    if (!amount) return '—';
    const num = Number(amount);
    if (isNaN(num)) return amount;
    return `₹${num.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  };

  const getDaysUntil = (dateString) => {
    try {
      const date = new Date(dateString);
      const now = new Date();
      const diffTime = date - now;
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
      return diffDays;
    } catch {
      return null;
    }
  };

  const daysUntil = remindAt ? getDaysUntil(remindAt) : null;
  const isOverdue = daysUntil !== null && daysUntil < 0;
  const isDueSoon = daysUntil !== null && daysUntil >= 0 && daysUntil <= 3;

  return (
    <div className={`reminder-card ${isOverdue ? 'reminder-card--overdue' : ''} ${isDueSoon ? 'reminder-card--due-soon' : ''}`}>
      <div className="reminder-card__header">
        <div className="reminder-card__icon">🔔</div>
        <div className="reminder-card__title">
          {language === 'hi-IN' ? 'भुगतान अनुस्मारक' : 'Payment Reminder'}
        </div>
      </div>

      <div className="reminder-card__content">
        <div className="reminder-card__message">
          {message}
        </div>

        {reminder.amount && (
          <div className="reminder-card__amount">
            <span className="reminder-card__amount-label">
              {language === 'hi-IN' ? 'राशि' : 'Amount'}
            </span>
            <span className="reminder-card__amount-value">
              {formatAmount(reminder.amount)}
            </span>
          </div>
        )}

        {remindAt && (
          <div className="reminder-card__date">
            <span className="reminder-card__date-label">
              {language === 'hi-IN' ? 'दिनांक' : 'Due Date'}
            </span>
            <span className="reminder-card__date-value">
              {formatDate(remindAt)}
            </span>
            {daysUntil !== null && (
              <span className={`reminder-card__days-until ${isOverdue ? 'reminder-card__days-until--overdue' : ''} ${isDueSoon ? 'reminder-card__days-until--soon' : ''}`}>
                {isOverdue 
                  ? (language === 'hi-IN' ? `${Math.abs(daysUntil)} दिन अतिदेय` : `${Math.abs(daysUntil)} days overdue`)
                  : daysUntil === 0
                  ? (language === 'hi-IN' ? 'आज देय' : 'Due today')
                  : daysUntil === 1
                  ? (language === 'hi-IN' ? 'कल देय' : 'Due tomorrow')
                  : (language === 'hi-IN' ? `${daysUntil} दिन बाद देय` : `Due in ${daysUntil} days`)
                }
              </span>
            )}
          </div>
        )}

        {accountNumber && (
          <div className="reminder-card__account">
            <span className="reminder-card__account-label">
              {language === 'hi-IN' ? 'खाता संख्या' : 'Account Number'}
            </span>
            <span className="reminder-card__account-value">
              {accountNumber}
            </span>
          </div>
        )}
      </div>
    </div>
  );
};

ReminderCard.propTypes = {
  reminder: PropTypes.shape({
    message: PropTypes.string,
    label: PropTypes.string,
    amount: PropTypes.oneOfType([PropTypes.number, PropTypes.string]),
    remind_at: PropTypes.string,
    remindAt: PropTypes.string,
    account_number: PropTypes.string,
    accountNumber: PropTypes.string,
  }),
  language: PropTypes.string,
};

export default ReminderCard;

