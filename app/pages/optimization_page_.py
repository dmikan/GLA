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
        self.optimization_settings = OptimizationSettingsComponent(self.db) 
        self.history = HistoryComponent() 
        
    def show(self):
        temp_path, load_mode = self.file_upload.show()
        is_data_ready = temp_path is not None and Path(temp_path).exists()

        if is_data_ready and load_mode:
            try:
                loader = DataLoader(temp_path)
                if load_mode == "csv_upload":
                    loaded_data = loader.load_data_ui()
                elif load_mode == "manual_input":
                    loaded_data = loader.load_data_ui()  
                if not loaded_data[0]:
                    st.error("Error: the data was loaded, but no valid wells/production was found.")
                    is_data_ready = False
                    self._show_tabs(is_data_ready, loaded_data) 

            except Exception as e:
                st.error(f"Error processing the file with DataLoader: {e}")
                is_data_ready = False
        else:
            is_data_ready = False
        


    def _show_tabs(self, is_data_ready, loaded_data):
        tab1, tab2, tab3 = st.tabs([
            "Global Optimization", 
            "Optimization with QGL given", 
            "Optimization History"
        ])
        with tab1:
            if is_data_ready:
                self.optimization_settings.show_global_optimization(loaded_data)
            else:
                st.warning("Please load data first to perform the optimization")

        with tab2:
            if is_data_ready:
                self.optimization_settings.show_constrained_optimization(loaded_data)
            else:
                st.warning("Please load data first to perform the optimization")

        with tab3:
            self.history.show()
