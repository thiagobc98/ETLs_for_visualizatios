SELECT fk_id_contrato,
	id_fatura,
    vencimento_fatura,
    pagamento_fatura,
    status_fatura
	
FROM faturas
WHERE exc_fatura = 'F'
