import streamlit as st
from pathlib import Path
import pandas as pd
from io import StringIO
import os
from app.components.file_upload.manual_input_component import ManualInputComponent
from app.components.file_upload.csv_input_component import CSVInputComponent
from app.components.file_upload.proper_input_component import ProperInputComponent

class FileUploadComponent:   

    def show(self):
        self._init_session_state()  
        tmp_dir = self._get_tmp_dir()    
        option = self._choose_data_loading_method()

        #st.session_state.data_load_mode = None
        #st.session_state.temp_path = None
        
        if option == "Upload csv file":
            csv_input = CSVInputComponent(tmp_dir)
            csv_input.load()
        elif option == "Manual input":
            manual_input = ManualInputComponent(tmp_dir)
            manual_input.load()
        elif option == "Generate from Prosper":
            proper_input = ProperInputComponent(tmp_dir)
            proper_input.load()
        return st.session_state.temp_path, st.session_state.data_load_mode


    def _init_session_state(self):
        if 'uploaded_file' not in st.session_state:
            st.session_state.uploaded_file = None
        if 'temp_path' not in st.session_state:
            st.session_state.temp_path = None
        if 'data_load_mode' not in st.session_state:
            st.session_state.data_load_mode = None


    def _get_tmp_dir(self):
        is_snowflake = os.path.exists("/home/udf")
        if is_snowflake:
            return Path("/tmp")
        else:
            project_root = Path(__file__).parent.parent.parent.parent
            local_path = project_root / "tmp"
            local_path.mkdir(parents=True, exist_ok=True)
            return local_path    

    def _choose_data_loading_method(self):
        option = st.radio(
            "Choose a data loading method:",
            options=["Upload csv file", "Manual input", "Generate from Prosper"],
            horizontal=True
        )
        return option




