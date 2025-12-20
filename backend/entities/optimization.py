"""
Optimization Entity

"""
from datetime import datetime
from dataclasses import dataclass
from typing import List

from backend.entities.well_result import WellResult

@dataclass
class Optimization:
    """Class representing optimization results"""
    id: int = None
    execution_date: datetime = datetime.now()
    total_production: float = 0.0  # Barrels of oil per day (BOPD)
    total_gas_injection: float = 0.0  # Total gas injection (MSCF/D)
    gas_injection_limit: float = 0.0  # Gas injection limit (MSCF/D)
    oil_price: float = 0.0  # Oil price per barrel (USD)
    gas_price: float = 0.0  # Gas price per unit (USD)
    plant_name: str = ""  # Plant/field name
    source_file: str = ""  # Original data source file
    well_results: List['WellResult'] = None  # List of associated well results

    def __post_init__(self):
        if self.well_results is None:
            self.well_results = []


    @classmethod
    def create_table(cls, db):
        """Create table and sequence for this entity"""
        queries = [
            "CREATE SEQUENCE IF NOT EXISTS optimizations_id_seq START WITH 1 INCREMENT BY 1",
            """
            CREATE TABLE IF NOT EXISTS optimizations (
                id INTEGER PRIMARY KEY DEFAULT optimizations_id_seq.NEXTVAL,
                execution_date TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
                total_production FLOAT,
                total_gas_injection FLOAT,
                gas_injection_limit FLOAT,
                oil_price FLOAT,
                gas_price FLOAT,
                plant_name VARCHAR(100),
                source_file VARCHAR(255)
            )
            """
        ]
        for query in queries:
            db.execute(query)

    @property
    def table_name(self) -> str:
        return "optimizations"

    @classmethod 
    def to_dict(self) -> dict:
        """Convert object to dictionary for database operations"""
        return {
            "total_production": self.total_production,
            "total_gas_injection": self.total_gas_injection,
            "gas_injection_limit": self.gas_injection_limit,
            "oil_price": self.oil_price,
            "gas_price": self.gas_price,
            "plant_name": self.plant_name,
            "source_file": self.source_file
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Optimization':
        """Create object from dictionary"""
        if not data:
            return None
                 
        data = {k.lower(): v for k, v in data.items()} 
        return cls(
            id=data.get('id'),
            execution_date=data.get('execution_date', datetime.now()),
            total_production=data.get('total_production', 0.0),
            total_gas_injection=data.get('total_gas_injection', 0.0),
            gas_injection_limit=data.get('gas_injection_limit', 0.0),
            oil_price=data.get('oil_price', 0.0),
            gas_price=data.get('gas_price', 0.0),
            plant_name=data.get('plant_name', ''),
            source_file=data.get('source_file', '')
        )