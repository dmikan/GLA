import streamlit as st
import pandas as pd
from io import StringIO

class CSVInputComponent:
    def __init__(self, tmp_dir):
        self.tmp_dir = tmp_dir
    
    def load(self):
        up_file = st.file_uploader("Upload csv file with production data", type="csv")
        if up_file is not None:
            csv_data = self._handle_csv_input(up_file)
            if csv_data is not None and csv_data[1]:
                st.session_state.data_load_mode = "csv_upload"
                st.session_state.temp_path = csv_data[1]

    def _handle_csv_input(self, up_file):
        content = up_file.getvalue()
        decoded_content = content.decode("utf-8")     
        df = pd.read_csv(StringIO(decoded_content), header=None)
        tmp_path = self.tmp_dir / f"data_csv_file.csv"
        with open(tmp_path, "wb") as f:
            f.write(content)
        return df, tmp_path                