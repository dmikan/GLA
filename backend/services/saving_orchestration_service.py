from backend.services.optimization_service import OptimizationService
from backend.services.well_result_service import WellResultService
from backend.entities.well_result import WellResult
from backend.entities.optimization import Optimization
from backend.entities.database import SnowflakeDB
from backend.repositories.optimization_repository import OptimizationRepository
from backend.repositories.well_result_repository import WellResultRepository
#Orchestration pattern
class SavingOrchestrationService:
    def __init__(self, db: SnowflakeDB):
        self.db = db
    """Orchestrates the saving of complete optimization results"""

    def save_constrained_optimization_results(self, data: dict) -> int:
        """Saves complete optimization results including wells"""

        # in case of not having access to snowflake directly create the tables from the service
        #Optimization.create_table(self.db)
        #WellResult.create_table(self.db)


        optimization_repository = OptimizationRepository(self.db)
        well_result_repository = WellResultRepository(self.db)
        optimization_service = OptimizationService(optimization_repository)
        well_result_service = WellResultService(well_result_repository)

        # Create the optimization record passing the complete dictionary
        opt_id = optimization_service.create_field_optimization(
            total_production=data["total_prod"],
            total_gas_injection=data["total_qgl"],
            gas_injection_limit=data.get("qgl_limit", 1000),
            oil_price=data.get("oil_price", 0.0),
            gas_price=data.get("gas_price", 0.0),
            plant_name=str(data["info"][0])
        )

        # Create well results passing also the same dictionary
        for well in data["wells_data"]:
            well_result_service.create_well_result(
                optimization_id=opt_id,
                well_number=well["well_number"], 
                well_name=well["well_name"], 
                optimal_production=well["optimal_production"], 
                optimal_gas_injection=well["optimal_gas_injection"]
        )

        return opt_id


    def save_global_optimization_results(self, data: dict) -> int:
        """Saves complete optimization results including wells"""
        pass

