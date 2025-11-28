import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
from app.pages.optimization_page import OptimizationPage
from app.pages.other_services_page import OtherServicesPage
from app.pages.historical_data_page import HistoricalPage

def main():
    # Configuración inicial
    st.set_page_config(page_title="Optimizador de Pozos", layout="wide")
    st.title("🛢️ Optimización de Distribución de Gas")

    # --- Pestañas ---
    tabs = st.sidebar.radio(
        "Selecciona una opción", 
        ["Optimización", "Datos Históricos" ,"Otros servicios"]
    )

    if tabs == "Optimización":
        page = OptimizationPage()
        page.show()
    elif tabs == "Datos Históricos":
        page = HistoricalPage()
        page.show()   
    elif tabs == "Otros servicios":
        page = OtherServicesPage()
        page.show()

if __name__ == "__main__":
    main()
