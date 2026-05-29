SELECT C.codigo_contrato, 
    MIN(vencimento_fatura) 
FROM faturas F
INNER JOIN contratos C ON F.fk_id_contrato = C.id_contrato
WHERE C.exc_contrato = 'F' 
	AND F.exc_fatura = 'F' 
    AND C.date_inicio_contrato >= '2023-01-01'  
GROUP BY id_contrato;