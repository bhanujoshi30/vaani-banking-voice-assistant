import PropTypes from "prop-types";
import logo from "../assets/sun-logo.svg";

import "./SunHeader.css";

const SunHeader = ({ subtitle, actionSlot, mobileMenuButton }) => (
  <header className="sun-header">
    <div className="sun-header__identity">
      <img className="sun-header__logo" src={logo} alt="Sun National Bank logo" />
      <div className="sun-header__text">
        <p className="sun-header__title">Sun National Bank</p>
        {subtitle && <p className="sun-header__subtitle">{subtitle}</p>}
      </div>
      {mobileMenuButton && (
        <div className="sun-header__mobile-menu">
          {mobileMenuButton}
        </div>
      )}
    </div>
    {actionSlot && <div className="sun-header__actions">{actionSlot}</div>}
  </header>
);

SunHeader.propTypes = {
  subtitle: PropTypes.string,
  actionSlot: PropTypes.node,
  mobileMenuButton: PropTypes.node,
};

SunHeader.defaultProps = {
  subtitle: undefined,
  actionSlot: null,
  mobileMenuButton: null,
};

export default SunHeader;


