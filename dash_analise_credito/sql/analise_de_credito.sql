-- --
-- --  KAIROS 
-- -- 
-- SELECT 
--     PE.nome_pretendente,
--     PE.doc_pretendente,
--     PE.profissao_pretendente,
--     PE.renda_presumida_pretendente,
--     PE.renda_pretendente,
--     PE.score_assertiva_pretendente,
    
-- 	CASE 
-- 	    WHEN PE.score_assertiva_pretendente BETWEEN 0 AND 100 THEN "0 - 100" 
-- 	    WHEN PE.score_assertiva_pretendente BETWEEN 100 AND 200 THEN "100 - 200"
-- 	    WHEN PE.score_assertiva_pretendente BETWEEN 200 AND 300 THEN "200 - 300" 
-- 	    WHEN PE.score_assertiva_pretendente BETWEEN 300 AND 400 THEN "300 - 400" 
-- 	    WHEN PE.score_assertiva_pretendente BETWEEN 400 AND 500 THEN "400 - 500" 
-- 	    WHEN PE.score_assertiva_pretendente BETWEEN 500 AND 600 THEN "500 - 600" 
-- 	    WHEN PE.score_assertiva_pretendente BETWEEN 600 AND 700 THEN "600 - 700" 
-- 	    WHEN PE.score_assertiva_pretendente BETWEEN 700 AND 800 THEN "700 - 800" 
-- 	    WHEN PE.score_assertiva_pretendente BETWEEN 800 AND 900 THEN "800 - 900" 
-- 	    WHEN PE.score_assertiva_pretendente BETWEEN 900 AND 1000 THEN "900 - 1000" 
-- 	    ELSE "Null" 
-- 	END AS 'faixa_de_score',
	
--     CASE 
--         WHEN (PE.vinculo_empregaticio = 1) THEN 'Aposentado/Pensionista'
--         WHEN (PE.vinculo_empregaticio = 2) THEN 'Autônomo'
--         WHEN (PE.vinculo_empregaticio = 3) THEN 'Empresário'
--         WHEN (PE.vinculo_empregaticio = 4) THEN 'Estudante'
--         WHEN (PE.vinculo_empregaticio = 5) THEN 'Funcionário CLT'
--         WHEN (PE.vinculo_empregaticio = 6) THEN 'Funcionário Público'
--         WHEN (PE.vinculo_empregaticio = 7) THEN 'Profissional Liberal'
--         WHEN (PE.vinculo_empregaticio = 8) THEN 'Renda proveniente de aluguéis'
--     END AS 'vinculo_empregaticio',

--     CASE
--         WHEN
--             (PE.resultado_analise_pretendente = 1) THEN 'Análise de Crédito Aprovada'
		
-- 		WHEN (PE.resultado_analise_pretendente = 2
-- 				OR PE.resultado_analise_pretendente = 3
--                 OR PE.resultado_analise_pretendente = 7)
--         THEN 'Análise de Crédito Pré-Aprovado'
      
--         WHEN
--             (PE.resultado_analise_pretendente = 4) 
-- 		THEN
--             'Análise de Crédito Elegível para Manual'
-- 		WHEN (PE.resultado_analise_pretendente = 5) THEN 'Análise de Crédito Recusa contornável'

--         WHEN (PE.resultado_analise_pretendente = 6) THEN 'Análise de Crédito Recusada'
--     END AS 'Resultado_Analise_Pretendente',

--     PE.resultado_final,
--     PA.id_parceiro,
--     PA.nome_parceiro,
--     DATE_FORMAT(PE.data_hora_insert, '%d/%m/%Y') AS data_analise,
--     FORMAT(PE.aluguel_pretendente, 2, 'de_DE') AS valor_aluguel_analisado,
--     PE.resultado_analise_pretendente,
--     PE.origem_analise
-- FROM pretendentes PE
--     INNER JOIN usuarios U ON PE.user_add_pretendente = U.id_usu
--     INNER JOIN parceiros PA ON U.id_usu = PA.user_parceiro
-- WHERE resultado_analise_pretendente != 0
--     AND fk_id_pretendente_pretendentes IS NULL
--     AND PE.origem_analise = 1
--     AND YEAR(PE.data_hora_insert) >= 2023

-- UNION ALL 

-- --
-- -- ROCKET 
-- --
-- SELECT 
--     PE.nome_pretendente,
--     PE.doc_pretendente,
--     PE.profissao_pretendente,
--     PE.renda_presumida_pretendente,
--     PE.renda_pretendente,
--     PE.score_assertiva_pretendente,
    
