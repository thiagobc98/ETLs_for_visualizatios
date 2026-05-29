SELECT codigo_contrato, 
	nome_parceiro, 
	date_inicio_contrato, 
	meses_duracao_contrato, 
	FORMAT(valor_aluguel_contrato, 2, 'de_DE') AS valor_aluguel_contrato, 
	FORMAT(taxa_contrato, 2, 'de_DE') AS taxa_contrato, 
	FORMAT(taxa_admin_contrato, 2, 'de_DE')AS taxa_admin_contrato, 
	name_status,
	pu.nome_produto,
	CASE 	
		WHEN c.migracao = 0 THEN "Nao"
		WHEN c.migracao = 1 THEN "Sim"
		ELSE c.migracao
	END AS 'migracao',
    CASE
		WHEN c.pontualizado = 0 THEN "Não"
        WHEN c.pontualizado = 1 THEN "Sim"
        WHEN c.pontualizado = 2 THEN "Tombamento"
	END AS 'pontualizado'
FROM contratos c
	INNER JOIN parceiros p ON c.fk_id_parceiro_parceiros = p.id_parceiro
	INNER JOIN status_contrato s ON c.fk_id_status_status_contrato = s.id_status
	INNER JOIN produtos_up pu ON pu.id_produtos_up = c.fk_id_produtos_up 
WHERE c.fk_id_status_status_contrato IN (2,3,4) AND c.exc_contrato = 'F' AND p.exc_parceiro = 'F'
ORDER BY nome_parceiro
