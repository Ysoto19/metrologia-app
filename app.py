# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import os
import math
from datetime import datetime
import io

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    REPORTLAB_DISPONIBLE = True
except ImportError:
    REPORTLAB_DISPONIBLE = False

BASE_DIR = os.getcwd()
EQUIPOS_PATH = os.path.join(BASE_DIR, "equipos.csv")
HISTORIAL_PATH = os.path.join(BASE_DIR, "historial_metrologia.csv")

def inicializar_csvs():
    try:
        if not os.path.exists(EQUIPOS_PATH) or os.path.getsize(EQUIPOS_PATH) == 0:
            df_init = pd.DataFrame([
                {"serial": "MAN-001", "descripcion": "Manometro digital de presion", "modelo": "PG-100", "marca": "Wika", "estado": "Activo", "frecuencia_meses": 6},
                {"serial": "BAL-005", "descripcion": "Balanza analitica de precision", "modelo": "ME204", "marca": "Mettler Toledo", "estado": "Calibracion Pendiente", "frecuencia_meses": 12},
                {"serial": "TER-010", "descripcion": "Termohigrometro digital", "modelo": "TH-20", "marca": "Testo", "estado": "En Mantenimiento", "frecuencia_meses": 6},
                {"serial": "MD-YC-102-2243", "descripcion": "CALIBRADOR CON RELOJ", "modelo": "505-742-51J", "marca": "MITUTOYO", "estado": "Activo", "frecuencia_meses": 12}
            ])
            df_init.to_csv(EQUIPOS_PATH, index=False, encoding='utf-8-sig')
    except Exception:
        pass
    
    try:
        if not os.path.exists(HISTORIAL_PATH) or os.path.getsize(HISTORIAL_PATH) == 0:
            df_h_init = pd.DataFrame(columns=[
                "serial", "fecha", "magnitud", "valor_nominal", "valor_real", "error", 
                "emp", "incertidumbre_combinada", "factor_k", "incertidumbre_expandida", "conformidad",
                "num_certificado", "ubicacion", "departamento", "temperatura", "humedad",
                "patron_desc", "patron_marca", "patron_serial", "tecnico", "aprobado_por",
                "unidad_medida", "observaciones", "relacion_ep_u"
            ])
            df_h_init.to_csv(HISTORIAL_PATH, index=False, encoding='utf-8-sig')
    except Exception:
        pass

inicializar_csvs()

def leer_csv(path, columnas):
    try:
        if os.path.exists(path) and os.path.getsize(path) > 0:
            return pd.read_csv(path)
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

COLUMNAS_EQUIPOS = ["serial", "descripcion", "modelo", "marca", "estado", "frecuencia_meses"]
COLUMNAS_HISTORIAL = [
    "serial", "fecha", "magnitud", "valor_nominal", "valor_real", "error", 
    "emp", "incertidumbre_combinada", "factor_k", "incertidumbre_expandida", "conformidad",
    "num_certificado", "ubicacion", "departamento", "temperatura", "humedad",
    "patron_desc", "patron_marca", "patron_serial", "tecnico", "aprobado_por",
    "unidad_medida", "observaciones", "relacion_ep_u"
]

st.set_page_config(page_title="Sistema Metrologico GUM / ISO 17025", layout="wide")

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.title("Acceso Restringido - Sistema Metrologico Industrial")
    st.markdown("Por favor, introduzca la contrasena corporativa de acceso para continuar con la auditoria de calidad.")
    
    password_input = st.text_input("Contrasena", type="password")
    if st.button("Iniciar Sesion"):
        if password_input == "metrologia2026":
            st.session_state.autenticado = True
            st.success("Acceso concedido.")
            st.rerun()
        else:
            st.error("Contrasena incorrecta. Intente nuevamente.")
    st.stop()

st.title("Sistema Metrologico Industrial - Trazabilidad y Calidad (ISO 9001 / ISO 17025)")
st.success("Sistema activo con control de acceso GUM / ISO. Sesion autorizada.")

tab1, tab2, tab3 = st.tabs(["Calibracion y GUM", "Inventario de Equipos (ISO 9001)", "Historial y Tendencias"])

