# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import os
import math
from datetime import datetime, date
import io

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    REPORTLAB_DISPONIBLE = True
except ImportError:
    REPORTLAB_DISPONIBLE = False

# --- CONFIGURACIÓN Y RUTAS ---
BASE_DIR = os.getcwd()
EQUIPOS_PATH = os.path.join(BASE_DIR, "equipos.csv")
PATRONES_PATH = os.path.join(BASE_DIR, "patrones_inventario.csv")
HISTORIAL_PATH = os.path.join(BASE_DIR, "historial_metrologia.csv")

def inicializar_csvs():
    try:
        if not os.path.exists(EQUIPOS_PATH) or os.path.getsize(EQUIPOS_PATH) == 0:
            df_init = pd.DataFrame([
                {"serial": "MAN-001", "descripcion": "Manometro digital de presion", "modelo": "PG-100", "marca": "Wika", "estado": "Activo", "frecuencia_meses": 6, "ultima_calibracion": "2025-06-01"},
                {"serial": "BAL-005", "descripcion": "Balanza analitica de precision", "modelo": "ME204", "marca": "Mettler Toledo", "estado": "Calibracion Pendiente", "frecuencia_meses": 12, "ultima_calibracion": "2025-01-15"},
                {"serial": "TER-010", "descripcion": "Termohigrometro digital", "modelo": "TH-20", "marca": "Testo", "estado": "En Mantenimiento", "frecuencia_meses": 6, "ultima_calibracion": "2025-08-10"},
                {"serial": "MD-YC-102-2243", "descripcion": "CALIBRADOR CON RELOJ", "modelo": "505-742-51J", "marca": "MITUTOYO", "estado": "Activo", "frecuencia_meses": 12, "ultima_calibracion": "2025-05-20"}
            ])
            df_init.to_csv(EQUIPOS_PATH, index=False, encoding='utf-8-sig')
    except Exception:
        pass

    try:
        if not os.path.exists(PATRONES_PATH) or os.path.getsize(PATRONES_PATH) == 0:
            df_pat_init = pd.DataFrame([
                {"codigo_patron": "CC-YJ-102-259", "descripcion": "JUEGO DE BLOQUES PATRÓN", "marca": "MITUTOYO", "emp": 0.00002, "vencimiento": "2027-05-20"},
                {"codigo_patron": "CC-M-005-001", "descripcion": "JUEGO DE PESAS CLASE M1", "marca": "RICE LAKE", "emp": 0.00010, "vencimiento": "2027-10-15"},
                {"codigo_patron": "CC-P-010-099", "descripcion": "MANÓMETRO PATRÓN DIGITAL", "marca": "WIKA", "emp": 0.05000, "vencimiento": "2026-12-31"},
                {"codigo_patron": "CC-GEN-001", "descripcion": "PATRÓN GENERAL DE REFERENCIA", "marca": "ESTÁNDAR", "emp": 0.00010, "vencimiento": "2027-01-01"}
            ])
            df_pat_init.to_csv(PATRONES_PATH, index=False, encoding='utf-8-sig')
    except Exception:
        pass
    
    try:
        if not os.path.exists(HISTORIAL_PATH) or os.path.getsize(HISTORIAL_PATH) == 0:
            df_h_init = pd.DataFrame(columns=[
                "serial", "fecha", "magnitud", "valor_nominal", "valor_real", "error", 
                "emp", "incertidumbre_combinada", "factor_k", "incertidumbre_expandida", "conformidad",
                "num_certificado", "ubicacion", "departamento", "temperatura", "humedad",
                "patron_desc", "patron_marca", "patron_serial", "tecnico", "aprobado_por",
                "unidad_medida", "observaciones", "relacion_ep_u", "repetibilidad", "timestamp_auditoria"
            ])
            df_h_init.to_csv(HISTORIAL_PATH, index=False, encoding='utf-8-sig')
    except Exception:
        pass

inicializar_csvs()

def leer_csv(path, columnas):
    try:
        if os.path.exists(path) and os.path.getsize(path) > 0:
            df = pd.read_csv(path)
            for col in columnas:
                if col not in df.columns:
                    df[col] = ""
            return df
        else:
            inicializar_csvs()
            return pd.read_csv(path)
    except Exception:
        return pd.DataFrame(columns=columnas)

def guardar_csv(df, path):
    try:
        df.to_csv(path, index=False, encoding='utf-8-sig')
    except Exception:
        pass

