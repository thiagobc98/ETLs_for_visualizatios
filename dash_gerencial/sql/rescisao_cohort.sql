SELECT 
    C.codigo_contrato,
    C.date_inicio_contrato AS data_de_inicio,
    IF(C.data_rescisao_contrato IS NULL, 
    	 C.date_finalizacao_contrato, C.data_rescisao_contrato
    ) AS data_de_rescisao,
    UPPER(P.nome_parceiro) AS parceiro
FROM contratos C
INNER JOIN parceiros P ON P.id_parceiro = C.fk_id_parceiro_parceiros 
WHERE C.exc_contrato = 'F' AND 
	P.exc_parceiro = 'F' AND 
	C.fk_id_status_status_contrato IN (2, 3, 4) AND
	C.date_inicio_contrato >= '2023-01-01'  
GROUP BY C.codigo_contrato 
ORDER BY C.date_inicio_contrato, C.codigo_contrato ;