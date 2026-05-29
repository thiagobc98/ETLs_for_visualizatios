SELECT 
	F.id_fatura, 
	'boletos_pagos' AS tipo_select,
	DATE_FORMAT(F.pagamento_fatura, '%d/%m/%Y') AS dt_fluxo,

    FORMAT(F.valor_pago_fatura - (
		SELECT IFNULL(SUM(valor_lan), 0) FROM lancamentos L
		WHERE fk_id_fatura = id_fatura AND credito_lan = 5 AND exc_lan = 'F' 
	) , 2, 'de_DE') AS valor

FROM faturas F
WHERE F.exc_fatura = 'F' 
    AND F.url_boleto_fatura IS NOT NULL -- Garante que o boleto foi gerado
    AND F.pagamento_fatura  IS NOT NULL -- Pegar apenas boletos pagos 
HAVING dt_fluxo <= CURDATE()
    
UNION ALL

SELECT 
	F.id_fatura, 
	'repasse_terceiros' AS tipo_select, 
	
	CONCAT(
		'12/', LPAD(MONTH(vencimento_fatura), 2, '0'), '/',YEAR(vencimento_fatura)
	) AS dt_fluxo,

	IF (pagamento_fatura  IS NOT NULL, 
		FORMAT((L.valor_lan * -1), 2, 'de_DE'),
		0
	)AS valor

FROM faturas F 
INNER JOIN lancamentos L ON L.fk_id_fatura = F.id_fatura 
WHERE F.exc_fatura = 'F'  
	AND L.exc_lan = 'F' AND L.credito_lan = 6
HAVING dt_fluxo <= CURDATE()
    
UNION ALL

SELECT 
	 F.id_fatura, 
     'repasse_proprietario' AS tipo_select,
	 DATE_FORMAT(F.data_repasse_fatura, '%d/%m/%Y') AS dt_fluxo,
     CASE 
     	WHEN(
	     	FORMAT(IF (pagamento_fatura  IS NOT NULL,  
		     	(
		     		((
						SELECT IFNULL(SUM(valor_lan), 0) FROM lancamentos 
				    	WHERE fk_id_fatura = id_fatura AND credito_lan = 1 AND exc_lan = 'F'
		     		)-(
			        	SELECT IFNULL(SUM(valor_lan), 0) FROM lancamentos 
			        	WHERE fk_id_fatura = id_fatura AND debito_lan = 1 AND exc_lan = 'F'
		        	))
					
		        )*-1, 
				(
					((
						SELECT IFNULL(SUM(valor_lan), 0) FROM lancamentos L
		    			WHERE fk_id_fatura = id_fatura AND credito_lan = 1 AND exc_lan = 'F' AND L.fk_id_release IN (1, 2, 4, 17)
					)-(
		    			SELECT IFNULL(SUM(valor_lan), 0) FROM lancamentos L
						WHERE fk_id_fatura = id_fatura AND debito_lan = 1 AND exc_lan = 'F' AND L.fk_id_release IN (1, 2, 4, 17)
					)) 
				)* -1
	    	), 2, 'de_DE') 
     	) > 0 THEN 0
     	ELSE 
     		FORMAT(IF (pagamento_fatura  IS NOT NULL,  
		     	(
		     		((
						SELECT IFNULL(SUM(valor_lan), 0) FROM lancamentos 
				    	WHERE fk_id_fatura = id_fatura AND credito_lan = 1 AND exc_lan = 'F'
		     		)-(
			        	SELECT IFNULL(SUM(valor_lan), 0) FROM lancamentos 
			        	WHERE fk_id_fatura = id_fatura AND debito_lan = 1 AND exc_lan = 'F'
		        	))
					
		        )*-1, 
				(
					((
						SELECT IFNULL(SUM(valor_lan), 0) FROM lancamentos L
		    			WHERE fk_id_fatura = id_fatura AND credito_lan = 1 AND exc_lan = 'F' AND L.fk_id_release IN (1, 2, 4, 17)
					)-(
		    			SELECT IFNULL(SUM(valor_lan), 0) FROM lancamentos L
						WHERE fk_id_fatura = id_fatura AND debito_lan = 1  AND exc_lan = 'F' AND L.fk_id_release IN (1, 2, 4, 17)
					)) 
				)* -1
	    	), 2, 'de_DE') 
     END AS valor
