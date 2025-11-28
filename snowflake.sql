-- 1. Configuración inicial
CREATE DATABASE IF NOT EXISTS SANDBOX;
USE DATABASE SANDBOX;

-- 2. Crear esquema
CREATE SCHEMA IF NOT EXISTS GLTB;

CREATE SEQUENCE IF NOT EXISTS optimizations_id_seq START WITH 1 INCREMENT BY 1;

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
);

CREATE SEQUENCE IF NOT EXISTS well_results_id_seq START WITH 1 INCREMENT BY 1;

CREATE TABLE IF NOT EXISTS well_results (
    id INTEGER PRIMARY KEY DEFAULT well_results_id_seq.NEXTVAL,
    optimization_id INTEGER REFERENCES optimizations(id),
    well_number INTEGER,
    well_name VARCHAR(100),
    optimal_production FLOAT,
    optimal_gas_injection FLOAT
);

-- Prueba la consulta
SELECT * FROM SANDBOX.GLTB.OPTIMIZATIONS;

-- Prueba la consulta
SELECT * FROM SANDBOX.GLTB.WELL_RESULTS;