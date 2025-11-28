import streamlit as st
from components.historical_data.historical_data_component import HistoricalDataComponents

class HistoricalPage:
    def show(self):
        st.subheader("Datos Históricos")
        
        components = HistoricalDataComponents()
        
        # Mostrar gráficos en pestañas
        tab1, tab2 = st.tabs(["Relación Gas-Líquido", "Importancia de Variables"])
        
        with tab1:
            components.render_scatter_plot()
        
        with tab2:
            components.render_mutual_info_heatmap()
