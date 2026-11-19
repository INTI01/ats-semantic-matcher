import re
from typing import Dict, List
import numpy as np
from sentence_transformers import SentenceTransformer, util

MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

# Catálogo base de habilidades/tecnologías frecuentes para contraste rápido
CATALOGO_HABILIDADES = [
    "python",
    "fastapi",
    "django",
    "flask",
    "laravel",
    "php",
    "javascript",
    "typescript",
    "react",
    "node.js",
    "java",
    "c#",
    ".net",
    "sql",
    "postgresql",
    "mysql",
    "sql server",
    "oracle",
    "mongodb",
    "redis",
    "docker",
    "kubernetes",
    "git",
    "github",
    "gitlab",
    "linux",
    "aws",
    "azure",
    "gcp",
    "rest api",
    "apis rest",
    "microservicios",
    "pandas",
    "numpy",
    "scikit-learn",
    "tensorflow",
    "pytorch",
    "machine learning",
    "nlp",
    "power bi",
    "tableau",
    "excel",
    "etl",
    "scrum",
    "agile",
    "sap",
]

_MODELO_CACHE = None


def obtener_modelo() -> SentenceTransformer:
  """Carga y cachea en memoria el modelo preentrenado de Hugging Face."""
  global _MODELO_CACHE
  if _MODELO_CACHE is None:
    _MODELO_CACHE = SentenceTransformer(MODEL_NAME)
  return _MODELO_CACHE


def truncar_texto(texto: str, max_caracteres: int = 4000) -> str:
  """Recorta textos muy extensos para mantener tiempos de inferencia rápidos en CPU."""
  texto = texto.strip()
  if len(texto) <= max_caracteres:
    return texto
  return texto[:max_caracteres]


def calcular_similitud_semantica(texto_vacante: str, texto_cv: str) -> float:
  """Calcula el porcentaje de compatibilidad semántica (0 a 100) entre vacante y CV."""
  if not texto_vacante.strip() or not texto_cv.strip():
    return 0.0

  modelo = obtener_modelo()
  vacante_prep = truncar_texto(texto_vacante, 2500)
  cv_prep = truncar_texto(texto_cv, 4000)

  embeddings = modelo.encode(
      [vacante_prep, cv_prep], convert_to_tensor=True, normalize_embeddings=True
  )
  similitud = float(util.cos_sim(embeddings[0], embeddings[1]).item())

  # Asegurar rango válido [0.0, 100.0]
  porcentaje = max(0.0, min(100.0, similitud * 100.0))
  return round(porcentaje, 2)


def extraer_habilidades(texto: str) -> List[str]:
  """Detecta habilidades técnicas/transversales presentes en el texto."""
  texto_lower = texto.lower()
  encontradas = []

  for skill in CATALOGO_HABILIDADES:
    patron = r"(?<!\w)" + re.escape(skill) + r"(?!\w)"
    if re.search(patron, texto_lower):
      encontradas.append(skill.upper() if len(skill) <= 4 else skill.title())

  # Evitar duplicados preservando orden
  return list(dict.fromkeys(encontradas))


def evaluar_candidato(texto_vacante: str, texto_cv: str) -> Dict:
  """Ejecuta el análisis completo de matching semántico y contraste de habilidades."""
  match_score = calcular_similitud_semantica(texto_vacante, texto_cv)

  skills_vacante = extraer_habilidades(texto_vacante)
  skills_cv = extraer_habilidades(texto_cv)

  set_vacante = {s.lower() for s in skills_vacante}
  set_cv = {s.lower() for s in skills_cv}

  coincidentes = [s for s in skills_vacante if s.lower() in set_cv]
  faltantes = [s for s in skills_vacante if s.lower() not in set_cv]

  return {
      "porcentaje_match": match_score,
      "habilidades_cv": skills_cv,
      "habilidades_coincidentes": coincidentes,
      "habilidades_faltantes": faltantes,
  }