-- 1. Configuración inicial
CREATE DATABASE IF NOT EXISTS SANDBOX;
USE DATABASE SANDBOX;

-- 2. Crear esquema
CREATE SCHEMA IF NOT EXISTS GLTB;

CREATE SEQUENCE IF NOT EXISTS field_optimizations_id_seq START WITH 1 INCREMENT BY 1;

CREATE TABLE IF NOT EXISTS field_optimizations (
    id INTEGER PRIMARY KEY DEFAULT field_optimizations_id_seq.NEXTVAL,
    execution_date TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    total_production FLOAT,
    total_gas_injection FLOAT,
    gas_injection_limit FLOAT,
    oil_price FLOAT,
    gas_price FLOAT,
    field_name VARCHAR(100)
);

CREATE SEQUENCE IF NOT EXISTS well_optimizations_id_seq START WITH 1 INCREMENT BY 1;

CREATE TABLE IF NOT EXISTS well_optimizations (
    id INTEGER PRIMARY KEY DEFAULT well_optimizations_id_seq.NEXTVAL,
    field_optimization_id INTEGER REFERENCES field_optimizations(id),
    well_number INTEGER,
    well_name VARCHAR(100),
    optimal_production FLOAT,
    optimal_gas_injection FLOAT
);

-- Prueba la consulta
SELECT * FROM SANDBOX.GLTB.FIELD_OPTIMIZATIONS;

-- Prueba la consulta
SELECT * FROM SANDBOX.GLTB.WELL_OPTIMIZATIONS;