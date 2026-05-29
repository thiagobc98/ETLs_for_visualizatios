SELECT
    P.nome_parceiro, 
    S.name_status, 
    F.status_fatura, 
    F.adicional_fatura, 
    UPPER(F.status_repasse_fatura) AS status_repasse_fatura,
    FORMAT(F.valor_pago_fatura, 2, 'de_DE') AS valor_fatura, 
    FORMAT(C.valor_aluguel_contrato, 2, 'de_DE') AS valor_aluguel_contrato, 
    DATE_FORMAT(F.data_repasse_fatura, '%d/%m/%Y') AS data_repasse_fatura,
    DATE_FORMAT(F.vencimento_fatura, '%d/%m/%Y') AS data_vencimento_fatura,
    DATE_FORMAT(F.pagamento_fatura, '%d/%m/%Y') AS data_pagamento_fatura
    
FROM contratos C
    INNER JOIN faturas F ON F.fk_id_contrato = C.id_contrato
    INNER JOIN imoveis I ON C.fk_id_imovel_imoveis = I.id_imovel
    INNER JOIN parceiros P ON P.id_parceiro = I.fk_id_parceiro_parceiros 
    INNER JOIN status_contrato S ON S.id_status = C.fk_id_status_status_contrato 
WHERE data_repasse_fatura IS NOT NULL -- verificar despesas não garantidas: despesas que a up não garante
    AND F.exc_fatura = 'F' 
    AND C.exc_contrato = 'F'
    AND F.exc_fatura = 'F'
    AND F.url_boleto_fatura IS NOT NULL -- Garante que o boleto foi gerado
    AND F.status_fatura = 'PG'
    AND F.pagamento_fatura is not null
GROUP BY codigo_contrato, data_repasse_fatura
ORDER BY codigo_contrato, data_repasse_fatura