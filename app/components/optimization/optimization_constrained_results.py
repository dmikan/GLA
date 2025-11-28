import streamlit as st
import pandas as pd
from components.utils.style_utils import ChartStyle

class OptimizationConstrainedResults:
    def __init__(self):
        self.chart_style = ChartStyle()


    '''
    Método para mostrar los resultados de la optimización.
    Este método se encarga de mostrar los resultados de la optimización, incluyendo métricas resumen y gráficos de curvas de pozo.
    Se encarga de mostrar los resultados detallados por pozo y las métricas resumen.
    '''
    def show(self, results, well_result):
        self._show_summary_metrics(results['summary'])
        st.markdown("---")
        self._plot_well_curves(results, well_result)
        st.subheader("Resultados Detallados por Pozo")
        self._show_well_results(well_result)

   
    '''
    Método para mostrar las métricas resumen de la optimización.
    Este método se encarga de mostrar las métricas resumen de la optimización, incluyendo la producción total, el QGL total utilizado y el límite de QGL configurado.
    Se encarga de mostrar las métricas en columnas para una mejor visualización.
    '''

    def _show_summary_metrics(self, summary):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Producción Total", 
                f"{summary['total_production']:.2f} bbl"
            )
        
        with col2:
            st.metric(
                "QGL Total Utilizado", 
                f"{summary['total_qgl']:.2f} Mscf",
                delta=f"{(summary['total_qgl']/summary['qgl_limit']*100):.1f}% del límite"
            )
        
        with col3:
            st.metric(
                "Límite QGL Configurado", 
                f"{summary['qgl_limit']:.2f} Mscf"
            )


    def _plot_well_curves(self, results, well_result):
        if not results.get('plot_data') or not well_result:
            st.warning("No hay datos suficientes para graficar")
            return
        
        fig_prod = self.chart_style.create_well_curves_chart(results, well_result)
        st.plotly_chart(fig_prod, use_container_width=True)



    def _show_well_results(self, well_result):
        if not well_result:
            st.warning("No hay datos de pozos para mostrar")
            return
        
        try:
            well_data = [{
                "Pozo": getattr(result, 'well_name', 'N/A'),
                "Producción": getattr(result, 'optimal_production', 0),
                "QGL": getattr(result, 'optimal_gas_injection', 0)
            } for result in well_result]
            
            df = pd.DataFrame(well_data)
            
            if "Pozo" not in df.columns:
                df = df.rename(columns={"well_name": "Pozo"})
            
            st.dataframe(df.set_index("Pozo").style.format({
                "Producción": "{:.2f}",
                "QGL": "{:.2f}"
            }))
            
        except Exception as e:
            st.error(f"Error al mostrar resultados: {str(e)}")
            st.write("Datos recibidos:", well_result)