COLUMNAS_EQUIPOS = ["serial", "descripcion", "modelo", "marca", "estado", "frecuencia_meses", "ultima_calibracion"]
COLUMNAS_PATRONES = ["codigo_patron", "descripcion", "marca", "emp", "vencimiento"]
COLUMNAS_HISTORIAL = [
    "serial", "fecha", "magnitud", "valor_nominal", "valor_real", "error", 
    "emp", "incertidumbre_combinada", "factor_k", "incertidumbre_expandida", "conformidad",
    "num_certificado", "ubicacion", "departamento", "temperatura", "humedad",
    "patron_desc", "patron_marca", "patron_serial", "tecnico", "aprobado_por",
    "unidad_medida", "observaciones", "relacion_ep_u", "repetibilidad", "timestamp_auditoria"
]

st.set_page_config(page_title="SCE Venvidrio - Sistema Industrial Avanzado", layout="wide")

# --- DISEÑO TEMA OSCURO CORPORATIVO (SALA DE CONTROL) ---
st.markdown("""
    <style>
    .stApp {
        background-color: #0f172a !important;
        color: #f1f5f9 !important;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }
    h1, h2, h3, h4, h5, h6, 
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: #ffffff !important;
        font-weight: 600 !important;
    }
    p, span, label, .stText, .stMarkdown, .stSelectbox label {
        color: #cbd5e1 !important;
    }
    div[data-testid="stVerticalBlock"] > div > div.stContainer, div.stExpander {
        background-color: #1e293b !important;
        border: 1px solid #334155 !important;
        border-radius: 10px !important;
        padding: 1.2rem !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2) !important;
    }
    div[data-testid="stMetric"] {
        background-color: #1e293b !important;
        border: 1px solid #334155 !important;
        padding: 15px 20px !important;
        border-radius: 10px !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2) !important;
    }
    div[data-testid="stMetric"] label {
        color: #94a3b8 !important;
        font-weight: 500 !important;
    }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-weight: 700 !important;
    }
    .stButton>button {
        background-color: #2563eb !important;
        color: white !important;
        border-radius: 6px !important;
        padding: 0.5rem 1rem !important;
        font-weight: 500 !important;
        border: none !important;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1) !important;
        transition: all 0.2s ease-in-out;
    }
    .stButton>button:hover {
        background-color: #1d4ed8 !important;
        box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.4) !important;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #1e293b;
        padding: 6px;
        border-radius: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 40px;
        background-color: #0f172a;
        border-radius: 6px;
        color: #94a3b8 !important;
        font-weight: 500;
        border: 1px solid #334155;
    }
    .stTabs [aria-selected="true"] {
        background-color: #2563eb !important;
        color: white !important;
        border: none !important;
    }
    </style>
""", unsafe_allow_html=True)

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.markdown("<br><br>", unsafe_allow_html=True)
    col_l1, col_l2, col_l3 = st.columns([1, 1.5, 1])
    with col_l2:
        st.markdown("### 🔒 Acceso Restringido")
        st.markdown("Sistema de Control de Calibración - Venvidrio")
        
        with st.form("login_form"):
            password_input = st.text_input("Contraseña Corporativa", type="password")
            submit_login = st.form_submit_button("Iniciar Sesión", use_container_width=True)
            
        if submit_login:
            if password_input == "metrologia2026":
                st.session_state.autenticado = True
                st.success("Acceso concedido.")
                st.rerun()
            else:
                st.error("Contraseña incorrecta.")
    st.stop()

st.markdown("## Sistema de Control de Calibración (SCE)")
st.markdown("<p style='color: #94a3b8 !important; margin-top: -10px;'>Plataforma metrológica industrial con trazabilidad GUM y control normativo ISO/IEC 17025.</p>", unsafe_allow_html=True)
st.markdown("---")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Dashboard", 
    "📋 Inventario", 
    "🧰 Patrones",
    "⚙️ Calibración y GUM", 
    "📈 Historial y Reportes"
])

