import streamlit as st
import pandas as pd
from datetime import date
from sqlalchemy import create_engine,text
import numpy as np

# Reemplaza con tus valores reales
db_url = st.secrets["DB_URL"]

# Crear engine
engine = create_engine(db_url)

# ---------------- CARGAR ARCHIVO EXCEL LOCAL --------------------
@st.cache_data
def cargar_empleados_desde_excel(ruta_excel):
    try:
        df = pd.read_excel(ruta_excel, dtype={"No. Empleado": str})
        df.set_index("No. Empleado", inplace=True)
        return df
    except Exception as e:
        st.error(f"Error al cargar el archivo: {e}")
        return pd.DataFrame()

# ---------------- LOGIN ----------------
def login():
    st.title("🔐 Inicio de sesión")

    correo = st.text_input("Correo electrónico")
    contraseña = st.text_input("Contraseña", type="password")

    if st.button("Iniciar sesión"):
        if not correo or not contraseña:
            st.warning("⚠️ Por favor, completa todos los campos.")
            return

        try:
            # Consulta para verificar credenciales
            query = text("SELECT * FROM usuarios WHERE correo = :correo AND contraseña = :contraseña")
            with engine.connect() as conn:
                result = conn.execute(query, {"correo": correo, "contraseña": contraseña}).fetchone()

            if result:
                st.session_state["user"] = dict(result._mapping)
                st.session_state["autenticado"] = True
                st.success("✅ Inicio de sesión exitoso.")
                st.rerun()
            else:
                st.error("❌ Credenciales incorrectas. Intenta de nuevo.")
        except Exception as e:
            st.error(f"❌ Error al conectarse a la base de datos: {e}")



#--------------------AGREGAR NUEVO USUARIO --------------
def registrar_usuario():
    st.title("📝 Registro de usuario")

    correo = st.text_input("Nuevo correo")
    contraseña = st.text_input("Nueva contraseña", type="password")

    if st.button("Registrarme"):
        if not correo or not contraseña:
            st.warning("⚠️ Por favor, completa ambos campos.")
            return

        try:
            with engine.connect() as conn:
                # Verifica si el correo ya existe
                query_check = text("SELECT 1 FROM usuarios WHERE correo = :correo")
                result = conn.execute(query_check, {"correo": correo}).fetchone()

                if result:
                    st.error("❌ Este correo ya está registrado.")
                    return

                # Inserta el nuevo usuario (UUID se genera automáticamente)
                query_insert = text("INSERT INTO usuarios (correo, contraseña) VALUES (:correo, :contraseña)")
                conn.execute(query_insert, {"correo": correo, "contraseña": contraseña})
                st.success("✅ Usuario registrado exitosamente.")

        except Exception as e:
            st.error(f"❌ Error al registrar el usuario: {e}")
#--------------------REGISTRO DE ESTILO CSS --------------
def registrar_estilo_sidebar():
    #CSS para boton animado
    st.markdown("""  
        <style>
        .sidebar > button {
            background-color: #004E66;
            color: white !important;
            padding: 5px 50px;
            text-align: center;
            text-decoration: none;
            display: block;
            font-size: 16px;
            margin: 10px auto;
            border: none;
            border-radius: 8px;
            transition: background-color 0.3s ease, transform 0.2s ease;
            cursor: pointer;
        }
            .stButton > button:hover {    
                background-color: #2B6F84;
                color: white !important;
                transform: scale(1.05);
                }
        </style>
    """, unsafe_allow_html=True)



