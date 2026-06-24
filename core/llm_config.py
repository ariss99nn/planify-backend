from langchain_ollama import OllamaLLM, OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_classic.memory import ConversationBufferMemory

# Configuración
OLLAMA_BASE_URL = "http://localhost:11434"
LLM_MODEL = "llama3"
EMBEDDING_MODEL = "nomic-embed-text"

def get_llm():
    return OllamaLLM(  # Nueva API
        model=LLM_MODEL,
        base_url=OLLAMA_BASE_URL,
        temperature=0.7,
        top_k=40,
        top_p=0.9,
        repeat_penalty=1.1,
    )

def get_embeddings():
    return OllamaEmbeddings(  # Nueva API
        model=EMBEDDING_MODEL,
        base_url=OLLAMA_BASE_URL,
    )

def get_vector_store(persist_directory="./chroma_db"):
    embeddings = get_embeddings()
    return Chroma(
        persist_directory=persist_directory,
        embedding_function=embeddings,
    )

def get_conversational_chain(vector_store=None):
    llm = get_llm()
    
    if vector_store:
        retriever = vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 4}
        )
        
        # Prompt para la conversación
        prompt = ChatPromptTemplate.from_messages([
            ("system", """Eres un asistente útil. Usa el siguiente contexto para responder preguntas.
            Contexto: {context}
            
            Historial de conversación: {chat_history}"""),
            ("human", "{input}")
        ])
        
        # Crear cadenas con las nuevas APIs
        document_chain = create_stuff_documents_chain(llm, prompt)
        retrieval_chain = create_retrieval_chain(retriever, document_chain)
        
        return retrieval_chain
    else:
        return llm

# Función para mantener historial manualmente
class ConversationalChainWrapper:
    def __init__(self, retrieval_chain):
        self.chain = retrieval_chain
        self.chat_history = []
    
    def invoke(self, question):
        response = self.chain.invoke({
            "input": question,
            "chat_history": self.chat_history
        })
        self.chat_history.append(("user", question))
        self.chat_history.append(("assistant", response['answer']))
        return response