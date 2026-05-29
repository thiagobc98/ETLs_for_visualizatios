SELECT  
    P.nome_parceiro AS parceiro, 
	S.name_status, 
	F.adicional_fatura, 
    UPPER(F.status_repasse_fatura) AS status_repasse_fatura,
	FORMAT(F.valor_pago_fatura, 2, 'de_DE') AS valor_fatura,     
    
    CASE 
     	WHEN(
		    FORMAT(IF (F.status_repasse_fatura = 'F', 0.0,
		        SUM((
		                SELECT IFNULL(SUM(valor_lan),0) FROM lancamentos 
		                WHERE  fk_id_fatura = id_fatura AND credito_lan = 1 AND exc_lan = 'F'
		            )-(
		                SELECT IFNULL(SUM(valor_lan),0) FROM lancamentos 
		                WHERE fk_id_fatura = id_fatura AND debito_lan = 1 AND exc_lan = 'F'
		            )
		        )
		    ), 2, 'de_DE')
		) < 0 THEN 0
    	ELSE (
			FORMAT(IF (F.status_repasse_fatura = 'F', 0.0,
		        SUM((
		                SELECT IFNULL(SUM(valor_lan),0) FROM lancamentos 
		                WHERE  fk_id_fatura = id_fatura AND credito_lan = 1 AND exc_lan = 'F'
		            )-(
		                SELECT IFNULL(SUM(valor_lan),0) FROM lancamentos 
		                WHERE fk_id_fatura = id_fatura AND debito_lan = 1 AND exc_lan = 'F'
		            )
		        )
		    ), 2, 'de_DE'))
	END AS 'valor_repasse_proprietario',
	
    CASE 
     	WHEN(
		    FORMAT(IF(F.status_repasse_fatura = 'F',0.0, 
		        SUM((
		                SELECT IFNULL(SUM(valor_lan),0) FROM lancamentos 
		                WHERE fk_id_fatura = id_fatura AND (credito_lan = 3 OR  credito_lan = 4)  AND exc_lan = 'F' 
		
		            )-(
		                SELECT IFNULL(SUM(valor_lan),0) FROM lancamentos 
		                WHERE fk_id_fatura = id_fatura AND (debito_lan = 3 OR debito_lan = 4) AND exc_lan = 'F'
		            ))
		    ), 2, 'de_DE') 
    	) < 0 THEN 0
    	ELSE (
    		FORMAT(IF(F.status_repasse_fatura = 'F',0.0, 
		        SUM((
		                SELECT IFNULL(SUM(valor_lan),0) FROM lancamentos 
		                WHERE fk_id_fatura = id_fatura AND (credito_lan = 3 OR  credito_lan = 4)  AND exc_lan = 'F' 
		
		            )-(
		                SELECT IFNULL(SUM(valor_lan),0) FROM lancamentos 
		                WHERE fk_id_fatura = id_fatura AND (debito_lan = 3 OR debito_lan = 4) AND exc_lan = 'F'
		            ))
		    ), 2, 'de_DE') )
    END AS 'valor_repasse_parceiro', 
    
    DATE_FORMAT(F.data_repasse_fatura, '%d/%m/%Y') AS data_repasse_fatura, 
	DATE_FORMAT(F.pagamento_fatura, '%d/%m/%Y') AS data_pagamento_fatura, 
    IF(F.data_repasse_fatura IS  NULL, '',
        CONCAT('25/',  LPAD(MONTH(vencimento_fatura), 2, '0'), '/', YEAR(vencimento_fatura)) 
    ) AS data_repasse_parceiro
        
FROM contratos C
    INNER JOIN faturas F ON F.fk_id_contrato = C.id_contrato
    INNER JOIN imoveis I ON C.fk_id_imovel_imoveis = I.id_imovel
    INNER JOIN parceiros P ON P.id_parceiro = I.fk_id_parceiro_parceiros 
    INNER JOIN status_contrato S ON S.id_status = C.fk_id_status_status_contrato 
WHERE data_repasse_fatura IS NOT NULL -- verificar despesas não garantidas: despesas que a up não garante
    AND F.exc_fatura = 'F' 
    AND C.exc_contrato = 'F'
    AND F.url_boleto_fatura IS NOT NULL -- Garante que o boleto foi gerado
GROUP BY C.codigo_contrato, F.data_repasse_fatura
ORDER BY C.codigo_contrato, F.data_repasse_fatura