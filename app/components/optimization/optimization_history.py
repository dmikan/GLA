import streamlit as st
import pandas as pd
from backend.models.database import SnowflakeDB
from backend.services.optimization_service import OptimizationService
from app.components.optimization.display_constrained_results import DisplayConstrainedResults

class OptimizationHistoryComponent:
    def __init__(self, db: SnowflakeDB):
        self.db = db
        self.display_constrained_results = None
        self.optimizations = None

    def show(self):
        st.subheader("History of optimizations")
        try:
            optimization_service = OptimizationService(self.db)
            self.optimizations = optimization_service.get_all_optimizations()
            self._show_optimizations_table()
            self._show_optimization_details()
        finally:
            print("History of optimizations shown successfully.")

    def _show_optimizations_table(self):
        history_data = [{
            "ID": opt.id,
            "Date": opt.execution_date.strftime("%Y-%m-%d %H:%M:%S"),
            "Plant": opt.plant_name,
            "Total Production (bbl)": opt.total_production,
            "Total QGL (Mscf)": opt.total_gas_injection,
            "QGL Limit": opt.gas_injection_limit,
            "(USD/bbl)": opt.oil_price,
            "(USD/Mscf)": opt.gas_price
        } for opt in self.optimizations]

        df_history = pd.DataFrame(history_data)

        st.dataframe(
            df_history.style.format({
                "Total Production (bbl)": "{:.2f}",
                "Total QGL (Mscf)": "{:.2f}",
                "QGL Limit": "{:.2f}",
                "(USD/bbl)": "{:.2f}",
                "(USD/Mscf)": "{:.2f}"
            }),
            use_container_width=True,
            height=300
        )

    def _show_optimization_details(self):
        selected_id = st.selectbox(
            "Select an optimization to view details",
            options=[opt.id for opt in self.optimizations],
            format_func=lambda x: f"optimization ID: {x} - {next((opt.plant_name for opt in self.optimizations if opt.id == x), '')}"
        )

        if selected_id:
            selected_optimization = next((opt for opt in self.optimizations if opt.id == selected_id), None)
            
            if selected_optimization:
                st.subheader(f"Detailed Results for Plant {selected_optimization.plant_name}")

                display_constrained_results = DisplayConstrainedResults(selected_optimization, selected_optimization.well_results)
                display_constrained_results._show_well_results_table()
                st.warning("The behavior graphs are not available in the history yet...")
                
                csv = pd.DataFrame([{
                    "Well": well.well_number,
                    "Name": well.well_name,
                    "Production (bbl)": well.optimal_production,
                    "QGL (Mscf)": well.optimal_gas_injection
                } for well in selected_optimization.well_results]).to_csv(index=False).encode('utf-8')
                
                st.download_button(
                    label="Download results as CSV",
                    data=csv,
                    file_name=f"optimization_results_{selected_optimization.id}.csv",
                    mime='text/csv'
                )