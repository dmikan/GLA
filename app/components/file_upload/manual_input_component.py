import streamlit as st
import pandas as pd

class ManualInputComponent:
    def __init__(self, tmp_dir):
        self.tmp_dir = tmp_dir

    def load(self):
        manual_data = self._handle_manual_input()
        if manual_data is not None and manual_data[1]:
            st.session_state.data_load_mode = "manual_input"
            st.session_state.temp_path = manual_data[1]   

    def _handle_manual_input(self):
        manual_data_df = self._show()
        if manual_data_df is not None and not manual_data_df.empty:
            df = manual_data_df
            field_name = df.iloc[2, 0] if len(df) > 2 and not pd.isna(df.iloc[2, 0]) else "manual_data"
            temp_path = self.tmp_dir / f"data_{field_name.lower().replace(' ', '_')}.csv"
            
            #if st.button("Guardar datos manuales"):
            try:
                df.to_csv(temp_path, index=False, header=False) 
                st.success(f"Data saved successfully.")
                st.session_state.uploaded_file = df
                return df, temp_path
            except Exception as e:
                st.error(f"Error saving data: {e}")
        return None, None 

    def _create_input_dataframe(self, num_wells, num_filas, input_columns_info, production_columns):
        input_df_info = pd.DataFrame(
            [["" for _ in input_columns_info]],
            columns=input_columns_info,
            index=[1]
        )
        
        input_df = pd.DataFrame(
            [["" for _ in production_columns] for _ in range(num_filas)],
            columns=production_columns,
            index=range(1, num_filas + 1)
        )
        
        return input_df_info, input_df

    def _build_final_dataframe(self, edited_input_df_info, edited_input_df):
        total_columns = len(edited_input_df.columns)
        final_df = pd.DataFrame(columns=range(total_columns))

        # Fila 1: Descripción
        final_df.loc[0] = ["description"] + [""] * (total_columns - 1)

        # Fila 2: Nombres de campos/pozos
        wells_header = edited_input_df_info.columns.tolist() + [""] * (total_columns - len(edited_input_df_info.columns))
        final_df.loc[1] = wells_header

        # Fila 3: Valores de campos/pozos
        if not edited_input_df_info.empty:
            wells_values = edited_input_df_info.iloc[0].tolist() + [""] * (total_columns - len(edited_input_df_info.columns))
            final_df.loc[2] = wells_values

        # Fila 4: Encabezados de datos
        final_df.loc[3] = edited_input_df.columns.tolist()

        # Filas siguientes: Datos de producción
        for i, row in edited_input_df.iterrows():
            final_df.loc[4 + i] = row.tolist()
        
        return final_df

    def _show(self):
        with st.expander("⚙️ Configuration Settings", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                num_wells = st.number_input("Number of wells", min_value=1, max_value=100, value=5, step=1)
            
            with col2:
                num_filas = st.number_input("Number of data rows", min_value=1, max_value=100, value=5, step=1)



        st.divider() 
        st.subheader("📋 Information of Fields and Wells")
        st.caption("Please define the field name and assign identifiers for each well below.")
        
        well_columns = [f"well_{i+1}" for i in range(num_wells)]
        input_columns_info = ["field"] + well_columns
        
        input_df_info, input_df = self._create_input_dataframe(
            num_wells, num_filas, input_columns_info,
            [item for i in range(1, num_wells + 1) for item in (f"q_inj_w{i}", f"fluid_w{i}")]
        )

        info_config = {"field": st.column_config.TextColumn("📍 Field")}
        info_config.update({col: st.column_config.TextColumn(f"🛢️ {col.replace('_', ' ').title()}") for col in well_columns})

        edited_input_df_info = st.data_editor(
            input_df_info,
            column_config=info_config, 
            num_rows="fixed",
            hide_index=True, 
            use_container_width=True,
            key="info_editor"
        )


        st.divider() 
        st.subheader("📊 Production Data Input")
        st.caption("Enter the daily injection rates and fluid types for the simulation.")

        prod_config = {}
        for i in range(1, num_wells + 1): 
            prod_config[f"q_inj_w{i}"] = st.column_config.TextColumn(f"QGL W{i}")
            prod_config[f"fluid_w{i}"] = st.column_config.TextColumn(f"QL W{i}")

        edited_input_df = st.data_editor(
            input_df,
            column_config=prod_config,  
            num_rows="fixed",
            hide_index=False,
            use_container_width=True,
            key="prod_editor"
        )
        
        if "index" not in edited_input_df.columns:
            edited_input_df.insert(0, "index", range(1, len(edited_input_df) + 1))

        return self._build_final_dataframe(edited_input_df_info, edited_input_df)