with tab1:
    df_e = leer_csv(EQUIPOS_PATH, COLUMNAS_EQUIPOS)
    
    if df_e.empty:
        st.warning("No hay equipos registrados. Por favor, ve a la pestana 'Inventario de Equipos' y anade al menos uno.")
    else:
        st.subheader("Registro de Calibraciones Internas")
        
        col_h1, col_h2, col_h3, col_h4 = st.columns(4)
        with col_h1:
            df_e['label'] = df_e['serial'].astype(str) + " - " + df_e['descripcion'].astype(str)
            selected_eq = st.selectbox("Equipo (JDE / Serial)", df_e['label'])
            serial = selected_eq.split(' - ')[0]
            num_certificado = st.text_input("Registro / Certificado Nro", value="YC-0006524")
        with col_h2:
            fecha_cal = st.date_input("Fecha Calibración", value=datetime.now())
            prox_cal = st.date_input("Próxima Calibración", value=datetime.now())
        with col_h3:
            ubicacion = st.text_input("Ubicación", value="MOLDES B")
            departamento = st.text_input("Departamento", value="GERENCIA DE CALIDAD")
        with col_h4:
            temperatura = st.number_input("Temperatura (°C)", value=20.00, format="%.2f")
            humedad = st.number_input("Humedad Relativa (%)", value=69.00, format="%.2f")
            higrometro = st.text_input("Higrómetro Patron", value="CC-YH-102-2237")

        resultado_calib = st.selectbox("Resultado de la Calibración", ["Calibrado", "Ajustado", "Rechazado"])
        
        st.markdown("---")
        
        sub_tab1, sub_tab2, sub_tab3 = st.tabs([
            "📌 Características Equipo / Patrón", 
            "📋 Pruebas - Calibrador", 
            "📊 Mediciones Prueba Exactitud"
        ])
        
        eq_info = df_e[df_e['serial'] == serial].iloc[0]
        
        with sub_tab1:
            col_eq, col_pat = st.columns(2)
            with col_eq:
                st.markdown("#### Características del Equipo")
                st.text_input("Código Equipo JDE", value=serial, disabled=True)
                st.text_input("Nombre Equipo", value=eq_info['descripcion'], disabled=True)
                st.text_input("Marca", value=eq_info['marca'], disabled=True)
                st.text_input("Modelo", value=eq_info['modelo'], disabled=True)
                rango_eq = st.text_input("Rango", value="0,00 a 6,00")
                emp_eq = st.number_input("Error Máx. Permisible (EMP)", value=0.00100, format="%.5f")
            with col_pat:
                st.markdown("#### Características del Patrón")
                patron_codigo = st.text_input("Código Patrón", value="CC-YJ-102-259")
                patron_nombre = st.text_input("Nombre Patrón", value="JUEGO DE BLOQUES PATRON")
                patron_marca = st.text_input("Marca Patrón", value="MITUTOYO")
                patron_modelo = st.text_input("Modelo Patrón", value="516-315")
                patron_rango = st.text_input("Rango Patrón", value="0,10 a 4,00")
                patron_emp = st.number_input("EMP Patrón", value=0.00002, format="%.5f")

        with sub_tab2:
            col_p1, col_p2 = st.columns(2)
            with col_p1:
                inspeccion_visual = st.text_area("Inspección Visual", value="CORRECTO FUNCIONAMIENTO")
            with col_p2:
                observaciones = st.text_area("Observaciones", value="DENTRO DEL EMP")
            palpadores_externos = st.selectbox("Palpadores Externos", ["Estándar", "Especial"])

        with sub_tab3:
            st.markdown("#### Mediciones Prueba Exactitud")
            unidad_medida = st.selectbox("Unidad de Medida", ["in", "mm", "PULGADA"])
            
            val_nom_ing = st.number_input("Valor Nominal de Pruebas", value=1.1900000, format="%.7f")
            col_l1, col_l2, col_l3, col_l4 = st.columns(4)
            with col_l1:
                lec1 = st.number_input("Lectura 1", value=1.1900000, format="%.7f")
            with col_l2:
                lec2 = st.number_input("Lectura 2", value=1.1900000, format="%.7f")
            with col_l3:
                lec3 = st.number_input("Lectura 3", value=1.1900000, format="%.7f")
            with col_l4:
                lec4 = st.number_input("Lectura 4", value=1.1910000, format="%.7f")
            
            lectura_promedio = (lec1 + lec2 + lec3 + lec4) / 4.0
            error_calculado = lectura_promedio - val_nom_ing
            incertidumbre_exp = st.number_input("Incertidumbre Expandida Mayor (U)", value=0.0008579180, format="%.10f")
            relacion_ep_u = emp_eq / incertidumbre_exp if incertidumbre_exp > 0 else 0.0
            
            st.info(f"**Lectura Promedio:** {lectura_promedio:.7f} {unidad_medida} | **Error Calculado:** {error_calculado:.7f} {unidad_medida} | **Relación (EMP / U):** {relacion_ep_u:.6f}")

        st.markdown("---")
        st.markdown("#### ✍️ Firmas y Responsables de Calidad")
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            tecnico_calibracion = st.text_input("Realizado por (Técnico / Analista)", value="PETIT CAMPOS ROBERT JOSE")
        with col_f2:
            aprobado_por = st.text_input("Aprobado por (Supervisor / Gerencia)", value="Ing. Calidad Venvidrio")

        if st.button("Guardar Registro y Validar Conformidad", type="primary"):
            conf = "CONFORME" if abs(error_calculado) <= emp_eq else "NO CONFORME"
            
            nuevo = pd.DataFrame([{
                "serial": serial, 
                "fecha": str(fecha_cal), 
                "magnitud": "Longitud / Calibrador",
                "valor_nominal": val_nom_ing, 
                "valor_real": lectura_promedio, 
                "error": error_calculado, 
                "emp": emp_eq, 
                "incertidumbre_combinada": incertidumbre_exp / 2.0,
                "factor_k": 2.0,
                "incertidumbre_expandida": incertidumbre_exp, 
                "conformidad": conf,
                "num_certificado": num_certificado,
                "ubicacion": ubicacion,
                "departamento": departamento,
                "temperatura": temperatura,
                "humedad": humedad,
                "patron_desc": patron_nombre,
                "patron_marca": patron_marca,
                "patron_serial": patron_codigo,
                "tecnico": tecnico_calibracion,
                "aprobado_por": aprobado_por,
                "unidad_medida": unidad_medida,
                "observaciones": observaciones,
                "relacion_ep_u": relacion_ep_u
            }])
            
            df_h = leer_csv(HISTORIAL_PATH, COLUMNAS_HISTORIAL)
            guardar_csv(pd.concat([df_h, nuevo], ignore_index=True), HISTORIAL_PATH)
            st.success(f"¡Certificado {num_certificado} guardado y registrado exitosamente con especificaciones completas!")

