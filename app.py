import os
import random
from datetime import date
import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, text

st.set_page_config(page_title="Red de Turismo Astronómico - PMV", page_icon="🔭", layout="wide")

DB_HOST = os.getenv("DB_HOST", "db")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_USER = os.getenv("DB_USER", "root")
DB_PASS = os.getenv("DB_PASSWORD", "rootpassword")
DB_NAME = os.getenv("DB_NAME", "turismo_astronomico")

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"

@st.cache_resource
def get_engine():
    return create_engine(DATABASE_URL, pool_pre_ping=True)

engine = get_engine()

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
    st.session_state.usuario = None
    st.session_state.rol = None
    st.session_state.nombre_persona = None

def autenticar_usuario(username, password):
    query = text("""
        SELECT u.nombre_usuario, r.nombre_rol, p.nombre_completo
        FROM Cuentas_usuarios u
        JOIN Personal p ON u.codigo_personal = p.codigo_personal
        JOIN Roles r ON p.codigo_rol = r.codigo_rol
        WHERE u.nombre_usuario = :usr AND u.contrasena = :pwd AND u.activo = 1 AND p.activo = 1
    """)
    with engine.connect() as conn:
        res = conn.execute(query, {"usr": username, "pwd": password}).fetchone()
    return res

if not st.session_state.autenticado:
    st.title("🔭 Sistema de Gestión — Red de Turismo Astronómico")
    st.subheader("Acceso al Producto Mínimo Viable (PMV)")
    col1, col2 = st.columns([1, 1])
    with col1:
        with st.form("login_form"):
            usr = st.text_input("Usuario", placeholder="admin o operador")
            pwd = st.text_input("Contraseña", type="password", placeholder="admin123 o oper123")
            submit = st.form_submit_button("Iniciar Sesión")
            if submit:
                user_row = autenticar_usuario(usr.strip(), pwd.strip())
                if user_row:
                    st.session_state.autenticado = True
                    st.session_state.usuario = user_row[0]
                    st.session_state.rol = user_row[1]
                    st.session_state.nombre_persona = user_row[2]
                    st.rerun()
                else:
                    st.error("Credenciales inválidas o cuenta inactiva.")
    with col2:
        st.info(
            "**Cuentas de prueba habilitadas:**\n"
            "- **Administrador:** `admin` / `admin123` (Acceso completo + CRUD maestros)\n"
            "- **Operador:** `operador` / `oper123` (Gestión de Reservas + Dashboard)"
        )
    st.stop()

st.sidebar.title("🔭 Turismo Astronómico")
st.sidebar.markdown(f"**Usuario:** {st.session_state.nombre_persona}")
st.sidebar.markdown(f"**Rol:** `{st.session_state.rol.upper()}`")

opciones_menu = ["📊 Dashboard Analítico", "📅 Gestión de Reservas"]
if st.session_state.rol == "admin":
    opciones_menu.append("⚙️ Administración (CRUD Maestros)")

pagina = st.sidebar.radio("Navegación", opciones_menu)

if st.sidebar.button("Cerrar Sesión"):
    st.session_state.autenticado = False
    st.session_state.usuario = None
    st.session_state.rol = None
    st.rerun()

