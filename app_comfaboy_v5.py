import streamlit as st
import pandas as pd

# Configuración inicial de la página
st.set_page_config(page_title="Simulador de Subsidios - Comfaboy", layout="wide")
st.title("🏨 Análisis de Servicio de Alojamiento - Comparativo Línea Base vs Simulación")

# --- 0. CONSTANTES DE LA LÍNEA BASE (VALORES FIJOS) ---
HAB_BASE = 10
DIAS_BASE = 365
OCUPACION_PCT_BASE = 0.50
CF_BASE = 120000000.0
CVU_BASE = 30000.0
RECARGO_D_BASE = 0.10
SUB_A_BASE = 0.80
SUB_B_BASE = 0.70

# Cálculos de Línea Base
cap_max_base = HAB_BASE * DIAS_BASE
noches_vendidas_base = cap_max_base * OCUPACION_PCT_BASE

cf_unitario_base = CF_BASE / noches_vendidas_base if noches_vendidas_base > 0 else 0
cv_totales_base = CVU_BASE * noches_vendidas_base
ct_ocupacion_base = CF_BASE + cv_totales_base
tarifa_c_base = ct_ocupacion_base / noches_vendidas_base if noches_vendidas_base > 0 else 0
tarifa_d_base = tarifa_c_base * (1 + RECARGO_D_BASE)

tarifa_a_base = tarifa_c_base * (1 - SUB_A_BASE)
v_sub_a_base = tarifa_c_base * SUB_A_BASE
tarifa_b_base = tarifa_c_base * (1 - SUB_B_BASE)
v_sub_b_base = tarifa_c_base * SUB_B_BASE


# --- PASO 1: DATOS GENERALES Y CAPACIDAD ---
st.header("1. Datos Generales y Capacidad")
st.write("Modifica los parámetros para ver cómo cambian respecto a la línea base (50%).")

col1, col2, col3 = st.columns(3)
with col1:
    num_habitaciones = st.number_input("Número de Habitaciones", min_value=1, value=HAB_BASE, step=1)
with col2:
    dias_operacion = st.number_input("Días de Operación al Año", min_value=1, value=DIAS_BASE, step=1)
with col3:
    ocupacion_base_pct = st.number_input("Ocupación Simulada (%)", min_value=0.0, max_value=100.0, value=50.0, step=1.0)
    ocupacion_sim = ocupacion_base_pct / 100.0

capacidad_max_sim = num_habitaciones * dias_operacion
noches_vendidas_sim = capacidad_max_sim * ocupacion_sim

st.markdown("### 📌 Comparativo de Capacidad")
resumen_capacidad = pd.DataFrame({
    "Escenario": ["Línea Base Fija", "Simulación Modificada"],
    "Ocupación (%)": [f"{OCUPACION_PCT_BASE*100:.0f}%", f"{ocupacion_base_pct:.0f}%"],
    "Capacidad Máxima Teórica": [f"{cap_max_base:,.0f}", f"{capacidad_max_sim:,.0f}"],
    "Noches Base Vendidas": [f"{noches_vendidas_base:,.0f}", f"{noches_vendidas_sim:,.0f}"]
}).set_index("Escenario")
st.table(resumen_capacidad)


# --- PASO 2: ESTRUCTURA DE COSTOS Y TARIFA PLENA ---
st.markdown("---")
st.header("2. Estructura de Costos y Tarifa Plena (Categoría C)")
st.write("Observa cómo varía el costo y la tarifa C al cambiar tus proyecciones.")

col1, col2, col3 = st.columns(3)
with col1:
    costos_fijos = st.number_input("Costos Fijos Anuales (CF) [$]", min_value=0.0, value=CF_BASE, step=1000000.0)
with col2:
    costo_var_unitario = st.number_input("Costo Variable Unitario (CVU) [$]", min_value=0.0, value=CVU_BASE, step=1000.0)
