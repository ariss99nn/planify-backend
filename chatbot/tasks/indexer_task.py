from celery import shared_task


@shared_task(name='chatbot.reindexar')
def reindexar_datos_sistema():
    from langchain_chroma import Chroma
    from langchain_huggingface import HuggingFaceEmbeddings
    from langchain_core.documents import Document

    docs = []

    try:
        from ficha.models.ficha_model import Ficha
        for f in Ficha.objects.filter(estado=Ficha.Estado.ACTIVA).select_related('version__programa', 'jefe_grupo__user'):
            jefe = f.jefe_grupo.user.nombre_completo if f.jefe_grupo else 'sin asignar'
            docs.append(Document(
                page_content=(
                    f"Ficha {f.codigo_ficha} del programa {f.version.programa.nombre} "
                    f"versión {f.version.numero}. Etapa {f.get_etapa_display()}, "
                    f"trimestre {f.trimestre}, jornada {f.get_jornada_display()}. "
                    f"Jefe de grupo: {jefe}. Estudiantes activos: {f.numero_estudiantes_real}."
                ),
                metadata={'tipo': 'ficha', 'id': f.pk},
            ))
    except Exception as e:
        print(f'[indexer] Error fichas: {e}')

    try:
        from docentes.models.docente_model import Docente
        for d in Docente.objects.filter(estado=True).select_related('user'):
            docs.append(Document(
                page_content=(
                    f"Docente {d.user.nombre_completo}, especialidad: {d.especialidad}. "
                    f"Máximo {d.horas_max_efectivas} horas semanales."
                ),
                metadata={'tipo': 'docente', 'id': d.pk},
            ))
    except Exception as e:
        print(f'[indexer] Error docentes: {e}')

    try:
        from aulas.models.aula_model import Aula
        for a in Aula.objects.filter(estado=Aula.Estado.ACTIVA).select_related('bloque'):
            docs.append(Document(
                page_content=(
                    f"Aula {a.codigo_aula}, tipo {a.get_tipo_aula_display()}, "
                    f"capacidad {a.capacidad}, bloque {a.bloque.nombre} piso {a.piso}."
                ),
                metadata={'tipo': 'aula', 'id': a.pk},
            ))
    except Exception as e:
        print(f'[indexer] Error aulas: {e}')

    try:
        from competencia.models.competencia_model import Competencia
        for c in Competencia.objects.all():
            docs.append(Document(
                page_content=f"Competencia {c.codigo}: {c.nombre}. Tipo: {c.get_tipo_display()}.",
                metadata={'tipo': 'competencia', 'id': c.pk},
            ))
    except Exception as e:
        print(f'[indexer] Error competencias: {e}')

    try:
        from programa.models.programa_model import Programa
        for p in Programa.objects.filter(estado=Programa.Estado.ACTIVO):
            docs.append(Document(
                page_content=(
                    f"Programa {p.nombre}, nivel {p.get_nivel_display()}. "
                    f"Horas lectivas: {p.horas_lectivas}, prácticas: {p.horas_practicas}. "
                    f"Trimestres totales: {p.trimestres_totales}."
                ),
                metadata={'tipo': 'programa', 'id': p.pk},
            ))
    except Exception as e:
        print(f'[indexer] Error programas: {e}')

    if not docs:
        print('[indexer] Sin documentos para indexar.')
        return

    embeddings = HuggingFaceEmbeddings(
        model_name='sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2',
        model_kwargs={'device': 'cpu'},
    )

    vectorstore = Chroma.from_documents(
        documents=docs,
        embedding=embeddings,
        persist_directory='./chroma_db',
        collection_name='planify',
    )
    print(f'[indexer] {len(docs)} documentos indexados correctamente.')