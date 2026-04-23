import React, { Component } from "react";
import PropTypes from "prop-types";
import { connect } from "react-redux";
import { withRouter } from "react-router-dom";
import { deleteNote, updateNote } from "./NotesActions";
import { Button, Modal, Form } from "react-bootstrap";

class Note extends Component {
  constructor(props) {
    super(props);
    this.state = {
      showModal: false,
      editTitle: props.note.title || "",
      editContent: props.note.content || "",
    };
  }

  componentDidUpdate(prevProps) {
    if (prevProps.note.id !== this.props.note.id) {
      this.setState({
        editTitle: this.props.note.title || "",
        editContent: this.props.note.content || "",
      });
    }
  }

  onDeleteClick = () => {
    const { note } = this.props;
    this.props.deleteNote(note.id);
  };

  onEditClick = () => {
    this.setState({
      showModal: true,
      editTitle: this.props.note.title || "",
      editContent: this.props.note.content || "",
    });
  };

  handleModalClose = () => {
    this.setState({ showModal: false });
  };

  handleInputChange = (e) => {
    this.setState({ [e.target.name]: e.target.value });
  };

  handleSaveChanges = () => {
    const { note } = this.props;
    const { editTitle, editContent } = this.state;
    this.props.updateNote(note.id, {
      title: editTitle,
      content: editContent,
    });
    this.setState({ showModal: false });
  };

  render() {
    const { note } = this.props;
    const { showModal, editTitle, editContent } = this.state;

    return (
      <div>
        <hr />
        <h4>{note.title || "Untitled Note"}</h4>
        <p>{note.content}</p>
        <Button variant="primary" size="sm" onClick={this.onEditClick}>
          Edit
        </Button>{" "}
        <Button variant="danger" size="sm" onClick={this.onDeleteClick}>
          Delete
        </Button>
        <Modal show={showModal} onHide={this.handleModalClose}>
          <Modal.Header closeButton>
            <Modal.Title>Edit Note</Modal.Title>
          </Modal.Header>
          <Modal.Body>
            <Form>
              <Form.Group controlId="editTitleId">
                <Form.Label>Title</Form.Label>
                <Form.Control
                  type="text"
                  name="editTitle"
                  value={editTitle}
                  onChange={this.handleInputChange}
                />
              </Form.Group>
              <Form.Group controlId="editContentId">
                <Form.Label>Content</Form.Label>
                <Form.Control
                  as="textarea"
                  rows={5}
                  name="editContent"
                  value={editContent}
                  onChange={this.handleInputChange}
                />
              </Form.Group>
            </Form>
          </Modal.Body>
          <Modal.Footer>
            <Button variant="secondary" onClick={this.handleModalClose}>
              Cancel
            </Button>
            <Button variant="primary" onClick={this.handleSaveChanges}>
              Save Changes
            </Button>
          </Modal.Footer>
        </Modal>
      </div>
    );
  }
}

Note.propTypes = {
  note: PropTypes.object.isRequired,
};
const mapStateToProps = (state) => ({});

export default connect(mapStateToProps, { deleteNote, updateNote })(
  withRouter(Note),
);
