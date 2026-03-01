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
        self._choose_dimension()
        self._create_labels_list()
        self._initialize_and_update_dataframes()
        self._show_and_fill_manual_input_dataframes()
        self._build_dataframe_to_optimizer()
        self._manual_input_persistence()   

    def _choose_dimension(self):
        """
        This method is used to choose the dimension of the manual input dataframes.
        """
        with st.expander("⚙️ Configuration Settings", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                self.num_wells = st.number_input("Number of wells", min_value=1, max_value=100, value=5, step=1)
            with col2:
                self.num_rows = st.number_input("Number of data rows", min_value=1, max_value=100, value=5, step=1)
        return True

    def _create_labels_list(self):
        """
        This method is used to create the labels for the manual input dataframes.
        """
        self.field_wells_labels = ["field"] + [f"well_{i+1}" for i in range(self.num_wells)]
        self.wct_labels = [f"Well_{i+1}_wct" for i in range(self.num_wells)]
        self.injection_production_labels = [item for i in range(1, self.num_wells + 1) for item in (f"Well_{i}_inj", f"Well_{i}_fluid")]
        return True

    def _build_empty_dataframe(self, labels_list, single_row_flag):
        """
        This method is used to build an empty dataframe with the given labels.
        """
        if single_row_flag:
            return pd.DataFrame([["" for _ in labels_list]], 
                                columns=labels_list, 
                                index=[1])
                                
        return pd.DataFrame([["" for _ in labels_list] for _ in range(self.num_rows)],
                            columns=labels_list,
                            index=range(1, self.num_rows + 1)
        )

    def _merge_with_saved(self, new_dataframe, session_key_filled_dataframe):
        """
        This method is used to merge the new empty dataframe with the saved dataframe.
        """
        saved_dataframe = st.session_state.get(session_key_filled_dataframe)
        if saved_dataframe is None:
            return new_dataframe
        new_dataframe.update(saved_dataframe)
        return new_dataframe

    def _flush_editor_to_session(self, editor_key_prefix, session_key_filled_dataframe, labels_list, single_row_flag):
        """
        This method is used to flush the editor state to the session state.
        """
        prev_num_wells = st.session_state.get("prev_num_wells", self.num_wells)
        # this is the editor state of changes made by the user
        changes_editor_state: dict = st.session_state.get(f"{editor_key_prefix}_{prev_num_wells}") 
        if changes_editor_state is not None:
            saved_df = st.session_state.get(session_key_filled_dataframe)      
            changes_df = pd.DataFrame(changes_editor_state.get("edited_rows", {})).T
            changes_df.index = changes_df.index.astype(int) + 1
            saved_df.update(changes_df)
            st.session_state.session_key_filled_dataframe = saved_df



    def _initialize_and_update_dataframes(self):
        """
        This method is used to initialize the dataframes.
        """
        self._flush_editor_to_session(editor_key_prefix="field_wells_editor", 
                                    session_key_filled_dataframe="field_wells_df", 
                                    labels_list=self.field_wells_labels, 
                                    single_row_flag=True)
                                    
        self._flush_editor_to_session(editor_key_prefix="wct_editor", 
                                    session_key_filled_dataframe="wct_df", 
                                    labels_list=self.wct_labels, 
                                    single_row_flag=True)
                                    
        self._flush_editor_to_session(editor_key_prefix="prod_editor", 
                                    session_key_filled_dataframe="injection_production_df", 
                                    labels_list=self.injection_production_labels, 
                                    single_row_flag=False)




        self.field_wells_df = self._build_empty_dataframe(labels_list=self.field_wells_labels, 
                                                        single_row_flag=True)

        self.wct_df = self._build_empty_dataframe(labels_list=self.wct_labels, 
                                                        single_row_flag=True)
                                                        
        self.injection_production_df = self._build_empty_dataframe(labels_list=self.injection_production_labels, 
                                                        single_row_flag=False)




        self.field_wells_df = self._merge_with_saved(new_dataframe=self.field_wells_df, 
                                                    session_key_filled_dataframe="field_wells_df")

        self.wct_df = self._merge_with_saved(new_dataframe=self.wct_df, 
                                            session_key_filled_dataframe="wct_df")

        self.injection_production_df = self._merge_with_saved(new_dataframe=self.injection_production_df, 
                                                            session_key_filled_dataframe="injection_production_df")


        return True

    def _show_and_fill_manual_input_dataframes(self):
        """
        This method is used to show and fill the manual input dataframes.
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
            key=f"field_wells_editor_{self.num_wells}"
        )

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
            key=f"wct_editor_{self.num_wells}"
        )

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
            key=f"prod_editor_{self.num_wells}"
        )

        st.session_state.field_wells_df = self.filled_field_wells_df
        st.session_state.wct_df = self.filled_wct_df
        st.session_state.injection_production_df = self.filled_injection_production_df
        st.session_state.prev_num_wells = self.num_wells
        st.session_state.prev_num_rows = self.num_rows
        
        return True

    def _build_dataframe_to_optimizer(self):
        """
        This method is used to build the dataframe to the optimizer.
        """
        try:
            total_columns = len(self.filled_injection_production_df.columns) + 1
            self.final_df = pd.DataFrame(columns=range(total_columns))

            self.final_df.loc[0] = ["description"] + [""] * (total_columns - 1)

            wells_header = self.filled_field_wells_df.columns.tolist()
            wells_header += [""] * (total_columns - len(wells_header))
            self.final_df.loc[1] = wells_header

            wells_values = self.filled_field_wells_df.iloc[0].tolist()
            wells_values += [""] * (total_columns - len(wells_values))
            self.final_df.loc[2] = wells_values

            wct_values = ["wct"] + self.filled_wct_df.iloc[0].tolist()
            wct_values += [""] * (total_columns - len(wct_values))
            self.final_df.loc[3] = wct_values

            data_headers = ["index"] + self.filled_injection_production_df.columns.tolist()
            self.final_df.loc[4] = data_headers

            for i, (idx, row) in enumerate(self.filled_injection_production_df.iterrows()):
                row_values = [idx + 1] + row.tolist()
                self.final_df.loc[5 + i] = row_values

            return True
        except Exception as e:
            st.error(f"Error building the final DataFrame: {e}")
            return False

    def _manual_input_persistence(self):
        """
        This method is used to persist the manual input data.
        """
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