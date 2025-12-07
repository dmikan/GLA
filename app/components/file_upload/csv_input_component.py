import streamlit as st
import pandas as pd
from io import StringIO

class CSVInputComponent:
    def __init__(self, tmp_dir):
        self.tmp_dir = tmp_dir
        self.up_file = None

    def show_csv_loader_widget(self):
        self.up_file = st.file_uploader("Upload csv file with production data", type="csv")

    def load(self):
        # Create csv in the specified temp_dir
        if self.up_file is not None:
            content = self.up_file.getvalue()
            decoded_content = content.decode("utf-8")
            df = pd.read_csv(StringIO(decoded_content), header=None)
            tmp_path = self.tmp_dir / f"data_csv_file.csv"
            with open(tmp_path, "wb") as f:
                f.write(content)
            if tmp_path is not None and tmp_path:
                st.session_state.data_load_mode = "csv_upload"
                st.session_state.temp_path = tmp_path