-- 	CASE 
-- 	    WHEN PE.score_assertiva_pretendente BETWEEN 0 AND 100 THEN "0 - 100" 
-- 	    WHEN PE.score_assertiva_pretendente BETWEEN 100 AND 200 THEN "100 - 200"
-- 	    WHEN PE.score_assertiva_pretendente BETWEEN 200 AND 300 THEN "200 - 300" 
-- 	    WHEN PE.score_assertiva_pretendente BETWEEN 300 AND 400 THEN "300 - 400" 
-- 	    WHEN PE.score_assertiva_pretendente BETWEEN 400 AND 500 THEN "400 - 500" 
-- 	    WHEN PE.score_assertiva_pretendente BETWEEN 500 AND 600 THEN "500 - 600" 
-- 	    WHEN PE.score_assertiva_pretendente BETWEEN 600 AND 700 THEN "600 - 700" 
-- 	    WHEN PE.score_assertiva_pretendente BETWEEN 700 AND 800 THEN "700 - 800" 
-- 	    WHEN PE.score_assertiva_pretendente BETWEEN 800 AND 900 THEN "800 - 900" 
-- 	    WHEN PE.score_assertiva_pretendente BETWEEN 900 AND 1000 THEN "900 - 1000" 
-- 	    ELSE "Null" 
-- 	END AS 'faixa_de_score',
	
    
-- 	CASE 
--         WHEN (PE.vinculo_empregaticio = 1) THEN 'Aposentado/Pensionista'
--         WHEN (PE.vinculo_empregaticio = 2) THEN 'Autônomo'
--         WHEN (PE.vinculo_empregaticio = 3) THEN 'Empresário'
--         WHEN (PE.vinculo_empregaticio = 4) THEN 'Estudante'
--         WHEN (PE.vinculo_empregaticio = 5) THEN 'Funcionário CLT'
--         WHEN (PE.vinculo_empregaticio = 6) THEN 'Funcionário Público'
--         WHEN (PE.vinculo_empregaticio = 7) THEN 'Profissional Liberal'
--         WHEN (PE.vinculo_empregaticio = 8) THEN 'Renda proveniente de aluguéis'
-- 	END AS 'vinculo_empregaticio',

--     CASE
--         WHEN
--             (PE.resultado_analise_pretendente = 1) THEN 'Análise de Crédito Aprovada'
		
-- 		WHEN (PE.resultado_analise_pretendente = 2
-- 				OR PE.resultado_analise_pretendente = 3
--                 OR PE.resultado_analise_pretendente = 7)
--                 THEN 'Análise de Crédito Pré-Aprovado'
      
--         WHEN
--             (PE.resultado_analise_pretendente = 4) 
-- 		THEN
--             'Análise de Crédito Elegível para Manual'
-- 		WHEN (PE.resultado_analise_pretendente = 5) THEN 'Análise de Crédito Recusa contornável'

--         WHEN (PE.resultado_analise_pretendente = 6) THEN 'Análise de Crédito Recusada'
--     END AS 'Resultado_Analise_Pretendente',

--     PE.resultado_final,
--     PA.id_parceiro,
--     PA.nome_parceiro,
--     DATE_FORMAT(PE.data_hora_insert, '%d/%m/%Y') AS data_analise,
--     FORMAT(PE.aluguel_pretendente, 2, 'de_DE') AS valor_aluguel_analisado,
--     PE.resultado_analise_pretendente,
--     PE.origem_analise
-- FROM pretendentes PE 
--     INNER JOIN user US ON PE.user_add_pretendente = US.id_user
--     INNER JOIN parceiros PA ON US.id_user = PA.user_parceiro
-- WHERE resultado_analise_pretendente != 0
--     AND fk_id_pretendente_pretendentes IS NULL
--     AND PE.origem_analise = 2
--     AND YEAR(PE.data_hora_insert) >= 2023

