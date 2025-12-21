from backend.services.optimization_service import OptimizationService
from backend.services.well_result_service import WellResultService
from backend.entities.well_result import WellResult
from backend.entities.optimization import Optimization
from backend.entities.database import SnowflakeDB

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

        optimization_service = OptimizationService(self.db)
        well_result_service = WellResultService(self.db)

        # Create the optimization record passing the complete dictionary
        opt_id = optimization_service.write_in_database(data)

        # Create well results passing also the same dictionary
        well_result_service.write_in_database(data, optimization_id=opt_id)

        return opt_id


    def save_global_optimization_results(self, data: dict) -> int:
        """Saves complete optimization results including wells"""
        pass

