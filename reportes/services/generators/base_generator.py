import io
from abc import ABC, abstractmethod


class BaseReportGenerator(ABC):
    """
    Clase base para todos los generadores de reportes.
    Las subclases solo implementan _get_queryset(), _get_headers() y
    _get_row(); la construcción de PDF y Excel vive aquí una sola vez.
    """

    titulo_reporte = 'Reporte'
    nombre_hoja = 'Hoja1'

    def __init__(self, filtros: dict):
        self.filtros = filtros

    @abstractmethod
    def _get_queryset(self):
        raise NotImplementedError

    @abstractmethod
    def _get_headers(self) -> list:
        raise NotImplementedError

    @abstractmethod
    def _get_row(self, objeto) -> list:
        raise NotImplementedError

    def generar_pdf(self) -> bytes:
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
            from reportlab.lib import colors
            from reportlab.lib.styles import getSampleStyleSheet
        except ImportError:
            raise RuntimeError('Instala reportlab: pip install reportlab')

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        elementos = [Paragraph(self.titulo_reporte, styles['Title'])]

        datos = [self._get_headers()]
        for objeto in self._get_queryset():
            datos.append(self._get_row(objeto))

        tabla = Table(datos)
        tabla.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
        ]))
        elementos.append(tabla)
        doc.build(elementos)
        return buffer.getvalue()

    def generar_excel(self) -> bytes:
        try:
            import openpyxl
        except ImportError:
            raise RuntimeError('Instala openpyxl: pip install openpyxl')

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = self.nombre_hoja
        ws.append(self._get_headers())
        for objeto in self._get_queryset():
            ws.append(self._get_row(objeto))

        buffer = io.BytesIO()
        wb.save(buffer)
        return buffer.getvalue()