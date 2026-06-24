from langchain_ollama import OllamaLLM, OllamaEmbeddings
from langchain_community.vectorstores import Chroma

OLLAMA_BASE_URL = "http://localhost:11434"


class CHRONOSIAChatbot:
    """
    RAG + contexto vivo de DB.
    El contexto_rol se inyecta como bloque de sistema antes de cada respuesta,
    garantizando que el LLM solo vea lo que el usuario tiene permitido.
    """

    def __init__(self):
        self.llm = OllamaLLM(
            model='llama3',
            base_url=OLLAMA_BASE_URL,
            temperature=0.5,
            top_k=40,
            top_p=0.9,
            repeat_penalty=1.1,
        )
        self.embeddings = OllamaEmbeddings(
            model='nomic-embed-text',
            base_url=OLLAMA_BASE_URL,
        )
        self.vectorstore = Chroma(
            embedding_function=self.embeddings,
            persist_directory='./chroma_db',
        )

    def responder(
        self,
        pregunta: str,
        historial: list,          # [{"role": "user"|"assistant", "content": "..."}]
        contexto_rol: str = '',   # generado por ContextBuilder
    ) -> str:

        # ── 1. Recuperar documentos relevantes del vectorstore ─────────────
        retriever = self.vectorstore.as_retriever(
            search_type='similarity',
            search_kwargs={'k': 5},
        )
        try:
            docs = retriever.invoke(pregunta)
            contexto_docs = "\n\n".join(d.page_content for d in docs)
        except Exception:
            contexto_docs = ''

        # ── 2. Construir historial como texto ──────────────────────────────
        # Solo los últimos 3 turnos para no saturar el contexto
        historial_txt = ''
        for msg in historial[-6:]:
            role_label = 'Usuario' if msg.get('role') == 'user' else 'Asistente'
            historial_txt += f"{role_label}: {msg.get('content', '')}\n"

        # ── 3. Prompt final ────────────────────────────────────────────────
        prompt = f"""Eres CHRONOSIA, el asistente inteligente del sistema académico PLANIFY.
Responde siempre en español, de forma clara, precisa y directa.
No inventes información; si no la tienes, dilo explícitamente.

══════════════════════════════
CONTEXTO DEL USUARIO (datos en tiempo real de la base de datos)
══════════════════════════════
{contexto_rol}

══════════════════════════════
INFORMACIÓN ADICIONAL DEL SISTEMA (base de conocimiento)
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

        return self.llm.invoke(prompt)