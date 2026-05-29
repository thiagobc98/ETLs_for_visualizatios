-- WITH contratos_agrupados AS (
--     SELECT 
--         p.nome_parceiro, 
--         pu.nome_produto,
--         COUNT(*) AS count_contratos,  -- Aqui conta o total de contratos
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
--         valor_aluguel,
--         valor_aluguel_acumulado,
--         (valor_aluguel / MAX(valor_aluguel_acumulado) OVER ()) * 100 AS porcentagem,
--         (valor_aluguel_acumulado / MAX(valor_aluguel_acumulado) OVER ()) * 100 AS porcentagem_acumulada
--     FROM contratos_ordenados
-- )
-- SELECT
--     nome_parceiro,
--     nome_produto,
--     count_contratos,
--     valor_aluguel,
--     valor_aluguel_acumulado,
--     porcentagem,
--     porcentagem_acumulada,
--     CASE 
--         WHEN porcentagem_acumulada <= 80 THEN 'A' 
--         WHEN porcentagem_acumulada > 80 AND porcentagem_acumulada <= 95 THEN 'B'
--         WHEN porcentagem_acumulada > 95 THEN 'C'
--     END AS classe
-- FROM resultado_final
-- ORDER BY porcentagem_acumulada;

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
--         valor_aluguel,
--         valor_aluguel_acumulado,
--         pontualizado,
--         (valor_aluguel / MAX(valor_aluguel_acumulado) OVER ()) * 100 AS porcentagem,
--         (valor_aluguel_acumulado / MAX(valor_aluguel_acumulado) OVER ()) * 100 AS porcentagem_acumulada
--     FROM contratos_ordenados
-- )

-- SELECT
--     nome_parceiro,
--     nome_produto,
--     count_contratos,
--     valor_aluguel,
--     valor_aluguel_acumulado,
--     pontualizado,
--     porcentagem,
--     porcentagem_acumulada,
--     CASE 
--         WHEN porcentagem_acumulada <= 80 THEN 'A' 
--         WHEN porcentagem_acumulada <= 95 THEN 'B'
--         ELSE 'C'
--     END AS classe
-- FROM resultado_final
-- ORDER BY porcentagem_acumulada;

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
        valor_aluguel,
        valor_aluguel_acumulado,
        pontualizado,
        date_inicio_contrato_mais_rescente,
        (valor_aluguel / MAX(valor_aluguel_acumulado) OVER ()) * 100 AS porcentagem,
        (valor_aluguel_acumulado / MAX(valor_aluguel_acumulado) OVER ()) * 100 AS porcentagem_acumulada
    FROM contratos_ordenados
)

SELECT
    nome_parceiro,
    nome_produto,
    count_contratos,
    valor_aluguel,
    valor_aluguel_acumulado,
    date_inicio_contrato_mais_rescente,
    porcentagem,
    porcentagem_acumulada,
    CASE 
        WHEN porcentagem_acumulada <= 80 THEN 'A' 
        WHEN porcentagem_acumulada <= 95 THEN 'B'
        ELSE 'C'
    END AS classe,
    pontualizado
FROM resultado_final
ORDER BY porcentagem_acumulada;