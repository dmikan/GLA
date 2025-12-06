from typing import List, Optional
from backend.models.optimization import Optimization
from backend.models.database import SnowflakeDB
import pandas as pd
from datetime import datetime

class OptimizationService:
    def __init__(self, db: SnowflakeDB):
        self.db = db # it is an aggregation relationship. it would be composition if self.db = SnowflakeDB().
    
    def create_optimization(self, data: dict) -> int:
        try:
            # step 1: get the next value of the sequence
            id_query = "SELECT optimizations_id_seq.NEXTVAL"
            rows = self.db.execute_query(id_query)
            new_id = rows[0]['NEXTVAL']

            # step 2: extract data from the dictionary
            total_prod = data["total_prod"]
            total_qgl = data["total_qgl"]
            qgl_limit = data.get("qgl_limit", 1000)
            oil_price = data.get("oil_price", 0.0)
            gas_price = data.get("gas_price", 0.0)
            field_name = data["info"][0]
            #filename = data["filename"]

            # step 3: make the insert with the extracted values
            query = """
                INSERT INTO optimizations (
                    id, execution_date, total_production, total_gas_injection, gas_injection_limit,
                    oil_price, gas_price, plant_name
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            params = (
                new_id,
                datetime.now(),
                float(total_prod),
                float(total_qgl),
                float(qgl_limit),
                float(oil_price),
                float(gas_price),
                str(field_name),
                #str(filename),
            )
            self.db.execute_query(query, params)
            return new_id
        except Exception as e:
            raise ValueError(f"Error creating optimization: {str(e)}")

    
    def get_latest(self) -> Optional[Optimization]:
        """Get the most recent optimization"""
        query = """
        SELECT * FROM optimizations 
        ORDER BY execution_date DESC 
        LIMIT 1
        """
        result = self.db.execute_query(query)
        return Optimization.from_dict(result[0]) if result else None
    



    def get_all_optimizations(self, limit: int = None) -> List[Optimization]:
        """Get all optimizations ordered by date descending"""
        query = """
        SELECT * FROM optimizations 
        ORDER BY execution_date DESC
        """
        if limit is not None:
            query += f" LIMIT {limit}"
        results = self.db.execute_query(query)
        #df = pd.read_sql(query, self.db.get_connection())
        return [Optimization.from_dict(row) for row in results]






if __name__ == "__main__":
    # Test the OptimizationService class
    db = SnowflakeDB()
    #Optimization.create_table(db)
    optimization_service = OptimizationService(db)
    results = optimization_service.get_all_optimizations()
    for result in results:
        print(result)
    
    # Example usage
    #try:
    #    id = optimization_service.create_optimization({
    #                                            "total_prod": 1000.0,
    #                                            "total_qgl": 500.0,
    #                                            "qgl_limit": 1000.0,
    #                                            "info": ["Plant A"], 
    #                                            "oil_price": 50.0,       
    #                                            "gas_price": 3.0,        
    #                                            "filename": "file.csv"
    #    })
 
        #df = df.sort_values(by="EXECUTION_DATE", ascending=False)
    #    print(id)
    #except Exception as e:
    #    print(f"Error: {e}")


