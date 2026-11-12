import numpy as np
import pandas as pd
import streamlit as st

# Configuración de la página
st.set_page_config(
    page_title="Productividad de Pozos - IPR Avanzado",
    page_icon="🛢️",
    layout="wide",
)

# Estilos CSS personalizados con fuentes grandes y botones rojos
st.markdown(
    """
    <style>
    /* Tamaño general del texto más grande en toda la app */
    html, body, [class*="css"] {
        font-size: 20px !important;
    }
    
    /* Títulos principales más grandes */
    h1 {
        font-size: 2.8rem !important;
        font-weight: 700 !important;
        color: #FF4B4B;
    }
    
    /* Subtítulos y encabezados de sección */
    h2, h3 {
        font-size: 2.1rem !important;
        font-weight: 600 !important;
    }
    
    /* Texto de las pestañas (tabs) más grande */
    .stTabs [data-baseweb="tab"] {
        font-size: 22px !important;
        font-weight: 600 !important;
        padding: 14px 26px !important;
    }
    
    /* Párrafos, etiquetas y textos descriptivos */
    p, label, .stMarkdown, .stNumberInput label {
        font-size: 1.25rem !important;
    }
    
    /* Personalización de los botones principales (Fondo rojo, borde rojo y texto blanco) */
    .stButton > button {
        background-color: #E63946 !important;
        color: white !important;
        border: 2px solid #E63946 !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-size: 1.2rem !important;
        padding: 0.5rem 1rem !important;
    }
    
    /* Efecto al pasar el cursor sobre el botón */
    .stButton > button:hover {
        background-color: #C52233 !important;
        border: 2px solid #C52233 !important;
        color: white !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🛢️ Herramienta Avanzada de Comportamiento de Afluencia (IPR)")
st.markdown(
    """
Esta aplicación calcula y genera las curvas de afluencia (IPR) para pozos petroleros 
utilizando los métodos de **Flujo Radial Estacionario**, **Vogel**, **Standing (con Eficiencia de Flujo / Daño)** 
y **Jones, Blount y Glaze (JBG - Turbulencia y Daño)**, manteniendo todos los apartados visibles al mismo tiempo.

**Creadores:**  
* Flores Carrillo Yael  
* Salas Navarro Agueda Jaqueline
"""
)

# Creación de pestañas para mostrar todos los métodos sin menús desplegables
tab1, tab2, tab3, tab4 = st.tabs([
    "1. Flujo Estacionario",
    "2. Método de Vogel",
    "3. Método de Standing",
    "4. Método JBG",
])

with tab1:
  st.header("📈 Flujo Radial en Régimen Estacionario (Yacimientos de Aceite)")
  st.markdown(
      "Calcula el gasto de aceite y el índice de productividad ($J^*$) bajo"
      " régimen estacionario ($p_e = \\text{cte}$)."
  )

  col1, col2 = st.columns(2)
  with col1:
    h = st.number_input("Espesor del yacimiento, h (ft)", value=53.0, key="h1")
    k_o = st.number_input(
        "Permeabilidad efectiva al aceite, $k_o$ (md)", value=8.2, key="ko1"
    )
    p_e = st.number_input(
        "Presión del yacimiento, $p_e$ (psia)", value=5651.0, key="pe1"
    )
    mu_o = st.number_input(
        "Viscosidad del aceite, $\\mu_o$ (cp)", value=1.7, key="mu1"
    )
    B_o = st.number_input(
        "Factor de volumen del aceite, $B_o$ (bbl/STB)", value=1.1, key="bo1"
    )
  with col2:
    r_e = st.number_input(
        "Radio de drene, $r_e$ (ft)", value=2980.0, key="re1"
    )
    r_w = st.number_input("Radio del pozo, $r_w$ (ft)", value=0.328, key="rw1")
    S = st.number_input("Factor de daño, $S$", value=0.0, key="s1")
    p_wf_min = st.number_input(
        "Presión mínima de fondo fluyente evaluada, $p_{wf}$ (psia)",
        value=0.0,
        key="pwfmin1",
    )

  if st.button("Calcular IPR - Flujo Estacionario", key="btn1"):
    if r_e <= r_w:
      st.error("El radio de drene ($r_e$) debe ser mayor que el radio del pozo ($r_w$).")
    else:
      denominador = 141.2 * B_o * mu_o * (np.log(r_e / r_w) + S)
      J_star = (h * k_o) / denominador
      st.success(f"**Índice de Productividad (J*):** {J_star:.4f} STB/day/psi")

      p_wf_vals = np.linspace(p_wf_min, p_e, 50)
      q_o_vals = J_star * (p_e - p_wf_vals)

      df_resultado = pd.DataFrame({
          "Gasto de Aceite, q_o (STB/d)": q_o_vals,
          "Presión de Fondo Fluyente, p_wf (psia)": p_wf_vals,
      })
      st.subheader("Curva IPR (Eje X: Gasto de Aceite | Eje Y: Presión)")
      st.line_chart(df_resultado.set_index("Gasto de Aceite, q_o (STB/d)"))

      with st.expander("Ver tabla de datos detallada"):
        st.dataframe(df_resultado)

with tab2:
  st.header("📉 Método de Vogel (Yacimientos de Aceite Saturado)")
  st.markdown(
      "Calcula el comportamiento de afluencia no lineal para yacimientos"
      " saturados utilizando la correlación adimensional de Vogel."
  )

  col1, col2 = st.columns(2)
  with col1:
    p_R = st.number_input(
        "Presión media del yacimiento, p_R (psia)", value=2500.0, key="pr2"
    )
    p_wf_test = st.number_input(
        "Presión de fondo fluyendo de prueba, p_wf (psia)",
        value=2000.0,
        key="pwftest2",
    )
    q_test = st.number_input(
        "Gasto medido a p_wf de prueba, q_o (STB/d)", value=650.0, key="qtest2"
    )
  with col2:
    p_wf_min_vogel = st.number_input(
        "Presión mínima para la curva, p_wf (psia)",
        value=0.0,
        key="pwfmin2",
    )

  if st.button("Calcular Curva IPR de Vogel", key="btn2"):
    if p_wf_test >= p_R:
      st.error(
          "La presión de prueba ($p_{wf}$) debe ser menor que la presión del"
          " yacimiento (p_R) para aplicar Vogel directamente."
      )
    else:
      rel_p = p_wf_test / p_R
      frac_q = 1.0 - (0.2 * rel_p) - (0.8 * (rel_p**2))
      q_omax = q_test / frac_q
      st.success(
          f"**Gasto Máximo o Potencial (q_omax / AOF):** {q_omax:.2f} STB/day"
      )

      p_wf_vals = np.linspace(p_wf_min_vogel, p_R, 50)
      rel_p_vals = p_wf_vals / p_R
      q_o_vals = q_omax * (
          1.0 - (0.2 * rel_p_vals) - (0.8 * (rel_p_vals**2))
      )

      df_vogel = pd.DataFrame({
          "Gasto de Aceite, q_o (STB/d)": q_o_vals,
          "Presión de Fondo Fluyente, p_wf (psia)": p_wf_vals,
      })
      st.subheader(
          "Curva IPR - Vogel (Eje X: Gasto de Aceite | Eje Y: Presión)"
      )
      st.line_chart(df_vogel.set_index("Gasto de Aceite, q_o (STB/d)"))

      with st.expander("Ver tabla de datos detallada"):
        st.dataframe(df_vogel)

with tab3:
  st.header("📊 Método de Standing (Considerando Daño y Eficiencia de Flujo)")
  st.markdown(
      "Extensión de Vogel que incorpora la **Eficiencia de Flujo (EF / FE)**"
      " para pozos dañados ($EF < 1$) o estimulados ($EF > 1$)."
  )

  col1, col2 = st.columns(2)
  with col1:
    p_R_std = st.number_input(
        "Presión media del yacimiento, p_R (psia)",
        value=3000.0,
        key="p_R_std",
    )
    p_wf_std = st.number_input(
        "Presión de fondo fluyendo de prueba, p_wf (psia)",
        value=2000.0,
        key="p_wf_std",
    )
    q_std = st.number_input(
        "Gasto medido a p_wf, q_o (bpd)", value=800.0, key="q_std"
    )
  with col2:
    ef = st.number_input(
        "Eficiencia de Flujo, EF (o FE)",
        value=0.6,
        min_value=0.1,
        max_value=3.0,
        step=0.1,
        key="ef3",
    )
    p_wf_min_std = st.number_input(
        "Presión mínima para la curva, p_wf (psia)",
        value=0.0,
        key="p_wf_min_std",
    )

  if st.button("Calcular IPR - Standing", key="btn3"):
    if p_wf_std >= p_R_std:
      st.error(
          "La presión de prueba ($p_{wf}$) debe ser menor que la presión del"
          " yacimiento ($\bar{p}_R$)."
      )
    else:
      term = 1.0 - (p_wf_std / p_R_std)
      denom = (1.8 * ef * term) - (0.8 * (ef**2) * (term**2))
      if denom <= 0:
        st.error(
            "Los valores ingresados generan un denominador no válido en la"
            " ecuación de Standing. Revise la EF y las presiones."
        )
      else:
        q_omax_ef1 = q_std / denom
        if ef <= 1.0:
          q_omax_ef = q_omax_ef1 * ((1.8 * ef) - (0.8 * (ef**2)))
        else:
          q_omax_ef = q_omax_ef1 * (0.624 + (0.376 * ef))

        st.success(
            f"**Potencial sin daño (q_omax, EF=1):** {q_omax_ef1:.2f} bpd"
            f" | **Potencial con EF={ef}:** {q_omax_ef:.2f} bpd"
        )

        p_wf_vals = np.linspace(p_wf_min_std, p_R_std, 50)
        terms = 1.0 - (p_wf_vals / p_R_std)
        q_o_vals = q_omax_ef1 * (
            (1.8 * ef * terms) - (0.8 * (ef**2) * (terms**2))
        )
        q_o_vals = np.maximum(q_o_vals, 0)

        df_std = pd.DataFrame({
            f"Gasto de Aceite, q_o (bpd) [EF={ef}]": q_o_vals,
            "Presión de Fondo Fluyente, p_wf (psia)": p_wf_vals,
        })
        st.subheader(
            "Curva IPR - Standing (Eje X: Gasto de Aceite | Eje Y: Presión)"
        )
        st.line_chart(df_std.set_index(f"Gasto de Aceite, q_o (bpd) [EF={ef}]"))

        with st.expander("Ver tabla de datos detallada"):
          st.dataframe(df_std)

with tab4:
  st.header("⚡ Método de Jones, Blount y Glaze (JBG - Turbulencia y Daño)")
  st.markdown(
      "Permite diferenciar las caídas de presión por flujo turbulento (no"
      " darciano) y por daño a la formación mediante una prueba de"
      " multi-gasto."
  )

  p_R_jbg = st.number_input(