# --- TAB 1: DASHBOARD Y ALERTAS ---
with tab1:
    st.subheader("Estado General de Instrumentos en Planta")
    df_e = leer_csv(EQUIPOS_PATH, COLUMNAS_EQUIPOS)
    if not df_e.empty:
        hoy = date.today()
        vencidos, por_vencer, al_dia = 0, 0, 0
        estados_lista = []
        for index, row in df_e.iterrows():
            f_ult_str = row.get("ultima_calibracion", str(hoy))
            try:
                f_ult = datetime.strptime(str(f_ult_str)[:10], "%Y-%m-%d").date()
                freq = int(row.get("frecuencia_meses", 12))
                meses_totales = f_ult.month + freq
                anio_prox = f_ult.year + (meses_totales - 1) // 12
                mes_prox = (meses_totales - 1) % 12 + 1
                f_prox = date(anio_prox, mes_prox, min(f_ult.day, 28))
                dias_restantes = (f_prox - hoy).days
                if dias_restantes < 0:
                    estado_semaforo = "🔴 VENCIDO"
                    vencidos += 1
                elif dias_restantes <= 30:
                    estado_semaforo = "🟡 PRÓXIMO A VENCER"
                    por_vencer += 1
                else:
                    estado_semaforo = "🟢 VIGENTE"
                    al_dia += 1
            except Exception:
                estado_semaforo = "⚪ INDETERMINADO"
                al_dia += 1
            estados_lista.append(estado_semaforo)
        df_e['estado_metrologico'] = estados_lista
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Equipos Vigentes", al_dia)
        c2.metric("Próximos a Vencer (<= 30 días)", por_vencer)
        c3.metric("Calibración Vencida", vencidos)
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.dataframe(df_e[['serial', 'descripcion', 'marca', 'frecuencia_meses', 'ultima_calibracion', 'estado_metrologico']], use_container_width=True)
    else:
        st.info("No hay registros en el inventario.")

# --- TAB 2: INVENTARIO DE EQUIPOS ---
with tab2:
    st.subheader("Inventario y Control de Instrumentos")
    df_e = leer_csv(EQUIPOS_PATH, COLUMNAS_EQUIPOS)
    with st.expander("➕ Registrar o Actualizar Instrumento"):
        with st.form("form_nuevo_equipo"):
            col_n1, col_n2, col_n3 = st.columns(3)
            with col_n1:
                n_serial = st.text_input("Serial / Código JDE")
                n_desc = st.text_input("Descripción del Instrumento")
            with col_n2:
                n_modelo = st.text_input("Modelo")
                n_marca = st.text_input("Marca")
            with col_n3:
                n_estado = st.selectbox("Estado Operativo", ["Activo", "Calibracion Pendiente", "En Mantenimiento", "Fuera de Servicio"])
                n_freq = st.selectbox("Frecuencia de Calibración (Meses)", [1, 3, 6, 12, 18, 24, 36])
            if st.form_submit_button("Guardar Instrumento"):
                nuevo_eq = pd.DataFrame([{
                    "serial": n_serial, "descripcion": n_desc, "modelo": n_modelo, 
                    "marca": n_marca, "estado": n_estado, "frecuencia_meses": int(n_freq),
                    "ultima_calibracion": str(date.today())
                }])
                if n_serial in df_e['serial'].values:
                    df_e = df_e[df_e['serial'] != n_serial]
                guardar_csv(pd.concat([df_e, nuevo_eq], ignore_index=True), EQUIPOS_PATH)
                st.success("¡Instrumento guardado exitosamente!")
                st.rerun()
                
    csv_inventario = df_e.to_csv(index=False).encode('utf-8-sig')
    st.download_button("📥 Descargar Base de Inventario (.csv)", data=csv_inventario, file_name="Inventario_SCE_Venvidrio.csv", mime="text/csv")
    st.markdown("<br>", unsafe_allow_html=True)
    st.dataframe(df_e, use_container_width=True)
    
    # --- AQUÍ PEGABAS EL NUEVO BLOQUE PARA TAB 2 ---
    st.markdown("---")
    st.subheader("🗑️ Gestión de Eliminación")
    with st.expander("¿Deseas eliminar un equipo del inventario?"):
        serial_a_borrar = st.selectbox("Selecciona el Serial a eliminar", df_e['serial'].tolist())
        if st.button("Eliminar Registro Permanentemente", type="primary"):
            df_e = df_e[df_e['serial'] != serial_a_borrar]
            guardar_csv(df_e, EQUIPOS_PATH)
            st.success(f"El equipo {serial_a_borrar} ha sido eliminado.")
            st.rerun()