with tab2:
    st.subheader("Control e Inventario de Instrumentos (Requisito ISO 9001)")
    df_e = leer_csv(EQUIPOS_PATH, COLUMNAS_EQUIPOS)
    
    with st.expander("Anadir / Registrar Nuevo Instrumento"):
        with st.form("form_nuevo_equipo"):
            col_n1, col_n2, col_n3 = st.columns(3)
            with col_n1:
                n_serial = st.text_input("Serial")
                n_desc = st.text_input("Descripcion")
            with col_n2:
                n_modelo = st.text_input("Modelo")
                n_marca = st.text_input("Marca")
            with col_n3:
                n_estado = st.selectbox("Estado", ["Activo", "Calibracion Pendiente", "En Mantenimiento", "Fuera de Servicio"])
                n_freq = st.selectbox("Frecuencia (Meses)", [1, 3, 6, 12, 18, 24, 36])
            
            if st.form_submit_button("Guardar"):
                nuevo_eq = pd.DataFrame([{"serial": n_serial, "descripcion": n_desc, "modelo": n_modelo, "marca": n_marca, "estado": n_estado, "frecuencia_meses": int(n_freq)}])
                if n_serial in df_e['serial'].values:
                    df_e = df_e[df_e['serial'] != n_serial]
                guardar_csv(pd.concat([df_e, nuevo_eq], ignore_index=True), EQUIPOS_PATH)
                st.rerun()

    csv_inventario = df_e.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 Descargar Inventario (.csv)",
        data=csv_inventario,
        file_name="Inventario_Equipos_Venvidrio.csv",
        mime="text/csv",
        key="btn_descargar_inventario"
    )

    st.dataframe(df_e, use_container_width=True)

