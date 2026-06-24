# chatbot/services/indexer.py
"""
Indexa datos del sistema en el vectorstore para que el chatbot
pueda responder preguntas sobre el estado real del sistema.
Se ejecuta como tarea Celery cada noche.
"""
from celery import shared_task


@shared_task
def reindexar_datos_sistema():
    from langchain_community.vectorstores import Chroma
    from langchain_community.embeddings import OllamaEmbeddings
    from langchain_classic.schema import Document

    docs = []

    # Fichas activas
    from ficha.models.ficha_model import Ficha
    for ficha in Ficha.objects.filter(estado=True).select_related(
        'version__programa', 'jefe_grupo__user'
    ):
        docs.append(Document(
            page_content=(
                f"Ficha {ficha.codigo_ficha} del programa "
                f"{ficha.version.programa.nombre}, etapa {ficha.etapa}, "
                f"trimestre {ficha.trimestre}, jornada {ficha.jornada}, "
                f"jefe de grupo: {ficha.jefe_grupo.user.nombre if ficha.jefe_grupo else 'sin asignar'}, "
                f"estudiantes reales: {ficha.numero_estudiantes_real}."
            ),
            metadata={'tipo': 'ficha', 'id': ficha.pk},
        ))

    # Docentes
    from docentes.models.docente_model import Docente
    for docente in Docente.objects.filter(estado=True).select_related('user'):
        docs.append(Document(
            page_content=(
                f"Docente {docente.user.nombre}, especialidad {docente.especialidad}, "
                f"máximo {docente.horas_max_semanales} horas semanales."
            ),
            metadata={'tipo': 'docente', 'id': docente.pk},
        ))

    embeddings = OllamaEmbeddings(model='llama3')
    vectorstore = Chroma(
        embedding_function=embeddings,
        persist_directory='./chroma_db',
    )
    vectorstore.add_documents(docs)
    vectorstore.persist()