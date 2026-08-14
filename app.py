import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Configuración de la página
st.set_page_config(page_title="Sistema de Gestión Metrológica", page_icon="📊", layout="wide")

# Sistema de Autenticación Simple
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    if st.session_state["password_correct"]:
        return True

    st.sidebar.subheader("🔒 Seguridad")
    password = st.sidebar.text_input("Contraseña de acceso", type="password")
    if st.sidebar.button("Ingresar"):
        if password == "1234":
            st.session_state["password_correct"] = True
            st.rerun()
        else:
            st.sidebar.error("Contraseña incorrecta")
    
    st.markdown("""
    # 🔒 Acceso Restringido
    Por favor, ingrese la contraseña correcta en el menú lateral para acceder al Sistema de Gestión Metrológica.
    """)
    return False

if not check_password():
    st.stop()

# Función de lectura blindada con datos iniciales por defecto si está vacío
def leer_csv_seguro(path, columnas_default, datos_ejemplo=None):
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        df_ini = pd.DataFrame(columns=columnas_default)
        if datos_ejemplo:
            df_ini.loc[0] = datos_ejemplo
        df_ini.to_csv(path, index=False, encoding='utf-8')
        return df_ini
    
    try:
        return pd.read_csv(path, encoding='utf-8')
    except Exception:
        try:
            return pd.read_csv(path, encoding='latin-1')
        except Exception:
            df_ini = pd.DataFrame(columns=columnas_default)
            if datos_ejemplo:
                df_ini.loc[0] = datos_ejemplo
            df_ini.to_csv(path, index=False, encoding='utf-8')
            return df_ini

# Cargar archivos de forma segura
df_equipos = leer_csv_seguro(
    "equipos.csv", 
    ["serial", "descripcion", "modelo", "marca", "estado"],
    ["EQ-001", "Multímetro Digital", "87V", "Fluke", "Operativo"]
)
df_equipos.columns = [str(c).strip().lower() for c in df_equipos.columns]
if 'estado' not in df_equipos.columns:
    df_equipos['estado'] = 'Operativo'

df_historial = leer_csv_seguro("historial_metrologia.csv", [
    "serial", "fecha", "temperatura", "humedad", 
    "incertidumbre_patrones", "valor_nominal", "valor_real", 
    "dimensiones", "error", "incertidumbre"
])
df_historial.columns = [str(c).strip().lower() for c in df_historial.columns]

st.title("📊 Sistema de Gestión Metrológica")

# --- SECCIÓN 1: ADMINISTRAR / ELIMINAR / ESTADO DE EQUIPOS ---
with st.expander("⚙️ Administrar Equipos (Menú desplegable de estados y nuevos equipos)", expanded=True):
    st.markdown("""
    * **Columna Estado:** Haz clic en la celda de estado para abrir el **menú desplegable** y seleccionar la etiqueta correspondiente.
    * **Para agregar un equipo nuevo:** Escribe los datos en la tabla o usa el símbolo **`+`**.
    * No olvides hacer clic en **Guardar cambios en Equipos** al terminar.
    """)
    
    df_equipos_editado = st.data_editor(
        df_equipos,
        num_rows="dynamic",
        key="editor_equipos",
        use_container_width=True,
        column_config={
            "estado": st.column_config.SelectboxColumn(
                "Estado del Equipo",
                help="Seleccione el estado operacional actual",
                options=["Operativo", "En Mantenimiento", "Fuera de Servicio"],
                required=True,
            )
        }
    )
    
    if st.button("💾 Guardar cambios en Equipos"):
        df_equipos_editado = df_equipos_editado.dropna(subset=[df_equipos_editado.columns[0]])
        df_equipos_editado.to_csv("equipos.csv", index=False, encoding='utf-8')
        st.success("¡Lista de equipos y estados actualizada correctamente!")
        st.rerun()

st.markdown("---")
st.subheader("Gestión Metrológica y Calibraciones")

