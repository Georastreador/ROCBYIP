def lgpd_check(plan: dict) -> dict:
    issues = []
    secrecy = plan.get("user",{}).get("secrecy")
    security = plan.get("security",[])

    if secrecy in ("restrito","confidencial","secreto"):
        if not security:
            issues.append("Plano com sigilo elevado requer medidas de segurança definidas.")
        else:
            must = {"controle de acesso","criptografia","trilha de auditoria"}
            if not must.intersection(set([s.lower() for s in security])):
                issues.append("Inclua medidas de: controle de acesso, criptografia ou trilha de auditoria.")

    tw = plan.get("time_window",{})
    s, e = tw.get("start"), tw.get("end")
    if s and e and s > e:
        issues.append("Faixa de tempo inválida: início posterior ao fim.")

    if plan.get("aspects_essential") and not plan.get("aspects_to_know"):
        issues.append("Liste os Aspectos a Conhecer derivados dos Aspectos Essenciais.")

    return {"ok": len(issues) == 0, "issues": issues}
