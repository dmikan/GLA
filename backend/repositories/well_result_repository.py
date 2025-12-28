from backend.entities.well_result import WellResult
from backend.entities.database import SnowflakeDB
from typing import List

class WellResultRepository:
    def __init__(self, db: SnowflakeDB):
        self.db = db

    def save(self, result: WellResult) -> bool:
        """Save a WellResult entity"""
        query = """
        INSERT INTO well_optimizations (
            field_optimization_id, well_number, well_name,
            optimal_production, optimal_gas_injection
        ) VALUES (%s, %s, %s, %s, %s)
        """
        try:
            params = (
                    result.optimization_id,
                    result.well_number,
                    result.well_name,
                    result.optimal_production,
                    result.optimal_gas_injection
                )
            self.db.execute_query(query, params)
            return True
        except Exception as e:
            raise e

    def find_by_optimization_id(self, opt_id: int) -> List[WellResult]:
        query = """
            SELECT * FROM well_optimizations 
            WHERE field_optimization_id = %s
            """
        results = self.db.execute_query(query, (opt_id,))
        return [WellResult.from_dict(row) for row in results]


    def find_latest(self, limit: int = None) -> List[WellResult]:
        query = """
            SELECT w.*, o.execution_date 
            FROM well_optimizations w
            JOIN (
            SELECT id, execution_date
            FROM field_optimizations o
            ORDER BY execution_date DESC
            LIMIT 1
            ) AS o
            ON w.field_optimization_id = o.id                           
            """
        if limit:
            query += f" LIMIT {limit}"
        results = self.db.execute_query(query)
        return [WellResult.from_dict(row) for row in results]