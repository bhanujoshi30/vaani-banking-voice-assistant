import PropTypes from 'prop-types';
import './InvestmentSelectionTable.css';

/**
 * InvestmentSelectionTable component - Displays available investment schemes in a table format
 * Users can click on an investment scheme to get detailed information
 */
const InvestmentSelectionTable = ({ investments, language = 'en-IN', onInvestmentSelect }) => {
  if (!investments || investments.length === 0) {
    return null;
  }

  const handleInvestmentClick = (investmentType) => {
    if (onInvestmentSelect) {
      onInvestmentSelect(investmentType);
    }
  };

  const getInvestmentDisplayName = (investmentType) => {
    const names = {
      'ppf': language === 'hi-IN' ? 'पीपीएफ' : 'PPF',
      'nps': language === 'hi-IN' ? 'एनपीएस' : 'NPS',
      'ssy': language === 'hi-IN' ? 'सुकन्या समृद्धि योजना' : 'Sukanya Samriddhi Yojana',
      'elss': language === 'hi-IN' ? 'ईएलएसएस' : 'ELSS',
      'fd': language === 'hi-IN' ? 'फिक्स्ड डिपॉजिट' : 'Fixed Deposit',
      'rd': language === 'hi-IN' ? 'रिकरिंग डिपॉजिट' : 'Recurring Deposit',
      'nsc': language === 'hi-IN' ? 'नेशनल सेविंग्स सर्टिफिकेट' : 'NSC',
    };
    return names[investmentType] || investmentType.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  const getInvestmentDescription = (investmentType) => {
    const descriptions = {
      'ppf': language === 'hi-IN' 
        ? 'लंबी अवधि की कर बचत योजना' 
        : 'Long-term tax-saving scheme',
      'nps': language === 'hi-IN' 
        ? 'बाजार-लिंक्ड सेवानिवृत्ति योजना' 
        : 'Market-linked retirement scheme',
      'ssy': language === 'hi-IN' 
        ? 'बेटी के लिए बचत योजना' 
        : 'Girl child savings scheme',
      'elss': language === 'hi-IN' 
        ? 'टैक्स सेविंग म्यूचुअल फंड' 
        : 'Tax-saving mutual funds',
      'fd': language === 'hi-IN' 
        ? 'निश्चित ब्याज दर के साथ सुरक्षित निवेश' 
        : 'Safe investment with fixed returns',
      'rd': language === 'hi-IN' 
        ? 'नियमित मासिक बचत योजना' 
        : 'Regular monthly savings scheme',
      'nsc': language === 'hi-IN' 
        ? 'कर बचत बचत प्रमाणपत्र' 
        : 'Tax-saving savings certificate',
    };
    return descriptions[investmentType] || '';
  };

  return (
    <div className="investment-selection-table-container">
      <div className="investment-selection-table-header">
        <h3 className="investment-selection-table-title">
          {language === 'hi-IN' ? 'उपलब्ध निवेश योजनाएं' : 'Available Investment Schemes'}
        </h3>
        <p className="investment-selection-table-subtitle">
          {language === 'hi-IN' 
            ? 'विस्तृत जानकारी के लिए किसी भी निवेश योजना पर क्लिक करें या बोलें' 
            : 'Click or speak any investment scheme for detailed information'}
        </p>
      </div>
      
      <div className="investment-selection-table">
        {investments.map((investment, index) => (
          <div
            key={investment.type || index}
            className="investment-selection-row"
            onClick={() => handleInvestmentClick(investment.type || investment)}
            role="button"
            tabIndex={0}
            onKeyDown={(e) => {
              if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                handleInvestmentClick(investment.type || investment);
              }
            }}
          >
            <div className="investment-selection-row-content">
              <div className="investment-selection-row-icon">
                {investment.icon || '💰'}
              </div>
              <div className="investment-selection-row-info">
                <div className="investment-selection-row-name">
                  {investment.name || getInvestmentDisplayName(investment.type || investment)}
                </div>
                <div className="investment-selection-row-description">
                  {investment.description || getInvestmentDescription(investment.type || investment)}
                </div>
              </div>
              <div className="investment-selection-row-arrow">
                →
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

InvestmentSelectionTable.propTypes = {
  investments: PropTypes.arrayOf(
    PropTypes.shape({
      type: PropTypes.string,
      name: PropTypes.string,
      description: PropTypes.string,
      icon: PropTypes.string,
    })
  ).isRequired,
  language: PropTypes.string,
  onInvestmentSelect: PropTypes.func,
};

export default InvestmentSelectionTable;

