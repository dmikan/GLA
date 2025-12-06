# services/fitting_service.py
import numpy as np
from typing import List, Dict, Tuple
from scipy import optimize
import matplotlib.pyplot as plt

class FittingService:
    """Service that handles all curve fitting operations and performance curve modeling"""
    def __init__(self, q_gl_list: List[np.ndarray], q_oil_list: List[np.ndarray]):
        """
        Initialize with well data
        
        Args:
            q_gl_list: List of arrays containing gas lift rates for each well
            q_oil_list: List of arrays containing oil production rates for each well
        """
        self.q_gl_list = q_gl_list
        self.q_oil_list = q_oil_list
        self.q_gl_range = None
        self.y_pred_list = None
        self.plot_data = None

    def _calculate_qgl_range(self) -> np.ndarray:
        q_gl_max = max([np.max(j) for j in self.q_gl_list])
        return np.logspace(0.1, np.log10(q_gl_max), 1000)


    def _prepare_well_data(self, q_gl: List[float], q_oil: List[float]) -> Tuple[np.ndarray, np.ndarray]:
        q_gl = np.array(q_gl, dtype=float)
        q_oil = np.array(q_oil, dtype=float)
        valid_mask = ~(np.isnan(q_gl) | np.isnan(q_oil) | 
                     np.isinf(q_gl) | np.isinf(q_oil))
        q_gl = q_gl[valid_mask]
        q_oil = q_oil[valid_mask]
        return np.maximum(q_gl, 1e-10), q_oil

    def _nishikiori_parameters(self):
        """Return default parameters for Nishikiori model"""
        p0 = [100, 0.1, 100, 100, 50]
        bounds = (
            [-np.inf, -np.inf, 0, -1000, 0],
            [np.inf, np.inf, 200, 1000, 150]
        )
        return p0, bounds

    def _trinidad_parameters(self):
        """Return default parameters for Trinidad model"""
        p0 = [100, -0.1, 100, 100, 50]
        bounds = (
            [-np.inf, -np.inf, 0, 0, 0],
            [np.inf, 0, 200, 1000, 150]
        )  
        return p0, bounds      

    def _fit_model(self, q_gl: np.ndarray, q_oil: np.ndarray, range: np.ndarray) -> np.ndarray:
        """Internal method to fit a single well's data"""
        try:
            p0, bounds = self._trinidad_parameters()
            params_list, _ = optimize.curve_fit(
                self._model_namdar,
                q_gl,
                q_oil,
                p0=p0,
                bounds=bounds,
                maxfev=10000
            )
            
            print("✅ Parameters adjusted:", [f"{param:.2f}" for param in params_list])
            y_pred = self._model_namdar(range, *params_list)
            return np.maximum(y_pred, 0)         
        except Exception as e:
            print(f"❌ Error in the adjustment: {str(e)}")
            return np.zeros_like(range) + np.mean(q_oil)


    def _model_namdar(self, q_gl_range: np.ndarray, a: float, b: float, c: float, 
                    d: float, e: float) -> np.ndarray:
        q_gl_range = np.maximum(q_gl_range, 1e-10)  
        return (
            a + b * q_gl_range + c * (q_gl_range ** 0.7) +
            d * np.log(q_gl_range) + e * np.exp(-(q_gl_range ** 0.6)))
            

    def _model_dan(self, q_gl_range: np.ndarray, a: float, b: float, c: float,
                d: float, e: float) -> np.ndarray:
        q_gl_range = np.maximum(q_gl_range, 1e-10)
        return (
            a + b * q_gl_range + c * (q_gl_range ** 0.5) +
            d * np.log(q_gl_range) + e * np.exp(-q_gl_range))

    def perform_fitting_group(self) -> Dict:
        """
        Perform curve fitting for all wells
        
        Returns:
            Dictionary containing:
            - qgl_range: Generated gas lift range
            - y_pred_list: Predicted oil rates for each well
            - plot_data: Visualization-ready data for each well
        """
        self.q_gl_range = self._calculate_qgl_range()
        self.y_pred_list = []
        self.plot_data = []

        for well_num, (q_gl, q_oil) in enumerate(zip(self.q_gl_list, self.q_oil_list)):

            # Prepare, clean data and perform fitting
            q_gl_clean, q_oil_clean = self._prepare_well_data(q_gl, q_oil)
            y_pred = self._fit_model(q_gl_clean, q_oil_clean, self.q_gl_range)
            self.y_pred_list.append(y_pred)
            
            # Store plot data
            self.plot_data.append({
                "well_num": well_num + 1,
                "q_gl_actual": q_gl_clean,
                "q_oil_actual": q_oil_clean,
                "q_gl_range": self.q_gl_range,
                "q_oil_predicted": y_pred
            })

        return {
            "qgl_range": self.q_gl_range,
            "y_pred_list": self.y_pred_list,
            "plot_data": self.plot_data
        }