#--------------------MENU PRINCIPAL --------------
def menu_principal():
    st.markdown("""
    <h1 style='text-align: left; margin-top: 0;'>
        🏠 Menú principal
    </h1>
""", unsafe_allow_html=True)
    registrar_estilo_sidebar()
    st.set_page_config(initial_sidebar_state="expanded")

    # Imagen redonda en el sidebar
    url_imagen = "https://raw.githubusercontent.com/gabrielcanela91/Mi_Proyecto_Streamlit/main/capacitacion.png"
    st.sidebar.markdown(f"""
        <style>
            .circle-img {{
                display: block;
                margin-left: auto;
                margin-right: auto;
                border-radius: 50%;
                border: 3px solid #004E66;
                width: 120px;
                height: 120px;
                object-fit: cover;
            }}
        </style>
        <img src="{url_imagen}" class="circle-img">
    """, unsafe_allow_html=True)

    st.sidebar.markdown("<h2 style='margin-top:0;'>Menú Principal</h2>", unsafe_allow_html=True)
            
        # Botón funcional que te lleva directamente al paso 1 (índice 1 = Bienvenida)
    if st.sidebar.button("Registrar Capacitaciones"):
        st.session_state["paso_actual"] = 1
        st.rerun()

    if st.sidebar.button("Registros"):
        st.session_state["paso_actual"] = 5
        st.rerun()

# ---------------- PESTAÑA 1: INTRODUCCIÓN ----------------
def mostrar_bienvenida():
    st.title("Bienvenida")
    st.markdown("""
    ### Estimado/a Supervisor/a:

    Bienvenido/a al formulario de **registro de capacitaciones**.

    Por favor, complete cada paso cuidadosamente:
    1. Ingrese el código del colaborador.
    2. Verifique que el nombre y puesto coincidan.
    3. Complete el formulario de capacitación.
    4. Revise los registros completados en la pestaña final.

    ¡Gracias por su colaboración en el desarrollo de nuestro equipo!
    """)

# ---------------- PESTAÑA 2: CÓDIGOS MÚLTIPLES ----------------
def ingresar_codigo_empleado():
    st.title("👤 Paso 1: Ingresar Código(s) de Empleado")
    texto = st.text_area("Ingrese uno o varios códigos separados por coma (,):").strip()
    
    if texto:
        codigos = [c.strip().zfill(3) for c in texto.split(",") if c.strip()]
        st.session_state["codigos_empleados"] = codigos
        st.success(f"Se registraron {len(codigos)} código(s). Pase al siguiente paso.")

# ---------------- PESTAÑA 3: VERIFICACIÓN ----------------
def verificar_empleado(empleados_df):
    st.title("📌 Paso 2: Verificar Información del Empleado")
    codigos = st.session_state.get("codigos_empleados", [])

    if not codigos:
        st.warning("Debe ingresar al menos un código en el paso anterior.")
        return

    encontrados = empleados_df.loc[empleados_df.index.intersection(codigos)]

    if encontrados.empty:
        st.warning("No se encontró ningún empleado con los códigos proporcionados.")
    else:
        st.write("### Empleados encontrados:")
        st.dataframe(encontrados[["Nombre", "Puesto"]])

