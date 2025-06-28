import streamlit as st
import pandas as pd
from datetime import date
from supabase import create_client, Client
import numpy as np

# Reemplaza con tus valores reales
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]

supabase: Client = create_client(url, key)

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
        try:
            auth_response = supabase.auth.sign_in_with_password({
                "email": correo,
                "password": contraseña
            })

            session = auth_response.session
            user = auth_response.user

            if session and user:
                st.session_state["user"] = user
                st.session_state["autenticado"] = True
                st.success("✅ Inicio de sesión exitoso.")
                st.rerun()
            else:
                st.error("❌ No se pudo iniciar sesión. Verifica tu correo y contraseña.")
        except Exception as e:
            st.error(f"❌ Error al iniciar sesión: {e}")



#--------------------AGREGAR NUEVO USUARIO --------------
def registrar_usuario():
    st.title("📝 Registro de usuario")
    correo = st.text_input("Nuevo correo")
    contraseña = st.text_input("Nueva contraseña", type="password")
    if st.button("Registrarme"):
        try:
            res = supabase.auth.sign_up({
                "email": correo,
                "password": contraseña
            })
            st.success("✅ Usuario registrado. Verifica tu correo.")
        except Exception as e:
            st.error(f"❌ Error al registrarte: {e}")



# ---------------- PESTAÑA 1: INTRODUCCIÓN ----------------
def mostrar_bienvenida():
    st.title("🏠 Bienvenida")
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
            user = st.session_state.get("user")

            if not user or "id" not in user:
                st.error("⚠️ No hay usuario autenticado. Por favor, inicie sesión.")
                return

            for codigo in codigos:
                if codigo not in empleados_df.index:
                    continue

                datos = empleados_df.loc[codigo]

                nuevo = {
                    "Fecha": fecha.strftime("%Y/%m/%d"),
                    "Nombre Programa": nombre_programa,
                    "Tipo Programa": tipo_programa,
                    "Categoría": categoria,
                    "Modalidad": modalidad,
                    "Proveedor": proveedor,
                    "Facilitador": facilitador,
                    "Lugar": lugar,
                    "No. Empleado": codigo,
                    "Nombre Empleado": datos["Nombre"],
                    "Puesto": datos["Puesto"],
                    "Área": datos["Área"],
                    "Departamento": datos["Departamento"],
                    "Tipología Puesto": datos["Tipología Puesto"],
                    "Edad": datos["Edad"],
                    "Empresa": datos["Empresa"],
                    "Duración (Días)": duracion_dias,
                    "Duración (HRs/Día)": duracion_hrs_dia,
                    "Horas Capacitadas": horas_capacitadas,
                    "Asignado (Ubits)": asignado,
                    "user_id": user["id"] if isinstance(user, dict) else user.id  # Protección doble  # 👈 Esto es lo que se envía a Supabase
                }

                if "registros" not in st.session_state:
                    st.session_state["registros"] = []

                st.session_state["registros"].append(nuevo)

                try:
                    # Convertir tipos de datos antes de enviar
                    nuevo_convertido = {
                        k: int(v) if isinstance(v, (pd.Int64Dtype().type, np.int64)) else
                        float(v) if isinstance(v, (np.float64,)) else v
                        for k, v in nuevo.items()
                    }

                    session = supabase.auth.get_session()
                    user_id = session.user.id if session and session.user else None

                    st.write("🧾 Usuario autenticado:", supabase.auth.get_user())
                    supabase.table("capacitacion").insert(nuevo_convertido).execute()
                except Exception as e:
                    st.error(f"❌ Error al guardar en Supabase: {e}")

            st.success("✅ Registros guardados para todos los empleados.")


# ---------------- PESTAÑA 5: VER REGISTROS ----------------
def ver_registros():
    st.title("📄 Registros Guardados")
    if "registros" in st.session_state and st.session_state["registros"]:
        df_registros = pd.DataFrame(st.session_state["registros"])
        st.dataframe(df_registros)
    else:
        st.info("No hay registros disponibles.")

# ---------------- NAVEGACIÓN ENTRE PASOS ----------------
def navegacion_botones(empleados_df):
    pasos = [
        mostrar_bienvenida,
        ingresar_codigo_empleado,
        lambda: verificar_empleado(empleados_df),
        lambda: formulario_capacitacion(empleados_df),
        ver_registros
    ]

    titulos = ["Bienvenida", "Código", "Verificar", "Formulario", "Registros"]

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