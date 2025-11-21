import PropTypes from 'prop-types';
import './LoanSelectionTable.css';

/**
 * LoanSelectionTable component - Displays available loan types in a table format
 * Users can click on a loan type to get detailed information
 */
const LoanSelectionTable = ({ loans, language = 'en-IN', onLoanSelect }) => {
  if (!loans || loans.length === 0) {
    return null;
  }

  const handleLoanClick = (loanType) => {
    if (onLoanSelect) {
      onLoanSelect(loanType);
    }
  };

  const getLoanDisplayName = (loanType) => {
    const names = {
      'home_loan': language === 'hi-IN' ? 'होम लोन' : 'Home Loan',
      'personal_loan': language === 'hi-IN' ? 'पर्सनल लोन' : 'Personal Loan',
      'auto_loan': language === 'hi-IN' ? 'ऑटो लोन' : 'Auto Loan',
      'education_loan': language === 'hi-IN' ? 'एजुकेशन लोन' : 'Education Loan',
      'business_loan': language === 'hi-IN' ? 'बिजनेस लोन' : 'Business Loan',
      'gold_loan': language === 'hi-IN' ? 'गोल्ड लोन' : 'Gold Loan',
      'loan_against_property': language === 'hi-IN' ? 'प्रॉपर्टी के खिलाफ लोन' : 'Loan Against Property',
    };
    return names[loanType] || loanType.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  const getLoanDescription = (loanType) => {
    const descriptions = {
      'home_loan': language === 'hi-IN' 
        ? 'अपने सपनों का घर खरीदें' 
        : 'Buy your dream home',
      'personal_loan': language === 'hi-IN' 
        ? 'तत्काल वित्तीय समाधान' 
        : 'Instant financial solutions',
      'auto_loan': language === 'hi-IN' 
        ? 'कार, बाइक और वाणिज्यिक वाहन' 
        : 'Cars, bikes & commercial vehicles',
      'education_loan': language === 'hi-IN' 
        ? 'भारत या विदेश में शिक्षा' 
        : 'Study in India or abroad',
      'business_loan': language === 'hi-IN' 
        ? 'MSME और SME वित्तपोषण' 
        : 'MSME & SME financing',
      'gold_loan': language === 'hi-IN' 
        ? 'सोने के गहनों के खिलाफ तत्काल नकदी' 
        : 'Instant cash against gold ornaments',
      'loan_against_property': language === 'hi-IN' 
        ? 'संपत्ति मूल्य का उपयोग करें' 
        : 'Unlock your property value',
    };
    return descriptions[loanType] || '';
  };

  return (
    <div className="loan-selection-table-container">
      <div className="loan-selection-table-header">
        <h3 className="loan-selection-table-title">
          {language === 'hi-IN' ? 'उपलब्ध ऋण प्रकार' : 'Available Loan Types'}
        </h3>
        <p className="loan-selection-table-subtitle">
          {language === 'hi-IN' 
            ? 'विस्तृत जानकारी के लिए किसी भी ऋण प्रकार पर क्लिक करें या बोलें' 
            : 'Click or speak any loan type for detailed information'}
        </p>
      </div>
      
      <div className="loan-selection-table">
        {loans.map((loan, index) => (
          <div
            key={loan.type || index}
            className="loan-selection-row"
            onClick={() => handleLoanClick(loan.type || loan)}
            role="button"
            tabIndex={0}
            onKeyDown={(e) => {
              if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                handleLoanClick(loan.type || loan);
              }
            }}
          >
            <div className="loan-selection-row-content">
              <div className="loan-selection-row-icon">
                {loan.icon || '🏦'}
              </div>
              <div className="loan-selection-row-info">
                <div className="loan-selection-row-name">
                  {loan.name || getLoanDisplayName(loan.type || loan)}
                </div>
                <div className="loan-selection-row-description">
                  {loan.description || getLoanDescription(loan.type || loan)}
                </div>
              </div>
              <div className="loan-selection-row-arrow">
                →
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

LoanSelectionTable.propTypes = {
  loans: PropTypes.arrayOf(
    PropTypes.shape({
      type: PropTypes.string,
      name: PropTypes.string,
      description: PropTypes.string,
      icon: PropTypes.string,
    })
  ).isRequired,
  language: PropTypes.string,
  onLoanSelect: PropTypes.func,
};

export default LoanSelectionTable;

