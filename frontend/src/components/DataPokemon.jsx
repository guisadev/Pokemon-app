import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Container, Row, Col, ListGroup, Button, Pagination, Modal, Card, Spinner, Alert } from 'react-bootstrap';

function PokemonList() {
  const [pokemons, setPokemons] = useState([]);
  const [currentPageUrl, setCurrentPageUrl] = useState('/api/pokemon/'); // Start with the initial API endpoint
  const [nextPageUrl, setNextPageUrl] = useState(null);
  const [previousPageUrl, setPreviousPageUrl] = useState(null);
  const [selectedPokemon, setSelectedPokemon] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showModal, setShowModal] = useState(false); // State for modal visibility

  // Effect to fetch data whenever currentPageUrl changes
  useEffect(() => {
    setLoading(true);
    setError(null); // Clear previous errors
    setSelectedPokemon(null); // Close details when changing page
    setShowModal(false); // Close modal when changing page

    axios.get(currentPageUrl)
      .then(response => {
        setPokemons(response.data.results); // Assuming results is the array of pokemon
        setNextPageUrl(response.data.next);
        setPreviousPageUrl(response.data.previous);
        setLoading(false);
      })
      .catch(err => {
        console.error('Error fetching data:', err);
        setError('Failed to fetch data. Please try again.');
        setLoading(false);
      });
  }, [currentPageUrl]); // Rerun the effect when currentPageUrl changes

  // Function to handle clicking on a Pokemon name to show details and open modal
  const handlePokemonClick = (pokemon) => {
    setSelectedPokemon(pokemon);
    setShowModal(true); // Open the modal
  };

  // Function to close the detail modal
  const handleCloseModal = () => {
    setShowModal(false);
    setSelectedPokemon(null); // Clear selected pokemon when modal is closed
  };

  // Functions to handle pagination
  const goToNextPage = () => {
    if (nextPageUrl) {
      setCurrentPageUrl(nextPageUrl);
    }
  };

  const goToPreviousPage = () => {
    if (previousPageUrl) {
      setCurrentPageUrl(previousPageUrl);
    }
  };

  return (
    <Container className="mt-4">
      <h2 className="mb-4">Pokémon List</h2>

      {loading && (
        <div className="text-center">
          <Spinner animation="border" role="status">
            <span className="visually-hidden">Loading...</span>
          </Spinner>
          <p>Loading Pokémon...</p>
        </div>
      )}

      {error && (
        <Alert variant="danger">{error}</Alert>
      )}

      {!loading && !error && (
        <>
          {/* Pokemon List */}
          <Row>
            <Col>
              <ListGroup>
                {pokemons.map(pokemon => (
                  <ListGroup.Item
                    key={pokemon.id}
                    action // Makes the list item clickable
                    onClick={() => handlePokemonClick(pokemon)}
                    style={{ cursor: 'pointer' }}
                  >
                    {pokemon.name}
                  </ListGroup.Item>
                ))}
              </ListGroup>
            </Col>
          </Row>

          {/* Pagination Controls */}
          <Row className="mt-4 justify-content-center">
            <Col xs="auto">
              <Button
                onClick={goToPreviousPage}
                disabled={!previousPageUrl}
                className="me-2" // Add some margin to the right
              >
                Previous Page
              </Button>
              <Button
                onClick={goToNextPage}
                disabled={!nextPageUrl}
              >
                Next Page
              </Button>
            </Col>
          </Row>
        </>
      )}


      {/* Pokemon Detail Modal */}
      <Modal show={showModal} onHide={handleCloseModal} centered>
        <Modal.Header closeButton>
          <Modal.Title>{selectedPokemon ? `${selectedPokemon.name} Details` : 'Pokémon Details'}</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {selectedPokemon && (
            <Card>
              <Card.Body>
                 {selectedPokemon.front_default_sprite && (
                    <Card.Img
                      variant="top"
                      src={selectedPokemon.front_default_sprite}
                      alt={selectedPokemon.name}
                      style={{ width: '150px', height: '150px', display: 'block', margin: '0 auto' }}
                    />
                  )}
                <Card.Title className="text-center mt-3">{selectedPokemon.name}</Card.Title>
                <Card.Text>
                  <strong>ID:</strong> {selectedPokemon.id}<br/>
                  <strong>Height:</strong> {selectedPokemon.height}<br/>
                  <strong>Weight:</strong> {selectedPokemon.weight}<br/>
                  <strong>Types:</strong>{' '}
                  {selectedPokemon.types && selectedPokemon.types.map(type => type.type ? type.type.name : 'Unknown Type').join(', ')}
                </Card.Text>
              </Card.Body>
            </Card>
          )}
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={handleCloseModal}>
            Close
          </Button>
        </Modal.Footer>
      </Modal>
    </Container>
  );
}

export default PokemonList;