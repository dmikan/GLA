from backend.services.optimization_model_service import OptimizationModel
import numpy as np
from scipy.interpolate import interp1d

class OptimizationGlobalPipelineService:
    """Handles the complete optimization workflow from data processing to solution"""
    
    def __init__(self, 
                q_gl_common_range: np.ndarray,
                q_oil_rates_list: list,
                qgl_min: int = 0,
                p_qoil: float = 0.0,
                p_qgl: float = 0.0,
                max_iterations: int = 40,
                max_qgl: int = 20000):
        """
        Initialize the optimization pipeline with required parameters
        
        Args:
            q_gl_common_range: Array of gas lift injection rates
            q_oil_rates_list: List of well production predictions
            qgl_limit: Total gas lift availability constraint
            p_qoil: Oil price for economic calculation
            p_qgl: Gas lift cost for economic calculation
        """
        self.q_gl_common_range = q_gl_common_range
        self.q_oil_rates_list = q_oil_rates_list
        self.qgl_min = qgl_min
        self.p_qoil = p_qoil
        self.p_qgl = p_qgl
        self.model = None
        self.result_prod_rates = None
        self.result_optimal_qgl = None
        self.current_qgl = None
        self.optimization_results = {"qgl_limit": [], "total_production": [], "total_qgl": []}
        self.qgl_history = []
        self.qgl_min = 0
        self.max_iterations = max_iterations
        self.max_qgl = max_qgl


    ''' 
    this method runs the optimization pipeline for a range of gas lift injection rates
    it uses a logspace to generate the range of gas lift injection rates and 
    it runs the optimization pipeline for each gas lift injection rate
    it returns the optimization results
    '''
    def run(self) -> dict:
        log_vals = np.logspace(start=1, stop=np.log10(self.max_qgl), num=self.max_iterations)
        log_vals = np.unique(log_vals)
        
        for i, qgl_limit in enumerate(log_vals): 
            dic_optim_result = self._execute(qgl_limit)
            qgl_history = self._list_optim(dic_optim_result, qgl_limit)
            if self._has_stabilized(values=qgl_history, window_size=12, tolerance=1e-15):
                break    
        self._interpolate_results()
        self._calculate_global_marginal_analysis()     
        return self.optimization_results

    ''' 
    this method checks if the gas lift injection rate has stabilized 
    it uses a window size to check if the gas lift injection rate has stabilized
    it returns True if the gas lift injection rate has stabilized
    '''               
    def _has_stabilized(self, values, window_size=3, tolerance=1e-6) -> bool:
            if len(values) < window_size:
                return False
            recent = values[-window_size:]
            return all(abs(x - recent[0]) < tolerance for x in recent)

    ''' 
    this method calculates the optimal gas lift rates using marginal analysis 
    it returns the optimal gas lift rates for each well 
    '''
    def _calculate_marginal_analysis(self) -> list:
        delta_q_gl = np.diff(self.q_gl_common_range)
        p_qgl_optim_list = []
        
        for well in range(len(self.q_oil_rates_list)):
            delta_q_oil = np.diff(self.q_oil_rates_list[well])
            mp = delta_q_oil / delta_q_gl  # Marginal Product
            mrp = self.p_qoil * mp  # Marginal Revenue Product
            qgl_values = self.q_gl_common_range[:-1]
            
            # Find last point where MRP >= gas lift cost
            optimal_idx = np.where(mrp >= self.p_qgl)[0][-1] if any(mrp >= self.p_qgl) else len(mrp)-1
            p_qgl_optim_list.append(qgl_values[optimal_idx])      
        return p_qgl_optim_list

    ''' 
    this method sets up the optimization model and configure the optimization model 
    with parameters
    '''
    def _setup_optimization_model(self, p_qgl_optim_list: list, qgl_limit: int) -> None:
        self.model = OptimizationModel(
            q_gl=self.q_gl_common_range,
            q_fluid_wells=self.q_oil_rates_list,
            available_qgl_total=qgl_limit,
            qgl_min=self.qgl_min,
            p_qgl_list=p_qgl_optim_list
        )
        self.model.define_optimisation_problem()
        self.model.define_variables()
        self.model.build_objective_function()
        self.model.add_constraints()


    ''' 
    this method runs the complete optimization pipeline using the other methods
    it returns the optimization results
    '''
    def _execute(self, qgl_limit) -> dict:
        p_qgl_optim_list = self._calculate_marginal_analysis() # Step 1: Marginal analysis 
        self._setup_optimization_model(p_qgl_optim_list, qgl_limit) # Step 2: Model setup
        self.model.solve_prob() # Step 3: Solve optimization
        self.result_prod_rates = self.model.get_maximised_prod_rates() # Step 4: Get results
        self.result_optimal_qgl = self.model.get_optimal_injection_rates()  
        return self._format_results(qgl_limit)


    ''' 
    this method formats the results into a dictionary
    it returns the formatted results
    '''
    def _format_results(self, qgl_limit) -> dict:
        return {
            "total_production": sum(self.result_prod_rates),
            "total_qgl": sum(self.result_optimal_qgl),
            "qgl_limit": qgl_limit,
            "well_production_rates": self.result_prod_rates,
            "well_gas_injection_rates": self.result_optimal_qgl
        }

    ''' 
    this method stores the optimization results in a list
    it returns the list of optimization results
    '''
    def _list_optim(self, dic_optim_result, qgl_limit) -> list:
        """Run the complete optimization pipeline"""
        current_qgl = dic_optim_result["total_qgl"]
        self.optimization_results["qgl_limit"].append(qgl_limit)
        self.optimization_results["total_production"].append(dic_optim_result["total_production"])
        self.optimization_results["total_qgl"].append(dic_optim_result["total_qgl"])
        self.qgl_history.append(current_qgl)
        return self.qgl_history


    def _calculate_global_marginal_analysis(self) -> None:
        """Calculate optimal gas lift rates using marginal analysis"""
        delta_q_gl_total = np.diff(self.optimization_results["qgl_dense"])
        delta_q_oil_total = np.diff(self.optimization_results["prod_dense"])
        mrp_total = self.p_qoil * (delta_q_oil_total / delta_q_gl_total)
        qgl_values_total = self.optimization_results["qgl_dense"][:-1]

        optimal_idx = np.where(mrp_total >= self.p_qgl)[0][-1] if any(mrp_total >= self.p_qgl) else len(mrp_total)-1
        p_qgl_optim_total = qgl_values_total[optimal_idx]
        p_qoil_optim_total = self.optimization_results["prod_dense"][optimal_idx]
        self.optimization_results["p_qgl_optim_total"] = p_qgl_optim_total
        self.optimization_results["p_qoil_optim_total"] = p_qoil_optim_total


    def _interpolate_results(self) -> None:
        """
        Interpolate total production (Y) vs. total QGL (X) to create a smooth curve 
        and generates a new, dense set of points for marginal analysis.
        
        Returns:
            dict: Diccionario con 'qgl_dense' (X) y 'prod_dense' (Y) interpolados.
        """
        
        # 1. get data points
        qgl_points = np.array(self.optimization_results["total_qgl"])
        prod_points = np.array(self.optimization_results["total_production"])
        
        # 2. remove duplicates and sort
        unique_indices = np.unique(qgl_points, return_index=True)[1]
        qgl_points = qgl_points[unique_indices]
        prod_points = prod_points[unique_indices]
        
        # 3. create interpolation function
        f_interp = interp1d(
            qgl_points, 
            prod_points, 
            kind='linear' 
        )
        
        # 4. generate new dense range of QGL
        qgl_min_interp = qgl_points.min()
        qgl_max_interp = qgl_points.max()
        
        qgl_dense = np.linspace(qgl_min_interp, qgl_max_interp, 100)
        
        # 5. apply interpolation function
        prod_dense = f_interp(qgl_dense)
        
        self.optimization_results["qgl_dense"] = qgl_dense
        self.optimization_results["prod_dense"] = prod_dense