import streamlit as st
from pathlib import Path
from components.file_upload.file_upload_component import FileUploadComponent
from components.optimization.optimization_charts import OptimizationChartsComponent
from components.history.history_component import HistoryComponent
from backend.models.database import SnowflakeDB

class OptimizationPage:
    def __init__(self):
        self.file_upload = FileUploadComponent()
        self.optimization_charts = OptimizationChartsComponent()
        self.history = HistoryComponent()
        self.db = SnowflakeDB()

    def show(self):
        temp_path = self.file_upload.show()
        data_loaded = temp_path is not None and Path(temp_path).exists()
        
        tab1, tab2, tab3 = st.tabs([
            "Optimización Global", 
            "Optimización con QGL dado", 
            "Historial de Optimizaciones"
        ])

        with tab1:
            if data_loaded:
                self.optimization_charts.show_global_optimization(temp_path, self.db)
            else:
                st.warning("Por favor cargue datos primero para realizar la optimización")

        with tab2:
            if data_loaded:
                self.optimization_charts.show_constrained_optimization(temp_path, self.db)
            else:
                st.warning("Por favor cargue datos primero para realizar la optimización")

        with tab3:
            self.history.show()