# --- TAB 3: GESTIÓN MANUAL DE PATRONES Y ALERTAS ---
with tab3:
    st.subheader("Control, Ingreso Manual y Vigencia de Patrones de Referencia")
    df_p = leer_csv(PATRONES_PATH, COLUMNAS_PATRONES)
    
    with st.expander("➕ Ingresar Manualmente Nuevo Patrón de Referencia"):
        with st.form("form_patron_manual"):
            cp1, cp2, cp3 = st.columns(3)
            with cp1:
                p_cod = st.text_input("Código del Patrón (Ej. CC-XX-001)")
                p_desc = st.text_input("Nombre / Descripción del Patrón")
            with cp2:
                p_marca = st.text_input("Marca del Patrón")
                p_emp = st.number_input("EMP (Error Máx. Permisible del Patrón)", value=0.00002, format="%.5f")
            with cp3:
                p_venc = st.date_input("Fecha de Vencimiento del Certificado", value=date.today())
            if st.form_submit_button("Guardar Patrón en Base de Datos"):
                if p_cod.strip() == "" or p_desc.strip() == "":
                    st.error("El código y la descripción del patrón no pueden estar vacíos.")
                else:
                    nuevo_pat = pd.DataFrame([{
                        "codigo_patron": p_cod.strip(), 
                        "descripcion": p_desc.strip().upper(), 
                        "marca": p_marca.strip().upper(), 
                        "emp": p_emp, 
                        "vencimiento": str(p_venc)
                    }])
                    if p_cod in df_p['codigo_patron'].values:
                        df_p = df_p[df_p['codigo_patron'] != p_cod]
                    guardar_csv(pd.concat([df_p, nuevo_pat], ignore_index=True), PATRONES_PATH)
                    st.success("¡Patrón registrado con éxito y base de datos actualizada!")
                    st.rerun()

    if not df_p.empty:
        hoy = date.today()
        estados_pat = []
        for _, row in df_p.iterrows():
            f_venc_str = str(row.get("vencimiento", str(hoy)))[:10]
            try:
                f_venc = datetime.strptime(f_venc_str, "%Y-%m-%d").date()
                dias_restantes = (f_venc - hoy).days
                if dias_restantes < 0:
                    estados_pat.append("🔴 VENCIDO")
                elif dias_restantes <= 30:
                    estados_pat.append("🟡 PRÓXIMO A VENCER")
                else:
                    estados_pat.append("🟢 VIGENTE")
            except Exception:
                estados_pat.append("⚪ INDETERMINADO")
        df_p['estado_vigencia'] = estados_pat

    csv_patrones = df_p.to_csv(index=False).encode('utf-8-sig')
    st.download_button("📥 Descargar Base de Patrones (.csv)", data=csv_patrones, file_name="Patrones_SCE_Venvidrio.csv", mime="text/csv")
    st.markdown("<br>", unsafe_allow_html=True)
    st.dataframe(df_p, use_container_width=True)
    
    # ... (debajo de tu código existente en TAB 3) ...
    st.markdown("---")
    st.subheader("🗑️ Gestión de Eliminación de Patrones")
    with st.expander("¿Deseas eliminar un patrón del sistema?"):
        patron_a_borrar = st.selectbox("Selecciona el Código del Patrón a eliminar", df_p['codigo_patron'].tolist())
        if st.button("Eliminar Patrón", type="primary"):
            df_p = df_p[df_p['codigo_patron'] != patron_a_borrar]
            guardar_csv(df_p, PATRONES_PATH)
            st.success(f"El patrón {patron_a_borrar} ha sido eliminado.")
            st.rerun()

