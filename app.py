import os
import pandas as pd
import streamlit as st
import database
import nlp_engine
import pdf_parser

# Configuración general de la aplicación
st.set_page_config(
    page_title="ATS Semántico | Matching de CVs con PLN",
    page_icon="🎯",
    layout="wide",
)

# Inicializar tablas en base de datos de forma segura
database.init_db()


@st.cache_resource
def cargar_motor_pln():
  """Precarga y mantiene en caché el modelo preentrenado de Hugging Face."""
  return nlp_engine.obtener_modelo()


# Encabezado principal
st.title("🎯 ATS Semántico — Motor de Matching de CVs con PLN")
st.caption(
    "Evaluación semántica de candidatos mediante modelos preentrenados de"
    " Hugging Face y persistencia relacional."
)

# Precarga silenciosa del modelo para que la primera evaluación sea ágil
with st.spinner("Verificando motor de lenguaje natural..."):
  cargar_motor_pln()

# Indicadores superiores rápidos
vacantes_existentes = database.listar_vacantes()
total_vacantes = len(vacantes_existentes)

col_m1, col_m2, col_m3 = st.columns(3)
col_m1.metric("Vacantes Activas", total_vacantes)
col_m2.metric("Modelo PLN", "MiniLM-L12-v2")
col_m3.metric(
    "Persistencia",
    "PostgreSQL / Supabase"
    if not database.DATABASE_URL.startswith("sqlite")
    else "SQLite Local",
)

st.divider()

# Pestañas principales de la plataforma
tab_vacantes, tab_evaluacion, tab_ranking = st.tabs([
    "📋 1. Gestión de Vacantes",
    "📄 2. Evaluación Semántica de CVs",
    "🏆 3. Ranking y Gestión de Candidatos",
])

# =====================================================================
# MÓDULO 1 (FASE 4.1): GESTIÓN Y REGISTRO DE VACANTES
# =====================================================================
with tab_vacantes:
  st.subheader("Registrar Nueva Oferta Laboral")
  st.write(
      "Define el puesto, el área y el perfil/requisitos detallados. Esta"
      " descripción será convertida en vectores semánticos para comparar"
      " currículums."
  )

  with st.form("form_crear_vacante", clear_on_submit=True):
    col1, col2 = st.columns([2, 1])
    with col1:
      titulo = st.text_input(
          "Título del puesto *",
          placeholder="Ej. Desarrollador Backend Python / FastAPI",
      )
    with col2:
      area = st.selectbox(
          "Área / Departamento",
          [
              "Tecnología / Ingeniería",
              "Datos / Inteligencia Artificial",
              "Producto / Gestión",
              "Operaciones / Logística",
              "Administración / Finanzas",
              "Comercial / Marketing",
          ],
      )

    descripcion = st.text_area(
        "Descripción del puesto, responsabilidades y requisitos técnicos *",
        height=180,
        placeholder=(
            "Describe las funciones principales, años de experiencia"
            " deseables, tecnologías requeridas (Python, SQL, Docker, APIs"
            " REST, etc.) y habilidades clave..."
        ),
    )

    # Plantilla rápida opcional para agilizar pruebas en vivo
    enviar_vacante = st.form_submit_button(
        "💾 Guardar Vacante en Base de Datos", type="primary"
    )

  if enviar_vacante:
    if not titulo.strip() or not descripcion.strip():
      st.error(
          "Debes completar al menos el **Título del puesto** y la"
          " **Descripción / Requisitos**."
      )
    else:
      nueva_vacante = database.crear_vacante(titulo, area, descripcion)
      st.success(
          f"Vacante **'{nueva_vacante.titulo}'** registrada con éxito (ID"
          f" #{nueva_vacante.id})."
      )
      st.rerun()

  st.divider()
  st.subheader("Vacantes Registradas")

  vacantes_actualizadas = database.listar_vacantes()
  if not vacantes_actualizadas:
    st.info(
        "Aún no hay vacantes registradas. Crea la primera usando el formulario"
        " superior."
    )
  else:
    datos_vacantes = [
        {
            "ID": v.id,
            "Puesto": v.titulo,
            "Área": v.area,
            "Requisitos / Descripción": (
                v.descripcion[:160] + "..."
                if len(v.descripcion) > 160
                else v.descripcion
            ),
            "Fecha Creación": (
                v.fecha_creacion.strftime("%Y-%m-%d %H:%M")
                if v.fecha_creacion
                else ""
            ),
        }
        for v in vacantes_actualizadas
    ]
    st.dataframe(
        pd.DataFrame(datos_vacantes), use_container_width=True, hide_index=True
    )

    # Selector para inspeccionar la descripción completa de una vacante
    opciones_vac = {f"#{v.id} — {v.titulo}": v for v in vacantes_actualizadas}
    seleccion_detalle = st.selectbox(
        "Inspeccionar perfil completo de una vacante:",
        options=list(opciones_vac.keys()),
    )
    vac_sel = opciones_vac[seleccion_detalle]
    with st.expander(f"Ver detalle completo de: {vac_sel.titulo}", expanded=False):
      st.markdown(f"**Área:** {vac_sel.area}")
      st.write(vac_sel.descripcion)

