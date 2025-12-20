from backend.services.optimization_service import OptimizationService
from backend.services.well_result_service import WellResultService
from backend.entities.well_result import WellResult
from backend.entities.optimization import Optimization
from backend.entities.database import SnowflakeDB

class ResultsService:
    def __init__(self, db: SnowflakeDB):
        self.db = db
    """Orchestrates the saving of complete optimization results"""

    def save_optimization_results(self, data: dict) -> int:
        """Saves complete optimization results including wells"""

        #Optimization.create_table(db)
        #WellResult.create_table(db)

        optimization_service = OptimizationService(self.db)
        well_result_service = WellResultService(self.db)

        # Crear el registro de optimización pasando el diccionario completo
        opt_id = optimization_service.create_optimization(data)

        # Crear resultados de pozos pasando también el mismo diccionario
        well_result_service.create_well_batch(data, optimization_id=opt_id)

        return opt_id
