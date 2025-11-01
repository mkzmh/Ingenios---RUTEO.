import streamlit as st
import time
from routing_logic import COORDENADAS_LOTES, solve_route_optimization, VEHICLES 

st.set_page_config(page_title="Optimizador de Rutas", layout="wide")

st.title("🚚 Optimizador de Rutas Bimodal (TSP)")
st.caption("Calcula la división óptima de lotes para dos camiones y su ruta más corta usando GraphHopper.")

# --- Área de Input y Validación ---
col1, col2 = st.columns([3, 1])

with col1:
    lotes_input = st.text_input(
        "Ingrese los lotes a visitar (separados por coma):",
        placeholder="Ej: A05, A10, B05, B10, C95, D01, K01"
    )

with col2:
    st.write(" ") # Espacio para alinear
    st.write(" ")
    calculate_button = st.button("Calcular Rutas", type="primary")

# --- Lógica de Ejecución al presionar el botón ---
if calculate_button:
    
    # 1. Limpieza y Validación de Input
    all_stops_to_visit = [s.strip().upper() for s in lotes_input.split(',') if s.strip()]
    num_lotes = len(all_stops_to_visit)
    MIN_LOTES = 3
    MAX_LOTES = 7
    
    # Validación de cantidad
    if num_lotes < MIN_LOTES or num_lotes > MAX_LOTES:
        st.error(f"❌ Error: Debe ingresar entre **{MIN_LOTES}** y **{MAX_LOTES}** lotes. Ingresó {num_lotes}.")
        st.stop()
        
    # Validación de lotes válidos
    invalid_stops = [s for s in all_stops_to_visit if s not in COORDENADAS_LOTES]
    if invalid_stops:
        st.error(f"❌ Error: Lotes no válidos encontrados: {', '.join(invalid_stops)}. Corrija la lista.")
        st.stop()
        
    # --- Ejecutar el cálculo y mostrar estado ---
    st.info(f"⏳ Iniciando cálculo TSP para {num_lotes} lotes. Esto tomará al menos 1.5 minutos (debido a la espera de API).")
    
    # Usar un spinner para mostrar que está trabajando
    with st.spinner('Realizando cálculo óptimo y agrupando rutas (¡75s de espera incluidos!)...'):
        try:
            # 2. Llamar a la lógica de ruteo
            results = solve_route_optimization(all_stops_to_visit)
            
            # 3. Mostrar Resultados
            if "error" in results:
                st.error(f"❌ Error en la API de Ruteo: {results['error']}")
                st.stop()
            
            st.success("✅ Cálculo finalizado y rutas optimizadas.")
            
            # --- Visualización de Resultados en Streamlit ---
            
            st.header("Resumen General")
            st.metric("Distancia Interna de Agrupación (Minimización)", f"{results['agrupacion_distancia_km']} km")
            
            res_a = results.get('ruta_a', {})
            res_b = results.get('ruta_b', {})

            col_a, col_b = st.columns(2)
            
            # Reporte Camión A
            with col_a:
                st.subheader(f"Camión 1: **{res_a.get('patente', 'N/A')}**")
                st.markdown(f"**Nombre:** {VEHICLES.get(res_a.get('patente'), {}).get('name', 'Ruta A')}")
                st.markdown(f"**Lotes Asignados:** `{' -> '.join(res_a.get('lotes_asignados', []))}`")
                st.markdown(f"**Distancia Total Optimizada:** **{res_a.get('distancia_km', 'N/A')} km**")
                st.markdown(f"**Orden Óptimo:** `Ingenio -> {' -> '.join(res_a.get('orden_optimo', []))} -> Ingenio`")
                st.markdown(f"🔗 [Ver Ruta A en GeoJSON.io]({res_a.get('geojson_link', '#')})")
                
            # Reporte Camión B
            with col_b:
                st.subheader(f"Camión 2: **{res_b.get('patente', 'N/A')}**")
                st.markdown(f"**Nombre:** {VEHICLES.get(res_b.get('patente'), {}).get('name', 'Ruta B')}")
                st.markdown(f"**Lotes Asignados:** `{' -> '.join(res_b.get('lotes_asignados', []))}`")
                st.markdown(f"**Distancia Total Optimizada:** **{res_b.get('distancia_km', 'N/A')} km**")
                st.markdown(f"**Orden Óptimo:** `Ingenio -> {' -> '.join(res_b.get('orden_optimo', []))} -> Ingenio`")
                st.markdown(f"🔗 [Ver Ruta B en GeoJSON.io]({res_b.get('geojson_link', '#')})")


        except Exception as e:
            st.error(f"❌ Ocurrió un error inesperado durante el ruteo. Error: {e}")
            st.caption("Verifique los logs en la terminal CMD para más detalles.")
