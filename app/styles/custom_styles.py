import streamlit as st

def inject_global_css():
    """Inyecta todos los estilos CSS personalizados para la aplicación."""
    custom_css = """
    <style>
        /* general style for the metric container */
        .metric-card {
            background-color: #1a1e26; /* background color */
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2);
            height: 100%; /* all cards have the same height */
        }
        /* style for the metric title */
        .metric-title {
            color: #9AA0A6; /* text color */
            font-size: 14px;
            margin-bottom: 5px;
            font-weight: 500;
        }
        /* style for the metric value */
        .metric-value {
            color: #FFFFFF; /* text color */
            font-size: 28px;
            font-weight: 700;
            line-height: 1.2;
        }
        /* style for the metric unit */
        .metric-unit {
            font-size: 18px;
            color: #9AA0A6;
        }
        /* style for the metric status tag */
        .status-tag {
            font-size: 14px;
            font-weight: 600;
            margin-top: 10px;
            color: #00E676; /* text color */
        }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)
    
# Esto es limpio, claro y fácil de importar.