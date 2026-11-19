import os
from fpdf import FPDF


class CVPDF(FPDF):

  def header(self):
    self.set_font("Helvetica", "B", 14)
    self.cell(0, 10, "CURRICULUM VITAE", align="C", new_x="LMARGIN", new_y="NEXT")
    self.ln(2)


def crear_cv(nombre_archivo, datos):
  pdf = CVPDF()
  pdf.add_page()
  pdf.set_auto_page_break(auto=True, margin=15)

  # Datos personales
  pdf.set_font("Helvetica", "B", 13)
  pdf.cell(0, 8, datos["nombre"], new_x="LMARGIN", new_y="NEXT")

  pdf.set_font("Helvetica", "", 10)
  pdf.cell(
      0,
      6,
      f"Email: {datos['email']} | Telefono: {datos['telefono']} | Ubicacion:"
      f" {datos['ubicacion']}",
      new_x="LMARGIN",
      new_y="NEXT",
  )
  pdf.ln(4)

  # Perfil profesional
  pdf.set_font("Helvetica", "B", 11)
  pdf.cell(0, 7, "PERFIL PROFESIONAL", new_x="LMARGIN", new_y="NEXT")
  pdf.set_font("Helvetica", "", 10)
  pdf.multi_cell(0, 5, datos["perfil"])
  pdf.ln(4)

  # Experiencia laboral
  pdf.set_font("Helvetica", "B", 11)
  pdf.cell(0, 7, "EXPERIENCIA LABORAL", new_x="LMARGIN", new_y="NEXT")
  pdf.set_font("Helvetica", "", 10)
  for exp in datos["experiencia"]:
    pdf.multi_cell(0, 5, f"- {exp}")
    pdf.ln(1)
  pdf.ln(3)

  # Habilidades tecnicas
  pdf.set_font("Helvetica", "B", 11)
  pdf.cell(0, 7, "HABILIDADES Y TECNOLOGIAS", new_x="LMARGIN", new_y="NEXT")
  pdf.set_font("Helvetica", "", 10)
  pdf.multi_cell(0, 5, datos["habilidades"])
  pdf.ln(4)

  # Educacion
  pdf.set_font("Helvetica", "B", 11)
  pdf.cell(0, 7, "FORMACION ACADEMICA", new_x="LMARGIN", new_y="NEXT")
  pdf.set_font("Helvetica", "", 10)
  pdf.multi_cell(0, 5, datos["educacion"])

  ruta_salida = os.path.join("sample_cvs", nombre_archivo)
  pdf.output(ruta_salida)
  print(f"Generado: {ruta_salida}")