with tab3:
    st.subheader("Historial de Calibraciones y Emision de Informes")
    df_h = leer_csv(HISTORIAL_PATH, COLUMNAS_HISTORIAL)
    df_e = leer_csv(EQUIPOS_PATH, COLUMNAS_EQUIPOS)
    
    if not df_h.empty:
        csv_historial = df_h.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📊 Descargar Historial Completo de Calibraciones (.csv)",
            data=csv_historial,
            file_name="Historial_Calibraciones_Completo.csv",
            mime="text/csv",
            key="btn_descargar_historial"
        )

        serial_filtro = st.selectbox("Filtrar por Serial", df_h['serial'].unique())
        df_eq = df_h[df_h['serial'] == serial_filtro]
        st.dataframe(df_eq, use_container_width=True)
        
        if REPORTLAB_DISPONIBLE:
            def header_footer(canvas, doc):
                canvas.saveState()
                logo_path = "logo_venvidrio.png"
                if os.path.exists(logo_path):
                    canvas.drawImage(logo_path, 510, 750, width=70, height=40, preserveAspectRatio=True, mask='auto')
                
                canvas.setFont("Helvetica-Bold", 11)
                canvas.drawString(30, 765, "LABORATORIO DE METROLOGÍA - VENEZOLANA DEL VIDRIO (VENVIDRIO)")
                canvas.line(30, 745, 580, 745)
                
                canvas.setFont("Helvetica", 8)
                canvas.drawString(30, 30, "Documento de Calidad ISO/IEC 17025 - Controlado")
                canvas.drawRightString(580, 30, f"Pagina {doc.page}")
                canvas.restoreState()

            def generar_informe_calibracion_formal(row, s_eq, df_equipos):
                buffer = io.BytesIO()
                doc = SimpleDocTemplate(
                    buffer, 
                    pagesize=letter, 
                    rightMargin=36, 
                    leftMargin=36, 
                    topMargin=54, 
                    bottomMargin=40
                )
                styles = getSampleStyleSheet()
                
                COLOR_PRIMARY = colors.HexColor("#0f172a")
                COLOR_SECONDARY = colors.HexColor("#2563eb")
                COLOR_BG_HEADER = colors.HexColor("#f8fafc")
                COLOR_BORDER = colors.HexColor("#cbd5e1")
                
                est_titulo = ParagraphStyle(
                    'TituloModerno', 
                    parent=styles['Heading1'], 
                    fontSize=14, 
                    leading=18,
                    fontName="Helvetica-Bold", 
                    alignment=0, 
                    textColor=COLOR_PRIMARY, 
                    spaceAfter=4
                )
                est_subtitulo = ParagraphStyle(
                    'SubTituloModerno',
                    parent=styles['Normal'],
                    fontSize=9,
                    leading=12,
                    fontName="Helvetica-Bold",
                    textColor=COLOR_SECONDARY,
                    spaceAfter=8
                )
                est_cell = ParagraphStyle(
                    'CellText',
                    parent=styles['Normal'],
                    fontSize=8.5,
                    leading=11,
                    fontName="Helvetica"
                )
                est_cell_bold = ParagraphStyle(
                    'CellTextBold',
                    parent=est_cell,
                    fontName="Helvetica-Bold",
                    textColor=COLOR_PRIMARY
                )
                est_cell_header = ParagraphStyle(
                    'CellTextHeader',
                    parent=est_cell,
                    fontName="Helvetica-Bold",
                    textColor=colors.white
                )
                est_legal = ParagraphStyle(
                    'LegalText',
                    parent=styles['Normal'],
                    fontSize=7.5,
                    leading=10,
                    fontName="Helvetica",
                    textColor=colors.HexColor("#334155")
                )

                info_eq = df_equipos[df_equipos['serial'] == s_eq].iloc[0]
                um = row.get('unidad_medida', 'in')
                
                story = [
                    Spacer(1, 10),
                    Paragraph("REGISTRO DE CALIBRACIÓN INTERNA", est_titulo),
                    Paragraph(f"Certificado Nro: {row.get('num_certificado', 'YC-000000')}", est_subtitulo),
                    Spacer(1, 5)
                ]
                
                data_gen = [
                    [
                        Paragraph(f"<b>Fecha Registro:</b> {row.get('fecha', '')}", est_cell),
                        Paragraph(f"<b>Ubicación:</b> {row.get('ubicacion', 'MOLDES B')}", est_cell),
                        Paragraph(f"<b>Departamento:</b> {row.get('departamento', 'GERENCIA DE CALIDAD')}", est_cell)
                    ],
                    [
                        Paragraph(f"<b>Temperatura:</b> {row.get('temperatura', '20.00')} °C", est_cell),
                        Paragraph(f"<b>Humedad Relativa:</b> {row.get('humedad', '69.00')} %", est_cell),
                        Paragraph(f"<b>Resultado:</b> {row.get('conformidad', 'CONFORME')}", est_cell_bold)
                    ]
                ]
                t_gen = Table(data_gen, colWidths=[180, 180, 180])
                t_gen.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,-1), COLOR_BG_HEADER),
                    ('BOX', (0,0), (-1,-1), 1, COLOR_BORDER),
                    ('INNERGRID', (0,0), (-1,-1), 0.5, COLOR_BORDER),
                    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                    ('TOPPADDING', (0,0), (-1,-1), 6),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 6),
                    ('LEFTPADDING', (0,0), (-1,-1), 8),
                    ('RIGHTPADDING', (0,0), (-1,-1), 8),
                ]))
                story.append(t_gen)
                story.append(Spacer(1, 10))
                
                data_comp = [
                    [Paragraph("<b>CARACTERÍSTICAS DEL EQUIPO</b>", est_cell_bold), Paragraph("<b>CARACTERÍSTICAS DEL PATRÓN</b>", est_cell_bold)],
                    [Paragraph(f"<b>Código JDE:</b> {s_eq}<br/><b>Nombre:</b> {info_eq['descripcion']}<br/><b>Marca / Modelo:</b> {info_eq['marca']} / {info_eq['modelo']}<br/><b>Serial:</b> {s_eq}", est_cell),
                     Paragraph(f"<b>Código Patrón:</b> {row.get('patron_serial', 'CC-YJ-102-259')}<br/><b>Nombre:</b> {row.get('patron_desc', 'JUEGO DE BLOQUES PATRON')}<br/><b>Marca:</b> {row.get('patron_marca', 'MITUTOYO')}<br/><b>Serial:</b> 970711", est_cell)]
                ]
                t_comp = Table(data_comp, colWidths=[270, 270])
                t_comp.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,0), COLOR_BG_HEADER),
                    ('BOX', (0,0), (-1,-1), 1, COLOR_BORDER),
                    ('INNERGRID', (0,0), (-1,-1), 0.5, COLOR_BORDER),
                    ('VALIGN', (0,0), (-1,-1), 'TOP'),
                    ('TOPPADDING', (0,0), (-1,-1), 6),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 6),
                    ('LEFTPADDING', (0,0), (-1,-1), 8),
                    ('RIGHTPADDING', (0,0), (-1,-1), 8),
                ]))
                story.append(t_comp)
                story.append(Spacer(1, 10))
                
                story.append(Paragraph("<b>MEDICIONES Y EVALUACIÓN DE EXACTITUD</b>", est_subtitulo))
                data_med = [
                    [
                        Paragraph(f"<b>Valor Nominal ({um})</b>", est_cell_header), 
                        Paragraph(f"<b>Valor Real ({um})</b>", est_cell_header), 
                        Paragraph(f"<b>Error Calculado ({um})</b>", est_cell_header), 
                        Paragraph(f"<b>EMP ({um})</b>", est_cell_header), 
                        Paragraph("<b>Evaluación</b>", est_cell_header)
                    ],
                    [
                        Paragraph(f"{row.get('valor_nominal', 0):.7f}", est_cell),
                        Paragraph(f"{row.get('valor_real', 0):.7f}", est_cell),
                        Paragraph(f"{row.get('error', 0):.7f}", est_cell),
                        Paragraph(f"{row.get('emp', 0.001):.5f}", est_cell),
                        Paragraph(f"<b>{row.get('conformidad', 'CONFORME')}</b>", est_cell)
                    ]
                ]
                t_med = Table(data_med, colWidths=[110, 110, 110, 100, 100])
                t_med.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,0), COLOR_PRIMARY),
                    ('BOX', (0,0), (-1,-1), 1, COLOR_BORDER),
                    ('INNERGRID', (0,0), (-1,-1), 0.5, COLOR_BORDER),
                    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                    ('TOPPADDING', (0,0), (-1,-1), 5),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 5),
                    ('LEFTPADDING', (0,0), (-1,-1), 5),
                    ('RIGHTPADDING', (0,0), (-1,-1), 5),
                ]))
                story.append(t_med)
                story.append(Spacer(1, 10))

                # Bloque de Incertidumbre y Unidad de Medida
                u_exp = row.get('incertidumbre_expandida', 0.0008579180)
                rel_val = row.get('relacion_ep_u', 1.1656)
                obs_text = row.get('observaciones', 'DENTRO DEL EMP')

                data_extra = [
                    [
                        Paragraph(f"<b>Incertidumbre Expandida Mayor:</b> {u_exp:.10f} {um}", est_cell),
                        Paragraph(f"<b>Unidad de Medida :</b> {um}", est_cell_bold)
                    ],
                    [
                        Paragraph(f"<b>Error Permisible / Incertidumbre:</b> {rel_val:.6f}", est_cell),
                        Paragraph(f"<b>Resultado Calibración:</b> {row.get('conformidad', 'Calibrado')}", est_cell)
                    ]
                ]
                t_extra = Table(data_extra, colWidths=[270, 270])
                t_extra.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,-1), COLOR_BG_HEADER),
                    ('BOX', (0,0), (-1,-1), 1, COLOR_BORDER),
                    ('INNERGRID', (0,0), (-1,-1), 0.5, COLOR_BORDER),
                    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                    ('TOPPADDING', (0,0), (-1,-1), 5),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 5),
                    ('LEFTPADDING', (0,0), (-1,-1), 8),
                    ('RIGHTPADDING', (0,0), (-1,-1), 8),
                ]))
                story.append(t_extra)
                story.append(Spacer(1, 8))

                # Bloque de Observaciones
                data_obs = [
                    [Paragraph("<b>OBSERVACIONES</b>", est_cell_bold)],
                    [Paragraph(f"{obs_text}", est_cell)]
                ]
                t_obs = Table(data_obs, colWidths=[540])
                t_obs.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,0), COLOR_BG_HEADER),
                    ('BOX', (0,0), (-1,-1), 1, COLOR_BORDER),
                    ('INNERGRID', (0,0), (-1,-1), 0.5, COLOR_BORDER),
                    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                    ('TOPPADDING', (0,0), (-1,-1), 5),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 5),
                    ('LEFTPADDING', (0,0), (-1,-1), 8),
                    ('RIGHTPADDING', (0,0), (-1,-1), 8),
                ]))
                story.append(t_obs)
                story.append(Spacer(1, 8))

                # Texto legal GUM
                texto_legal = (
                    "La incertidumbre se calculó usando un factor de cobertura <b>2</b> para un nivel de confianza de <b>95%</b> considerando como "
                    "tipo A: La variabilidad de mediciones, y como tipo B: la asociada al patrón, a la resolución del equipo, a la apreciación del "
                    "observador, a la temperatura y al coeficiente de expansión térmica."
                )
                story.append(Paragraph(texto_legal, est_legal))
                story.append(Spacer(1, 10))

                # Firmas Autorizadas
                tecnico_val = row.get('tecnico', 'PETIT CAMPOS ROBERT JOSE')
                aprobado_val = row.get('aprobado_por', 'Ing. Calidad Venvidrio')
                
                data_firmas = [
                    [
                        Paragraph(f"<b>Realizado por:</b> {tecnico_val}", est_cell),
                        Paragraph(f"<b>Aprobado por:</b> {aprobado_val}", est_cell)
                    ]
                ]
                t_firmas = Table(data_firmas, colWidths=[270, 270])
                t_firmas.setStyle(TableStyle([
                    ('BOX', (0,0), (-1,-1), 1, COLOR_BORDER),
                    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                    ('TOPPADDING', (0,0), (-1,-1), 6),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 6),
                    ('LEFTPADDING', (0,0), (-1,-1), 8),
                    ('RIGHTPADDING', (0,0), (-1,-1), 8),
                ]))
                story.append(t_firmas)
                
                doc.build(story, onFirstPage=header_footer, onLaterPages=header_footer)
                buffer.seek(0)
                return buffer.getvalue()

            if not df_eq.empty:
                ultimo = df_eq.iloc[-1]
                pdf_bytes = generar_informe_calibracion_formal(ultimo, serial_filtro, df_e)
                st.download_button(
                    label="📥 Descargar Informe de Calibración Oficial con Títulos Visibles (PDF)",
                    data=pdf_bytes,
                    file_name=f"Informe_Calibracion_{serial_filtro}.pdf",
                    mime="application/pdf",
                    key="btn_descargar_pdf_formal"
                )
        else:
            st.error("Libreria 'reportlab' no encontrada.")
    else:
        st.info("No hay registros disponibles para generar informes.")