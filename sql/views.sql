-- Média por sala
CREATE OR REPLACE VIEW avg_temp_por_sala AS
SELECT "room_id/id" AS sala,
       AVG(temp) AS temperatura_media
FROM temperature_readings
GROUP BY "room_id/id";

-- Leituras por hora
CREATE OR REPLACE VIEW leituras_por_hora AS
SELECT EXTRACT(HOUR FROM noted_date) AS hora,
       COUNT(*) AS contagem
FROM temperature_readings
GROUP BY hora;

-- Max e Min por dia
CREATE OR REPLACE VIEW temp_max_min_por_dia AS
SELECT DATE(noted_date) AS dia,
       MAX(temp) AS temp_max,
       MIN(temp) AS temp_min
FROM temperature_readings
GROUP BY dia;