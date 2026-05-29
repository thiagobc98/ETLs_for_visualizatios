-- SELECT PA.id_parceiro, 
--     PA.nome_parceiro, 
--     DATE_FORMAT( PE.data_hora_insert, '%d/%m/%Y') AS data_analise, 
--     FORMAT(PE.aluguel_pretendente, 2, 'de_DE') AS valor_aluguel_analisado,
--     PE.resultado_analise_pretendente,
--     PU.nome_produto
-- FROM pretendentes PE
--     INNER JOIN usuarios U ON PE.user_add_pretendente = U.id_usu
--     INNER JOIN parceiros PA ON U.id_usu = PA.user_parceiro
--     INNER JOIN produtos_up PU ON PU.id_produtos_up = PA.fk_id_produtos_up_produtos_up
-- WHERE resultado_analise_pretendente != 0 
--     AND fk_id_pretendente_pretendentes IS NULL
--     AND PE.origem_analise = 1

-- UNION ALL 

-- SELECT PA.id_parceiro, 
--     PA.nome_parceiro, 
--     DATE_FORMAT( PE.data_hora_insert, '%d/%m/%Y') AS data_analise, 
--     FORMAT(PE.aluguel_pretendente, 2, 'de_DE') AS valor_aluguel_analisado,
--     PE.resultado_analise_pretendente,
--     PU.nome_produto
-- FROM pretendentes PE
--     INNER JOIN user US ON PE.user_add_pretendente = US.id_user
--     INNER JOIN parceiros PA ON US.id_user = PA.user_parceiro
-- 	INNER JOIN produtos_up PU ON PU.id_produtos_up = PA.fk_id_produtos_up_produtos_up
-- WHERE resultado_analise_pretendente != 0 
--     AND fk_id_pretendente_pretendentes IS NULL
-- 	AND PE.origem_analise = 2

 SELECT PA.id_parceiro, 
     PA.nome_parceiro, 
     DATE_FORMAT(tbf.data_hora_insert, '%d/%m/%Y') AS data_analise,
     FORMAT(tbf.valor_aluguel, 2, 'de_DE') AS valor_aluguel_analisado,
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
     PU.nome_produto
 FROM tb_ficha tbf
     JOIN tb_ficha_pretendente tbfp ON tbfp.tb_ficha_id = tbf.id
	 JOIN tb_pretendente tbp ON tbp.id = tbfp.pretendente_id
	 JOIN tb_assertiva_score tbas ON tbas.id = tbfp.tb_assertiva_score_id
	 JOIN tb_ficha_historico_status tbfhs ON tbfhs.tb_ficha_id = tbf.id
     INNER JOIN parceiros PA ON tbf.fk_parceiro_id = PA.user_parceiro
     INNER JOIN produtos_up PU ON PU.id_produtos_up = PA.fk_id_produtos_up_produtos_up
 WHERE  YEAR(tbf.data_hora_insert) >= 2025 AND MONTH(tbf.data_hora_insert) >= 05
    AND tbfhs.tb_status_novo != 0



