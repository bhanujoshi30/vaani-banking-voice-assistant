import { useState } from 'react';
import PropTypes from 'prop-types';
import { downloadDocument } from '../../utils/documentDownload.js';
import './LoanInfoCard.css';

/**
 * LoanInfoCard component - Displays loan product information in card format
 */
const LoanInfoCard = ({ loanInfo, language = 'en-IN', accessToken = null }) => {
  const [isDownloading, setIsDownloading] = useState(false);

  const handleDownload = async () => {
    if (!loanInfo || isDownloading) return;
    
    setIsDownloading(true);
    try {
      const loanName = loanInfo.name || loanInfo.title || '';
      await downloadDocument('loan', loanName, language, accessToken);
    } catch (error) {
      console.error('Error downloading loan document:', error);
      alert(language === 'hi-IN' 
        ? 'दस्तावेज़ डाउनलोड करने में त्रुटि: ' + error.message
        : 'Error downloading document: ' + error.message
      );
    } finally {
      setIsDownloading(false);
    }
  };
  if (!loanInfo) {
    return null;
  }

  const formatAmount = (amount) => {
    if (!amount) return '—';
    
    // If it's already a string with Rs. or ₹, return as is
    if (typeof amount === 'string') {
      const trimmed = amount.trim();
      // If it already has currency symbol, return as is
      if (trimmed.startsWith('Rs.') || trimmed.startsWith('₹') || trimmed.startsWith('INR')) {
        return trimmed;
      }
      // If it's a number string, add rupee symbol
      const num = Number(trimmed.replace(/[,\s]/g, ''));
      if (!isNaN(num)) {
        return `₹${num.toLocaleString('en-IN', { maximumFractionDigits: 0 })}`;
      }
      // If it contains text like "crore", "lakhs", etc., add Rs. prefix
      if (trimmed.match(/\d/)) {
        return `Rs. ${trimmed}`;
      }
      return trimmed;
    }
    
    // If it's a number, format it
    const num = Number(amount);
    if (!isNaN(num)) {
      return `₹${num.toLocaleString('en-IN', { maximumFractionDigits: 0 })}`;
    }
    
    return amount;
  };

  const formatLoanAmountRange = (amountRange) => {
    if (!amountRange) return '—';
    
    // If it's already a string with Rs. or ₹, return as is
    if (typeof amountRange === 'string') {
      const trimmed = amountRange.trim();
      // If it already has currency symbol, return as is
      if (trimmed.includes('Rs.') || trimmed.includes('₹') || trimmed.includes('INR')) {
        return trimmed;
      }
      // If it's a range like "10,000 - 1 crore", add Rs. prefix to both parts
      if (trimmed.includes(' - ') || trimmed.includes(' to ')) {
        const separator = trimmed.includes(' - ') ? ' - ' : ' to ';
        const parts = trimmed.split(separator);
        return parts.map(part => {
          const partTrimmed = part.trim();
          if (partTrimmed.startsWith('Rs.') || partTrimmed.startsWith('₹')) {
            return partTrimmed;
          }
          // Check if it's a number
          const num = Number(partTrimmed.replace(/[,\s]/g, ''));
          if (!isNaN(num)) {
            return `Rs. ${num.toLocaleString('en-IN', { maximumFractionDigits: 0 })}`;
          }
          // If it contains text like "crore", "lakhs", add Rs. prefix
          return `Rs. ${partTrimmed}`;
        }).join(separator);
      }
      // Single amount - add Rs. if not present
      if (!trimmed.startsWith('Rs.') && !trimmed.startsWith('₹')) {
        const num = Number(trimmed.replace(/[,\s]/g, ''));
        if (!isNaN(num)) {
          return `Rs. ${num.toLocaleString('en-IN', { maximumFractionDigits: 0 })}`;
        }
        return `Rs. ${trimmed}`;
      }
      return trimmed;
    }
    
    return amountRange;
  };

  const formatRate = (rate) => {
    if (!rate) return '—';
    return `${rate}%`;
  };

  return (
    <div className="loan-info-card">
      <div className="loan-info-card__header">
        <div className="loan-info-card__icon">🏦</div>
        <div className="loan-info-card__title">
          {loanInfo.name || loanInfo.title || (language === 'hi-IN' ? 'ऋण जानकारी' : 'Loan Information')}
        </div>
        <button
          className="loan-info-card__download-btn"
          onClick={handleDownload}
          disabled={isDownloading}
          title={language === 'hi-IN' ? 'विस्तृत दस्तावेज़ डाउनलोड करें' : 'Download detailed document'}
          aria-label={language === 'hi-IN' ? 'विस्तृत दस्तावेज़ डाउनलोड करें' : 'Download detailed document'}
        >
          {isDownloading ? (
            <>
              <span className="loan-info-card__download-icon">⏳</span>
              <span className="loan-info-card__download-text">
                {language === 'hi-IN' ? 'डाउनलोड हो रहा है...' : 'Downloading...'}
              </span>
            </>
          ) : (
            <>
              <span className="loan-info-card__download-icon">📥</span>
              <span className="loan-info-card__download-text">
                {language === 'hi-IN' ? 'विस्तृत दस्तावेज़ डाउनलोड करें' : 'Download detailed document'}
              </span>
            </>
          )}
        </button>
      </div>

      <div className="loan-info-card__content">
        {loanInfo.interest_rate !== undefined && (
          <div className="loan-info-card__field">
            <span className="loan-info-card__label">
              {language === 'hi-IN' ? 'ब्याज दर' : 'Interest Rate'}
            </span>
            <span className="loan-info-card__value loan-info-card__value--highlight">
              {formatRate(loanInfo.interest_rate)}
            </span>
          </div>
        )}

        {(loanInfo.min_amount !== undefined || loanInfo.max_amount !== undefined || loanInfo.loan_amount) && (
          <div className="loan-info-card__field">
            <span className="loan-info-card__label">
              {language === 'hi-IN' ? 'ऋण राशि' : 'Loan Amount'}
            </span>
            <span className="loan-info-card__value">
              {loanInfo.loan_amount ? (
                // If loan_amount is provided as a single string (e.g., "Rs. 10,000 to Rs. 1 crore")
                formatLoanAmountRange(loanInfo.loan_amount)
              ) : (
                // Otherwise format min and max separately
                `${formatAmount(loanInfo.min_amount)} - ${formatAmount(loanInfo.max_amount)}`
              )}
            </span>
          </div>
        )}

        {loanInfo.tenure && (
          <div className="loan-info-card__field">
            <span className="loan-info-card__label">
              {language === 'hi-IN' ? 'अवधि' : 'Tenure'}
            </span>
            <span className="loan-info-card__value">{loanInfo.tenure}</span>
          </div>
        )}

        {loanInfo.eligibility && (
          <div className="loan-info-card__field loan-info-card__field--full">
            <span className="loan-info-card__label">
              {language === 'hi-IN' ? 'पात्रता' : 'Eligibility'}
            </span>
            <span className="loan-info-card__value">{loanInfo.eligibility}</span>
          </div>
        )}

        {loanInfo.description && (
          <div className="loan-info-card__description">
            {loanInfo.description}
          </div>
        )}

        {(() => {
          // Safely handle features - ensure it's an array
          let featuresArray = [];
          if (loanInfo.features) {
            if (Array.isArray(loanInfo.features)) {
              featuresArray = loanInfo.features;
            } else if (typeof loanInfo.features === 'string') {
              // If features is a string, try to split it or wrap it in an array
              featuresArray = [loanInfo.features];
            }
          }
          
          if (featuresArray.length > 0) {
            return (
              <div className="loan-info-card__features">
                <div className="loan-info-card__features-title">
                  {language === 'hi-IN' ? 'विशेषताएं' : 'Features'}
                </div>
                <ul className="loan-info-card__features-list">
                  {featuresArray.map((feature, index) => (
                    <li key={index}>{feature}</li>
                  ))}
                </ul>
              </div>
            );
          }
          return null;
        })()}
      </div>
    </div>
  );
};

LoanInfoCard.propTypes = {
  loanInfo: PropTypes.shape({
    name: PropTypes.string,
    title: PropTypes.string,
    interest_rate: PropTypes.oneOfType([PropTypes.number, PropTypes.string]),
    min_amount: PropTypes.oneOfType([PropTypes.number, PropTypes.string]),
    max_amount: PropTypes.oneOfType([PropTypes.number, PropTypes.string]),
    tenure: PropTypes.string,
    eligibility: PropTypes.string,
    description: PropTypes.string,
    features: PropTypes.arrayOf(PropTypes.string),
  }),
  language: PropTypes.string,
  accessToken: PropTypes.string,
};

export default LoanInfoCard;

