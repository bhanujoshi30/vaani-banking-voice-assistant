import { useMemo, useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import { requestStatementDownload } from '../../api/client.js';
import './StatementRequestCard.css';

const PERIOD_PRESETS = [
  { id: 'week', labelEn: 'Last 7 days', labelHi: 'पिछले 7 दिन', days: 7 },
  { id: 'month', labelEn: 'Last 30 days', labelHi: 'पिछले 30 दिन', days: 30 },
  { id: 'quarter', labelEn: 'Last 3 months', labelHi: 'पिछले 3 महीने', days: 90 },
  { id: 'half_year', labelEn: 'Last 6 months', labelHi: 'पिछले 6 महीने', days: 180 },
  { id: 'year', labelEn: 'Last 12 months', labelHi: 'पिछले 12 महीने', days: 365 },
  { id: 'custom', labelEn: 'Custom range', labelHi: 'कस्टम अवधि', days: null },
];

const formatDate = (date) => new Date(date).toISOString().split('T')[0];

const getDateFromDays = (days) => formatDate(new Date(Date.now() - days * 24 * 60 * 60 * 1000));

const StatementRequestCard = ({
  accounts = [],
  language = 'en-IN',
  session,
  detectedAccount,
  detectedPeriod,
  requiresAccount,
  requiresPeriod,
  onDownload,
  onSuccess,
}) => {
  const today = useMemo(() => formatDate(new Date()), []);
  const defaultFrom = useMemo(() => getDateFromDays(30), []);

  const [selectedAccount, setSelectedAccount] = useState(
    detectedAccount || accounts[0]?.accountNumber || accounts[0]?.account_number || ''
  );
  const initialPreset = detectedPeriod?.periodType || (requiresPeriod ? '' : 'month');
  const [selectedPreset, setSelectedPreset] = useState(initialPreset);
  const [customFrom, setCustomFrom] = useState(detectedPeriod?.fromDate || defaultFrom);
  const [customTo, setCustomTo] = useState(detectedPeriod?.toDate || today);

  // Update selected account when detectedAccount changes
  useEffect(() => {
    if (detectedAccount) {
      setSelectedAccount(detectedAccount);
    } else if (accounts.length > 0 && !selectedAccount) {
      setSelectedAccount(accounts[0]?.accountNumber || accounts[0]?.account_number || '');
    }
  }, [detectedAccount, accounts]);

  // Update selected preset when detectedPeriod changes
  useEffect(() => {
    if (detectedPeriod?.periodType) {
      setSelectedPreset(detectedPeriod.periodType);
      if (detectedPeriod.fromDate) {
        setCustomFrom(detectedPeriod.fromDate);
      }
      if (detectedPeriod.toDate) {
        setCustomTo(detectedPeriod.toDate);
      }
    }
  }, [detectedPeriod]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');

  const computeDates = () => {
    if (selectedPreset === 'custom') {
      return { fromDate: customFrom, toDate: customTo };
    }
    const preset = PERIOD_PRESETS.find((item) => item.id === selectedPreset) || PERIOD_PRESETS[1];
    return {
      fromDate: getDateFromDays(preset.days),
      toDate: today,
    };
  };

  const validateDates = (fromDate, toDate) => {
    if (!fromDate || !toDate) {
      return language === 'hi-IN'
        ? 'कृपया तिथि सीमा चुनें।'
        : 'Please select a valid date range.';
    }
    if (fromDate > toDate) {
      return language === 'hi-IN'
        ? 'प्रारंभ तिथि समाप्ति तिथि से पहले होनी चाहिए।'
        : 'Start date must be before end date.';
    }
    const diffDays = (new Date(toDate) - new Date(fromDate)) / (1000 * 60 * 60 * 24);
    if (diffDays > 365) {
      return language === 'hi-IN'
        ? 'अवधि 365 दिनों से अधिक नहीं हो सकती।'
        : 'The period cannot exceed 365 days.';
    }
    return null;
  };

  const handlePrepareStatement = async () => {
    setError('');
    setSuccessMessage('');

    if (!selectedAccount) {
      setError(
        language === 'hi-IN' ? 'कृपया कोई खाता चुनें।' : 'Please select an account.'
      );
      return;
    }

    if (!selectedPreset) {
      setError(
        language === 'hi-IN' ? 'कृपया अवधि चुनें।' : 'Please select a period.'
      );
      return;
    }

    const { fromDate, toDate } = computeDates();
    const validationError = validateDates(fromDate, toDate);
    if (validationError) {
      setError(validationError);
      return;
    }

    setLoading(true);
    try {
      const statementData = await requestStatementDownload({
        accessToken: session.accessToken,
        payload: {
          accountNumber: selectedAccount,
          fromDate,
          toDate,
          periodType: selectedPreset,
        },
      });

      if (onDownload) {
        onDownload(statementData);
      }

      const successMessage = language === 'hi-IN'
        ? `खाता स्टेटमेंट सफलतापूर्वक डाउनलोड हो गया है। खाता: ${selectedAccount.slice(-5)} (${fromDate} से ${toDate} तक)`
        : `Account statement downloaded successfully. Account: ${selectedAccount.slice(-5)} (${fromDate} to ${toDate})`;

      setSuccessMessage(
        language === 'hi-IN'
          ? 'स्टेटमेंट तैयार है। डाउनलोड आरंभ हो गया है।'
          : 'Statement prepared. Download started.'
      );
      
      // Add success message to chat
      if (onSuccess) {
        onSuccess(successMessage);
      }
    } catch (err) {
      setError(err.message || (language === 'hi-IN' ? 'त्रुटि हुई।' : 'Something went wrong.'));
    } finally {
      setLoading(false);
    }
  };

  const renderPresetButton = (preset) => (
    <button
      key={preset.id}
      type="button"
      className={`statement-request__preset-btn ${
        selectedPreset === preset.id ? 'statement-request__preset-btn--active' : ''
      }`}
      onClick={() => setSelectedPreset(preset.id)}
    >
      {language === 'hi-IN' ? preset.labelHi : preset.labelEn}
    </button>
  );

  return (
    <div className="statement-request">
      <div className="statement-request__header">
        <div>
          <h3>{language === 'hi-IN' ? 'स्टेटमेंट डाउनलोड' : 'Download Statement'}</h3>
          <p>
            {language === 'hi-IN'
              ? 'खाता और अवधि चुनें, फिर स्टेटमेंट डाउनलोड करें।'
              : 'Select an account and period to download your statement.'}
          </p>
        </div>
      </div>

      <div className="statement-request__control">
        <label>
          {language === 'hi-IN' ? 'खाता चुनें' : 'Select account'}
          <select
            value={selectedAccount}
            onChange={(e) => setSelectedAccount(e.target.value)}
            required
          >
            <option value="">
              {language === 'hi-IN' ? 'खाता चुनें' : 'Choose account'}
            </option>
            {accounts.map((account) => {
              const accountNumber = account.accountNumber || account.account_number || '';
              const accountType = account.accountType || account.account_type || 'Account';
              return (
                <option key={accountNumber} value={accountNumber}>
                  {accountType?.replace('AccountType.', '') || 'Account'} • {accountNumber}
                </option>
              );
            })}
          </select>
        </label>
        {requiresAccount && !selectedAccount && (
          <small className="statement-request__hint">
            {language === 'hi-IN'
              ? 'कृपया वह खाता चुनें जिसका स्टेटमेंट चाहिए।'
              : 'Please choose the account you need the statement for.'}
          </small>
        )}
      </div>

      <div className="statement-request__control">
        <label>
          {language === 'hi-IN' ? 'अवधि चुनें' : 'Select period'}
          <div className="statement-request__presets">
            {PERIOD_PRESETS.map(renderPresetButton)}
          </div>
        </label>
        {selectedPreset === 'custom' && (
          <div className="statement-request__dates">
            <label>
              {language === 'hi-IN' ? 'प्रारंभ तिथि' : 'From date'}
              <input
                type="date"
                value={customFrom}
                max={customTo}
                onChange={(e) => setCustomFrom(e.target.value)}
              />
            </label>
            <label>
              {language === 'hi-IN' ? 'समाप्ति तिथि' : 'To date'}
              <input
                type="date"
                value={customTo}
                min={customFrom}
                max={today}
                onChange={(e) => setCustomTo(e.target.value)}
              />
            </label>
          </div>
        )}
        {requiresPeriod && selectedPreset === '' && (
          <small className="statement-request__hint">
            {language === 'hi-IN'
              ? 'कृपया वह अवधि चुनें जिसके लिए स्टेटमेंट चाहिए।'
              : 'Please choose the time period you need the statement for.'}
          </small>
        )}
      </div>

      {error && <div className="statement-request__error">{error}</div>}
      {successMessage && <div className="statement-request__success">{successMessage}</div>}

      <div className="statement-request__actions">
        <button
          type="button"
          className="statement-request__submit"
          onClick={handlePrepareStatement}
          disabled={loading}
        >
          {loading
            ? language === 'hi-IN'
              ? 'तैयार किया जा रहा है...'
              : 'Preparing...'
            : language === 'hi-IN'
              ? 'स्टेटमेंट डाउनलोड करें'
              : 'Download Statement'}
        </button>
      </div>
    </div>
  );
};

StatementRequestCard.propTypes = {
  accounts: PropTypes.arrayOf(
    PropTypes.shape({
      account_number: PropTypes.string.isRequired,
      account_type: PropTypes.string,
    })
  ),
  language: PropTypes.string,
  session: PropTypes.shape({
    accessToken: PropTypes.string,
  }).isRequired,
  detectedAccount: PropTypes.string,
  detectedPeriod: PropTypes.shape({
    periodType: PropTypes.string,
    fromDate: PropTypes.string,
    toDate: PropTypes.string,
  }),
  requiresAccount: PropTypes.bool,
  requiresPeriod: PropTypes.bool,
  onDownload: PropTypes.func,
  onSuccess: PropTypes.func,
};

export default StatementRequestCard;

