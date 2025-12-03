import streamlit as st
from pathlib import Path
from app.components.file_upload.file_upload_component import FileUploadComponent
from app.components.optimization.optimization_settings import OptimizationSettingsComponent
from app.components.history.history_component import HistoryComponent
from backend.models.database import SnowflakeDB
from backend.services.data_loader_service import DataLoader

class OptimizationPage:
    def __init__(self):
        self.db = SnowflakeDB()
        self.file_upload = FileUploadComponent()
        self.history = HistoryComponent() 

    def show(self):
        optimization_settings = OptimizationSettingsComponent(self.db)
        temp_path, load_mode = self.file_upload.show()
        is_data_ready = temp_path is not None and Path(temp_path).exists()
        loader = DataLoader(temp_path)

        
        tab1, tab2, tab3 = st.tabs([
            "Global Optimization", 
            "Constrained Optimization", 
            "Optimization History"
        ])

        with tab1:
            if is_data_ready:
                loaded_data = loader.load_data()
                optimization_settings.show_global_settings()
                optimization_settings.run_optimization(loaded_data)
            else:
                st.warning("Please load data first to perform the optimization")

        with tab2:
            if is_data_ready:
                loaded_data = loader.load_data()
                optimization_settings.show_constrained_settings()
                optimization_settings.run_constrained_optimization(loaded_data)
            else:
                st.warning("Please load data first to perform the optimization")

        with tab3:
            self.history.show()