# Filtrar filas vacías o con serial nulo
df_equipos_editado = df_equipos_editado.dropna(subset=[df_equipos_editado.columns[0]])
df_equipos_editado = df_equipos_editado[df_equipos_editado[df_equipos_editado.columns[0]].astype(str).str.strip() != ""]

if not df_equipos_editado.empty:
    col_serial = df_equipos_editado.columns[0]
    col_desc = df_equipos_editado.columns[1] if len(df_equipos_editado.columns) > 1 else col_serial
    col_est = 'estado' if 'estado' in df_equipos_editado.columns else df_equipos_editado.columns[-1]
    
    s_ser = df_equipos_editado[col_serial].fillna("").astype(str)
    s_des = df_equipos_editado[col_desc].fillna("").astype(str)
    s_est = df_equipos_editado[col_est].fillna("Operativo").astype(str)

    df_equipos_editado['opcion'] = s_ser + " - " + s_des + " [" + s_est + "]"
    
    selected_serial_label = st.selectbox("Seleccione el Equipo a Calibrar / Medir", df_equipos_editado['opcion'])
    
    if selected_serial_label and str(selected_serial_label).lower() != 'nan' and ' - ' in str(selected_serial_label):
        serial_actual = str(selected_serial_label).split(' - ')[0].strip()
        
        col_hist_serial = next((c for c in df_historial.columns if 'serial' in c or 'codigo' in c), 'serial')
        tabla_export = df_historial[df_historial[col_hist_serial].astype(str).str.strip() == serial_actual]
        tabla_export = tabla_export.loc[:, ~tabla_export.columns.duplicated()]

        # --- FORMULARIO PARA REGISTRAR NUEVA MEDICIÓN METROLÓGICA ---
        with st.form("form_nueva_medicion", clear_on_submit=True):
            st.subheader("➕ Registrar Nueva Medición / Calibración")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                f_fecha = st.date_input("Fecha de medición", value=datetime.now())
                f_temp = st.number_input("Valor de la temperatura (°C)", value=20.0, format="%.2f")
                f_hum = st.number_input("Humedad relativa (%)", value=50.0, format="%.2f")
            with col2:
                f_dim = st.text_input("Dimensiones del equipo", value="N/A")
                f_val_nom = st.number_input("Valor nominal del equipo", value=0.0, format="%.4f")
                f_val_real = st.number_input("Valor real obtenido", value=0.0, format="%.4f")
            with col3:
                f_inc_pat = st.number_input("Valor de la incertidumbre de los patrones", value=0.001, format="%.5f")
                f_inc_total = st.number_input("Incertidumbre combinada calculada", value=0.002, format="%.5f")
            
            btn_submit = st.form_submit_button("📥 Guardar Nueva Medición")
            
            if btn_submit:
                f_error = f_val_real - f_val_nom
                
                nuevo_registro = pd.DataFrame([{
                    "serial": serial_actual,
                    "fecha": str(f_fecha),
                    "temperatura": f_temp,
                    "humedad": f_hum,
                    "incertidumbre_patrones": f_inc_pat,
                    "valor_nominal": f_val_nom,
                    "valor_real": f_val_real,
                    "dimensiones": f_dim,
                    "error": f_error,
                    "incertidumbre": f_inc_total
                }])
                
                df_total = leer_csv_seguro("historial_metrologia.csv", [
                    "serial", "fecha", "temperatura", "humedad", 
                    "incertidumbre_patrones", "valor_nominal", "valor_real", 
                    "dimensiones", "error", "incertidumbre"
                ])
                df_total = pd.concat([df_total, nuevo_registro], ignore_index=True)
                df_total.to_csv("historial_metrologia.csv", index=False, encoding='utf-8')
                st.success("¡Medición metrológica registrada con éxito!")
                st.rerun()

        st.subheader("Registros Históricos del Equipo Seleccionado")
        
        tabla_editada = st.data_editor(
            tabla_export, 
            num_rows="dynamic", 
            key=f"editor_{serial_actual}",
            use_container_width=True
        )

        if st.button("💾 Guardar cambios y eliminar registros históricos"):
            df_total = leer_csv_seguro("historial_metrologia.csv", [
                "serial", "fecha", "temperatura", "humedad", 
                "incertidumbre_patrones", "valor_nominal", "valor_real", 
                "dimensiones", "error", "incertidumbre"
            ])
            df_total.columns = [str(c).strip().lower() for c in df_total.columns]
            df_total = df_total.loc[:, ~df_total.columns.duplicated()]
            
            df_total = df_total[df_total[col_hist_serial].astype(str).str.strip() != serial_actual]
            df_total = pd.concat([df_total, tabla_editada], ignore_index=True)
            
            df_total.to_csv("historial_metrologia.csv", index=False, encoding='utf-8')
            st.success("¡Registros históricos actualizados correctamente!")
            st.rerun()

        st.subheader("Tendencia de la Incertidumbre y Error en el Tiempo")
        if not tabla_editada.empty:
            cols_lower = [c.lower() for c in tabla_editada.columns]
            col_fecha = next((tabla_editada.columns[i] for i, c in enumerate(cols_lower) if 'fecha' in c), None)
            col_inc = next((tabla_editada.columns[i] for i, c in enumerate(cols_lower) if 'incertidumbre' in c and 'patron' not in c), None)
            col_err = next((tabla_editada.columns[i] for i, c in enumerate(cols_lower) if 'error' in c), None)
            
            if col_fecha and col_inc and col_err:
                try:
                    chart_data = tabla_editada.set_index(col_fecha)[[col_inc, col_err]]
                    st.line_chart(chart_data)
                except Exception:
                    st.info("No se pudo generar el gráfico. Verifique que los campos numéricos sean correctos.")
            else:
                st.info("No se encontraron las columnas exactas de fecha, incertidumbre o error para graficar.")
        else:
            st.info("No hay registros históricos para este equipo.")
    else:
        st.info("Seleccione un equipo válido.")
