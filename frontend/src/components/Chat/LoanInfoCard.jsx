import PropTypes from 'prop-types';
import './LoanInfoCard.css';

/**
 * LoanInfoCard component - Displays loan product information in card format
 */
const LoanInfoCard = ({ loanInfo, language = 'en-IN' }) => {
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

        {loanInfo.features && loanInfo.features.length > 0 && (
          <div className="loan-info-card__features">
            <div className="loan-info-card__features-title">
              {language === 'hi-IN' ? 'विशेषताएं' : 'Features'}
            </div>
            <ul className="loan-info-card__features-list">
              {loanInfo.features.map((feature, index) => (
                <li key={index}>{feature}</li>
              ))}
            </ul>
          </div>
        )}
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
};

export default LoanInfoCard;

