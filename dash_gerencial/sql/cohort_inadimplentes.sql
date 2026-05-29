SELECT 
    C.codigo_contrato,
    C.date_inicio_contrato,
    IF(C.data_rescisao_contrato IS NULL, 
    	 C.date_finalizacao_contrato, C.data_rescisao_contrato
    ) AS data_de_rescisao,
    P.nome_parceiro,
    F.id_fatura,
    F.vencimento_fatura,
    F.pagamento_fatura,
    F.status_fatura,
    IF(F.vencimento_fatura > current_date(), 0, 1) AS 'Inadimplentes'
FROM
    contratos C
        INNER JOIN
    faturas F ON F.fk_id_contrato = C.id_contrato
        INNER JOIN
    parceiros P ON P.id_parceiro = C.fk_id_parceiro_parceiros
WHERE
        C.exc_contrato = 'F'
        AND F.exc_fatura = 'F'
        AND P.exc_parceiro = 'F'
        #AND F.adicional_fatura = 'F'
        AND F.url_boleto_fatura IS NOT NULL
        AND F.pagamento_fatura IS NULL
        AND F.status_fatura = 'PE'
        AND C.fk_id_status_status_contrato IN (2 , 3, 4)
        AND F.vencimento_fatura < current_date()
#        AND nome_parceiro = 'VIA M EMPREENDIMENTOS IMOBILIARIOS LTDA'
