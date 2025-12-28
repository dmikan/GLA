from backend.entities.well_result import WellResult
from typing import List
from backend.repositories.well_result_repository import WellResultRepository

class WellResultService:
    def __init__(self, well_result_repository: WellResultRepository):
        self.well_result_repository = well_result_repository
    
    
    def create_well_result(self, optimization_id: int, well_number: int, well_name: str, optimal_production: float, optimal_gas_injection: float) -> bool:
        """Create multiple well results in a single transaction"""
        try:
            well_result = WellResult()
            well_result.optimization_id = optimization_id
            well_result.well_number = well_number
            well_result.well_name = well_name
            well_result.optimal_production = optimal_production
            well_result.optimal_gas_injection = optimal_gas_injection
            self.well_result_repository.save(well_result)  
            return True
        except Exception as e:
            raise ValueError(f"Error creating well results: {str(e)}")

    def get_latest_well_results(self) -> List[WellResult]:
        return self.well_result_repository.find_latest()
    
    
    def get_well_results_by_optimization(self, optimization_id: int) -> List[WellResult]:
        results = self.well_result_repository.find_by_optimization_id(optimization_id)
        return results

