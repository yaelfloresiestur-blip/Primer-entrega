import numpy as np
import pandas as pd
import streamlit as st

# Configuración de la página
st.set_page_config(
    page_title="Productividad de Pozos - IPR", page_icon="🛢️", layout="wide"
)

st.title("🛢️ Herramienta de Comportamiento de Afluencia (IPR)")
st.markdown(
    """
Esta aplicación calcula y genera las curvas de afluencia (IPR) para pozos petroleros 
utilizando los métodos de **Flujo Radial en Régimen Estacionario** y **Vogel**, 
basado en los fundamentos de ingeniería de yacimientos.
"""
)

# Menú lateral para seleccionar el método
metodo = st.sidebar.selectbox(
    "Seleccione el Método de Cálculo",
    [
        "Flujo Radial en Régimen Estacionario",
        "Método de Vogel (Aceite Saturado)",
    ],
)

if metodo == "Flujo Radial en Régimen Estacionario":
  st.header("📈 Flujo Radial en Régimen Estacionario (Yacimientos de Aceite)")
  st.markdown(
      "Calcula el gasto de aceite y el índice de productividad ($J^*$) bajo"
      " régimen estacionario ($p_e = \\text{cte}$)."
  )

  col1, col2 = st.columns(2)

  with col1:
    st.subheader("Parámetros del Yacimiento y Pozo")
    h = st.number_input("Espesor del yacimiento, h (ft)", value=53.0)
    k_o = st.number_input(
        "Permeabilidad efectiva al aceite, $k_o$ (md)", value=8.2
    )
    p_e = st.number_input("Presión del yacimiento, $p_e$ (psia)", value=5651.0)
    mu_o = st.number_input("Viscosidad del aceite, $\\mu_o$ (cp)", value=1.7)
    B_o = st.number_input(
        "Factor de volumen del aceite, $B_o$ (bbl/STB)", value=1.1
    )

  with col2:
    st.subheader("Geometría y Daño")
    r_e = st.number_input("Radio de drene, $r_e$ (ft)", value=2980.0)
    r_w = st.number_input("Radio del pozo, $r_w$ (ft)", value=0.328)
    S = st.number_input("Factor de daño, $S$", value=0.0)
    p_wf_min = st.number_input(
        "Presión mínima de fondo fluyente evaluada, $p_{wf}$ (psia)", value=0.0
    )

  if st.button("Calcular IPR - Flujo Estacionario"):
    # Validación del logaritmo
    if r_e <= r_w:
      st.error("El radio de drene ($r_e$) debe ser mayor que el radio del pozo ($r_w$).")
    else:
      # Cálculo del Índice de Productividad (J*) según la ecuación del Archivo 2
      # J* = (h * k_o) / (141.2 * B_o * mu_o * (ln(r_e / r_w) + S))
denominador = 141.2 * B_o * mu_o * (np.log(r_e / r_w) + S)
      J_star = (h * k_o) / denominador

      st.success(
          f"**Índice de Productividad ($J^*$):** {J_star:.4f} STB/day/psi"
      )

      # Generar datos para la curva IPR
      p_wf_vals = np.linspace(p_wf_min, p_e, 50)
      # q_o = J* * (p_e - p_wf)
      q_o_vals = J_star * (p_e - p_wf_vals)

      df_resultado = pd.DataFrame({
          "Presión de Fondo Fluyente, p_wf (psia)": p_wf_vals,
          "Gasto de Aceite, q_o (STB/d)": q_o_vals,
      })

      st.subheader("Resultados de la Curva IPR")
      st.line_chart(df_resultado.set_index("Presión de Fondo Fluyente, p_wf (psia)"))

      with st.expander("Ver tabla de datos detallada"):
        st.dataframe(df_resultado)

elif metodo == "Método de Vogel (Aceite Saturado)":
  st.header("📉 Método de Vogel (Yacimientos de Aceite Saturado)")
  st.markdown(
      "Calcula el comportamiento de afluencia no lineal para yacimientos"
      " saturados utilizando la correlación adimensional de Vogel."
  )

  col1, col2 = st.columns(2)

  with col1:
    st.subheader("Datos de la Prueba")
    p_R = st.number_input(
        "Presión media del yacimiento, $\\bar{p}_R$ (psia)", value=2500.0
    )
    p_wf_test = st.number_input(
        "Presión de fondo fluyendo de prueba, $p_{wf}$ (psia)", value=2000.0
    )
    q_test = st.number_input(
        "Gasto medido a $p_{wf}$ de prueba, $q_o$ (STB/d)", value=650.0
    )

  with col2:
    st.subheader("Opciones de Evaluación")
    p_wf_min_vogel = st.number_input(
        "Presión mínima para la curva, $p_{wf}$ (psia)", value=0.0
    )

  if st.button("Calcular Curva IPR de Vogel"):
    if p_wf_test >= p_R:
      st.error(
          "La presión de prueba ($p_{wf}$) debe ser menor que la presión del"
          " yacimiento ($\\bar{p}_R$) para aplicar Vogel directamente."
      )
    else:
      # Paso 1: Relación p_wf / p_R en la prueba
      rel_p = p_wf_test / p_R

      # Paso 2: Obtener la fracción q_o / q_omax mediante la ecuación de Vogel
      # q_o / q_omax = 1 - 0.2(p_wf/p_R) - 0.8(p_wf/p_R)^2
      frac_q = 1.0 - 0.2 * rel_p - 0.8 * (rel_p**2)

      # Paso 3: Calcular el potencial del pozo q_omax (AOF)
      q_omax = q_test / frac_q

      st.success(
          f"**Gasto Máximo o Potencial ($q_{omax}$ / AOF):**"
          f" {q_omax:.2f} STB/day"
      )

      # Paso 4: Generar la curva IPR completa
      p_wf_vals = np.linspace(p_wf_min_vogel, p_R, 50)
      rel_p_vals = p_wf_vals / p_R
      q_o_vals = q_omax * (
          1.0 - 0.2 * rel_p_vals - 0.8 * (rel_p_vals**2)
      )

      df_vogel = pd.DataFrame({
          "Presión de Fondo Fluyente, p_wf (psia)": p_wf_vals,
          "Gasto de Aceite, q_o (STB/d)": q_o_vals,
      })

      st.subheader("Curva IPR - Vogel")
      st.line_chart(df_vogel.set_index("Presión de Fondo Fluyente, p_wf (psia)"))

      with st.expander("Ver tabla de datos detallada"):
        st.dataframe(df_vogel)