# --- TAB 4: CALIBRACIÓN Y GUM ---
with tab4:
    df_e = leer_csv(EQUIPOS_PATH, COLUMNAS_EQUIPOS)
    df_p = leer_csv(PATRONES_PATH, COLUMNAS_PATRONES)
    
    if df_e.empty:
        st.warning("Debe registrar al menos un equipo en la pestaña de Inventario.")
    elif df_p.empty:
        st.warning("Debe registrar al menos un patrón en la pestaña de Patrones antes de calibrar.")
    else:
        st.subheader("Calibración Interna, Selección de Patrón y Cálculo GUM")
        col_h1, col_h2, col_h3, col_h4 = st.columns(4)
        with col_h1:
            df_e['label'] = df_e['serial'].astype(str) + " - " + df_e['descripcion'].astype(str)
            selected_eq = st.selectbox("Seleccionar Equipo", df_e['label'])
            serial = selected_eq.split(' - ')[0]
            num_certificado = st.text_input("Nro de Certificado / Registro", value="YC-2026-0100")
        with col_h2:
            fecha_cal = st.date_input("Fecha de Calibración", value=datetime.now())
            prox_cal = st.date_input("Próxima Calibración", value=datetime.now())
        with col_h3:
            # CAMBIO: Ubicación ingresada manualmente mediante campo de texto
            ubicacion = st.text_input("Ubicación en Planta", value="LÍNEA DE PRODUCCIÓN").upper()
            departamento = st.text_input("Departamento", value="CONTROL DE CALIDAD")
        with col_h4:
            temperatura = st.number_input("Temperatura (°C)", value=20.00, format="%.2f")
            humedad = st.number_input("Humedad Relativa (%)", value=65.00, format="%.2f")
            higrometro = st.text_input("Higrómetro Patrón", value="CC-YH-102-2237")
            repetibilidad = st.number_input("Repetibilidad", value=0.0000, format="%.4f")

        st.markdown("---")
        eq_info = df_e[df_e['serial'] == serial].iloc[0]

        sub_tab1, sub_tab2, sub_tab3 = st.tabs([
            "📌 Ficha Técnica y Selección de Patrón", 
            "📋 Inspección Visual", 
            "📊 Mediciones y GUM Automático"
        ])
        
        with sub_tab1:
            col_eq, col_pat = st.columns(2)
            with col_eq:
                st.markdown("#### Instrumento Bajo Prueba")
                st.text_input("Serial", value=serial, disabled=True)
                st.text_input("Descripción", value=eq_info['descripcion'], disabled=True)
                emp_eq = st.number_input("Error Máx. Permisible (EMP) del Equipo", value=0.00100, format="%.5f")
            
            with col_pat:
                st.markdown("#### Selección Manual de Patrón Registrado")
                df_p['label_patron'] = df_p['codigo_patron'].astype(str) + " - " + df_p['descripcion'].astype(str)
                selected_pat_label = st.selectbox("Seleccionar Patrón desde la Base de Datos", df_p['label_patron'])
                
                patron_sel = df_p[df_p['label_patron'] == selected_pat_label].iloc[0]
                patron_codigo = patron_sel['codigo_patron']
                patron_nombre = patron_sel['descripcion']
                patron_marca = patron_sel['marca']
                patron_emp = float(patron_sel['emp'])
                patron_vencimiento = str(patron_sel['vencimiento'])

                try:
                    venc_patron_dt = datetime.strptime(patron_vencimiento[:10], "%Y-%m-%d").date()
                    patron_vencido = venc_patron_dt < date.today()
                except Exception:
                    patron_vencido = False

                if patron_vencido:
                    st.error(f"⚠️ ATENCIÓN: El patrón seleccionado ({patron_codigo}) está VENCIDO (Venció el: {patron_vencimiento}).")
                else:
                    st.success(f"✅ Patrón vigente (Vence el: {patron_vencimiento} | EMP: {patron_emp})")

        with sub_tab2:
            col_p1, col_p2 = st.columns(2)
            with col_p1:
                inspeccion_visual = st.text_area("Inspección Visual y Mecánica", value="BUEN ESTADO / OPERATIVO")
            with col_p2:
                observaciones = st.text_area("Observaciones Generales", value="DENTRO DE LOS LÍMITES PERMISIBLES")

        with sub_tab3:
            st.markdown("#### Adquisición de Lecturas y Evaluación GUM")
            unidad_medida = st.selectbox("Unidad de Medida", ["in", "mm", "psi", "kg", "°C"])
            val_nom_ing = st.number_input("Valor Nominal de Referencia", value=2.0000000, format="%.7f")
            
            c_l1, c_l2, c_l3, c_l4 = st.columns(4)
            with c_l1:
                lec1 = st.number_input("Lectura 1", value=2.0000500, format="%.7f")
            with c_l2:
                lec2 = st.number_input("Lectura 2", value=2.0000400, format="%.7f")
            with c_l3:
                lec3 = st.number_input("Lectura 3", value=2.0000600, format="%.7f")
            with c_l4:
                lec4 = st.number_input("Lectura 4", value=2.0000500, format="%.7f")
            
            resolucion_equipo = st.number_input("Resolución del Instrumento", value=0.0001000, format="%.7f")
            
            lecturas = [lec1, lec2, lec3, lec4]
            n = len(lecturas)
            lectura_promedio = sum(lecturas) / n
            error_calculado = lectura_promedio - val_nom_ing

            for i, l in enumerate(lecturas, 1):
                if abs(l - val_nom_ing) > emp_eq:
                    st.warning(f"⚠️ Alerta: Lectura {i} ({l}) supera el EMP configurado.")

            if n > 1:
                varianza = sum((x - lectura_promedio) ** 2 for x in lecturas) / (n - 1)
                s_media = math.sqrt(varianza / n)
                repetibilidad_calculada = math.sqrt(varianza)
            else:
                s_media = 0.0
                repetibilidad_calculada = 0.0
            
            u_resolucion = resolucion_equipo / math.sqrt(12)
            u_patron = patron_emp / 3.0
            incertidumbre_combinada = math.sqrt(s_media**2 + u_resolucion**2 + u_patron**2)
            factor_k = 2.0
            incertidumbre_exp = incertidumbre_combinada * factor_k
            relacion_ep_u = emp_eq / incertidumbre_exp if incertidumbre_exp > 0 else 0.0
            
            st.markdown("<br>", unsafe_allow_html=True)
            st.info(f"**Promedio:** {lectura_promedio:.7f} {unidad_medida} | **Error:** {error_calculado:.7f} {unidad_medida}")
            st.warning(f"📊 **Repetibilidad (Desviación Estándar):** {repetibilidad_calculada:.7f} {unidad_medida}")
            st.success(f"**Incertidumbre Combinada (u_c):** {incertidumbre_combinada:.10f} | **Incertidumbre Expandida (U, k=2):** {incertidumbre_exp:.10f}")

        st.markdown("---")
        st.markdown("#### ✍️ Firmas y Auditoría")
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            tecnico_calibracion = st.text_input("Realizado por (Técnico Metrólogo)", value="PETIT CAMPOS ROBERT JOSE")
        with col_f2:
            aprobado_por = st.text_input("Aprobado por (Supervisor de Calidad)", value="Gerencia de Calidad Venvidrio")

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Guardar Calibración y Emitir Veredicto", type="primary", use_container_width=True):
            conf = "CONFORME" if abs(error_calculado) <= emp_eq else "NO CONFORME"
            timestamp_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            nuevo = pd.DataFrame([{
                "serial": serial, "fecha": str(fecha_cal), "magnitud": "Metrología Dimensional / General",
                "valor_nominal": val_nom_ing, "valor_real": lectura_promedio, "error": error_calculado, 
                "emp": emp_eq, "incertidumbre_combinada": incertidumbre_combinada, "factor_k": factor_k,
                "incertidumbre_expandida": incertidumbre_exp, "conformidad": conf, "num_certificado": num_certificado,
                "ubicacion": ubicacion, "departamento": departamento, "temperatura": temperatura, "humedad": humedad,
                "patron_desc": patron_nombre, "patron_marca": patron_marca, "patron_serial": patron_codigo,
                "tecnico": tecnico_calibracion, "aprobado_por": aprobado_por, "unidad_medida": unidad_medida,
                "observaciones": observaciones, "relacion_ep_u": relacion_ep_u, "repetibilidad": repetibilidad_calculada,
                "timestamp_auditoria": timestamp_actual
            }])
            
            df_h = leer_csv(HISTORIAL_PATH, COLUMNAS_HISTORIAL)
            guardar_csv(pd.concat([df_h, nuevo], ignore_index=True), HISTORIAL_PATH)
            
            df_e.loc[df_e['serial'] == serial, 'ultima_calibracion'] = str(fecha_cal)
            guardar_csv(df_e[['serial', 'descripcion', 'modelo', 'marca', 'estado', 'frecuencia_meses', 'ultima_calibracion']], EQUIPOS_PATH)
            
            st.success(f"¡Calibración registrada y auditada con éxito bajo el certificado {num_certificado}!")

