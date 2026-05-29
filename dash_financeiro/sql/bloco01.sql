SELECT
    F.id_fatura,
	DATE_FORMAT(F.pagamento_fatura, '%d/%m/%Y') AS data_pagamento_fatura,
	
    CASE
        WHEN
        YEAR(F.pagamento_fatura) >= YEAR(DATE_ADD(F.vencimento_fatura, INTERVAL 2 MONTH)) AND
            MONTH(F.pagamento_fatura) >= MONTH(DATE_ADD(F.vencimento_fatura, INTERVAL 2 MONTH))
        THEN 1 ELSE 0
    END AS pago_atraso_2_ou_mais,

	CASE
		WHEN
            YEAR(F.pagamento_fatura) = YEAR(DATE_ADD(F.vencimento_fatura, INTERVAL 1 MONTH)) AND
            MONTH(F.pagamento_fatura) = MONTH(DATE_ADD(F.vencimento_fatura, INTERVAL 1 MONTH))
        THEN 1 ELSE 0
    END AS pago_atraso_1_mes,

	CASE
       	WHEN
            YEAR(F.pagamento_fatura) = YEAR(F.vencimento_fatura) AND
            MONTH(F.pagamento_fatura) = MONTH(F.vencimento_fatura)
        THEN 1 ELSE 0
    END AS pago_no_mes,

	CASE
        WHEN
            YEAR(F.pagamento_fatura) <= YEAR(DATE_SUB(F.vencimento_fatura, INTERVAL 1 MONTH)) AND
            MONTH(F.pagamento_fatura) <= MONTH(DATE_SUB(F.vencimento_fatura, INTERVAL 1 MONTH))
        THEN 1 ELSE 0
    END AS pago_antecipado_1_mes,

    FORMAT(F.valor_pago_fatura, 2, 'de_DE') AS valor_pago_fatura, -- isso é para deixar no formato correto do sheet ler
    C.codigo_contrato,
    Pup.nome_produto

FROM faturas F
INNER JOIN contratos C ON F.fk_id_contrato = C.id_contrato
INNER JOIN produtos_up Pup ON Pup.id_produtos_up = C.fk_id_produtos_up
WHERE F.exc_fatura = 'F'
    AND F.url_boleto_fatura IS NOT NULL -- Garante que o boleto foi gerado
    AND F.pagamento_fatura IS NOT NULL
    AND F.status_fatura = 'PG'
ORDER BY F.pagamento_fatura DESC