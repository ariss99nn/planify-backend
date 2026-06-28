from langchain_groq import ChatGroq
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

GROQ_API_KEY = None  # se carga desde settings
CHROMA_DIR   = './chroma_db'


class CHRONOSIAChatbot:

    def __init__(self):
        import os
        from django.conf import settings

        api_key = getattr(settings, 'GROQ_API_KEY', None) or os.getenv('GROQ_API_KEY')

        self.llm = ChatGroq(
            model='llama-3.1-8b-instant',
            api_key=api_key,
            temperature=0.5,
        )

        # Embeddings locales livianos — no necesitan GPU ni Ollama
        self.embeddings = HuggingFaceEmbeddings(
            model_name='sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2',
            model_kwargs={'device': 'cpu'},
        )

        self.vectorstore = Chroma(
            embedding_function=self.embeddings,
            persist_directory=CHROMA_DIR,
            collection_name='planify',
        )

    def responder(
        self,
        pregunta: str,
        historial: list,
        contexto_rol: str = '',
    ) -> str:
        # ── RAG ──────────────────────────────────────────────────────────────
        try:
            retriever = self.vectorstore.as_retriever(
                search_type='similarity',
                search_kwargs={'k': 5},
            )
            docs      = retriever.invoke(pregunta)
            contexto_docs = '\n\n'.join(d.page_content for d in docs)
        except Exception:
            contexto_docs = ''

        # ── Historial ────────────────────────────────────────────────────────
        historial_txt = ''
        for msg in historial[-6:]:
            rol_label     = 'Usuario' if msg.get('role') == 'user' else 'Asistente'
            historial_txt += f"{rol_label}: {msg.get('content', '')}\n"

        # ── Prompt ───────────────────────────────────────────────────────────
        prompt = f"""Eres CHRONOSIA, el asistente inteligente del sistema académico PLANIFY.
Responde siempre en español, de forma clara, precisa y directa.
No inventes información; si no la tienes, dilo explícitamente.
No reveles datos de usuarios que no correspondan al rol del solicitante.

══════════════════════════════
CONTEXTO DEL USUARIO (datos en tiempo real)
══════════════════════════════
{contexto_rol}

══════════════════════════════
INFORMACIÓN ADICIONAL DEL SISTEMA
══════════════════════════════
{contexto_docs if contexto_docs else 'Sin documentos adicionales relevantes.'}

══════════════════════════════
HISTORIAL DE CONVERSACIÓN
══════════════════════════════
{historial_txt if historial_txt else 'Inicio de conversación.'}

══════════════════════════════
PREGUNTA ACTUAL
══════════════════════════════
{pregunta}

RESPUESTA:"""

        # ChatGroq devuelve un AIMessage, extraemos el texto
        response = self.llm.invoke(prompt)
        return response.content