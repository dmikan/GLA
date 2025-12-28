from typing import List, Optional
from backend.entities.optimization import Optimization
from backend.repositories.optimization_repository import OptimizationRepository

class OptimizationService:
    def __init__(self, optimization_repository: OptimizationRepository):
        self.optimization_repository = optimization_repository

    def create_field_optimization(self, total_production: float, total_gas_injection: float, gas_injection_limit: float, oil_price: float, gas_price: float, plant_name: str) -> int:
        try:
            opt = Optimization() 
            opt.total_production = total_production
            opt.total_gas_injection = total_gas_injection
            opt.gas_injection_limit = gas_injection_limit
            opt.oil_price = oil_price
            opt.gas_price = gas_price
            opt.field_name = plant_name
            return self.optimization_repository.save(opt)
        except Exception as e:
            raise ValueError(f"Error creating optimization: {str(e)}")


    def get_latest_field_optimization(self) -> Optional[Optimization]:
        return self.optimization_repository.find_latest()


    def list_field_optimizations(self, limit: int = 10) -> List[Optimization]:
        return self.optimization_repository.find_all(limit=limit)


    