# =====================================================================
# MÓDULO 2 (FASE 4.2): EVALUACIÓN SEMÁNTICA DE CVs EN LOTE
# =====================================================================
with tab_evaluacion:
  st.subheader("Evaluar Currículums en PDF contra una Vacante")

  vacantes_eval = database.listar_vacantes()
  if not vacantes_eval:
    st.warning(
        "Primero debes registrar al menos una vacante en la pestaña **1."
        " Gestión de Vacantes**."
    )
  else:
    opciones_eval = {
        f"#{v.id} — {v.titulo} ({v.area})": v for v in vacantes_eval
    }
    vacante_elegida_label = st.selectbox(
        "Selecciona la vacante a evaluar:",
        options=list(opciones_eval.keys()),
        key="selector_vacante_eval",
    )
    vacante_obj = opciones_eval[vacante_elegida_label]

    with st.expander("Ver perfil de la vacante seleccionada", expanded=True):
      st.write(vacante_obj.descripcion)

    archivos_subidos = st.file_uploader(
        "Sube uno o varios currículums en formato PDF",
        type=["pdf"],
        accept_multiple_files=True,
        help=(
            "Puedes seleccionar varios archivos PDF a la vez (por ejemplo, los"
            " de la carpeta sample_cvs/)."
        ),
    )

    ejecutar_matching = st.button(
        "🚀 Ejecutar Matching Semántico y Guardar en BD",
        type="primary",
        disabled=not archivos_subidos,
    )

    if ejecutar_matching and archivos_subidos:
      resultados_sesion = []
      barra_progreso = st.progress(0, text="Iniciando evaluación de CVs...")

      for idx, archivo in enumerate(archivos_subidos):
        barra_progreso.progress(
            (idx + 1) / len(archivos_subidos),
            text=f"Procesando {archivo.name} ({idx + 1}/{len(archivos_subidos)})...",
        )

        try:
          datos_pdf = pdf_parser.procesar_cv_pdf(
              archivo.getvalue(), archivo.name
          )
          texto_cv = datos_pdf["texto"]

          if not texto_cv.strip():
            st.warning(
                f"El archivo **{archivo.name}** no contiene texto extraíble"
                " (podría ser una imagen escaneada)."
            )
            continue

          analisis = nlp_engine.evaluar_candidato(
              vacante_obj.descripcion, texto_cv
          )
          skills_texto = (
              ", ".join(analisis["habilidades_cv"])
              if analisis["habilidades_cv"]
              else "No detectadas"
          )

          database.guardar_postulacion(
              vacante_id=vacante_obj.id,
              nombre_archivo=archivo.name,
              candidato_nombre=datos_pdf["candidato_nombre"],
              email=datos_pdf["email"],
              telefono=datos_pdf["telefono"],
              porcentaje_match=analisis["porcentaje_match"],
              habilidades_detectadas=skills_texto,
          )

          resultados_sesion.append({
              "Candidato": datos_pdf["candidato_nombre"],
              "Archivo": archivo.name,
              "Match (%)": analisis["porcentaje_match"],
              "Email": datos_pdf["email"],
              "Teléfono": datos_pdf["telefono"],
              "Coincidentes": (
                  ", ".join(analisis["habilidades_coincidentes"]) or "—"
              ),
              "Faltantes": ", ".join(analisis["habilidades_faltantes"]) or "—",
          })
        except Exception as e:
          st.error(f"Error al procesar **{archivo.name}**: {e}")

      barra_progreso.empty()

      if resultados_sesion:
        st.success(
            f"Se evaluaron y guardaron **{len(resultados_sesion)}** "
            f"postulación(es) para **'{vacante_obj.titulo}'**."
        )
        df_res = pd.DataFrame(resultados_sesion).sort_values(
            by="Match (%)", ascending=False
        )
        st.dataframe(df_res, use_container_width=True, hide_index=True)

