import streamlit as st
import pandas as pd
from app.components.utils.plotter import Plotter

class DisplayGlobalResults:
    def __init__(self, optimization_results: dict):
        self.plotter = None
        self.optimization_results = optimization_results

    def show(self):
        self.plotter = Plotter(self.optimization_results)
        fig = self.plotter.create_global_curve()
        st.plotly_chart(fig, use_container_width=True)
        