if pagina == "📊 Dashboard Analítico":
    st.title("📊 Dashboard Analítico de Turismo Astronómico")

    centros_df = pd.read_sql("SELECT codigo_centro, nombre FROM Centro_astronomico WHERE activo = 1", engine)
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        f_inicio = st.date_input("Fecha inicio", value=date(2025, 1, 1))
    with col_f2:
        f_fin = st.date_input("Fecha término", value=date(2026, 12, 31))
    with col_f3:
        opciones_centros = ["Todos"] + centros_df["nombre"].tolist()
        centro_sel = st.selectbox("Centro Astronómico", opciones_centros)

    filtro_centro_sql = ""
    params = {"fi": f_inicio, "ff": f_fin}
    if centro_sel != "Todos":
        filtro_centro_sql = " AND c.nombre = :cnom "
        params["cnom"] = centro_sel

    c1, c2 = st.columns(2)

    with c1:
        st.subheader("1. Asistentes Efectivos por Centro")
        q1 = text(f"""
            SELECT c.nombre AS Centro, COUNT(r.codigo_reserva) AS Asistentes
            FROM Centro_astronomico c
            JOIN Actividad a ON c.codigo_centro = a.codigo_centro
            JOIN Reservas r ON a.codigo_actividad = r.codigo_actividad
            WHERE r.asistencia_efectiva = 1 AND a.fecha BETWEEN :fi AND :ff {filtro_centro_sql}
            GROUP BY c.nombre ORDER BY Asistentes DESC
        """)
        df1 = pd.read_sql(q1, engine, params=params)
        if not df1.empty:
            st.bar_chart(df1.set_index("Centro")["Asistentes"])
        else:
            st.warning("Sin datos para el filtro seleccionado.")

    with c2:
        st.subheader("2. Observaciones por Tipo de Fenómeno")
        q2 = text(f"""
            SELECT
                CASE
                    WHEN fs.codigo_fenomeno IS NOT NULL THEN 'Solar'
                    WHEN fl.codigo_fenomeno IS NOT NULL THEN 'Lunar'
                    WHEN fep.codigo_fenomeno IS NOT NULL THEN 'Espacio Profundo'
                    ELSE 'Otro'
                END AS Categoria,
                COUNT(*) AS Observaciones
            FROM Actividad a
            JOIN Centro_astronomico c ON a.codigo_centro = c.codigo_centro
            JOIN Actividad_fenomeno af ON a.codigo_actividad = af.codigo_actividad
            LEFT JOIN Fenomenos_solares fs ON af.codigo_fenomeno = fs.codigo_fenomeno
            LEFT JOIN Fenomenos_lunares fl ON af.codigo_fenomeno = fl.codigo_fenomeno
            LEFT JOIN Fenomenos_espacios_profundos fep ON af.codigo_fenomeno = fep.codigo_fenomeno
            WHERE a.fecha BETWEEN :fi AND :ff {filtro_centro_sql}
            GROUP BY Categoria
        """)
        df2 = pd.read_sql(q2, engine, params=params)
        if not df2.empty:
            st.bar_chart(df2.set_index("Categoria")["Observaciones"])
        else:
            st.warning("Sin observaciones registradas en el período.")

    c3, c4 = st.columns(2)

    with c3:
        st.subheader("3. Evaluación Promedio por Centro")
        q3 = text(f"""
            SELECT c.nombre AS Centro, ROUND(AVG(e.puntuacion_general), 2) AS Calificacion_Promedio
            FROM Evaluaciones e
            JOIN Actividad a ON e.codigo_actividad = a.codigo_actividad
            JOIN Centro_astronomico c ON a.codigo_centro = c.codigo_centro
            WHERE a.fecha BETWEEN :fi AND :ff {filtro_centro_sql}
            GROUP BY c.nombre
        """)
        df3 = pd.read_sql(q3, engine, params=params)
        if not df3.empty:
            st.bar_chart(df3.set_index("Centro")["Calificacion_Promedio"])
        else:
            st.warning("Sin evaluaciones en el rango seleccionado.")

    with c4:
        st.subheader("4. Ingresos Efectivos por Modalidad (Indicador Equipo)")
        q4 = text(f"""
            SELECT a.modalidad AS Modalidad, SUM(a.precio) AS Ingresos_CLP
            FROM Actividad a
            JOIN Centro_astronomico c ON a.codigo_centro = c.codigo_centro
            JOIN Reservas r ON a.codigo_actividad = r.codigo_actividad
            WHERE r.asistencia_efectiva = 1 AND a.fecha BETWEEN :fi AND :ff {filtro_centro_sql}
            GROUP BY a.modalidad ORDER BY Ingresos_CLP DESC
        """)
        df4 = pd.read_sql(q4, engine, params=params)
        if not df4.empty:
            st.bar_chart(df4.set_index("Modalidad")["Ingresos_CLP"])
        else:
            st.warning("Sin ingresos registrados en el filtro.")

