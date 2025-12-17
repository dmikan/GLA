import streamlit as st
from pathlib import Path
from app.components.file_upload.file_upload_component import FileUploadComponent
from app.components.optimization.optimization_settings import OptimizationSettingsComponent
from app.components.optimization.optimization_history import OptimizationHistoryComponent
from app.components.optimization.optimization_execution import OptimizationExecutionComponent
from backend.models.database import SnowflakeDB
from backend.services.data_loader_service import DataLoader

class OptimizationPage:
    def __init__(self):
        self.db = SnowflakeDB()
        self.file_upload = FileUploadComponent()

    def show(self):
        optimization_settings = OptimizationSettingsComponent()
        optimization_execution = OptimizationExecutionComponent(self.db)
        optimization_history = OptimizationHistoryComponent(self.db)

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
                constrained_settings = optimization_settings.choose_constrained_settings()
                optimization_execution.run_constrained_optimization(loaded_data, constrained_settings)
                
            else:
                st.warning("Please load data first to perform the optimization")

        with tab2:
            if is_data_ready:
                loaded_data = loader.load_data()
                global_settings = optimization_settings.choose_global_settings()
                optimization_execution.run_global_optimization(loaded_data, global_settings)
            else:
                st.warning("Please load data first to perform the optimization")

        with tab3:
            optimization_history.show()
            #self.optimization_history.show_optimization_history()
            #self.optimization_history.show_well_details()
