import streamlit as st
import pandas as pd

# Configuración inicial de la página
st.set_page_config(page_title="Simulador de Subsidios - Comfaboy", layout="wide")
st.title("🏨 Análisis de Servicio de Alojamiento - Escenarios y Variaciones")

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
    "Línea Base (Fija)": [
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


# --- PASO 4: SIMULACIÓN DE ESCENARIOS FINANCIEROS (CONGELADOS VS SIMULADOS) ---
st.markdown("---")
st.header("4. Simulación de Escenarios y Variaciones")
st.write("La tabla inferior contiene los escenarios base congelados. Modifica las noches en la tabla para calcular la simulación con tus nuevas tarifas y obtener la variación absoluta y porcentual.")

# Coberturas Congeladas (Línea Base)
df_cobertura_base_fija = pd.DataFrame({
    "Categoría": ["A", "B", "C", "D"],
    "Escenario Inicial": [1265, 280, 210, 70],
    "Escenario 1 (+20%)": [1518, 336, 252, 84],
    "Escenario 3 (Solo A)": [2190, 0, 0, 0],
    "Escenario 4 (A y B)": [1790, 400, 0, 0],
    "Escenario 5 (Solo C)": [0, 0, 2190, 0]
}).set_index("Categoría")

st.subheader("Cobertura de Noches (Modificable)")
df_cobertura_sim = st.data_editor(df_cobertura_base_fija, use_container_width=True)

df_totales_sim = pd.DataFrame(df_cobertura_sim.sum()).T
df_totales_sim.index = ["TOTAL COBERTURA SIMULADA"]
st.dataframe(df_totales_sim.style.format("{:,.0f}"), use_container_width=True)

# Creamos pestañas para presentar las variaciones escenario por escenario
st.subheader("Resultados y Variaciones por Escenario")
tabs = st.tabs(df_cobertura_base_fija.columns.tolist())

conceptos = [
    "Noches Vendidas Anuales", 
    "Costos Fijos (CF)", 
    "Costos Variables Totales (CV)",
    "Costos Totales (CF + CV)", 
    "Ingresos por Tarifas", 
    "Subsidio a la Demanda (Otorgado)",
    "Ingresos Totales (Tarifas + Subsidios)", 
    "Resultado Operativo (Superávit/Déficit)",
    "SUBSIDIO A LA OFERTA"
]

for i, escenario in enumerate(df_cobertura_base_fija.columns):
    with tabs[i]:
        # --- CÁLCULO LÍNEA BASE (Congelado) ---
        n_a_base = df_cobertura_base_fija.loc["A", escenario]
        n_b_base = df_cobertura_base_fija.loc["B", escenario]
        n_c_base = df_cobertura_base_fija.loc["C", escenario]
        n_d_base = df_cobertura_base_fija.loc["D", escenario]
        
        noches_totales_b = n_a_base + n_b_base + n_c_base + n_d_base
        cv_totales_b = noches_totales_b * CVU_BASE
        ct_escenario_b = CF_BASE + cv_totales_b
        
        ing_tarifas_b = (n_a_base * tarifa_a_base) + (n_b_base * tarifa_b_base) + (n_c_base * tarifa_c_base) + (n_d_base * tarifa_d_base)
        sub_demanda_b = (n_a_base * v_sub_a_base) + (n_b_base * v_sub_b_base)
        ing_totales_b = ing_tarifas_b + sub_demanda_b
        
        res_operativo_b = ing_tarifas_b - ct_escenario_b
        sub_oferta_b = -(res_operativo_b + sub_demanda_b)
        
        valores_base = [
            noches_totales_b, CF_BASE, cv_totales_b, ct_escenario_b, 
            ing_tarifas_b, sub_demanda_b, ing_totales_b, res_operativo_b, sub_oferta_b
        ]
        
        # --- CÁLCULO SIMULACIÓN (Modificado) ---
        n_a_s = df_cobertura_sim.loc["A", escenario]
        n_b_s = df_cobertura_sim.loc["B", escenario]
        n_c_s = df_cobertura_sim.loc["C", escenario]
        n_d_s = df_cobertura_sim.loc["D", escenario]
        
        noches_totales_s = n_a_s + n_b_s + n_c_s + n_d_s
        cv_totales_s = noches_totales_s * costo_var_unitario
        ct_escenario_s = costos_fijos + cv_totales_s
        
        ing_tarifas_s = (n_a_s * tarifa_a_sim) + (n_b_s * tarifa_b_sim) + (n_c_s * tarifa_c_sim) + (n_d_s * tarifa_d_sim)
        sub_demanda_s = (n_a_s * v_sub_a_sim) + (n_b_s * v_sub_b_sim)
        ing_totales_s = ing_tarifas_s + sub_demanda_s
        
        res_operativo_s = ing_tarifas_s - ct_escenario_s
        sub_oferta_s = -(res_operativo_s + sub_demanda_s)
        
        valores_sim = [
            noches_totales_s, costos_fijos, cv_totales_s, ct_escenario_s, 
            ing_tarifas_s, sub_demanda_s, ing_totales_s, res_operativo_s, sub_oferta_s
        ]
        
        # --- CÁLCULO DE VARIACIONES ---
        var_abs = [s - b for s, b in zip(valores_sim, valores_base)]
        var_pct = []
        for s, b in zip(valores_sim, valores_base):
            if b != 0:
                var_pct.append((s - b) / abs(b))
            else:
                var_pct.append(0.0) # Evitar división por cero
                
        # Construcción de la tabla
        df_comp_esc = pd.DataFrame({
            "Concepto Financiero": conceptos,
            "Línea Base (Congelada)": valores_base,
            "Simulación": valores_sim,
            "Variación ($/Cant)": var_abs,
            "Variación (%)": var_pct
        }).set_index("Concepto Financiero")
        
        # Corrección: Uso de .map() en lugar de .applymap() para evitar AttributeError en pandas moderno
        st.dataframe(df_comp_esc.style.format({
            "Línea Base (Congelada)": "${:,.2f}",
            "Simulación": "${:,.2f}",
            "Variación ($/Cant)": "${:,.2f}",
            "Variación (%)": "{:,.2%}"
        }).format(
            formatter="{:,.0f}", subset=pd.IndexSlice[["Noches Vendidas Anuales"], ["Línea Base (Congelada)", "Simulación", "Variación ($/Cant)"]]
        ).map(
            lambda x: 'color: red' if isinstance(x, float) and x < 0 else ('color: green' if isinstance(x, float) and x > 0 else ''),
            subset=["Variación ($/Cant)", "Variación (%)"]
        ), use_container_width=True)
