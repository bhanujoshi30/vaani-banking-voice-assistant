import PropTypes from 'prop-types';
import './CustomerSupportCard.css';

/**
 * CustomerSupportCard component - Displays bank contact information and support details
 */
const CustomerSupportCard = ({ supportInfo, language = 'en-IN' }) => {
  if (!supportInfo) {
    return null;
  }

  const formatPhoneNumber = (phone) => {
    if (!phone) return '—';
    // Format phone number if needed
    return phone;
  };

  const formatEmail = (email) => {
    if (!email) return '—';
    return email;
  };

  const formatWebsite = (website) => {
    if (!website) return '—';
    // Ensure website has protocol
    if (website && !website.startsWith('http://') && !website.startsWith('https://')) {
      return `https://${website}`;
    }
    return website;
  };

  return (
    <div className="customer-support-card">
      <div className="customer-support-card__header">
        <div className="customer-support-card__icon">🏦</div>
        <div className="customer-support-card__title">
          {language === 'hi-IN' ? 'ग्राहक सहायता' : 'Customer Support'}
        </div>
      </div>

      <div className="customer-support-card__content">
        {supportInfo.headquarters_address && (
          <div className="customer-support-card__field customer-support-card__field--full">
            <span className="customer-support-card__label">
              {language === 'hi-IN' ? 'मुख्यालय पता' : 'Headquarters Address'}
            </span>
            <span className="customer-support-card__value customer-support-card__value--address">
              {supportInfo.headquarters_address}
            </span>
          </div>
        )}

        {supportInfo.customer_care_number && (
          <div className="customer-support-card__field">
            <span className="customer-support-card__label">
              {language === 'hi-IN' ? 'ग्राहक सेवा नंबर' : 'Customer Care Number'}
            </span>
            <span className="customer-support-card__value customer-support-card__value--highlight">
              <a href={`tel:${supportInfo.customer_care_number.replace(/\s/g, '')}`} className="customer-support-card__link">
                {formatPhoneNumber(supportInfo.customer_care_number)}
              </a>
            </span>
          </div>
        )}

        {supportInfo.branch_address && (
          <div className="customer-support-card__field customer-support-card__field--full">
            <span className="customer-support-card__label">
              {language === 'hi-IN' ? 'शाखा पता' : 'Branch Address'}
            </span>
            <span className="customer-support-card__value customer-support-card__value--address">
              {supportInfo.branch_address}
            </span>
          </div>
        )}

        {supportInfo.email && (
          <div className="customer-support-card__field">
            <span className="customer-support-card__label">
              {language === 'hi-IN' ? 'ईमेल पता' : 'Email Address'}
            </span>
            <span className="customer-support-card__value">
              <a href={`mailto:${supportInfo.email}`} className="customer-support-card__link">
                {formatEmail(supportInfo.email)}
              </a>
            </span>
          </div>
        )}

        {supportInfo.website && (
          <div className="customer-support-card__field">
            <span className="customer-support-card__label">
              {language === 'hi-IN' ? 'वेबसाइट' : 'Website'}
            </span>
            <span className="customer-support-card__value">
              <a 
                href={formatWebsite(supportInfo.website)} 
                target="_blank" 
                rel="noopener noreferrer"
                className="customer-support-card__link customer-support-card__link--website"
              >
                {supportInfo.website}
              </a>
            </span>
          </div>
        )}

        {supportInfo.business_hours && (
          <div className="customer-support-card__field customer-support-card__field--full">
            <span className="customer-support-card__label">
              {language === 'hi-IN' ? 'कार्य समय' : 'Business Hours'}
            </span>
            <span className="customer-support-card__value">
              {supportInfo.business_hours}
            </span>
          </div>
        )}
      </div>
    </div>
  );
};

CustomerSupportCard.propTypes = {
  supportInfo: PropTypes.shape({
    headquarters_address: PropTypes.string,
    customer_care_number: PropTypes.string,
    branch_address: PropTypes.string,
    email: PropTypes.string,
    website: PropTypes.string,
    business_hours: PropTypes.string,
  }),
  language: PropTypes.string,
};

export default CustomerSupportCard;

