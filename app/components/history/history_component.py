import streamlit as st
import pandas as pd
from backend.services.optimization_service import OptimizationService
from backend.models.database import SnowflakeDB
from app.components.optimization.display_constrained_results import DisplayConstrainedResults

class HistoryComponent:
    def __init__(self):
        self.results_component = DisplayConstrainedResults()

    def show(self):
        st.subheader("Historial of optimizations")
        db = SnowflakeDB()
        optimization_service = OptimizationService(db)
        try:
            optimizations = optimization_service.get_all_optimizations()
            self._show_optimizations_table(optimizations)
            self._show_optimization_details(optimizations)
        finally:
            print("Historial de optimizaciones mostrado correctamente.")

    def _show_optimizations_table(self, optimizations):
        historial_data = [{
            "ID": opt.id,
            "Fecha": opt.execution_date.strftime("%Y-%m-%d %H:%M:%S"),
            "Planta": opt.plant_name,
            "Producción Total (bbl)": opt.total_production,
            "QGL Total (Mscf)": opt.total_gas_injection,
            "Límite QGL": opt.gas_injection_limit,
            "(USD/bbl)": opt.oil_price,
            "(USD/Mscf)": opt.gas_price
        } for opt in optimizations]

        df_historial = pd.DataFrame(historial_data)

        st.dataframe(
            df_historial.style.format({
                "Producción Total (bbl)": "{:.2f}",
                "QGL Total (Mscf)": "{:.2f}",
                "Límite QGL": "{:.2f}",
                "(USD/bbl)": "{:.2f}",
                "(USD/Mscf)": "{:.2f}"
            }),
            use_container_width=True,
            height=300
        )

    def _show_optimization_details(self, optimizations):
        selected_id = st.selectbox(
            "Selecciona una optimización para ver detalles",
            options=[opt.id for opt in optimizations],
            format_func=lambda x: f"optimization ID: {x} - {next((opt.plant_name for opt in optimizations if opt.id == x), '')}"
        )

        if selected_id:
            selected_optimization = next((opt for opt in optimizations if opt.id == selected_id), None)
            
            if selected_optimization:
                st.subheader(f"Resultados Detallados por Pozo de planta {selected_optimization.plant_name}")
                self.results_component._show_well_results(selected_optimization.well_results)
                
                st.warning("Las gráficas de comportamiento no están disponibles en el historial...")
                
                csv = pd.DataFrame([{
                    "Pozo": pozo.well_number,
                    "Nombre": pozo.well_name,
                    "Producción (bbl)": pozo.optimal_production,
                    "QGL (Mscf)": pozo.optimal_gas_injection
                } for pozo in selected_optimization.well_results]).to_csv(index=False).encode('utf-8')
                
                st.download_button(
                    label="Descargar resultados como CSV",
                    data=csv,
                    file_name=f"resultados_optimizacion_{selected_optimization.id}.csv",
                    mime='text/csv'
                )