FROM faturas F 
WHERE data_repasse_fatura IS NOT NULL -- verificar despesas não garantidas: despesas que a up não garante
    AND F.exc_fatura = 'F' 
    AND F.url_boleto_fatura IS NOT NULL -- Garante que o boleto foi gerado
HAVING dt_fluxo <= CURDATE() 
    
UNION ALL

SELECT 
     F.id_fatura, 
     'repasse_parceiros' AS tipo_select,
     
     IF(F.data_repasse_fatura IS NULL, NULL, 
     	CONCAT('25/', LPAD(MONTH(vencimento_fatura), 2, '0'), '/', YEAR(vencimento_fatura))
     ) AS dt_fluxo,
 	 
     CASE 
     	WHEN(
	     	FORMAT(IF (pagamento_fatura  IS NOT NULL,  
		     	(
		     		((
						SELECT IFNULL(SUM(valor_lan), 0) FROM lancamentos 
				    	WHERE fk_id_fatura = id_fatura AND (credito_lan = 3 OR credito_lan = 4) AND exc_lan = 'F'
		     		)-(
			        	SELECT IFNULL(SUM(valor_lan), 0) FROM lancamentos 
			        	WHERE fk_id_fatura = id_fatura AND (debito_lan = 3 OR debito_lan = 4) AND exc_lan = 'F'
		        	))
					
		        )*-1, 
				(
					((
						SELECT IFNULL(SUM(valor_lan), 0) FROM lancamentos L
		    			WHERE fk_id_fatura = id_fatura AND (credito_lan = 3 OR credito_lan = 4) AND exc_lan = 'F' AND L.fk_id_release IN (1, 2, 4, 17)
					)-(
		    			SELECT IFNULL(SUM(valor_lan), 0) FROM lancamentos L
						WHERE fk_id_fatura = id_fatura AND (debito_lan = 3 OR debito_lan = 4) AND exc_lan = 'F' AND L.fk_id_release IN (1, 2, 4, 17)
					)) 
				)* -1
	    	), 2, 'de_DE') 
     	) > 0 THEN 0
     	ELSE 
     		FORMAT(IF (pagamento_fatura  IS NOT NULL,  
		     	(
		     		((
						SELECT IFNULL(SUM(valor_lan), 0) FROM lancamentos 
				    	WHERE fk_id_fatura = id_fatura AND (credito_lan = 3 OR credito_lan = 4) AND exc_lan = 'F'
		     		)-(
			        	SELECT IFNULL(SUM(valor_lan), 0) FROM lancamentos 
			        	WHERE fk_id_fatura = id_fatura AND (debito_lan = 3 OR debito_lan = 4) AND exc_lan = 'F'
		        	))
					
		        )*-1, 
				(
					((
						SELECT IFNULL(SUM(valor_lan), 0) FROM lancamentos L
		    			WHERE fk_id_fatura = id_fatura AND (credito_lan = 3 OR credito_lan = 4) AND exc_lan = 'F' AND L.fk_id_release IN (1, 2, 4, 17)
					)-(
		    			SELECT IFNULL(SUM(valor_lan), 0) FROM lancamentos L
						WHERE fk_id_fatura = id_fatura AND (debito_lan = 3 OR debito_lan = 4) AND exc_lan = 'F' AND L.fk_id_release IN (1, 2, 4, 17)
					)) 
				)* -1
	    	), 2, 'de_DE') 
     END AS valor
FROM faturas F 
WHERE data_repasse_fatura IS NOT NULL -- verificar despesas não garantidas: despesas que a up não garante
    AND F.exc_fatura = 'F' 
    AND F.url_boleto_fatura IS NOT NULL -- Garante que o boleto foi gerado
HAVING dt_fluxo <= CURDATE()