SELECT  
	C.codigo_contrato,
    C.id_contrato,
    F.id_fatura,
	P.nome_parceiro, 
	S.name_status, 
	F.adicional_fatura, 
    F.status_repasse_fatura,
	DATE_FORMAT(F.pagamento_fatura, '%d/%m/%Y') AS data_pagamento_fatura, 
    DATE_FORMAT(F.vencimento_fatura, '%d/%m/%Y') AS data_vencimento_fatura,	
	
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
		WHEN F.status_fatura = 'PE' AND F.pagamento_fatura IS NULL THEN 1 ELSE 0 
	END AS pagamento_em_aberto,
	
	CASE
	     WHEN F.status_fatura  = 'PG' AND F.pagamento_fatura <= DATE_ADD(F.vencimento_fatura, INTERVAL 5 DAY) THEN 1 ELSE 0
	END AS pagamento_em_dia,
	
	CASE
	     WHEN F.status_fatura  = 'PG' AND F.pagamento_fatura > DATE_ADD(F.vencimento_fatura, INTERVAL 5 DAY) THEN 1 ELSE 0
	END AS pagamento_em_atraso,
    Pup.nome_produto
	
FROM contratos C
	INNER JOIN faturas F ON F.fk_id_contrato = C.id_contrato
    INNER JOIN parceiros P ON P.id_parceiro = C.fk_id_parceiro_parceiros 
    INNER JOIN status_contrato S ON S.id_status = C.fk_id_status_status_contrato 
    INNER JOIN produtos_up Pup ON Pup.id_produtos_up = C.fk_id_produtos_up
WHERE F.exc_fatura = 'F' 
	AND C.exc_contrato = 'F' 
    AND F.url_boleto_fatura IS NOT NULL 
	AND F.vencimento_fatura  <= CURDATE() -- ADICIONAR +2 DIAS