candidatos = [
    (
        "01_carlos_mendoza_backend.pdf",
        {
            "nombre": "Carlos Alberto Mendoza Rios",
            "email": "carlos.mendoza.dev@gmail.com",
            "telefono": "987654321",
            "ubicacion": "Lima, Peru",
            "perfil": (
                "Desarrollador Backend con 3 anos de experiencia disenando APIs"
                " RESTful escalables, microservicios y arquitectura de bases de"
                " datos relacionales. Enfocado en codigo limpio, seguridad y"
                " despliegue en la nube."
            ),
            "experiencia": [
                (
                    "Desarrollador Python Backend en TechSoluciones SAC"
                    " (2024-2026): Implementacion de servicios con FastAPI y"
                    " Django, optimizacion de consultas en PostgreSQL y"
                    " despliegue con Docker."
                ),
                (
                    "Programador Junior en Sistemas Andinos (2023-2024):"
                    " Desarrollo de modulos internos en Python, integracion de"
                    " pasarelas de pago y automatizacion de reportes SQL."
                ),
            ],
            "habilidades": (
                "Python, FastAPI, Django, PostgreSQL, MySQL, SQLAlchemy,"
                " Docker, Git, Linux, REST APIs, Redis, AWS EC2."
            ),
            "educacion": (
                "Ingenieria de Software con Inteligencia Artificial - SENATI"
                " (Egresado)"
            ),
        },
    ),
    (
        "02_valeria_torres_fullstack.pdf",
        {
            "nombre": "Valeria Sofia Torres Huaman",
            "email": "valeria.torres.web@outlook.com",
            "telefono": "912345678",
            "ubicacion": "Lima, Peru",
            "perfil": (
                "Desarrolladora Web Full Stack especializada en aplicaciones"
                " empresariales modernas, integracion de interfaces dinamicas y"
                " gestion de bases de datos SQL."
            ),
            "experiencia": [
                (
                    "Desarrolladora Full Stack en InnovaDigital (2024-2026):"
                    " Construccion de portales web con Laravel, PHP,"
                    " JavaScript, React y MySQL. Consumo de APIs externas y"
                    " control de versiones con GitLab."
                ),
                (
                    "Practicante de Desarrollo Web en Consultora Lima"
                    " (2023-2024): Maquetacion con HTML5, CSS3, Bootstrap y"
                    " mantenimiento de sistemas administrativos."
                ),
            ],
            "habilidades": (
                "PHP, Laravel, JavaScript, React, HTML5, CSS3, Bootstrap,"
                " MySQL, SQL Server, Git, GitLab, APIs REST."
            ),
            "educacion": "Ingenieria de Sistemas - Universidad Tecnologica",
        },
    ),
    (
        "03_diego_ramirez_datos.pdf",
        {
            "nombre": "Diego Alejandro Ramirez Vega",
            "email": "diego.ramirez.data@gmail.com",
            "telefono": "945612378",
            "ubicacion": "Arequipa, Peru",
            "perfil": (
                "Analista de Datos e Inteligencia de Negocios con solidos"
                " conocimientos en procesamiento de informacion, modelos"
                " predictivos en Python y visualizacion ejecutiva."
            ),
            "experiencia": [
                (
                    "Analista de Datos en Retail Peru (2024-2026): Limpieza y"
                    " transformacion de datos con Pandas y SQL, creacion de"
                    " dashboards en Power BI y automatizacion de flujos ETL en"
                    " Python."
                ),
                (
                    "Asistente de Estadistica en Financiera Sur (2023-2024):"
                    " Analisis de riesgo crediticio y generacion de reportes"
                    " automatizados."
                ),
            ],
            "habilidades": (
                "Python, Pandas, NumPy, Scikit-Learn, SQL Server, PostgreSQL,"
                " Power BI, Excel Avanzado, ETL, Estadistica."
            ),
            "educacion": "Estadistica e Informatica - Universidad Nacional",
        },
    ),
    (
        "04_lucia_paredes_soporte.pdf",
        {
            "nombre": "Lucia Fernanda Paredes Quispe",
            "email": "lucia.paredes.ti@gmail.com",
            "telefono": "963852741",
            "ubicacion": "Lima, Peru",
            "perfil": (
                "Especialista en Soporte Tecnico TI e Infraestructura con"
                " experiencia en administracion de redes, servidores Windows y"
                " Linux, y atencion de incidencias nivel 2."
            ),
            "experiencia": [
                (
                    "Analista de Soporte TI en Corporacion Pacifico"
                    " (2023-2026): Administracion de Active Directory,"
                    " configuracion de routers y switches, soporte remoto y"
                    " gestion de tickets bajo marco ITIL."
                ),
                (
                    "Tecnico de Mesa de Ayuda en NetPeru (2022-2023):"
                    " Diagnostico de conectividad fibra optica, mantenimiento"
                    " preventivo de equipos y atencion al usuario."
                ),
            ],
            "habilidades": (
                "Redes TCP/IP, Linux, Windows Server, Active Directory,"
                " Virtualizacion, Ciberseguridad basica, ITIL, SQL basico."
            ),
            "educacion": "Administracion de Redes y Comunicaciones - SENATI",
        },
    ),
    (
        "05_andres_salazar_marketing.pdf",
        {
            "nombre": "Andres Felipe Salazar Cordova",
            "email": "andres.salazar.mkt@gmail.com",
            "telefono": "951753852",
            "ubicacion": "Trujillo, Peru",
            "perfil": (
                "Especialista en Marketing Digital y Estrategia Comercial con"
                " enfoque en posicionamiento de marca, campanas de pago y"
                " crecimiento de ventas B2C."
            ),
            "experiencia": [
                (
                    "Coordinador de Marketing en Agencia Creativa Norte"
                    " (2023-2026): Gestion de campanas en Meta Ads y Google"
                    " Ads, estrategia SEO/SEM y analisis de conversiones."
                ),
                (
                    "Community Manager en Grupo Comercial (2021-2023): Creacion"
                    " de contenido digital, gestion de redes sociales y"
                    " fidelizacion de clientes."
                ),
            ],
            "habilidades": (
                "Google Ads, Meta Business Suite, SEO, Google Analytics,"
                " Copywriting, Canva, CRM HubSpot, Estrategia Comercial."
            ),
            "educacion": "Ciencias de la Comunicacion y Marketing",
        },
    ),
    (
        "06_mariana_castro_admin.pdf",
        {
            "nombre": "Mariana Elena Castro Diaz",
            "email": "mariana.castro.adm@hotmail.com",
            "telefono": "974125896",
            "ubicacion": "Piura, Peru",
            "perfil": (
                "Administradora de Empresas con experiencia en gestion"
                " logistica, control de inventarios, facturacion y"
                " coordinacion de proveedores."
            ),
            "experiencia": [
                (
                    "Asistente Administrativa y Logistica en Distribuidora"
                    " Piura (2023-2026): Control de ordenes de compra,"
                    " conciliacion de facturas, manejo de ERP SAP basico y"
                    " supervision de almacen."
                ),
                (
                    "Auxiliar Contable en Estudio Contable Norte (2021-2023):"
                    " Registro de comprobantes, liquidacion de impuestos y"
                    " planillas."
                ),
            ],
            "habilidades": (
                "Gestion Logistica, SAP ERP, Facturacion Electronica, Excel"
                " Financiero, Control de Inventarios, Atencion al Cliente."
            ),
            "educacion": "Administracion de Empresas",
        },
    ),
]

if __name__ == "__main__":
  os.makedirs("sample_cvs", exist_ok=True)
  for archivo, info in candidatos:
    crear_cv(archivo, info)
  print("\nTodos los CVs de prueba fueron generados exitosamente.")