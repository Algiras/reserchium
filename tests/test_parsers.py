import pytest
from unittest.mock import patch, MagicMock
from reserchium.parsers.arxiv import fetch_and_ingest_arxiv
from reserchium.parsers.pdf import get_document_nodes

@patch("reserchium.parsers.arxiv.arxiv.Client")
@patch("reserchium.parsers.arxiv.ingest_documents")
@patch("reserchium.parsers.arxiv.get_document_nodes")
def test_arxiv_fetch_and_ingest(mock_get_nodes, mock_ingest, mock_arxiv_client):
    # Setup mocks
    mock_paper = MagicMock()
    mock_paper.title = "Test Paper"
    mock_author = MagicMock()
    mock_author.name = "Author1"
    mock_paper.authors = [mock_author]
    mock_paper.published.strftime.return_value = "2023-10-01"
    
    mock_client_instance = MagicMock()
    mock_client_instance.results.return_value = iter([mock_paper])
    mock_arxiv_client.return_value = mock_client_instance
    
    mock_doc = MagicMock()
    mock_doc.metadata = {}
    mock_get_nodes.return_value = [mock_doc]
    
    # Needs to mock download_pdf
    with patch.object(mock_paper, 'download_pdf', return_value="papers/1234.5678.pdf"):
        fetch_and_ingest_arxiv("1234.5678", "test_collection")
        
    mock_get_nodes.assert_called_once()
    mock_ingest.assert_called_once()

def test_get_document_nodes_not_found():
    with pytest.raises(FileNotFoundError):
        get_document_nodes("does_not_exist.pdf")
