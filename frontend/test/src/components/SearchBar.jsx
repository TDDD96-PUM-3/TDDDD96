import { useState } from "react";
import { Container, Row, Col, Form, InputGroup } from "react-bootstrap";
import { FiSearch } from "react-icons/fi";

export default function SearchBar({ onSearch }) {
  const [query, setQuery] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    onSearch(query);
  };

  return (
    <Container className="mt-4">
      <Row className="justify-content-md-center">
        <Col xs={12} md={7}>
          <Form onSubmit={handleSubmit}>
            <InputGroup>
              <Form.Control
                type="text"
                placeholder="Enter URL..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                style={{
                  borderRadius: "20px 0 0 20px",
                }}
              />
              <InputGroup.Text
                className="search-icon-box"
                onClick={() => onSearch(query)}
              >
                <FiSearch className="search-icon" />
              </InputGroup.Text>
            </InputGroup>
          </Form>
        </Col>
      </Row>
    </Container>
  );
}
