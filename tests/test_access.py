from portal.access import authorize_claims, email_domain, is_allowed_email


def test_institutional_domains_are_allowed():
    assert is_allowed_email("docente@ucpel.edu.br")
    assert is_allowed_email("ALUNO@SOU.UCPEL.EDU.BR")


def test_similar_domains_are_rejected():
    assert not is_allowed_email("pessoa@outro-ucpel.edu.br")
    assert not is_allowed_email("pessoa@ucpel.edu.br.example.com")
    assert not is_allowed_email("pessoa@gmail.com")


def test_invalid_addresses_have_no_domain():
    assert email_domain("") == ""
    assert email_domain("sem-arroba") == ""
    assert email_domain("a@@ucpel.edu.br") == ""


def test_verified_claims_are_required():
    allowed, email, reason = authorize_claims({"email": "aluno@sou.ucpel.edu.br", "email_verified": True})
    assert allowed
    assert email == "aluno@sou.ucpel.edu.br"
    assert reason == ""
    denied, _, message = authorize_claims({"email": "aluno@sou.ucpel.edu.br", "email_verified": False})
    assert not denied
    assert "confirmado" in message
