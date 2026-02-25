import streamlit as st
import pandas as pd

class ManualInputComponent:
    def __init__(self, tmp_dir):
        self.tmp_dir = tmp_dir
        self.num_wells = None
        self.num_rows = None
        
        self.field_wells_labels = None
        self.field_wells_df = None
        self.filled_field_wells_df = None

        self.injection_production_labels = None
        self.injection_production_df = None
        self.filled_injection_production_df = None

        self.wct_labels = None
        self.wct_df = None
        self.filled_wct_df = None

        self.final_df = None

    def load(self):
        """
        Load the manual input component.
        """
        self._choose_dimension()
        self._create_labels()
        self._create_input_empty_dataframe()
        self._show_and_fill_manual_input_dataframes()
        self._build_dataframe_to_optimizer()
        self._manual_input_persistence()   


    def _choose_dimension(self):
        """
        Choose the dimension of the manual input.
        """
        with st.expander("⚙️ Configuration Settings", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                self.num_wells = st.number_input("Number of wells", min_value=1, max_value=100, value=5, step=1)
            
            with col2:
                self.num_rows = st.number_input("Number of data rows", min_value=1, max_value=100, value=5, step=1)
        return True


    def _create_labels(self):
        """
        Create the labels for the manual input.
        """
        self.field_wells_labels = ["field"] + [f"well_{i+1}" for i in range(self.num_wells)]
        self.wct_labels = [f"Well_{i+1}_wct" for i in range(self.num_wells)]
        self.injection_production_labels = [item for i in range(1, self.num_wells + 1) for item in (f"Well_{i}_inj", f"Well_{i}_fluid")]
        return True


    def _create_input_empty_dataframe(self):
        """
        Create an empty dataframe for manual input.
        """
        self.field_wells_df = pd.DataFrame(
            [["" for _ in self.field_wells_labels]],
            columns=self.field_wells_labels,
            index=[1]
        )

        self.wct_df = pd.DataFrame(
            [["" for _ in self.wct_labels]],
            columns=self.wct_labels,
            index=[1]
        )
        
        self.injection_production_df = pd.DataFrame(
            [["" for _ in self.injection_production_labels] for _ in range(self.num_rows)],
            columns=self.injection_production_labels,
            index=range(1, self.num_rows + 1)
        )
        return True


    def _show_and_fill_manual_input_dataframes(self):
        """
        Show the manual input widget.
        """
        st.divider() 
        st.subheader("📋 Information of Fields and Wells")
        st.caption("Please define the field name and assign identifiers for each well below.")
        
        info_header = {"field": st.column_config.TextColumn("📍 Field")}
        info_header.update({col: st.column_config.TextColumn(f"🛢️ {col.replace('_', ' ').title()}") for col in self.field_wells_labels[1:]})

        self.filled_field_wells_df = st.data_editor(
            self.field_wells_df,
            column_config=info_header, 
            num_rows="fixed",
            hide_index=True, 
            use_container_width=True,
            key="field_wells_editor"
        )

        # WCT Input
        st.divider() 
        st.subheader("📋 Information of WCT")
        st.caption("Please define the wct for each well below.")
        
        wct_header = {col: st.column_config.TextColumn(f"📉 {col.replace('_', ' ')}") for col in self.wct_labels}
        self.filled_wct_df = st.data_editor(
            self.wct_df,
            column_config=wct_header, 
            num_rows="fixed",
            hide_index=True, 
            use_container_width=True,
            key="wct_editor"
        )

        # Production Data Input
        st.divider() 
        st.subheader("📊 Production Data Input")
        st.caption("Enter the daily injection rates and fluid types for the simulation.")

        prod_header = {col: st.column_config.TextColumn(f"{col.replace('_', ' ')}") for col in self.injection_production_labels}
        
        self.filled_injection_production_df = st.data_editor(
            self.injection_production_df,
            column_config=prod_header,  
            num_rows="fixed",
            hide_index=True,
            use_container_width=True,
            key="prod_editor"
        )

        return True


    def _build_dataframe_to_optimizer(self):
        try:
            total_columns = len(self.filled_injection_production_df.columns) + 1
            self.final_df = pd.DataFrame(columns=range(total_columns))

            # Row 0: description
            self.final_df.loc[0] = ["description"] + [""] * (total_columns - 1)

            # Row 1: well headers
            wells_header = self.filled_field_wells_df.columns.tolist()
            wells_header += [""] * (total_columns - len(wells_header))
            self.final_df.loc[1] = wells_header

            # Row 2: well values
            wells_values = self.filled_field_wells_df.iloc[0].tolist()
            wells_values += [""] * (total_columns - len(wells_values))
            self.final_df.loc[2] = wells_values

            # Row 3: wct values
            wct_values = ["wct"] + self.filled_wct_df.iloc[0].tolist()
            wct_values += [""] * (total_columns - len(wct_values))
            self.final_df.loc[3] = wct_values

            # Row 4: data headers
            data_headers = ["index"] + self.filled_injection_production_df.columns.tolist()
            self.final_df.loc[4] = data_headers

            # Following rows: production data
            for i, (idx, row) in enumerate(self.filled_injection_production_df.iterrows()):
                row_values = [idx + 1] + row.tolist()
                self.final_df.loc[5 + i] = row_values

            return True
        except Exception as e:
            st.error(f"Error building the final DataFrame: {e}")
            return False

    def _manual_input_persistence(self):
        try:
            if self.final_df is not None and not self.final_df.empty and len(self.final_df) > 2:
                df = self.final_df
                field_name = df.iloc[2, 0] if not pd.isna(df.iloc[2, 0]) else "manual_data"
                temp_path = self.tmp_dir / f"data_{field_name.lower().replace(' ', '_')}.csv"
                df.to_csv(temp_path, index=False, header=False)
                st.success(f"Data saved in {temp_path}")
                st.session_state.data_load_mode = "manual_input"
                st.session_state.temp_path = temp_path
                return True
            else:
                st.warning("Not enough data to save.")
                return False
        except Exception as e:
            st.error(f"Error saving the data: {e}")
            return False





