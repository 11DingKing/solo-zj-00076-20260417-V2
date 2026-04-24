import React, { Component } from "react";
import PropTypes from "prop-types";
import { connect } from "react-redux";
import { withRouter } from "react-router-dom";

import { Container, Navbar, Nav } from "react-bootstrap";
import { logout } from "../login/LoginActions";

import NotesList from "../notes/NotesList";
import AddNote from "../notes/AddNote";
import EmailVerificationBanner from "../common/EmailVerificationBanner";

class Dashboard extends Component {
  onLogout = () => {
    this.props.logout();
  };

  render() {
    const { user } = this.props.auth;
    return (
      <div>
        <EmailVerificationBanner />
        <Navbar bg="light">
          <Navbar.Brand href="/">Home</Navbar.Brand>
          <Navbar.Toggle />
          <Navbar.Collapse className="justify-content-end">
            <Navbar.Text>
              User: <b>{user.username}</b>
              {user.is_active === false && (
                <span style={{ marginLeft: '8px', color: '#dc3545', fontSize: '12px' }}>
                  (Unverified)
                </span>
              )}
            </Navbar.Text>
            <Nav.Link onClick={this.onLogout}>Logout</Nav.Link>
          </Navbar.Collapse>
        </Navbar>
        <Container>
          <NotesList />
          <AddNote />
        </Container>
      </div>
    );
  }
}

Dashboard.propTypes = {
  logout: PropTypes.func.isRequired,
  auth: PropTypes.object.isRequired
};

const mapStateToProps = state => ({
  auth: state.auth
});

export default connect(mapStateToProps, {
  logout
})(withRouter(Dashboard));