with col3:
    recargo_tarifa_d_pct = st.number_input("Recargo Tarifa D (%)", min_value=0.0, max_value=100.0, value=RECARGO_D_BASE*100, step=1.0)
    recargo_tarifa_d = recargo_tarifa_d_pct / 100.0

if noches_vendidas_sim > 0:
    cf_unitario_sim = costos_fijos / noches_vendidas_sim
    cv_totales_sim = costo_var_unitario * noches_vendidas_sim
    ct_ocupacion_sim = costos_fijos + cv_totales_sim
    tarifa_c_sim = ct_ocupacion_sim / noches_vendidas_sim
else:
    cf_unitario_sim = 0
    cv_totales_sim = 0
    ct_ocupacion_sim = costos_fijos
    tarifa_c_sim = 0

tarifa_d_sim = tarifa_c_sim * (1 + recargo_tarifa_d)

st.markdown("### 📌 Comparativo de Costos y Tarifas")
resumen_costos = pd.DataFrame({
    "Concepto": [
        "Costos Fijos Anuales (CF)", 
        "Costos Variables Totales (CV)", 
        "Costo Total a Ocupación", 
        "TARIFA C (Plena / Costo por noche)", 
        "TARIFA D (No Afiliados)"
    ],
    "Línea Base (Fija al 50%)": [
        f"$ {CF_BASE:,.0f}", f"$ {cv_totales_base:,.0f}", f"$ {ct_ocupacion_base:,.0f}", 
        f"$ {tarifa_c_base:,.0f}", f"$ {tarifa_d_base:,.0f}"
    ],
    "Simulación (Modificada)": [
        f"$ {costos_fijos:,.0f}", f"$ {cv_totales_sim:,.0f}", f"$ {ct_ocupacion_sim:,.0f}", 
        f"$ {tarifa_c_sim:,.0f}", f"$ {tarifa_d_sim:,.0f}"
    ]
}).set_index("Concepto")
st.table(resumen_costos)


# --- PASO 3: MATRIZ DE TARIFAS POR CATEGORÍA ---
st.markdown("---")
st.header("3. Matriz de Tarifas por Categoría")

col1, col2 = st.columns(2)
with col1:
    subsidio_a_pct = st.number_input("Subsidio Categoría A (%)", min_value=0.0, max_value=100.0, value=SUB_A_BASE*100, step=1.0)
    subsidio_a = subsidio_a_pct / 100.0
with col2:
    subsidio_b_pct = st.number_input("Subsidio Categoría B (%)", min_value=0.0, max_value=100.0, value=SUB_B_BASE*100, step=1.0)
    subsidio_b = subsidio_b_pct / 100.0

tarifa_a_sim = tarifa_c_sim * (1 - subsidio_a)
v_sub_a_sim = tarifa_c_sim * subsidio_a
tarifa_b_sim = tarifa_c_sim * (1 - subsidio_b)
v_sub_b_sim = tarifa_c_sim * subsidio_b

st.markdown("### 📌 Comparativo de Tarifas y Subsidios por Categoría")
matriz_tarifas = pd.DataFrame({
    "Categoría": ["Categoría A", "Categoría B", "Categoría C", "Categoría D"],
    "Subsidio (Base)": [f"{SUB_A_BASE*100:.0f}%", f"{SUB_B_BASE*100:.0f}%", "0%", "0%"],
    "Subsidio (Sim)": [f"{subsidio_a_pct:.0f}%", f"{subsidio_b_pct:.0f}%", "0%", "0%"],
    "Tarifa (Base)": [f"$ {tarifa_a_base:,.2f}", f"$ {tarifa_b_base:,.2f}", f"$ {tarifa_c_base:,.2f}", f"$ {tarifa_d_base:,.2f}"],
    "Tarifa (Sim)": [f"$ {tarifa_a_sim:,.2f}", f"$ {tarifa_b_sim:,.2f}", f"$ {tarifa_c_sim:,.2f}", f"$ {tarifa_d_sim:,.2f}"],
    "V. Subsidio (Base)": [f"$ {v_sub_a_base:,.2f}", f"$ {v_sub_b_base:,.2f}", "$ 0.00", "$ 0.00"],
    "V. Subsidio (Sim)": [f"$ {v_sub_a_sim:,.2f}", f"$ {v_sub_b_sim:,.2f}", "$ 0.00", "$ 0.00"]
}).set_index("Categoría")
st.table(matriz_tarifas)