else:
    st.info("No hay equipos registrados en el sistema.")

# --- SECCIÓN 2: INVENTARIO GENERAL Y DESCARGA (CON COLORES CONDICIONALES) ---
st.markdown("---")
with st.expander("📦 Ver Inventario Completo y Descargar Reportes de Calibración"):
    st.subheader("Inventario General de Equipos")
    
    def resaltar_estado(val):
        if str(val).strip().lower() == 'operativo':
            return 'background-color: rgba(46, 204, 113, 0.25); color: #2ecc71; font-weight: bold;'
        elif str(val).strip().lower() == 'en mantenimiento':
            return 'background-color: rgba(241, 196, 15, 0.25); color: #f1c40f; font-weight: bold;'
        elif str(val).strip().lower() == 'fuera de servicio':
            return 'background-color: rgba(231, 76, 60, 0.25); color: #e74c3c; font-weight: bold;'
        return ''

    df_inv_clean = df_equipos_editado.drop(columns=['opcion'], errors='ignore')
    
    if 'estado' in df_inv_clean.columns:
        df_styled = df_inv_clean.style.map(resaltar_estado, subset=['estado'])
        st.dataframe(df_styled, use_container_width=True)
    else:
        st.dataframe(df_inv_clean, use_container_width=True)
    
    st.subheader("Historial Completo de Calibraciones (Todas las Mediciones)")
    df_hist_global = leer_csv_seguro("historial_metrologia.csv", [
        "serial", "fecha", "temperatura", "humedad", 
        "incertidumbre_patrones", "valor_nominal", "valor_real", 
        "dimensiones", "error", "incertidumbre"
    ])
    st.dataframe(df_hist_global, use_container_width=True)
    
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        csv_equipos = df_inv_clean.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Descargar Inventario de Equipos (CSV)",
            data=csv_equipos,
            file_name="inventario_equipos.csv",
            mime="text/csv"
        )
    with col_d2:
        csv_hist = df_hist_global.to_csv(index=False, encoding='utf-8').encode('utf-8')
        st.download_button(
            label="📥 Descargar Historial de Calibraciones (CSV)",
            data=csv_hist,
            file_name="historial_calibraciones.csv",
            mime="text/csv"
        )