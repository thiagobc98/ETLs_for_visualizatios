-- WITH contratos_agrupados AS (
--     SELECT 
--         p.nome_parceiro, 
--         pu.nome_produto,
--         COUNT(*) AS count_contratos,
--         SUM(c.valor_aluguel_contrato) AS valor_aluguel
--     FROM contratos c
--         INNER JOIN parceiros p ON c.fk_id_parceiro_parceiros = p.id_parceiro
--         INNER JOIN status_contrato s ON c.fk_id_status_status_contrato = s.id_status
--         INNER JOIN produtos_up pu ON pu.id_produtos_up = c.fk_id_produtos_up 
--     WHERE c.fk_id_status_status_contrato IN (2,3,4) 
--       AND c.codigo_contrato NOT LIKE 'S-%'
--       AND c.exc_contrato = 'F' AND p.exc_parceiro = 'F'
--     GROUP BY p.nome_parceiro, pu.nome_produto
-- ),
-- contratos_ordenados AS (
--     SELECT 
--         nome_parceiro,
--         nome_produto,
--         count_contratos,
--         valor_aluguel,
--         SUM(valor_aluguel) OVER (
--             ORDER BY valor_aluguel DESC 
--             ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
--         ) AS valor_aluguel_acumulado
--     FROM contratos_agrupados
-- ),
-- resultado_final AS (
--     SELECT
--         nome_parceiro,
--         nome_produto,
--         count_contratos,
--         SUM(count_contratos) OVER (
--             ORDER BY count_contratos DESC 
--             ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
--         ) AS qtd_acumulado
--     FROM contratos_ordenados
-- ),
-- max_acumulado AS (
--     SELECT MAX(qtd_acumulado) AS max_qtd_acumulado
--     FROM resultado_final
-- ),
-- percentuais AS (
--     SELECT
--         rf.nome_parceiro,
--         rf.nome_produto,
--         rf.count_contratos,
--         rf.qtd_acumulado,
--         (rf.count_contratos / ma.max_qtd_acumulado) * 100 AS porcentagem,
--         (SUM(rf.count_contratos) OVER (
--             ORDER BY rf.qtd_acumulado 
--             ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
--         ) / ma.max_qtd_acumulado) * 100 AS porcentagem_acumulada
--     FROM resultado_final rf
--     CROSS JOIN max_acumulado ma
--     ORDER BY rf.nome_parceiro DESC
-- )
-- SELECT 
--     p.nome_parceiro,
--     p.nome_produto,
--     p.count_contratos,
--     p.qtd_acumulado,
--     p.porcentagem,
--     p.porcentagem_acumulada,
--     CASE 
--         WHEN p.porcentagem_acumulada <= 80 THEN 'A' 
--         WHEN p.porcentagem_acumulada > 80 AND p.porcentagem_acumulada <= 95 THEN 'B'
--         WHEN p.porcentagem_acumulada > 95 AND p.porcentagem_acumulada <= 100 THEN 'C'
--     END AS classe
-- FROM percentuais p;


-- WITH contratos_agrupados AS (
--     SELECT 
--         p.nome_parceiro, 
--         pu.nome_produto,
--         COUNT(*) AS count_contratos,
--         SUM(c.valor_aluguel_contrato) AS valor_aluguel,
--         MAX(c.pontualizado) AS pontualizado
--     FROM contratos c
--         INNER JOIN parceiros p ON c.fk_id_parceiro_parceiros = p.id_parceiro
--         INNER JOIN status_contrato s ON c.fk_id_status_status_contrato = s.id_status
--         INNER JOIN produtos_up pu ON pu.id_produtos_up = c.fk_id_produtos_up 
--     WHERE c.fk_id_status_status_contrato IN (2,3,4) 
--       AND c.codigo_contrato NOT LIKE 'S-%'
--       AND c.exc_contrato = 'F' 
--       AND p.exc_parceiro = 'F'
--     GROUP BY p.nome_parceiro, pu.nome_produto
-- ),

-- contratos_ordenados AS (
--     SELECT 
--         nome_parceiro,
--         nome_produto,
--         count_contratos,
--         valor_aluguel,
--         pontualizado,
--         SUM(valor_aluguel) OVER (
--             ORDER BY valor_aluguel DESC 
--             ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
--         ) AS valor_aluguel_acumulado
--     FROM contratos_agrupados
-- ),

