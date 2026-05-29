SELECT 
    DATE_FORMAT(F.vencimento_fatura, '%d/%m/%Y') AS vencimento_fatura,

    FORMAT(
        SUM(CASE WHEN L.fk_id_release = 5 THEN valor_lan ELSE 0 END), 2, 'de_DE'
    ) AS 'taxa_boleto',

    FORMAT(
        SUM(CASE WHEN L.fk_id_release = 6 THEN valor_lan ELSE 0 END), 2, 'de_DE'
    ) AS 'taxa_ted_doc_pix',

    FORMAT(
        SUM(CASE WHEN L.fk_id_release = 7 THEN valor_lan ELSE 0 END), 2, 'de_DE'
    ) AS 'taxa_servico',

    FORMAT(
        SUM(CASE WHEN L.fk_id_release = 15 THEN valor_lan ELSE 0 END), 2, 'de_DE'
    ) AS 'taxa_administracao_parcela_up',

    FORMAT(
        SUM(CASE WHEN L.fk_id_release = 16 THEN valor_lan ELSE 0 END), 2, 'de_DE'
    ) AS 'taxa_contrato_parcela_up'
 
FROM faturas F 
INNER JOIN lancamentos L ON L.fk_id_fatura = F.id_fatura
WHERE F.data_repasse_fatura IS NOT NULL 
    AND F.exc_fatura = 'F'
    AND F.url_boleto_fatura IS NOT NULL 
    AND L.exc_lan = 'F'
    AND L.fk_id_release in (5,6,7,15,16)
    AND L.credito_lan = 5
    AND F.vencimento_fatura <= CURDATE()
    AND F.pagamento_fatura IS NOT NULL
    AND F.status_fatura = 'PG'
GROUP BY YEAR(F.vencimento_fatura), MONTH(F.vencimento_fatura) 
ORDER BY F.vencimento_fatura