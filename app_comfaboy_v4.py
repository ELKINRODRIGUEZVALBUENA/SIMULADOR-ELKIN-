import streamlit as st
import pandas as pd

# Configuración inicial de la página
st.set_page_config(page_title="Simulador de Subsidios - Comfaboy", layout="wide")
st.title("🏨 Análisis de Servicio de Alojamiento")

# --- PASO 1: DATOS GENERALES Y CAPACIDAD ---
st.header("1. Datos Generales y Capacidad")
st.write("Modifica los parámetros para calcular la capacidad instalada y las noches base vendidas.")

col1, col2, col3 = st.columns(3)

with col1:
    num_habitaciones = st.number_input("Número de Habitaciones", min_value=1, value=10, step=1)
with col2:
    dias_operacion = st.number_input("Días de Operación al Año", min_value=1, value=365, step=1)
with col3:
    ocupacion_base_pct = st.number_input("Ocupación Base (%)", min_value=0.0, max_value=100.0, value=50.0, step=1.0)
    ocupacion_base = ocupacion_base_pct / 100.0

# Cálculos de capacidad
capacidad_maxima = num_habitaciones * dias_operacion
noches_vendidas = capacidad_maxima * ocupacion_base

st.markdown("### 📌 Resumen de Capacidad")
resumen_capacidad = pd.DataFrame({
    "Parámetro": ["Capacidad Máxima Teórica (Noches-Habitación)", "Noches-Habitación Base Vendidas"],
    "Valor": [f"{capacidad_maxima:,.0f}", f"{noches_vendidas:,.0f}"],
    "Unidad": ["Noches/Año", "Noches/Año"]
})
st.table(resumen_capacidad)


# --- PASO 2: ESTRUCTURA DE COSTOS Y TARIFA PLENA (CATEGORÍA C) ---
st.markdown("---")
st.header("2. Estructura de Costos y Tarifa Plena (Categoría C)")
st.write("Establece el costo y la tarifa base en función de la proyección de ventas calculada en el Paso 1.")

col1, col2, col3 = st.columns(3)

with col1:
    costos_fijos = st.number_input("Costos Fijos Anuales (CF) [$]", min_value=0.0, value=120000000.0, step=1000000.0)
with col2:
    costo_var_unitario = st.number_input("Costo Variable Unitario (CVU) por noche [$]", min_value=0.0, value=30000.0, step=1000.0)
with col3:
    recargo_tarifa_d_pct = st.number_input("Recargo Tarifa D (%)", min_value=0.0, max_value=100.0, value=10.0, step=1.0)
    recargo_tarifa_d = recargo_tarifa_d_pct / 100.0

# Cálculos de costos y tarifas
if noches_vendidas > 0:
    cf_unitario = costos_fijos / noches_vendidas
    cv_totales = costo_var_unitario * noches_vendidas
    costo_total_ocupacion = costos_fijos + cv_totales
    tarifa_c = costo_total_ocupacion / noches_vendidas
else:
    cf_unitario = 0
    cv_totales = 0
    costo_total_ocupacion = costos_fijos
    tarifa_c = 0

tarifa_d = tarifa_c * (1 + recargo_tarifa_d)

st.markdown("### 📌 Resumen de Costos y Tarifas")
resumen_costos = pd.DataFrame({
    "Concepto": ["Costos Fijos Anuales (CF)", "Costos Variables Unitarios (CVU)", "Costo Total a Ocupación Tarifa C", "TARIFA D"],
    "Valor Anual": [f"$ {costos_fijos:,.0f}", f"$ {cv_totales:,.0f}", f"$ {costo_total_ocupacion:,.0f}", f"{recargo_tarifa_d_pct:.0f}%"],
    "Costo Unitario (por noche)": [f"$ {cf_unitario:,.0f}", f"$ {costo_var_unitario:,.0f}", f"$ {tarifa_c:,.0f}", f"$ {tarifa_d:,.0f}"]
})
st.table(resumen_costos)


# --- PASO 3: MATRIZ DE TARIFAS POR CATEGORÍA ---
st.markdown("---")
st.header("3. Matriz de Tarifas por Categoría")
st.write("Aplica los porcentajes de subsidio para las categorías A y B calculando la tarifa final y el valor subsidiado.")

col1, col2 = st.columns(2)

with col1:
    subsidio_a_pct = st.number_input("Subsidio Categoría A (%)", min_value=0.0, max_value=100.0, value=80.0, step=1.0)
    subsidio_a = subsidio_a_pct / 100.0
with col2:
    subsidio_b_pct = st.number_input("Subsidio Categoría B (%)", min_value=0.0, max_value=100.0, value=70.0, step=1.0)
    subsidio_b = subsidio_b_pct / 100.0

# Cálculos de tarifas con subsidio
tarifa_a = tarifa_c * (1 - subsidio_a)
valor_subsidio_a = tarifa_c * subsidio_a

tarifa_b = tarifa_c * (1 - subsidio_b)
valor_subsidio_b = tarifa_c * subsidio_b

st.markdown("### 📌 Matriz de Tarifas")
matriz_tarifas = pd.DataFrame({
    "Categoría": ["Categoría A", "Categoría B", "Categoría C", "Categoría D (No Afiliados)"],
    "SUBSIDIO": [f"{subsidio_a_pct:.0f}%", f"{subsidio_b_pct:.0f}%", "0%", "0%"],
    "Tarifa por Noche": [f"$ {tarifa_a:,.2f}", f"$ {tarifa_b:,.2f}", f"$ {tarifa_c:,.2f}", f"$ {tarifa_d:,.2f}"],
    "Valor Subsidio": [f"$ {valor_subsidio_a:,.2f}", f"$ {valor_subsidio_b:,.2f}", "$ 0.00", "$ 0.00"]
})
st.table(matriz_tarifas)


# --- PASO 4: SIMULACIÓN DE ESCENARIOS FINANCIEROS ---
st.markdown("---")
st.header("4. Simulación de Escenarios Financieros")
st.write("Modifica directamente en la tabla la cantidad de noches vendidas por categoría. Los indicadores financieros y el total de cobertura se recalcularán al instante.")

df_cobertura_base = pd.DataFrame({
    "Categoría": ["A", "B", "C", "D"],
    "Escenario Inicial": [1265, 280, 210, 70],
    "Escenario 1 (+20%)": [1518, 336, 252, 84],
    "Escenario 3 (Solo A)": [2190, 0, 0, 0],
    "Escenario 4 (A y B)": [1790, 400, 0, 0],
    "Escenario 5 (Solo C)": [0, 0, 2190, 0]
}).set_index("Categoría")

st.subheader("Cobertura Real y Escenarios (Modificable)")
# Tabla editable para ingresar los valores de cada categoría
df_cobertura = st.data_editor(df_cobertura_base, use_container_width=True)

# Cálculo y visualización de la fila TOTAL COBERTURA
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
    
    cv_totales_escenario = noches_totales * costo_var_unitario
    ct_escenario = costos_fijos + cv_totales_escenario
    
    ingresos_tarifas = (n_a * tarifa_a) + (n_b * tarifa_b) + (n_c * tarifa_c) + (n_d * tarifa_d)
    subsidios_otorgados = (n_a * valor_subsidio_a) + (n_b * valor_subsidio_b)
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
