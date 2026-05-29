SELECT 
    P.nome_parceiro, F.status_fatura,
	
    IF (F.valor_pago_fatura IS NOT NULL, 
		FORMAT(F.valor_pago_fatura, 2, 'de_DE'), 
		FORMAT(((
			SELECT IFNULL(SUM(valor_lan), 0) FROM lancamentos l
	    	WHERE l.fk_id_fatura = F.id_fatura AND l.debito_lan = 2  AND l.exc_lan = 'F'
		)-(
	    	SELECT IFNULL(SUM(valor_lan), 0) FROM lancamentos l
	    	WHERE l.fk_id_fatura = F.id_fatura AND l.credito_lan = 2 AND l.exc_lan = 'F'
		)), 2, 'de_DE')
	) AS valor_fatura, 

    CASE 
        WHEN SUM(CASE WHEN F.status_fatura = 'PE' THEN 1 ELSE 0 END) = 1 
        THEN 1 ELSE 0 
    END AS contratos_com_1_boleto_em_aberto,

    CASE 
        WHEN SUM(CASE WHEN F.status_fatura = 'PE' THEN 1 ELSE 0 END) = 2 
        THEN 1 ELSE 0 
    END AS contratos_com_2_boletos_em_aberto,

    CASE 
        WHEN SUM(CASE WHEN F.status_fatura = 'PE' THEN 1 ELSE 0 END) = 3 
        THEN 1 ELSE 0
    END AS contratos_com_3_boletos_em_aberto,

    CASE 
        WHEN SUM(CASE WHEN F.status_fatura = 'PE' THEN 1 ELSE 0 END) >= 4 
        THEN 1 ELSE 0
    END AS contratos_com_4_ou_mais_boletos_em_aberto,

 	SUM(CASE WHEN F.status_fatura = 'PE' THEN 1 ELSE 0 END) AS quantidade_de_boletos,
	IF (C.fk_id_status_status_contrato = '2', 'Ativo', 'Não Ativo') AS status_contrato,
    Pup.nome_produto


FROM contratos C
	INNER JOIN faturas F ON F.fk_id_contrato = C.id_contrato
    INNER JOIN imoveis I ON C.fk_id_imovel_imoveis = I.id_imovel
    INNER JOIN parceiros P ON P.id_parceiro = I.fk_id_parceiro_parceiros 
    INNER JOIN status_contrato S ON S.id_status = C.fk_id_status_status_contrato 
	INNER JOIN produtos_up Pup ON Pup.id_produtos_up = C.fk_id_produtos_up

WHERE F.status_fatura = 'PE'
    AND F.exc_fatura = 'F' 
    AND C.exc_contrato = 'F'
    AND F.url_boleto_fatura IS NOT NULL 
    AND F.pagamento_fatura IS NULL
    AND F.vencimento_fatura <= CURDATE()
	AND F.adicional_fatura = 'F'

GROUP BY C.id_contrato