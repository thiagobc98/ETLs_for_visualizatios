SELECT id_contrato,
codigo_contrato, 
	nome_parceiro, 
	date_inicio_contrato, 
    data_pausa_contrato,
	meses_duracao_contrato, 
	FORMAT(valor_aluguel_contrato, 2, 'de_DE') AS valor_aluguel_contrato,
	name_status,
	CASE 	
		WHEN c.migracao = 0 THEN "Nao"
		WHEN c.migracao = 1 THEN "Sim"
		ELSE c.migracao
	END AS 'migracao',
    p.email_parceiro,
    e.rua_end, 
    e.numero_end,
    e.complemento_end,
    e.bairro_end,
    e.cidade_end, 
    e.estado_end,
    e.cep_end,
    smp.nome AS 'Status motivo pausa'
FROM contratos c
	INNER JOIN parceiros p ON c.fk_id_parceiro_parceiros = p.id_parceiro
	INNER JOIN status_contrato s ON c.fk_id_status_status_contrato = s.id_status
    LEFT JOIN imoveis i ON  c.fk_id_imovel_imoveis = i.id_imovel
    INNER JOIN enderecos e ON e.id_ator = i.id_imovel 
    LEFT JOIN tb_status_motivos_pausa smp ON smp.id = c.fk_id_motivo_pausa
WHERE exc_contrato = 'F' AND exc_parceiro = 'F' AND
fk_id_status_status_contrato IN (2,3,4) AND e.fk_id_cat_pessoascategorias = 5 