# ---------------- PESTAÑA 4: FORMULARIO ----------------
def formulario_capacitacion(empleados_df):
    st.title("📝 Paso 3: Registro de Capacitación")

    codigos = st.session_state.get("codigos_empleados", [])

    if not codigos:
        st.warning("Debe ingresar al menos un código válido en el Paso 1.")
        return

    with st.form("formulario_general"):
        fecha = st.date_input("Fecha", value=date.today())
        nombre_programa = st.text_input("Nombre Programa")
        tipo_programa = st.text_input("Tipo de Programa")
        categoria = st.text_input("Categoría")
        modalidad = st.selectbox("Modalidad", ["Presencial", "Virtual", "Híbrida", "Otra"])
        proveedor = st.text_input("Proveedor")
        facilitador = st.text_input("Facilitador")
        lugar = st.text_input("Lugar del evento")
        duracion_dias = st.number_input("Duración del Programa (Días)", min_value=0, step=1)
        duracion_hrs_dia = st.number_input("Duración (HRs Por Día)", min_value=0.0, step=0.5)
        horas_capacitadas = st.number_input("Horas Capacitadas", min_value=0.0, step=0.5)
        asignado = st.selectbox("Asignado (Ubits)", ["Sí", "No"])

        enviar = st.form_submit_button("Guardar registro para todos")

        if enviar:
            user = st.session_state.get("user")  # opcional si tienes usuario autenticado

            with engine.begin() as conn:
                for codigo in codigos:
                    if codigo not in empleados_df.index:
                        continue

                    datos = empleados_df.loc[codigo]

                    insert_data = {
                        "fecha": fecha.strftime("%Y-%m-%d"),
                        "nombre_programa": nombre_programa,
                        "tipo_programa": tipo_programa,
                        "categoria": categoria,
                        "modalidad": modalidad,
                        "proveedor": proveedor,
                        "facilitador": facilitador,
                        "lugar": lugar,
                        "no_empleado": codigo,
                        "nombre_empleado": datos["Nombre"],
                        "puesto": datos["Puesto"],
                        "area": datos["Área"],
                        "departamento": datos["Departamento"],
                        "tipologia_puesto": datos["Tipología Puesto"],
                        "edad": int(datos["Edad"]),
                        "empresa": datos["Empresa"],
                        "duracion_dias": duracion_dias,
                        "duracion_hrs_dia": duracion_hrs_dia,
                        "horas_capacitadas": horas_capacitadas,
                        "asignado_ubits": asignado
                    }

                    try:
                        query = text("""
                            INSERT INTO capacitacion (
                                fecha, nombre_programa, tipo_programa, categoria, modalidad, proveedor, facilitador,
                                lugar, no_empleado, nombre_empleado, puesto, area, departamento, tipologia_puesto,
                                edad, empresa, duracion_dias, duracion_hrs_dia, horas_capacitadas, asignado_ubits
                            )
                            VALUES (
                                :fecha, :nombre_programa, :tipo_programa, :categoria, :modalidad, :proveedor, :facilitador,
                                :lugar, :no_empleado, :nombre_empleado, :puesto, :area, :departamento, :tipologia_puesto,
                                :edad, :empresa, :duracion_dias, :duracion_hrs_dia, :horas_capacitadas, :asignado_ubits
                            )
                        """)
                        conn.execute(query, insert_data)
                    except Exception as e:
                        st.error(f"❌ Error al guardar capacitación para {codigo}: {e}")

            st.success("✅ Registros guardados exitosamente para todos los empleados.")


# ---------------- PESTAÑA 5: VER REGISTROS ----------------
def ver_registros():
    st.title("📄 Registros Guardados")

    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT * FROM capacitacion"))
            df = pd.DataFrame(result.fetchall(), columns=result.keys())
        if df.empty:
            st.info("No hay registros aún.")
        else:
            st.dataframe(df)
    except Exception as e:
        st.error(f"❌ Error al obtener los registros: {e}")


# ---------------- NAVEGACIÓN ENTRE PASOS ----------------
def navegacion_botones(empleados_df):
    pasos = [
        menu_principal,
        mostrar_bienvenida,
        ingresar_codigo_empleado,
        lambda: verificar_empleado(empleados_df),
        lambda: formulario_capacitacion(empleados_df),
        ver_registros
    ]

    titulos = [" ", "Bienvenida", "Código", "Verificar", "Formulario", "Registros"]

    paso_actual = st.session_state.get("paso_actual", 0)
    paso_actual = max(0, min(paso_actual, len(pasos) - 1))

    st.markdown(f"### {titulos[paso_actual]}")
    pasos[paso_actual]()

    col1, col2, col3 = st.columns([5, 2, 2])
    with col2:
        if st.button("⬅️ Anterior") and paso_actual > 0:
            st.session_state["paso_actual"] = paso_actual - 1
            st.rerun()
    with col3:
        if st.button("➡️ Siguiente") and paso_actual < len(pasos) - 1:
            st.session_state["paso_actual"] = paso_actual + 1
            st.rerun()

# ---------------- EJECUCIÓN PRINCIPAL ----------------
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False
if "paso_actual" not in st.session_state:
    st.session_state["paso_actual"] = 0

if not st.session_state["autenticado"]:
    login()
else:
    ruta_excel = r"Empleados_Ejemplo.xlsx"
    empleados_df = cargar_empleados_desde_excel(ruta_excel)

    if empleados_df.empty:
        st.warning("No se pudo cargar la base de empleados.")
    else:
        navegacion_botones(empleados_df)