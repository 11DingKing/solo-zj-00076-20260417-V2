import React, { Component } from "react";
import { withRouter, Link } from "react-router-dom";
import { connect } from "react-redux";
import axios from "axios";
import {
  Alert,
  Container,
  Button,
  Row,
  Col,
  Form,
  FormControl
} from "react-bootstrap";

class ResendActivation extends Component {
  constructor(props) {
    super(props);
    this.state = {
      email: "",
      emailError: "",
      status: "",
      retryAfter: null,
      rateLimited: false
    };
  }
  
  onChange = e => {
    this.setState({ [e.target.name]: e.target.value });
  };

  onResendClick = () => {
    this.setState({ 
      emailError: "", 
      status: "",
      rateLimited: false,
      retryAfter: null
    });

    const userData = {
      email: this.state.email
    };

    axios
      .post("/api/v1/users/resend_activation/", userData)
      .then(response => {
        this.setState({ status: "success" });
      })
      .catch(error => {
        if (error.response) {
          if (error.response.status === 429) {
            this.setState({ 
              status: "rate_limited",
              retryAfter: error.response.data.retry_after || 60
            });
          } else if (error.response.data.hasOwnProperty("email")) {
            this.setState({ emailError: error.response.data["email"] });
          } else {
            this.setState({ status: "error" });
          }
        } else {
          this.setState({ status: "error" });
        }
      });
  };
  
  render() {
    let errorAlert = (
      <Alert variant="danger">
        <Alert.Heading>Problem during activation email send</Alert.Heading>
        Please try again or contact service support for further help.
      </Alert>
    );

    let rateLimitedAlert = (
      <Alert variant="warning">
        <Alert.Heading>Too Many Requests</Alert.Heading>
        <p>
          Please wait {this.state.retryAfter} seconds before requesting another activation email.
        </p>
        <p className="mt-2">
          This limit is in place to prevent abuse. If you don't receive the email, 
          please check your spam folder before requesting another one.
        </p>
      </Alert>
    );

    let successAlert = (
      <Alert variant="success">
        <Alert.Heading>Email Sent</Alert.Heading>
        <p>
          We've sent you an email with the activation link. Please check your email.
        </p>
        <p>
          The link will expire in 24 hours for security reasons.
        </p>
        <p className="mt-3">
          <Link to="/login/">Go to Login</Link>
        </p>
      </Alert>
    );

    let form = (
      <div>
        <Form>
          <Form.Group controlId="emailId">
            <Form.Label>
              Your account is inactive. Please enter your email to resend the activation link.
            </Form.Label>
            <Form.Control
              isInvalid={this.state.emailError}
              type="text"
              name="email"
              placeholder="Enter your email address"
              value={this.state.email}
              onChange={this.onChange}
            />
            <FormControl.Feedback type="invalid">
              {this.state.emailError}
            </FormControl.Feedback>
          </Form.Group>
        </Form>
        <Button color="primary" onClick={this.onResendClick}>
          Send Activation Email
        </Button>
      </div>
    );

    let alert = "";
    if (this.state.status === "error") {
      alert = errorAlert;
    } else if (this.state.status === "rate_limited") {
      alert = rateLimitedAlert;
    } else if (this.state.status === "success") {
      alert = successAlert;
    }

    return (
      <Container>
        <Row>
          <Col md="6">
            <h1>Resend Activation Email</h1>
            {alert}
            {this.state.status !== "success" && this.state.status !== "rate_limited" && form}
          </Col>
        </Row>
      </Container>
    );
  }
}

ResendActivation.propTypes = {};

const mapStateToProps = state => ({});

export default connect(mapStateToProps)(withRouter(ResendActivation));
