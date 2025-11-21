import PropTypes from 'prop-types';
import './InvestmentInfoCard.css';

/**
 * InvestmentInfoCard component - Displays investment scheme information in card format
 */
const InvestmentInfoCard = ({ investmentInfo, language = 'en-IN' }) => {
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
    return `${rate}%`;
  };

  return (
    <div className="investment-info-card">
      <div className="investment-info-card__header">
        <div className="investment-info-card__icon">💰</div>
        <div className="investment-info-card__title">
          {investmentInfo.name || investmentInfo.title || (language === 'hi-IN' ? 'निवेश योजना' : 'Investment Scheme')}
        </div>
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
              {investmentInfo.investment_amount ? (
                formatAmount(investmentInfo.investment_amount)
              ) : (
                `${formatAmount(investmentInfo.min_amount)} - ${formatAmount(investmentInfo.max_amount)}`
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

        {investmentInfo.features && investmentInfo.features.length > 0 && (
          <div className="investment-info-card__features">
            <div className="investment-info-card__features-title">
              {language === 'hi-IN' ? 'विशेषताएं' : 'Features'}
            </div>
            <ul className="investment-info-card__features-list">
              {investmentInfo.features.map((feature, index) => (
                <li key={index}>{feature}</li>
              ))}
            </ul>
          </div>
        )}
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
};

export default InvestmentInfoCard;

