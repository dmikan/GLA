import streamlit as st
from pathlib import Path
from app.components.file_upload.file_upload_component import FileUploadComponent
from app.components.optimization.optimization_settings import OptimizationSettingsComponent
from app.components.optimization.optimization_history import OptimizationHistoryComponent
from backend.models.database import SnowflakeDB
from backend.services.data_loader_service import DataLoader

class OptimizationPage:
    def __init__(self):
        self.db = SnowflakeDB()
        self.file_upload = FileUploadComponent()
        self.optimization_history = HistoryComponent()

    def show(self):
        optimization_settings = OptimizationSettingsComponent(self.db)
        temp_path, load_mode = self.file_upload.show()
        is_data_ready = temp_path is not None and Path(temp_path).exists()
        loader = DataLoader(temp_path)


        tab1, tab2, tab3 = st.tabs([
            "Constrained Optimization",
            "Global Optimization",
            "Optimization History"
        ])

        with tab1:
            if is_data_ready:
                loaded_data = loader.load_data()
                optimization_settings.show_constrained_settings()
                optimization_settings.run_constrained_optimization(loaded_data)
            else:
                st.warning("Please load data first to perform the optimization")

        with tab2:
            if is_data_ready:
                loaded_data = loader.load_data()
                optimization_settings.show_global_settings()
                optimization_settings.run_global_optimization(loaded_data)
            else:
                st.warning("Please load data first to perform the optimization")

        with tab3:
            self.optimization_history.show_optimization_history()
            self.optimization_history.show_well_details()
