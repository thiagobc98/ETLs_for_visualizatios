SELECT
    C.id_contrato, P.id_parceiro, P.nome_parceiro AS 'Parceiro',
    FORMAT(
        SUM(
            IF (
                F.valor_pago_fatura IS NOT NULL,
                F.valor_pago_fatura,
                ((
                    (SELECT IFNULL(SUM(valor_lan), 0) FROM lancamentos l
                     WHERE l.fk_id_fatura = F.id_fatura AND l.debito_lan = 2 AND l.exc_lan = 'F') -
                    (SELECT IFNULL(SUM(valor_lan), 0) FROM lancamentos l
                     WHERE l.fk_id_fatura = F.id_fatura AND l.credito_lan = 2 AND l.exc_lan = 'F')
                )
            )
        )), 2, 'de_DE'
    ) AS valor_fatura,
    
    F.status_fatura,

    COUNT(*) AS quantidade_de_boletos,

    FORMAT(
        SUM(
            IF (
                F.valor_pago_fatura IS NOT NULL,
                F.valor_pago_fatura,
                ((
                    (SELECT IFNULL(SUM(valor_lan), 0) FROM lancamentos l
                     WHERE l.fk_id_fatura = F.id_fatura AND l.debito_lan = 2 AND l.exc_lan = 'F') -
                    (SELECT IFNULL(SUM(valor_lan), 0) FROM lancamentos l
                     WHERE l.fk_id_fatura = F.id_fatura AND l.credito_lan = 2 AND l.exc_lan = 'F')
                ))
            )
        ) / COUNT(*),
    2, 'de_DE')  AS valor_por_fatura_de_contrato,

	IF (C.fk_id_status_status_contrato = '2', 'Ativo', 'Não Ativo') AS status_contrato,
	Pup.nome_produto
        
FROM contratos C
INNER JOIN faturas F ON F.fk_id_contrato = C.id_contrato
INNER JOIN imoveis I ON C.fk_id_imovel_imoveis = I.id_imovel
INNER JOIN parceiros P ON P.id_parceiro = I.fk_id_parceiro_parceiros
INNER JOIN produtos_up Pup ON Pup.id_produtos_up = C.fk_id_produtos_up
WHERE F.status_fatura = 'PE'
AND F.exc_fatura = 'F'
AND C.exc_contrato = 'F'
AND F.url_boleto_fatura IS NOT NULL
AND F.pagamento_fatura IS NULL
AND F.vencimento_fatura <= CURDATE()
AND F.adicional_fatura = 'F'
GROUP BY id_contrato