# --- TAB 5: HISTORIAL, TENDENCIAS E INFORMES ---
with tab5:
    st.subheader("Historial de Certificados, Tendencias y Reportes PDF")
    df_h = leer_csv(HISTORIAL_PATH, COLUMNAS_HISTORIAL)
    df_e = leer_csv(EQUIPOS_PATH, COLUMNAS_EQUIPOS)
    
    if not df_h.empty:
        csv_historial = df_h.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📊 Descargar Historial Global con Auditoría (.csv)", data=csv_historial, file_name="Historial_Calibraciones_SCE.csv", mime="text/csv")
        st.markdown("<br>", unsafe_allow_html=True)
        
        serial_filtro = st.selectbox("Seleccionar Serial para Auditoría o Informe", df_h['serial'].unique())
        df_eq = df_h[df_h['serial'] == serial_filtro]
        st.dataframe(df_eq, use_container_width=True)
        
        if len(df_eq) > 1:
            st.markdown("#### 📈 Gráfico de Tendencia Histórica de Errores")
            df_tendencia = df_eq[['fecha', 'error']].copy()
            df_tendencia['fecha'] = pd.to_datetime(df_tendencia['fecha'])
            df_tendencia = df_tendencia.sort_values('fecha').set_index('fecha')
            st.line_chart(df_tendencia['error'])
        
        if REPORTLAB_DISPONIBLE:
            def header_footer(canvas, doc):
                canvas.saveState()
                canvas.drawImage("logo_venvidrio.png", 36, 745, width=120, height=50, preserveAspectRatio=True, mask='auto')
                canvas.setFont("Helvetica-Bold", 10)
                canvas.drawString(145, 760, "SISTEMA DE CONTROL DE CALIBRACIÓN (SCE) - VENVIDRIO")
                canvas.line(36, 750, 576, 750)
                canvas.setFont("Helvetica", 8)
                canvas.drawString(36, 25, "Norma ISO/IEC 17025 - Documento Controlado de Calidad")
                canvas.drawRightString(576, 25, f"Página {doc.page}")
                canvas.restoreState()

            def generar_pdf(row, s_eq, df_equipos, repetibilidad):
                buffer = io.BytesIO()
                doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=50, bottomMargin=40)
                styles = getSampleStyleSheet()

                c_prim = colors.HexColor("#0f172a")
                c_sec = colors.HexColor("#2563eb")
                c_bg = colors.HexColor("#f8fafc")
                c_bor = colors.HexColor("#cbd5e1")
                
                est_t = ParagraphStyle('T', parent=styles['Heading1'], fontSize=13, leading=16, fontName="Helvetica-Bold", textColor=c_prim)
                est_st = ParagraphStyle('ST', parent=styles['Normal'], fontSize=8.5, leading=11, fontName="Helvetica-Bold", textColor=c_sec)
                est_c = ParagraphStyle('C', parent=styles['Normal'], fontSize=8, leading=10, fontName="Helvetica")
                est_cb = ParagraphStyle('CB', parent=est_c, fontName="Helvetica-Bold", textColor=c_prim)
                
                info_eq = df_equipos[df_equipos['serial'] == s_eq].iloc[0] if s_eq in df_equipos['serial'].values else {'descripcion': '', 'marca': '', 'modelo': ''}
                um = row.get('unidad_medida', 'in')
                
                try:
                    val_nom = float(row.get('valor_nominal', 0))
                    val_real = float(row.get('valor_real', 0))
                    err = float(row.get('error', 0))
                    emp_v = float(row.get('emp', 0.001))
                    u_exp = float(row.get('incertidumbre_expandida', 0))
                    rep = float('repetibilidad')
                except ValueError:
                    val_nom, val_real, err, emp_v, u_exp, rep = 0.0, 0.0, 0.0, 0.001, 0.0, 0.0

                story = [
                    Spacer(1, 10),
                    Paragraph("INFORME OFICIAL DE CALIBRACIÓN (SCE INDUSTRIAL)", est_t),
                    Paragraph(f"Certificado Nro: {row.get('num_certificado', 'YC-000000')} | Auditado: {row.get('timestamp_auditoria', '')}", est_st),
                    Spacer(1, 6)
                ]
                
                data_gen = [
                    [Paragraph(f"<b>Fecha:</b> {row.get('fecha','')}", est_c), Paragraph(f"<b>Ubicación:</b> {row.get('ubicacion','')}", est_c), Paragraph(f"<b>Resultado:</b> {row.get('conformidad','')}", est_cb)],
                    [Paragraph(f"<b>Temperatura:</b> {row.get('temperatura','')} °C", est_c), Paragraph(f"<b>Humedad:</b> {row.get('humedad','')} %", est_c), Paragraph(f"<b>Depto:</b> {row.get('departamento','')}", est_c)]
                ]
                t_gen = Table(data_gen, colWidths=[180, 180, 180])
                t_gen.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), c_bg), ('BOX', (0,0), (-1,-1), 1, c_bor), ('INNERGRID', (0,0), (-1,-1), 0.5, c_bor), ('PADDING', (0,0), (-1,-1), 5)]))
                story.append(t_gen)
                story.append(Spacer(1, 8))
                
                p_serial = row.get('patron_serial', 'N/A')
                p_desc = row.get('patron_desc', 'Patrón General')
                p_marca = row.get('patron_marca', 'N/A')

                data_comp = [
                    [Paragraph("<b>INSTRUMENTO BAJO PRUEBA</b>", est_cb), Paragraph("<b>PATRÓN DE REFERENCIA VINCULADO</b>", est_cb)],
                    [Paragraph(f"<b>Serial:</b> {s_eq}<br/><b>Equipo:</b> {info_eq.get('descripcion','')}<br/><b>Marca:</b> {info_eq.get('marca','')}", est_c),
                     Paragraph(f"<b>Código Patrón:</b> {p_serial}<br/><b>Nombre:</b> {p_desc}<br/><b>Marca:</b> {p_marca}", est_c)]
                ]
                t_comp = Table(data_comp, colWidths=[270, 270])
                t_comp.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), c_bg), ('BOX', (0,0), (-1,-1), 1, c_bor), ('INNERGRID', (0,0), (-1,-1), 0.5, c_bor), ('PADDING', (0,0), (-1,-1), 6)]))
                story.append(t_comp)
                story.append(Spacer(1, 8))
                
                data_med = [
                    [Paragraph(f"<b>Valor Nominal ({um})</b>", est_cb), Paragraph(f"<b>Valor Real ({um})</b>", est_cb), Paragraph(f"<b>Error ({um})</b>", est_cb), Paragraph(f"<b>EMP ({um})</b>", est_cb), Paragraph("<b>Conformidad</b>", est_cb)],
                    [Paragraph(f"{val_nom:.7f}", est_c), Paragraph(f"{val_real:.7f}", est_c), Paragraph(f"{err:.7f}", est_c), Paragraph(f"{emp_v:.5f}", est_c), Paragraph(f"<b>{row.get('conformidad','')}</b>", est_cb)]
                ]
                t_med = Table(data_med, colWidths=[110, 110, 110, 100, 100])
                t_med.setStyle(TableStyle([('BOX', (0,0), (-1,-1), 1, c_bor), ('INNERGRID', (0,0), (-1,-1), 0.5, c_bor), ('PADDING', (0,0), (-1,-1), 5)]))
                story.append(t_med)
                story.append(Spacer(1, 8))

                data_inc = [
                    [Paragraph(f"<b>Repetibilidad:</b> {rep:.7f} {um}", est_c), Paragraph(f"<b>Incertidumbre Expandida (U, k=2):</b> {u_exp:.10f} {um}", est_c)]
                ]
                t_inc = Table(data_inc, colWidths=[270, 270])
                t_inc.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), c_bg), ('BOX', (0,0), (-1,-1), 1, c_bor), ('INNERGRID', (0,0), (-1,-1), 0.5, c_bor), ('PADDING', (0,0), (-1,-1), 5)]))
                story.append(t_inc)
                story.append(Spacer(1, 8))

                data_firmas = [
                    [Paragraph(f"<b>Realizado por:</b> {row.get('tecnico','')}", est_c), Paragraph(f"<b>Aprobado por:</b> {row.get('aprobado_por','')}", est_c)]
                ]
                t_firmas = Table(data_firmas, colWidths=[270, 270])
                t_firmas.setStyle(TableStyle([('BOX', (0,0), (-1,-1), 1, c_bor), ('PADDING', (0,0), (-1,-1), 6)]))
                story.append(t_firmas)
                
                doc.build(story, onFirstPage=header_footer, onLaterPages=header_footer)
                buffer.seek(0)
                return buffer.getvalue()

            if not df_eq.empty:
                st.markdown("<br>", unsafe_allow_html=True)
                ultimo = df_eq.iloc[-1]
                pdf_bytes = generar_pdf(ultimo, serial_filtro, df_e, repetibilidad)
                st.download_button("📥 Descargar Certificado Oficial en PDF", data=pdf_bytes, file_name=f"Certificado_SCE_{serial_filtro}.pdf", mime="application/pdf,")
    else:
        st.info("No hay registros disponibles en el historial.")