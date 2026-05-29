SELECT 
    C.codigo_contrato, 
    P.id_parceiro, 
    P.nome_parceiro, 
    C.date_inicio_contrato, 
    SC.name_status
FROM contratos C 
    INNER JOIN status_contrato SC ON SC.id_status = C.fk_id_status_status_contrato
    INNER JOIN parceiros P ON P.id_parceiro = C.fk_id_parceiro_parceiros
WHERE C.exc_contrato = 'F' AND P.exc_parceiro = 'F' AND YEAR(date_inicio_contrato) >= 2023 