# --- PASO 4: SIMULACIÓN DE ESCENARIOS FINANCIEROS ---
st.markdown("---")
st.header("4. Simulación de Escenarios Financieros (Con parámetros simulados)")
st.write("Esta tabla aplica tus Tarifas y Costos SIMULADOS a la distribución de noches. Puedes modificar las noches para ver el impacto total.")

df_cobertura_base = pd.DataFrame({
    "Categoría": ["A", "B", "C", "D"],
    "Escenario Inicial": [1265, 280, 210, 70],
    "Escenario 1 (+20%)": [1518, 336, 252, 84],
    "Escenario 3 (Solo A)": [2190, 0, 0, 0],
    "Escenario 4 (A y B)": [1790, 400, 0, 0],
    "Escenario 5 (Solo C)": [0, 0, 2190, 0]
}).set_index("Categoría")

st.subheader("Cobertura Real y Escenarios (Modificable)")
df_cobertura = st.data_editor(df_cobertura_base, use_container_width=True)

totales_cobertura = df_cobertura.sum()
df_totales = pd.DataFrame(totales_cobertura).T
df_totales.index = ["TOTAL COBERTURA"]
st.dataframe(df_totales.style.format("{:,.0f}"), use_container_width=True)

resultados_escenarios = {}

for escenario in df_cobertura.columns:
    n_a = df_cobertura.loc["A", escenario]
    n_b = df_cobertura.loc["B", escenario]
    n_c = df_cobertura.loc["C", escenario]
    n_d = df_cobertura.loc["D", escenario]
    
    noches_totales = n_a + n_b + n_c + n_d
    
    # Costos con variables simuladas
    cv_totales_escenario = noches_totales * costo_var_unitario
    ct_escenario = costos_fijos + cv_totales_escenario
    
    # Ingresos con tarifas simuladas
    ingresos_tarifas = (n_a * tarifa_a_sim) + (n_b * tarifa_b_sim) + (n_c * tarifa_c_sim) + (n_d * tarifa_d_sim)
    subsidios_otorgados = (n_a * v_sub_a_sim) + (n_b * v_sub_b_sim)
    ingresos_totales = ingresos_tarifas + subsidios_otorgados
    
    resultado_operativo = ingresos_tarifas - ct_escenario
    
    subsidio_demanda = subsidios_otorgados
    subsidio_oferta = -(resultado_operativo + subsidio_demanda) 
    
    resultados_escenarios[escenario] = [
        noches_totales, costos_fijos, cv_totales_escenario, ct_escenario, 
        ingresos_tarifas, subsidios_otorgados, ingresos_totales, 
        resultado_operativo, subsidio_demanda, subsidio_oferta
    ]

df_resultados_financieros = pd.DataFrame(resultados_escenarios, index=[
    "Noches Vendidas Anuales", "Costos Fijos (CF)", "Costos Variables Totales (CV)",
    "Costos Totales (CF + CV)", "Ingresos por tarifas", "Subsidios Otorgados (Caja)",
    "Ingresos Totales (Tarifas + Subsidios)", "Resultado Operativo (Superávit / Déficit)",
    "SUBSIDIO A LA DEMANDA", "SUBSIDIO A LA OFERTA"
])

st.subheader("Resultados de la Simulación")
st.dataframe(df_resultados_financieros.style.format(
    formatter={col: "${:,.2f}" for col in df_resultados_financieros.columns}
).format(
    formatter={col: "{:,.0f}" for col in df_resultados_financieros.columns}, 
    subset=pd.IndexSlice[["Noches Vendidas Anuales"], :]
), use_container_width=True)
