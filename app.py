import streamlit as st
import pandas as pd
import numpy as np
import datetime
import os

DATA_FILE = "historial_metrologia.csv"
EQUIPOS_FILE = "equipos.csv"

# --- CONTROL DE ACCESO (CONTRASEÑA) ---
PASSWORD_CORRECTA = "metro2026" # Cambia esto por la contraseña que quieras

st.sidebar.title("🔐 Seguridad")
password_ingresada = st.sidebar.text_input("Contraseña de acceso", type="password")

if password_ingresada != PASSWORD_CORRECTA:
    st.title("🔒 Acceso Restringido")
    st.warning("Por favor, ingrese la contraseña correcta en el menú lateral para acceder al Sistema de Gestión Metrológica.")
    st.stop()  # Detiene la ejecución para que nadie vea el contenido si no pone la clave
# ---------------------------------------

def load_data(file, columns):
    if os.path.exists(file):
        return pd.read_csv(file)
    return pd.DataFrame(columns=columns)

def save_data(df, file):
    df.to_csv(file, index=False)

st.set_page_config(page_title="App Metrología", layout="wide")

st.title("Instrumentos de Medición")

menu = ["Registrar Equipo", "Calcular Incertidumbre y Guardar", "Trazabilidad e Historial"]
choice = st.sidebar.selectbox("Menú de Navegación", menu)

if choice == "Registrar Equipo":
    st.header("➕ Registro de Nuevo Equipo de Medición")
    with st.form("registro_form"):
        serial = st.text_input("Código Interno / Serial")
        nombre = st.text_input("Nombre del Equipo (Ej. Balanza, Multímetro)")
        magnitud = st.text_input("Magnitud (Ej. Masa, Tensión, Temperatura)")
        submitted = st.form_submit_button("Guardar Equipo")
        if submitted:
            df = load_data(EQUIPOS_FILE, ["Serial", "Nombre", "Magnitud"])
            new_row = {"Serial": serial, "Nombre": nombre, "Magnitud": magnitud}
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            save_data(df, EQUIPOS_FILE)
            st.success(f"¡Equipo '{nombre}' registrado con éxito!")

elif choice == "Calcular Incertidumbre y Guardar":
    equipos_df = load_data(EQUIPOS_FILE, ["Serial", "Nombre", "Magnitud"])
    if not equipos_df.empty:
        selected_serial = st.selectbox("Seleccione el Equipo", equipos_df["Serial"] + " - " + equipos_df["Nombre"])
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Evaluación Tipo A\n### (Repetibilidad)")
            tipo_a = st.text_area("Ingrese las lecturas separadas por comas (Ej: 10.1, 10.0, 10.2, 10.1)", value="10.01, 10.02, 10.00, 10.01")
            
        with col2:
            st.markdown("### Evaluación Tipo B\n### (Patrón / Resolución)")
            u_patron = st.number_input("Incertidumbre estándar del Patrón (u_patron)", value=0.0100, format="%.4f")
            resolucion = st.number_input("Resolución del equipo", value=0.0100, format="%.4f")
            valor_ref = st.number_input("Valor de Referencia (Patrón)", value=10.0000, format="%.4f")
        
        if st.button("Calcular y Guardar en Historial"):
            lecturas = [float(x.strip()) for x in tipo_a.split(',')]
            u_a = np.std(lecturas, ddof=1) / np.sqrt(len(lecturas))
            u_combinada = np.sqrt(u_a**2 + u_patron**2 + (resolucion / (2 * np.sqrt(3)))**2)
            u_expandida = u_combinada * 2
            error = np.mean(lecturas) - valor_ref
            
            st.success("¡Cálculo realizado y guardado con éxito en la trazabilidad!")
            st.metric("Incertidumbre Expandida (U)", f"{u_expandida:.4f}")
            st.metric("Error Calculado", f"{error:.4f}")
            
            df = load_data(DATA_FILE, ["Serial", "Fecha", "U", "Error"])
            new_row = {"Serial": selected_serial.split(' - ')[0], "Fecha": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "U": u_expandida, "Error": error}
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            save_data(df, DATA_FILE)
    else:
        st.warning("Primero registre un equipo en el menú lateral.")

elif choice == "Trazabilidad e Historial":
    st.header("📊 Trazabilidad e Historial")
    equipos_df = load_data(EQUIPOS_FILE, ["Serial", "Nombre", "Magnitud"])
    if not equipos_df.empty:
        selected_serial = st.selectbox("Seleccione el Equipo", equipos_df["Serial"] + " - " + equipos_df["Nombre"])
        df = load_data(DATA_FILE, ["Serial", "Fecha", "U", "Error"])
        filtered_df = df[df["Serial"] == selected_serial.split(' - ')[0]]
        
        if not filtered_df.empty:
            tabla_export = filtered_df[["Fecha", "Error", "U"]].rename(columns={
                "Fecha": "fecha",
                "Error": "error",
                "U": "incertidumbre"
            })
            tabla_export["resultado"] = "Conforme"
            
            csv_data = tabla_export.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Descargar Historial en Excel/CSV",
                data=csv_data,
                file_name=f"Historial_{selected_serial.split(' - ')[0]}.csv",
                mime="text/csv"
            )
            
            st.subheader("Registros Históricos")
            st.dataframe(tabla_export, use_container_width=True)
            
            st.subheader("Tendencia de la Incertidumbre en el Tiempo")
            chart_data = tabla_export.set_index("fecha")[["incertidumbre", "error"]]
            st.line_chart(chart_data)
        else:
            st.info("No hay registros históricos para este equipo.")
    else:
        st.info("No hay equipos registrados.")