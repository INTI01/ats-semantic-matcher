import io
import re
from typing import BinaryIO, Union
from pypdf import PdfReader


def extraer_texto_pdf(archivo_pdf: Union[str, bytes, BinaryIO]) -> str:
  """Extrae y limpia el texto de un archivo PDF desde una ruta, bytes o archivo subido."""
  try:
    if isinstance(archivo_pdf, bytes):
      lector = PdfReader(io.BytesIO(archivo_pdf))
    else:
      lector = PdfReader(archivo_pdf)

    partes_texto = []
    for pagina in lector.pages:
      contenido = pagina.extract_text() or ""
      if contenido.strip():
        partes_texto.append(contenido)

    texto_crudo = "\n".join(partes_texto)
    # Normalizar múltiples espacios y saltos de línea excesivos
    texto_limpio = re.sub(r"[ \t]+", " ", texto_crudo)
    texto_limpio = re.sub(r"\n{2,}", "\n", texto_limpio)
    return texto_limpio.strip()
  except Exception as e:
    raise RuntimeError(f"Error al leer el archivo PDF: {e}") from e


def extraer_email(texto: str) -> str:
  """Busca el primer correo electrónico válido dentro del texto del CV."""
  patron_email = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
  coincidencias = re.findall(patron_email, texto)
  return coincidencias[0] if coincidencias else "No detectado"


def extraer_telefono(texto: str) -> str:
  """Busca un número telefónico (priorizando formato de 9 dígitos o con código de país)."""
  patron_telefono = r"(?:\+?\d{1,3}[\s-]?)?(?:\d[\s-]?){8,12}\d"
  candidatos = re.findall(patron_telefono, texto)
  for cand in candidatos:
    digitos = re.sub(r"\D", "", cand)
    if 8 <= len(digitos) <= 13:
      return digitos
  return "No detectado"


def extraer_nombre_estimado(texto: str, fallback_archivo: str = "") -> str:
  """Intenta identificar el nombre del candidato en las primeras líneas útiles del CV."""
  palabras_excluir = {
      "curriculum",
      "vitae",
      "cv",
      "perfil",
      "profesional",
      "experiencia",
      "laboral",
      "educacion",
      "formacion",
      "habilidades",
      "contacto",
      "email",
      "telefono",
      "ubicacion",
      "resumen",
  }
  lineas = [linea.strip() for linea in texto.splitlines() if linea.strip()]

  for linea in lineas[:8]:
    linea_limpia = re.sub(r"[^A-Za-zÁÉÍÓÚáéíóúÑñ\s]", "", linea).strip()
    palabras = linea_limpia.split()
    if 2 <= len(palabras) <= 5:
      if not any(p.lower() in palabras_excluir for p in palabras):
        return " ".join(p.capitalize() for p in palabras)

  if fallback_archivo:
    base = fallback_archivo.rsplit(".", 1)[0]
    base = re.sub(r"^\d+[_-]?", "", base).replace("_", " ").replace("-", " ")
    return base.title().strip() or "Candidato sin nombre"

  return "Candidato sin nombre"


def procesar_cv_pdf(
    archivo_pdf: Union[str, bytes, BinaryIO], nombre_archivo: str = "cv.pdf"
) -> dict:
  """Procesa un CV en PDF y devuelve su texto limpio junto con datos estructurados."""
  texto = extraer_texto_pdf(archivo_pdf)
  return {
      "nombre_archivo": nombre_archivo,
      "texto": texto,
      "candidato_nombre": extraer_nombre_estimado(texto, nombre_archivo),
      "email": extraer_email(texto),
      "telefono": extraer_telefono(texto),
      "longitud_caracteres": len(texto),
  }