from unittest.mock import patch, MagicMock, call
from django.test import TestCase, override_settings
from django.conf import settings

from chatbot.services.chatbot_service import ChatbotService
from chatbot.services.indexer import Indexer


# ─────────────────────────────────────────────────────────────────────────────
# ChatbotService
# ─────────────────────────────────────────────────────────────────────────────

class ChatbotServiceTest(TestCase):
    """Tests del servicio principal del chatbot RAG."""

    OLLAMA_CONFIG = {
        'BASE_URL':           'http://localhost:11434',
        'LLM_MODEL':          'llama3',
        'EMBEDDING_MODEL':    'nomic-embed-text',
        'CHROMA_PERSIST_DIR': '/tmp/chroma_test',
    }

    def _make_service(self):
        with override_settings(OLLAMA_CONFIG=self.OLLAMA_CONFIG):
            return ChatbotService()

    @patch('chatbot.services.chatbot_service.chromadb')
    @patch('chatbot.services.chatbot_service.requests.post')
    def test_preguntar_flujo_exitoso(self, mock_post, mock_chroma):
        """preguntar() devuelve texto de respuesta cuando Ollama responde OK."""
        # Mock ChromaDB
        mock_collection = MagicMock()
        mock_collection.query.return_value = {
            'documents': [['Contexto relevante sobre el sistema.']],
            'metadatas': [[{'fuente': 'manual'}]],
        }
        mock_client = MagicMock()
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_chroma.PersistentClient.return_value = mock_client

        # Mock Ollama
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'message': {'content': 'Esta es la respuesta del LLM.'}
        }
        mock_post.return_value = mock_response

        service = self._make_service()
        result = service.preguntar('¿Cómo funciona el sistema?', session_id='sess1')

        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)
        self.assertIn('respuesta', result.lower())

    @patch('chatbot.services.chatbot_service.chromadb')
    @patch('chatbot.services.chatbot_service.requests.post')
    def test_preguntar_ollama_caido_retorna_mensaje_amigable(self, mock_post, mock_chroma):
        """Si Ollama no responde, el servicio retorna mensaje de error amigable."""
        import requests

        mock_collection = MagicMock()
        mock_collection.query.return_value = {
            'documents': [['Contexto']],
            'metadatas': [[{}]],
        }
        mock_chroma.PersistentClient.return_value.get_or_create_collection.return_value = mock_collection
        mock_post.side_effect = requests.exceptions.ConnectionError('Ollama no disponible')

        service = self._make_service()
        result = service.preguntar('¿Qué es una ficha?', session_id='sess2')

        # Debe retornar string (mensaje de error), no lanzar excepción
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)

    @patch('chatbot.services.chatbot_service.chromadb')
    @patch('chatbot.services.chatbot_service.requests.post')
    def test_preguntar_mensaje_vacio_no_explota(self, mock_post, mock_chroma):
        """Mensaje vacío no debe lanzar excepción no controlada."""
        mock_collection = MagicMock()
        mock_collection.query.return_value = {
            'documents': [[]], 'metadatas': [[]]
        }
        mock_chroma.PersistentClient.return_value.get_or_create_collection.return_value = mock_collection

        service = self._make_service()
        try:
            result = service.preguntar('', session_id='sess3')
            # Si retorna algo, debe ser string
            self.assertIsInstance(result, str)
        except (ValueError, TypeError):
            pass  # Acceptable: el servicio puede rechazar mensajes vacíos

    @patch('chatbot.services.chatbot_service.chromadb')
    def test_nueva_sesion_genera_id_unico(self, mock_chroma):
        """nueva_sesion() debe generar IDs únicos en cada llamada."""
        mock_chroma.PersistentClient.return_value.get_or_create_collection.return_value = MagicMock()

        service = self._make_service()
        ids = {service.nueva_sesion() for _ in range(50)}
        self.assertEqual(len(ids), 50, 'Todos los session_id deben ser únicos.')

    @patch('chatbot.services.chatbot_service.chromadb')
    def test_nueva_sesion_retorna_string(self, mock_chroma):
        """nueva_sesion() debe retornar un string no vacío."""
        mock_chroma.PersistentClient.return_value.get_or_create_collection.return_value = MagicMock()

        service = self._make_service()
        session_id = service.nueva_sesion()
        self.assertIsInstance(session_id, str)
        self.assertGreater(len(session_id), 0)


# ─────────────────────────────────────────────────────────────────────────────
# Indexer
# ─────────────────────────────────────────────────────────────────────────────

class IndexerTest(TestCase):
    """Tests del indexador de documentos (ChromaDB + Ollama embeddings)."""

    OLLAMA_CONFIG = {
        'BASE_URL':           'http://localhost:11434',
        'LLM_MODEL':          'llama3',
        'EMBEDDING_MODEL':    'nomic-embed-text',
        'CHROMA_PERSIST_DIR': '/tmp/chroma_test',
    }

    def _make_indexer(self):
        with override_settings(OLLAMA_CONFIG=self.OLLAMA_CONFIG):
            return Indexer()

    @patch('chatbot.services.indexer.chromadb')
    @patch('chatbot.services.indexer.requests.post')
    def test_indexar_llama_chroma_upsert(self, mock_post, mock_chroma):
        """indexar() debe llamar collection.upsert() con los documentos dados."""
        mock_embed_response = MagicMock()
        mock_embed_response.status_code = 200
        mock_embed_response.json.return_value = {'embedding': [0.1, 0.2, 0.3]}
        mock_post.return_value = mock_embed_response

        mock_collection = MagicMock()
        mock_chroma.PersistentClient.return_value.get_or_create_collection.return_value = mock_collection

        indexer = self._make_indexer()
        docs = [
            {'id': 'doc1', 'texto': 'Información sobre fichas.', 'fuente': 'manual'},
            {'id': 'doc2', 'texto': 'Información sobre docentes.', 'fuente': 'sistema'},
        ]
        indexer.indexar(docs)

        mock_collection.upsert.assert_called_once()

    @patch('chatbot.services.indexer.chromadb')
    def test_esta_indexado_true_cuando_hay_documentos(self, mock_chroma):
        """esta_indexado() retorna True si la colección tiene documentos."""
        mock_collection = MagicMock()
        mock_collection.count.return_value = 5
        mock_chroma.PersistentClient.return_value.get_or_create_collection.return_value = mock_collection

        indexer = self._make_indexer()
        self.assertTrue(indexer.esta_indexado())

    @patch('chatbot.services.indexer.chromadb')
    def test_esta_indexado_false_cuando_coleccion_vacia(self, mock_chroma):
        """esta_indexado() retorna False si la colección está vacía."""
        mock_collection = MagicMock()
        mock_collection.count.return_value = 0
        mock_chroma.PersistentClient.return_value.get_or_create_collection.return_value = mock_collection

        indexer = self._make_indexer()
        self.assertFalse(indexer.esta_indexado())

    @patch('chatbot.services.indexer.chromadb')
    @patch('chatbot.services.indexer.requests.post')
    def test_indexar_lista_vacia_no_explota(self, mock_post, mock_chroma):
        """indexar() con lista vacía no debe lanzar excepción."""
        mock_chroma.PersistentClient.return_value.get_or_create_collection.return_value = MagicMock()
        indexer = self._make_indexer()
        try:
            indexer.indexar([])
        except (ValueError, TypeError):
            pass  # Aceptable si el servicio rechaza listas vacías
        except Exception as e:
            self.fail(f'indexar([]) lanzó excepción inesperada: {e}')
