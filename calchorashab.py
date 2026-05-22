import streamlit as st
from datetime import datetime, timedelta, time

def es_hora_habil(dt: datetime) -> bool:
    """Determina si un datetime cae dentro de la jornada laboral,

    aplicando el horario de viernes diferenciado solo de enero a septiembre.
    """
    dia_semana = dt.weekday()  # 0 = Lunes, 4 = Viernes, 5 = Sábado, 6 = Domingo 
    mes = dt.month             # 1 = Enero, 9 = Septiembre, 10 = Octubre...
    
    # Fines de semana libre
    if dia_semana >= 5:
        return False
        
    hora_actual = dt.time()
    
    # Por defecto, usamos el horario estándar (Lunes a Jueves)
    bloque1_inicio = time(9, 30)
    bloque1_fin = time(13, 30)
    bloque2_inicio = time(14, 30)
    bloque2_fin = time(18, 30)
    
    # Si es Viernes Y estamos entre Enero (1) y Septiembre (9) inclusive:
    if dia_semana == 4 and (1 <= mes <= 9):
        bloque1_inicio = time(9, 0)
        bloque1_fin = time(13, 0)
        bloque2_inicio = time(14, 0)
        bloque2_fin = time(15, 30)
    # Si es Viernes pero es Octubre, Noviembre o Diciembre, mantiene el bloque estándar.
        
    # Verificar si cae en el bloque de la mañana o de la tarde
    en_bloque1 = (bloque1_inicio <= hora_actual < bloque1_fin)
    en_bloque2 = (bloque2_inicio <= hora_actual < bloque2_fin)
    
    return en_bloque1 or en_bloque2

def calcular_horas_habiles(inicio: datetime, fin: datetime) -> float:
    """Calcula el total de horas hábiles entre dos fechas avanzando minuto a minuto."""
    if inicio >= fin:
        return 0.0
        
    minutos_habiles = 0
    enlace = inicio.replace(second=0, microsecond=0)
    fin_redondeado = fin.replace(second=0, microsecond=0)
    
    while enlace < fin_redondeado:
        if es_hora_habil(enlace):
            minutos_habiles += 1
        enlace += timedelta(minutes=1)
        
    return minutos_habiles / 60.0

# --- Interfaz de Streamlit ---
st.set_page_config(page_title="Calculadora de Horas Hábiles", page_icon="🕒")

st.title("🕒 Calculadora de Horas Hábiles")
st.markdown("""
Esta herramienta calcula el tiempo neto trabajado entre dos fechas, respetando la estacionalidad de la jornada:
* **Lunes a Jueves (Todo el año):** 09:30 a 13:30 y 14:30 a 18:30 *(8 hrs)*
* **Viernes (Enero a Septiembre):** 09:00 a 13:00 y 14:00 a 15:30 *(5.5 hrs)*
* **Viernes (Octubre a Diciembre):** Horario normal de 09:30 a 13:30 y 14:30 a 18:30 *(8 hrs)*
""")

st.divider()

col1, col2 = st.columns(2)

with col1:
    st.subheader("Fecha de Inicio")
    fecha_ini = st.date_input("Selecciona el día de inicio", datetime.now().date(), format="DD-MM-YYYY", key="f_ini")
    hora_ini = st.time_input("Selecciona la hora de inicio", time(9, 30), key="h_ini")
    dt_inicio = datetime.combine(fecha_ini, hora_ini)

with col2:
    st.subheader("Fecha de Término")
    fecha_fin = st.date_input("Selecciona el día de término", datetime.now().date(), format="DD-MM-YYYY", key="f_fin")
    hora_fin = st.time_input("Selecciona la hora de término", time(18, 30), key="h_fin")
    dt_fin = datetime.combine(fecha_fin, hora_fin)

st.divider()

if st.button("Calcular Tiempo Hábil", type="primary"):
    if dt_inicio >= dt_fin:
        st.error("Error: La fecha de inicio debe ser anterior a la fecha de término.")
    else:
        with st.spinner("Calculando minutos hábiles..."):
            total_horas = calcular_horas_habiles(dt_inicio, dt_fin)
            
        horas_enteras = int(total_horas)
        minutos_restantes = round((total_horas - horas_enteras) * 60)
        
        st.metric(label="Total Horas Hábiles", value=f"{total_horas:.2f} hrs")
        st.info(f"Equivale a **{horas_enteras} horas y {minutos_restantes} minutos** hábiles.")