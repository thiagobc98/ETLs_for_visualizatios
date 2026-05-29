SELECT 
	C.codigo_contrato,
	I.documento_inquilino
FROM contratos C
	INNER JOIN contratos_inquilinos CI ON CI.fk_id_contrato_contrato = C.id_contrato
	INNER JOIN inquilinos I ON I.id_inquilino = CI.fk_id_inquilino_inquilinos
WHERE C.exc_contrato = 'F' 
	AND I.exc_inquilino = 'F'
	AND CI.principal_ci = 'V'