elif pagina == "📅 Gestión de Reservas":
    st.title("📅 Gestión Transaccional de Reservas")

    df_act = pd.read_sql("""
        SELECT a.codigo_actividad, CONCAT(a.codigo_actividad, ' | ', c.nombre, ' | ', a.fecha, ' (', a.modalidad, ')') AS etiqueta
        FROM Actividad a
        JOIN Centro_astronomico c ON a.codigo_centro = c.codigo_centro
        ORDER BY a.fecha DESC
    """, engine)

    df_vis = pd.read_sql("""
        SELECT codigo_visitante, CONCAT(codigo_visitante, ' - ', nombre, ' ', apellido, ' (', pais_origen, ')') AS etiqueta
        FROM Visitantes ORDER BY codigo_visitante
    """, engine)

    with st.form("form_nueva_reserva"):
        st.subheader("Registrar Nueva Reserva")
        col1, col2 = st.columns(2)
        with col1:
            act_sel = st.selectbox("Seleccione Actividad", df_act["etiqueta"].tolist())
            vis_sel = st.selectbox("Seleccione Visitante", df_vis["etiqueta"].tolist())
        with col2:
            estado_sel = st.selectbox("Estado Inicial", ["Confirmada", "Completada"])
            asistencia_sel = st.checkbox("Asistencia Efectiva Confirmada")
            obs_txt = st.text_input("Observaciones (opcional)")

        guardar_res = st.form_submit_button("Guardar Reserva")
        if guardar_res:
            cod_act = act_sel.split(" | ")[0]
            cod_vis = vis_sel.split(" - ")[0]
            cod_res = f"RE{random.randint(1000, 9999)}"
            try:
                with engine.begin() as conn:
                    conn.execute(text("""
                        INSERT INTO Reservas (codigo_reserva, codigo_actividad, codigo_visitante, fecha_reserva, asistencia_efectiva, observaciones, estado)
                        VALUES (:r, :a, :v, :f, :asist, :obs, :est)
                    """), {
                        "r": cod_res,
                        "a": cod_act,
                        "v": cod_vis,
                        "f": date.today(),
                        "asist": 1 if asistencia_sel else 0,
                        "obs": obs_txt,
                        "est": estado_sel
                    })
                st.success(f"Reserva {cod_res} registrada correctamente.")
            except Exception as ex:
                st.error(f"No se pudo registrar la reserva (verifique duplicados): {ex}")

    st.subheader("Últimas Reservas Registradas")
    df_ultimas = pd.read_sql("""
        SELECT codigo_reserva, codigo_actividad, codigo_visitante, fecha_reserva, asistencia_efectiva, observaciones, estado
        FROM Reservas ORDER BY fecha_reserva DESC, codigo_reserva DESC LIMIT 15
    """, engine)
    st.dataframe(df_ultimas, use_container_width=True)

elif pagina == "⚙️ Administración (CRUD Maestros)":
    st.title("⚙️ Administración de Tablas Maestras (Rol Administrador)")
    tab1, tab2 = st.tabs(["🏛️ Centros Astronómicos", "🌌 Fenómenos Astronómicos (Borrado Lógico)"])

    with tab1:
        st.subheader("Listado de Centros Astronómicos")
        df_centros = pd.read_sql("SELECT * FROM Centro_astronomico", engine)
        st.dataframe(df_centros, use_container_width=True)

        with st.form("form_nuevo_centro"):
            st.markdown("**Crear Nuevo Centro Astronómico**")
            c_cod = st.text_input("Código Centro (ej. C06)")
            c_nom = st.text_input("Nombre del Centro")
            c_ubi = st.text_input("Ubicación")
            c_cap = st.number_input("Capacidad Máxima", min_value=10, max_value=1000, value=120)
            if st.form_submit_button("Crear Centro"):
                try:
                    with engine.begin() as conn:
                        conn.execute(text("""
                            INSERT INTO Centro_astronomico (codigo_centro, nombre, ubicacion, capacidad_maxima, activo)
                            VALUES (:c, :n, :u, :cap, 1)
                        """), {"c": c_cod.strip(), "n": c_nom.strip(), "u": c_ubi.strip(), "cap": int(c_cap)})
                    st.success("Centro astronómico creado exitosamente.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error al crear centro: {e}")

    with tab2:
        st.subheader("Catálogo de Fenómenos Astronómicos")
        df_fen = pd.read_sql("SELECT * FROM Fenomenos", engine)
        st.dataframe(df_fen, use_container_width=True)

        col_f_a, col_f_b = st.columns(2)
        with col_f_a:
            with st.form("form_nuevo_fen"):
                st.markdown("**Registrar Nuevo Fenómeno**")
                f_cod = st.text_input("Código Fenómeno (ej. F009)")
                f_nom = st.text_input("Nombre del Fenómeno")
                f_desc = st.text_input("Descripción")
                f_vis = st.selectbox("Visibilidad Estimada", ["Alta", "Media", "Baja"])
                if st.form_submit_button("Guardar Fenómeno"):
                    try:
                        with engine.begin() as conn:
                            conn.execute(text("""
                                INSERT INTO Fenomenos (codigo_fenomeno, nombre_fenomeno, descripcion, visibilidad_estimada, activo)
                                VALUES (:c, :n, :d, :v, 1)
                            """), {"c": f_cod.strip(), "n": f_nom.strip(), "d": f_desc.strip(), "v": f_vis})
                        st.success("Fenómeno agregado.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")

        with col_f_b:
            with st.form("form_desactivar_fen"):
                st.markdown("**Desactivación Lógica de Fenómeno**")
                fen_activos = df_fen[df_fen["activo"] == 1]["codigo_fenomeno"].tolist()
                fen_sel = st.selectbox("Seleccione código activo a desactivar", fen_activos)
                if st.form_submit_button("Desactivar (activo = 0)"):
                    with engine.begin() as conn:
                        conn.execute(text("UPDATE Fenomenos SET activo = 0 WHERE codigo_fenomeno = :c"), {"c": fen_sel})
                    st.warning(f"Fenómeno {fen_sel} desactivado lógicamente.")
                    st.rerun()