# =====================================================================
# MÓDULO 3 (FASE 4.3): RANKING, ESTADOS Y EXPORTACIÓN
# =====================================================================
with tab_ranking:
  st.subheader("Ranking de Candidatos y Seguimiento del Proceso")

  vacantes_rank = database.listar_vacantes()
  if not vacantes_rank:
    st.info("Aún no hay vacantes registradas.")
  else:
    opciones_rank = {
        f"#{v.id} — {v.titulo} ({v.area})": v for v in vacantes_rank
    }
    vac_rank_label = st.selectbox(
        "Selecciona una vacante para ver su ranking:",
        options=list(opciones_rank.keys()),
        key="selector_vacante_ranking",
    )
    vac_rank_obj = opciones_rank[vac_rank_label]

    postulaciones = database.obtener_postulaciones_por_vacante(vac_rank_obj.id)

    if not postulaciones:
      st.warning(
          "Esta vacante todavía no tiene CVs evaluados. Ve a la pestaña **2."
          " Evaluación Semántica de CVs** para procesar postulaciones."
      )
    else:
      # Tabla de ranking ordenada por porcentaje de match
      filas_ranking = [
          {
              "ID": p.id,
              "Candidato": p.candidato_nombre,
              "Match (%)": p.porcentaje_match,
              "Estado": p.estado,
              "Email": p.email,
              "Teléfono": p.telefono,
              "Habilidades Detectadas": p.habilidades_detectadas,
              "Archivo": p.nombre_archivo,
              "Fecha": (
                  p.fecha_evaluacion.strftime("%Y-%m-%d %H:%M")
                  if p.fecha_evaluacion
                  else ""
              ),
          }
          for p in postulaciones
      ]
      df_ranking = pd.DataFrame(filas_ranking)

      st.dataframe(df_ranking, use_container_width=True, hide_index=True)

      # Gráfico comparativo de compatibilidad
      st.markdown("#### Comparativa de Compatibilidad Semántica (%)")
      df_chart = df_ranking.set_index("Candidato")[["Match (%)"]]
      st.bar_chart(df_chart)

      # Cambio de estado del candidato persistido en BD
      st.markdown("#### Actualizar Estado de un Candidato")
      col_est1, col_est2, col_est3 = st.columns([2, 1, 1])
      opciones_post = {
          f"#{p.id} — {p.candidato_nombre} ({p.porcentaje_match}% | Actual:"
          f" {p.estado})": p.id
          for p in postulaciones
      }
      estados_disponibles = [
          "En revision",
          "Preseleccionado",
          "Entrevista",
          "Descartado",
      ]

      with col_est1:
        post_sel_label = st.selectbox(
            "Candidato:", options=list(opciones_post.keys())
        )
      with col_est2:
        nuevo_estado = st.selectbox("Nuevo estado:", options=estados_disponibles)
      with col_est3:
        st.write("")
        st.write("")
        if st.button("Actualizar Estado", type="primary"):
          database.actualizar_estado_postulacion(
              opciones_post[post_sel_label], nuevo_estado
          )
          st.success("Estado actualizado en la base de datos.")
          st.rerun()

      # Exportación a CSV
      st.divider()
      csv_bytes = df_ranking.to_csv(index=False).encode("utf-8-sig")
      st.download_button(
          label="⬇️ Descargar Ranking en CSV",
          data=csv_bytes,
          file_name=f"ranking_vacante_{vac_rank_obj.id}.csv",
          mime="text/csv",
      )