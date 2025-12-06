import streamlit as st
import pandas as pd
from app.components.utils.style_utils import ChartStyle

class DisplayGlobalResults:
    def __init__(self):
        self.chart_style = ChartStyle()

    def show(self, optimization_results: dict):
        fig = self.chart_style.create_global_optimization_chart(optimization_results)
        st.plotly_chart(fig, use_container_width=True)
        