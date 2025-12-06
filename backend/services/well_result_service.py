from backend.models.well_result import WellResult
from backend.models.database import SnowflakeDB
from typing import List

class WellResultService:
    def __init__(self, db: SnowflakeDB):
        self.db = db
    
    
    def create_well_batch(self, data: dict, optimization_id: int) -> bool:
        """Create multiple well results in a single transaction"""
        query = """
        INSERT INTO well_results (
            optimization_id, well_number, well_name,
            optimal_production, optimal_gas_injection
        ) VALUES (%s, %s, %s, %s, %s)
        """

        try:
            for well in data["wells_data"]:

                params = (
                    optimization_id,
                    well["well_number"],
                    well["well_name"],
                    float(well["optimal_production"]),
                    float(well["optimal_gas_injection"])
                )
                self.db.execute_query(query, params)
                
            return True
        except Exception as e:
            raise ValueError(f"Error creating well results: {str(e)}")

    def get_latest_well_results(self, limit: int = None) -> List[WellResult]:
        """Get all well results ordered by well number"""
        query = """
                SELECT w.*, o.execution_date 
                FROM well_results w
                JOIN (
                SELECT id, execution_date
                FROM optimizations o
                ORDER BY execution_date DESC
                LIMIT 1
                ) AS o
                ON w.optimization_id = o.id                           
                """
        if limit is not None:
            query += f" LIMIT {limit}"
        
        results = self.db.execute_query(query) 
        return [WellResult.from_dict(row) for row in results]
    
    def get_by_optimization(self, optimization_id: int) -> list[WellResult]:
        """Get all well results for an optimization"""
        query = "SELECT * FROM well_results WHERE optimization_id = %s"
        results = self.db.execute_query(query, (optimization_id,))
        return [WellResult.from_dict(row) for row in results]
    





if __name__ == "__main__":
    # Example usage
    db = SnowflakeDB()
    #WellResult.create_table(db)
    well_result_service = WellResultService(db)
    results = well_result_service.get_latest_well_results()
    for well in results:
        print(well)
    
    #try:
    #    # Example data
    #    data = {
    #        "wells_data": [
    #            {
    #                "well_number": 1,
    #                "well_name": "Well A",
    #                "optimal_production": 100.0,
    #                "optimal_gas_injection": 50.0
    #           },
    #            {
    #                "well_number": 2,
    #                "well_name": "Well B",
    #                "optimal_production": 150.0,
    #                "optimal_gas_injection": 75.0
    #            }
    #        ]
    #    }
    #    optimization_id = 1  # Example optimization ID
    #    well_result_service.create_well_batch(data, optimization_id)
    #    print("Well results created successfully.")
    #except Exception as e:
    #    print(f"Error creating well results: {e}")