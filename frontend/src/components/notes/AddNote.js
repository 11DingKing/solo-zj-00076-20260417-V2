import React, { Component } from "react";
import PropTypes from "prop-types";
import { connect } from "react-redux";
import { withRouter } from "react-router-dom";
import { Button, Form } from "react-bootstrap";
import { addNote } from "./NotesActions";

class AddNote extends Component {
  constructor(props) {
    super(props);
    this.state = {
      title: "",
      content: ""
    };
  }
  onChange = e => {
    this.setState({ [e.target.name]: e.target.value });
  };

  onAddClick = () => {
    const note = {
      title: this.state.title,
      content: this.state.content
    };
    this.props.addNote(note);
    this.setState({ title: "", content: "" });
  };

  render() {
    return (
      <div>
        <h2>Add new note</h2>
        <Form>
          <Form.Group controlId="titleId">
            <Form.Label>Title</Form.Label>
            <Form.Control
              type="text"
              name="title"
              placeholder="Enter note title"
              value={this.state.title}
              onChange={this.onChange}
            />
          </Form.Group>
          <Form.Group controlId="contentId">
            <Form.Label>Content</Form.Label>
            <Form.Control
              as="textarea"
              rows={3}
              name="content"
              placeholder="Enter note content"
              value={this.state.content}
              onChange={this.onChange}
            />
          </Form.Group>
        </Form>
        <Button variant="success" onClick={this.onAddClick}>
          Add note
        </Button>
      </div>
    );
  }
}

AddNote.propTypes = {
  addNote: PropTypes.func.isRequired
};

const mapStateToProps = state => ({});

export default connect(mapStateToProps, { addNote })(withRouter(AddNote));
