import { useState } from 'react';
import PropTypes from 'prop-types';
import { downloadDocument } from '../../utils/documentDownload.js';
import './InvestmentInfoCard.css';

/**
 * InvestmentInfoCard component - Displays investment scheme information in card format
 */
const InvestmentInfoCard = ({ investmentInfo, language = 'en-IN', accessToken = null }) => {
  const [isDownloading, setIsDownloading] = useState(false);

  const handleDownload = async () => {
    if (!investmentInfo || isDownloading) return;
    
    setIsDownloading(true);
    try {
      const investmentName = investmentInfo.name || investmentInfo.title || '';
      await downloadDocument('investment', investmentName, language, accessToken);
    } catch (error) {
      console.error('Error downloading investment document:', error);
      alert(language === 'hi-IN' 
        ? 'दस्तावेज़ डाउनलोड करने में त्रुटि: ' + error.message
        : 'Error downloading document: ' + error.message
      );
    } finally {
      setIsDownloading(false);
    }
  };
  if (!investmentInfo) {
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

  const formatRate = (rate) => {
    if (!rate) return '—';
    // If rate already contains %, don't add another one
    if (typeof rate === 'string' && rate.includes('%')) {
      return rate;
    }
    return `${rate}%`;
  };

  return (
    <div className="investment-info-card">
      <div className="investment-info-card__header">
        <div className="investment-info-card__icon">💰</div>
        <div className="investment-info-card__title">
          {investmentInfo.name || investmentInfo.title || (language === 'hi-IN' ? 'निवेश योजना' : 'Investment Scheme')}
        </div>
        <button
          className="investment-info-card__download-btn"
          onClick={handleDownload}
          disabled={isDownloading}
          title={language === 'hi-IN' ? 'विस्तृत दस्तावेज़ डाउनलोड करें' : 'Download detailed document'}
          aria-label={language === 'hi-IN' ? 'विस्तृत दस्तावेज़ डाउनलोड करें' : 'Download detailed document'}
        >
          {isDownloading ? (
            <>
              <span className="investment-info-card__download-icon">⏳</span>
              <span className="investment-info-card__download-text">
                {language === 'hi-IN' ? 'डाउनलोड हो रहा है...' : 'Downloading...'}
              </span>
            </>
          ) : (
            <>
              <span className="investment-info-card__download-icon">📥</span>
              <span className="investment-info-card__download-text">
                {language === 'hi-IN' ? 'विस्तृत दस्तावेज़ डाउनलोड करें' : 'Download detailed document'}
              </span>
            </>
          )}
        </button>
      </div>

      <div className="investment-info-card__content">
        {investmentInfo.interest_rate !== undefined && (
          <div className="investment-info-card__field">
            <span className="investment-info-card__label">
              {language === 'hi-IN' ? 'ब्याज दर' : 'Interest Rate'}
            </span>
            <span className="investment-info-card__value investment-info-card__value--highlight">
              {formatRate(investmentInfo.interest_rate)}
            </span>
          </div>
        )}

        {(investmentInfo.min_amount !== undefined || investmentInfo.max_amount !== undefined || investmentInfo.investment_amount) && (
          <div className="investment-info-card__field">
            <span className="investment-info-card__label">
              {language === 'hi-IN' ? 'निवेश राशि' : 'Investment Amount'}
            </span>
            <span className="investment-info-card__value">
              {/* Prioritize min_amount/max_amount over investment_amount for better accuracy */}
              {investmentInfo.min_amount !== undefined && investmentInfo.max_amount !== undefined ? (
                investmentInfo.max_amount === "No limit" || investmentInfo.max_amount === "no limit" ? (
                  `From ${formatAmount(investmentInfo.min_amount)}`
                ) : (
                  `${formatAmount(investmentInfo.min_amount)} - ${formatAmount(investmentInfo.max_amount)}`
                )
              ) : investmentInfo.investment_amount ? (
                formatAmount(investmentInfo.investment_amount)
              ) : (
                investmentInfo.min_amount ? formatAmount(investmentInfo.min_amount) : formatAmount(investmentInfo.max_amount)
              )}
            </span>
          </div>
        )}

        {investmentInfo.tenure && (
          <div className="investment-info-card__field">
            <span className="investment-info-card__label">
              {language === 'hi-IN' ? 'अवधि' : 'Tenure'}
            </span>
            <span className="investment-info-card__value">{investmentInfo.tenure}</span>
          </div>
        )}

        {investmentInfo.eligibility && (
          <div className="investment-info-card__field investment-info-card__field--full">
            <span className="investment-info-card__label">
              {language === 'hi-IN' ? 'पात्रता' : 'Eligibility'}
            </span>
            <span className="investment-info-card__value">{investmentInfo.eligibility}</span>
          </div>
        )}

        {investmentInfo.tax_benefits && (
          <div className="investment-info-card__field investment-info-card__field--full">
            <span className="investment-info-card__label">
              {language === 'hi-IN' ? 'कर लाभ' : 'Tax Benefits'}
            </span>
            <span className="investment-info-card__value">{investmentInfo.tax_benefits}</span>
          </div>
        )}

        {investmentInfo.description && (
          <div className="investment-info-card__description">
            {investmentInfo.description}
          </div>
        )}

        {(() => {
          // Safely handle features - ensure it's an array
          let featuresArray = [];
          if (investmentInfo.features) {
            if (Array.isArray(investmentInfo.features)) {
              featuresArray = investmentInfo.features;
            } else if (typeof investmentInfo.features === 'string') {
              // If features is a string, try to split it or wrap it in an array
              featuresArray = [investmentInfo.features];
            }
          }
          
          if (featuresArray.length > 0) {
            return (
              <div className="investment-info-card__features">
                <div className="investment-info-card__features-title">
                  {language === 'hi-IN' ? 'विशेषताएं' : 'Features'}
                </div>
                <ul className="investment-info-card__features-list">
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

InvestmentInfoCard.propTypes = {
  investmentInfo: PropTypes.shape({
    name: PropTypes.string,
    title: PropTypes.string,
    interest_rate: PropTypes.oneOfType([PropTypes.number, PropTypes.string]),
    min_amount: PropTypes.oneOfType([PropTypes.number, PropTypes.string]),
    max_amount: PropTypes.oneOfType([PropTypes.number, PropTypes.string]),
    investment_amount: PropTypes.string,
    tenure: PropTypes.string,
    eligibility: PropTypes.string,
    tax_benefits: PropTypes.string,
    description: PropTypes.string,
    features: PropTypes.arrayOf(PropTypes.string),
  }),
  language: PropTypes.string,
  accessToken: PropTypes.string,
};

export default InvestmentInfoCard;