SELECT 
    tbp.nome as 'nome_pretendente',
    tbp.documento as 'documento_pretendente',
    tbp.cargo_funcao as 'profissao_pretendente',
    tbp.renda as 'renda_pretendente',
    tbas.renda_presumida as 'renda_presumida_pretendente',
    tbas.score_assertiva as 'score_assertiva_pretendente',
    CASE 
	    WHEN tbas.score_assertiva BETWEEN 0 AND 100 THEN "0 - 100" 
	    WHEN tbas.score_assertiva BETWEEN 100 AND 200 THEN "100 - 200"
	    WHEN tbas.score_assertiva BETWEEN 200 AND 300 THEN "200 - 300" 
	    WHEN tbas.score_assertiva BETWEEN 300 AND 400 THEN "300 - 400" 
	    WHEN tbas.score_assertiva BETWEEN 400 AND 500 THEN "400 - 500" 
	    WHEN tbas.score_assertiva BETWEEN 500 AND 600 THEN "500 - 600" 
	    WHEN tbas.score_assertiva BETWEEN 600 AND 700 THEN "600 - 700" 
	    WHEN tbas.score_assertiva BETWEEN 700 AND 800 THEN "700 - 800" 
	    WHEN tbas.score_assertiva BETWEEN 800 AND 900 THEN "800 - 900" 
	    WHEN tbas.score_assertiva BETWEEN 900 AND 1000 THEN "900 - 1000" 
	    ELSE "Null" 
	END AS 'faixa_de_score',
    CASE 
        WHEN (tbp.vinculo_trabalhista_ramo_atividade = 1) THEN 'Aposentado/Pensionista'
        WHEN (tbp.vinculo_trabalhista_ramo_atividade = 2) THEN 'Autônomo'
        WHEN (tbp.vinculo_trabalhista_ramo_atividade = 3) THEN 'Profissional Liberal'
        WHEN (tbp.vinculo_trabalhista_ramo_atividade = 4) THEN 'Empresário'
        WHEN (tbp.vinculo_trabalhista_ramo_atividade = 5) THEN 'Funcionário Público'
        WHEN (tbp.vinculo_trabalhista_ramo_atividade = 6) THEN 'Funcionário CLT'
        WHEN (tbp.vinculo_trabalhista_ramo_atividade = 7) THEN 'Estudante'
        WHEN (tbp.vinculo_trabalhista_ramo_atividade = 8) THEN 'Renda proveniente de aluguéis'
    END AS 'vinculo_empregaticio',
    CASE
    WHEN tbfhs.tb_status_novo = 1 THEN 'Análise automática'
    WHEN tbfhs.tb_status_novo = 2 THEN 'Aprovado Análise automática'
    WHEN tbfhs.tb_status_novo = 3 THEN 'Pré-aprovado Análise automática'
    WHEN tbfhs.tb_status_novo = 4 THEN 'Eleito pra Humanizada Análise automática'
    WHEN tbfhs.tb_status_novo = 5 THEN 'Recusado Análise automática'
    WHEN tbfhs.tb_status_novo = 6 THEN 'Análise Humanizada Enviada'
    WHEN tbfhs.tb_status_novo = 7 THEN 'Análise Humanizada com Pendência'
    WHEN tbfhs.tb_status_novo = 8 THEN 'Em análise UP'
    WHEN tbfhs.tb_status_novo = 9 THEN 'Recusado Humanizada'
    WHEN tbfhs.tb_status_novo = 10 THEN 'Aprovado Humanizada'
    WHEN tbfhs.tb_status_novo = 11 THEN 'Aprovado Comportamental'
    WHEN tbfhs.tb_status_novo = 12 THEN 'Recusado Comportamental'
    WHEN tbfhs.tb_status_novo = 13 THEN 'Contrato Recebido'
    WHEN tbfhs.tb_status_novo = 14 THEN 'Pendência anti-fraude imobiliária'
    WHEN tbfhs.tb_status_novo = 15 THEN 'Anti-fraude em análise'
    WHEN tbfhs.tb_status_novo = 16 THEN 'Recusado anti-fraude'
    WHEN tbfhs.tb_status_novo = 17 THEN 'Aprovado anti-fraude'
    ELSE 'Status Desconhecido'
END AS 'Resultado_Analise_Pretendente',
    p.id_parceiro, 
    p.nome_parceiro,
    DATE_FORMAT(tbf.data_hora_insert, '%d/%m/%Y') AS data_analise,
    FORMAT(tbf.valor_aluguel, 2, 'de_DE') AS valor_aluguel_analisado
    
FROM 
    tb_ficha tbf
    JOIN parceiros p ON tbf.fk_parceiro_id = p.id_parceiro
JOIN tb_ficha_pretendente tbfp ON tbfp.tb_ficha_id = tbf.id
JOIN tb_pretendente tbp ON tbp.id = tbfp.pretendente_id
JOIN tb_assertiva_score tbas ON tbas.id = tbfp.tb_assertiva_score_id
JOIN tb_ficha_historico_status tbfhs ON tbfhs.tb_ficha_id = tbf.id
WHERE YEAR(tbf.data_hora_insert) >= 2025 AND MONTH(tbf.data_hora_insert) >= 05
    AND tbfhs.tb_status_novo != 0