-- resultado_final AS (
--     SELECT
--         nome_parceiro,
--         nome_produto,
--         count_contratos,
--         pontualizado,
--         SUM(count_contratos) OVER (
--             ORDER BY count_contratos DESC 
--             ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
--         ) AS qtd_acumulado
--     FROM contratos_ordenados
-- ),

-- max_acumulado AS (
--     SELECT MAX(qtd_acumulado) AS max_qtd_acumulado
--     FROM resultado_final
-- ),

-- percentuais AS (
--     SELECT
--         rf.nome_parceiro,
--         rf.nome_produto,
--         rf.count_contratos,
--         rf.pontualizado,
--         rf.qtd_acumulado,
--         (rf.count_contratos / ma.max_qtd_acumulado) * 100 AS porcentagem,
--         (SUM(rf.count_contratos) OVER (
--             ORDER BY rf.qtd_acumulado 
--             ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
--         ) / ma.max_qtd_acumulado) * 100 AS porcentagem_acumulada
--     FROM resultado_final rf
--     CROSS JOIN max_acumulado ma
-- )

-- SELECT 
--     p.nome_parceiro,
--     p.nome_produto,
--     p.count_contratos,
--     p.pontualizado,
--     p.qtd_acumulado,
--     p.porcentagem,
--     p.porcentagem_acumulada,
--     CASE 
--         WHEN p.porcentagem_acumulada <= 80 THEN 'A' 
--         WHEN p.porcentagem_acumulada <= 95 THEN 'B'
--         ELSE 'C'
--     END AS classe
-- FROM percentuais p
-- ORDER BY p.nome_parceiro DESC;

WITH contratos_agrupados AS (
    SELECT 
        p.nome_parceiro, 
        pu.nome_produto,
        COUNT(*) AS count_contratos,
        SUM(c.valor_aluguel_contrato) AS valor_aluguel,
        MAX(c.date_inicio_contrato) AS date_inicio_contrato_mais_rescente,
        MAX(c.pontualizado) AS pontualizado
    FROM contratos c
        INNER JOIN parceiros p 
            ON c.fk_id_parceiro_parceiros = p.id_parceiro
        INNER JOIN status_contrato s 
            ON c.fk_id_status_status_contrato = s.id_status
        INNER JOIN produtos_up pu 
            ON pu.id_produtos_up = c.fk_id_produtos_up 
    WHERE c.fk_id_status_status_contrato IN (2,3,4) 
      AND c.codigo_contrato NOT LIKE 'S-%'
      AND c.exc_contrato = 'F' 
      AND p.exc_parceiro = 'F'
    GROUP BY p.nome_parceiro, pu.nome_produto
),

contratos_ordenados AS (
    SELECT 
        nome_parceiro,
        nome_produto,
        count_contratos,
        valor_aluguel,
        date_inicio_contrato_mais_rescente,
        SUM(valor_aluguel) OVER (
            ORDER BY valor_aluguel DESC 
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS valor_aluguel_acumulado,
        pontualizado
    FROM contratos_agrupados
),

resultado_final AS (
    SELECT
        nome_parceiro,
        nome_produto,
        count_contratos,
        date_inicio_contrato_mais_rescente,
        SUM(count_contratos) OVER (
            ORDER BY count_contratos DESC 
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS qtd_acumulado,
        pontualizado
    FROM contratos_ordenados
),

max_acumulado AS (
    SELECT MAX(qtd_acumulado) AS max_qtd_acumulado
    FROM resultado_final
),

percentuais AS (
    SELECT
        rf.nome_parceiro,
        rf.nome_produto,
        rf.count_contratos,
        rf.date_inicio_contrato_mais_rescente,
        rf.qtd_acumulado,
        (rf.count_contratos / ma.max_qtd_acumulado) * 100 AS porcentagem,
        (SUM(rf.count_contratos) OVER (
            ORDER BY rf.qtd_acumulado 
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) / ma.max_qtd_acumulado) * 100 AS porcentagem_acumulada,
        rf.pontualizado
    FROM resultado_final rf
    CROSS JOIN max_acumulado ma
)

SELECT 
    p.nome_parceiro,
    p.nome_produto,
    p.count_contratos,
    p.qtd_acumulado,
    p.porcentagem,
    p.porcentagem_acumulada,
    CASE 
        WHEN p.porcentagem_acumulada <= 80 THEN 'A' 
        WHEN p.porcentagem_acumulada <= 95 THEN 'B'
        ELSE 'C'
    END AS classe,
    p.date_inicio_contrato_mais_rescente,
    p.pontualizado
FROM percentuais p
ORDER BY p.nome_parceiro DESC;