import numpy as np
import pandas as pd
import streamlit as st

# Configuración de la página
st.set_page_config(
    page_title="Productividad de Pozos - IPR Avanzado",
    page_icon="🛢️",
    layout="wide",
)

st.title("🛢️ Herramienta Avanzada de Comportamiento de Afluencia (IPR)")
st.markdown(
    """
Esta aplicación calcula y genera las curvas de afluencia (IPR) para pozos petroleros 
utilizando los métodos de **Flujo Radial Estacionario**, **Vogel**, **Standing (con Eficiencia de Flujo / Daño)** 
y **Jones, Blount y Glaze (JBG - Turbulencia y Daño)**, manteniendo todos los apartados visibles al mismo tiempo.
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

  if st.button("Calcular IPR - Flujo Estacionario"):
    if r_e <= r_w:
      st.error("El radio de drene ($r_e$) debe ser mayor que el radio del pozo ($r_w$).")
    else:
      denominador = 141.2 * B_o * mu_o * (np.log(r_e / r_w) + S)
      J_star = (h * k_o) / denominador
      st.success(f"**Índice de Productividad (J*):** {J_star:.4f} STB/day/psi")

      p_wf_vals = np.linspace(p_wf_min, p_e, 50)
      q_o_vals = J_star * (p_e - p_wf_vals)
      df_resultado = pd.DataFrame({
          "Presión de Fondo Fluyente, p_wf (psia)": p_wf_vals,
          "Gasto de Aceite, q_o (STB/d)": q_o_vals,
      })
      st.subheader("Resultados de la Curva IPR")
      st.line_chart(df_resultado.set_index("Presión de Fondo Fluyente, p_wf (psia)"))
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

  if st.button("Calcular Curva IPR de Vogel"):
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
          "Presión de Fondo Fluyente, p_wf (psia)": p_wf_vals,
          "Gasto de Aceite, q_o (STB/d)": q_o_vals,
      })
      st.subheader("Curva IPR - Vogel")
      st.line_chart(df_vogel.set_index("Presión de Fondo Fluyente, p_wf (psia)"))
      with st.expander("Ver tabla de datos detallada"):
        st.dataframe(df_vogel)

with tab3:
  st.header("📊 Método de Standing (Considerando Daño y Eficiencia de Flujo)")
  st.markdown(
      "Extensión de Vogel que incorpora la **Eficiencia de Flujo (EF / FE)**"
      " para pozos dañados ($EF < 1$) o estimulados ($EF > 1$)[cite: 92, 93]."
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

  if st.button("Calcular IPR - Standing"):
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
            "Presión de Fondo Fluyente, p_wf (psia)": p_wf_vals,
            f"Gasto de Aceite, q_o (bpd) [EF={ef}]": q_o_vals,
        })
        st.subheader("Curva IPR - Método de Standing")
        st.line_chart(df_std.set_index("Presión de Fondo Fluyente, p_wf (psia)"))
        with st.expander("Ver tabla de datos detallada"):
          st.dataframe(df_std)

with tab4:
  st.header("⚡ Método de Jones, Blount y Glaze (JBG - Turbulencia y Daño)")
  st.markdown(
      "Permite diferenciar las caídas de presión por flujo turbulento (no"
      " darciano) y por daño a la formación mediante una prueba de"
      " multi-gasto[cite: 102, 103, 104]."
  )

  p_R_jbg = st.number_input(
      "Presión media del yacimiento, p_R (psia)", value=4500.0, key="pr4"
  )
  st.markdown(
      "Ingrese los datos de la prueba de producción (multi-gasto /"
      " flow-after-flow)[cite: 104]:"
  )

  df_default = pd.DataFrame({
      "Gasto, q_o (bpd)": [550.0, 670.0, 750.0, 820.0],
      "Presión p_wf (psia)": [4474.0, 4465.0, 4459.0, 4452.0],
  })
  # Corregido con num_rows="dynamic"
  edited_df = st.data_editor(df_default, num_rows="dynamic", key="editor4")

  if st.button("Calcular JBG y Diagnóstico"):
    if len(edited_df) < 2:
      st.error(
          "Se requieren al menos 2 puntos de prueba para aplicar el método"
          " JBG."
      )
    else:
      q_arr = edited_df["Gasto, q_o (bpd)"].values.astype(float)
      pwf_arr = edited_df["Presión p_wf (psia)"].values.astype(float)

      if np.any(q_arr <= 0):
        st.error("Los gastos deben ser mayores a cero.")
      else:
        y_vals = (p_R_jbg - pwf_arr) / q_arr
        a, b = np.polyfit(q_arr, y_vals, 1)

        if a <= 0:
          q_max = p_R_jbg / b if b > 0 else 0
        else:
          discriminant = (b**2) + (4 * a * p_R_jbg)
          q_max = (-b + np.sqrt(discriminant)) / (2 * a)

        b_prime = b + (a * q_max)
        ratio_bb = b_prime / b if b != 0 else 0

        st.success(
            f"**Coeficiente de Turbulencia (a):** {a:.6f} (psi/bpd²)\n\n"
            f"**Indicador de Daño (b):** {b:.4f} (psi/bpd)\n\n"
            f"**Gasto Máximo / Potencial (q_max):** {q_max:.2f} bpd\n\n"
            f"**Parámetro b':** {b_prime:.4f} | **Relación b'/b:**"
            f" {ratio_bb:.2f}"
        )

        st.subheader("📋 Diagnóstico de la Terminación (Criterios JBG)")
        diag_msg = []
        if b <= 0.05:
          diag_msg.append(
              "✅ **Daño:** El pozo **no presenta daño** a la formación ($b"
              " \\le 0.05$)[cite: 104]."
          )
        else:
          diag_msg.append(
              "⚠️ **Daño:** El pozo **presenta daño** a la formación ($b >"
              " 0.05$)[cite: 104]."
          )

        if ratio_bb <= 2:
          diag_msg.append(
              "✅ **Turbulencia:** La turbulencia es baja o despreciable"
              " ($b'/b \\le 2$)[cite: 104]."
          )
        else:
          diag_msg.append(
              "⚠️ **Turbulencia:** Existe un efecto importante de flujo"
              " turbulento/no darciano ($b'/b > 2$)[cite: 104]."
          )

        if b <= 0.05 and ratio_bb <= 2:
          diag_msg.append(
              "🌟 **Recomendación:** La terminación del pozo es **muy buena**"
              "[cite: 104]."
          )
        elif b <= 0.05 and ratio_bb > 2:
          diag_msg.append(
              "💡 **Recomendación:** No se recomienda estimular. La baja"
              " productividad se debe a área insuficiente del intervalo"
              " disparado. Se sugiere **incrementar el área disparada**[cite: 104]."
          )
        elif b > 0.05 and ratio_bb <= 2:
          diag_msg.append(
              "💡 **Recomendación:** Se recomienda realizar un trabajo de"
              " **estimulación**[cite: 104]."
          )

        for msg in diag_msg:
          st.markdown(msg)

        q_curve = np.linspace(0, q_max, 50)
        pwf_curve = p_R_jbg - ((a * (q_curve**2)) + (b * q_curve))
        pwf_curve = np.maximum(pwf_curve, 0)

        df_jbg = pd.DataFrame(
            {"Gasto de Aceite, q_o (bpd)": q_curve, "Presión p_wf (psia)": pwf_curve}
        )
        st.subheader("Curva IPR - Método JBG")
        st.line_chart(df_jbg.set_index("Gasto de Aceite, q_o (bpd)"))
        with st.expander("Ver tabla de datos detallada"):
          st.dataframe(df_jbg)
