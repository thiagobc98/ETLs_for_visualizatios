SELECT
    P.nome_parceiro,
        
    COUNT(DISTINCT C.codigo_contrato) AS quantidade_total_de_contratos,
      
    SUM(CASE 
            WHEN DATE_ADD(F.vencimento_fatura, INTERVAL 2 DAY) < CURDATE()  
            AND F.status_fatura = 'PE'  
            AND F.url_boleto_fatura IS NOT NULL 
            AND F.pagamento_fatura IS NULL
    	THEN 1 ELSE 0 END
    ) AS boleto_em_aberto_em_atraso,

    COUNT(DISTINCT CASE 
            WHEN DATE_ADD(F.vencimento_fatura, INTERVAL 2 DAY) < CURDATE() 
            AND F.status_fatura = 'PE'
            AND F.url_boleto_fatura IS NOT NULL 
            AND F.pagamento_fatura IS NULL
    	THEN C.codigo_contrato END
    ) AS quantidade_contratos_com_boletos_em_atraso,

	FORMAT((COUNT(
   		DISTINCT CASE 
			WHEN DATE_ADD(F.vencimento_fatura, INTERVAL 2 DAY) < CURDATE() 
			AND F.status_fatura = 'PE'
			AND F.url_boleto_fatura IS NOT NULL
			AND F.pagamento_fatura IS NULL
       	THEN C.codigo_contrato END) 
       	/ COUNT(DISTINCT C.codigo_contrato)
	), 4, 'de_DE')  AS porcentagem_contratos_por_boletos_em_atraso

FROM contratos C
    INNER JOIN faturas F ON F.fk_id_contrato = C.id_contrato
    INNER JOIN parceiros P ON P.id_parceiro = C.fk_id_parceiro_parceiros
WHERE C.exc_contrato = 'F' 
	AND F.exc_fatura = 'F' 
	AND P.exc_parceiro = 'F' 
	AND F.adicional_fatura = 'F'
GROUP BY P.nome_parceiro
ORDER BY P.nome_parceiro 