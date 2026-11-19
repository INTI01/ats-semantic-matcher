from datetime import datetime
import os
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text, create_engine
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

# Usa DATABASE_URL si existe (útil luego para Supabase/PostgreSQL), o SQLite local por defecto
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///ats_database.db")

# SQLite necesita check_same_thread=False para trabajar con Streamlit
connect_args = (
    {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Vacante(Base):
  __tablename__ = "vacantes"

  id = Column(Integer, primary_key=True, index=True)
  titulo = Column(String(150), nullable=False)
  area = Column(String(100), nullable=False)
  descripcion = Column(Text, nullable=False)
  fecha_creacion = Column(DateTime, default=datetime.utcnow)

  postulaciones = relationship(
      "Postulacion", back_populates="vacante", cascade="all, delete-orphan"
  )


class Postulacion(Base):
  __tablename__ = "postulaciones"

  id = Column(Integer, primary_key=True, index=True)
  vacante_id = Column(Integer, ForeignKey("vacantes.id"), nullable=False)
  nombre_archivo = Column(String(200), nullable=False)
  candidato_nombre = Column(String(150), nullable=False)
  email = Column(String(150), default="No detectado")
  telefono = Column(String(50), default="No detectado")
  porcentaje_match = Column(Float, nullable=False)
  habilidades_detectadas = Column(Text, default="")
  estado = Column(
      String(50), default="En revision"
  )  # En revision, Preseleccionado, Entrevista, Descartado
  fecha_evaluacion = Column(DateTime, default=datetime.utcnow)

  vacante = relationship("Vacante", back_populates="postulaciones")


def init_db():
  """Crea las tablas en la base de datos si aún no existen."""
  Base.metadata.create_all(bind=engine)


def crear_vacante(titulo: str, area: str, descripcion: str) -> Vacante:
  """Registra una nueva oferta laboral en la base de datos."""
  db = SessionLocal()
  try:
    nueva = Vacante(
        titulo=titulo.strip(), area=area.strip(), descripcion=descripcion.strip()
    )
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva
  finally:
    db.close()


def listar_vacantes():
  """Devuelve todas las vacantes ordenadas de la más reciente a la más antigua."""
  db = SessionLocal()
  try:
    return db.query(Vacante).order_by(Vacante.fecha_creacion.desc()).all()
  finally:
    db.close()


def guardar_postulacion(
    vacante_id: int,
    nombre_archivo: str,
    candidato_nombre: str,
    email: str,
    telefono: str,
    porcentaje_match: float,
    habilidades_detectadas: str,
) -> Postulacion:
  """Guarda el resultado del matching semántico de un CV."""
  db = SessionLocal()
  try:
    postulacion = Postulacion(
        vacante_id=vacante_id,
        nombre_archivo=nombre_archivo,
        candidato_nombre=candidato_nombre,
        email=email,
        telefono=telefono,
        porcentaje_match=round(float(porcentaje_match), 2),
        habilidades_detectadas=habilidades_detectadas,
    )
    db.add(postulacion)
    db.commit()
    db.refresh(postulacion)
    return postulacion
  finally:
    db.close()


def obtener_postulaciones_por_vacante(vacante_id: int):
  """Obtiene las postulaciones de una vacante ordenadas por mayor compatibilidad."""
  db = SessionLocal()
  try:
    return (
        db.query(Postulacion)
        .filter(Postulacion.vacante_id == vacante_id)
        .order_by(Postulacion.porcentaje_match.desc())
        .all()
    )
  finally:
    db.close()


def actualizar_estado_postulacion(postulacion_id: int, nuevo_estado: str):
  """Actualiza el estado del candidato en el proceso de selección."""
  db = SessionLocal()
  try:
    post = (
        db.query(Postulacion).filter(Postulacion.id == postulacion_id).first()
    )
    if post:
      post.estado = nuevo_estado
      db.commit()
  finally:
    db.close()