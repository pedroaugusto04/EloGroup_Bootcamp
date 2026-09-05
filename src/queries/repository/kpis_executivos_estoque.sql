-- src/queries/repository/kpis_executivos_estoque.sql
-- Contagem total de SKUs com estoque disponível zerado (Ruptura Ativa).

SELECT 
    COUNT(*) AS stockout_skus 
FROM estoque 
WHERE em_ruptura = true;
