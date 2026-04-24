import React, { Component } from "react";
import { connect } from "react-redux";
import { Link } from "react-router-dom";
import { Alert, Button } from "react-bootstrap";
import PropTypes from "prop-types";

class EmailVerificationBanner extends Component {
  render() {
    const { auth } = this.props;
    
    if (!auth.user || auth.user.is_active === true || auth.user.is_verified === true) {
      return null;
    }

    const bannerStyle = {
      margin: 0,
      borderRadius: 0,
      border: 'none',
      padding: '12px 20px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      flexWrap: 'wrap',
      gap: '10px'
    };

    const textStyle = {
      margin: 0,
      display: 'flex',
      alignItems: 'center',
      gap: '8px',
      flexWrap: 'wrap'
    };

    return (
      <Alert variant="warning" style={bannerStyle}>
        <div style={textStyle}>
          <span>
            <strong>⚠️ Email not verified.</strong>
            &nbsp;Please verify your email address to unlock all features.
          </span>
        </div>
        <div>
          <Link to="/resend_activation" style={{ textDecoration: 'none' }}>
            <Button 
              variant="outline-warning" 
              size="sm"
              style={{ marginLeft: '8px' }}
            >
              Resend Verification Email
            </Button>
          </Link>
        </div>
      </Alert>
    );
  }
}

EmailVerificationBanner.propTypes = {
  auth: PropTypes.object.isRequired
};

const mapStateToProps = state => ({
  auth: state.auth
});

export default connect(mapStateToProps)(EmailVerificationBanner);
