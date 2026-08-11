from collections.abc import Mapping


ALLOWED_DOMAINS = frozenset({"ucpel.edu.br", "sou.ucpel.edu.br"})


def normalize_email(value: object) -> str:
    return str(value or "").strip().lower()


def email_domain(value: object) -> str:
    email = normalize_email(value)
    if email.count("@") != 1 or any(character.isspace() for character in email):
        return ""
    local, domain = email.rsplit("@", 1)
    if not local or not domain:
        return ""
    return domain.rstrip(".")


def is_allowed_email(value: object, domains: frozenset[str] = ALLOWED_DOMAINS) -> bool:
    return email_domain(value) in domains


def is_verified(value: object) -> bool:
    return value is True or str(value).strip().lower() == "true"


def authorize_claims(claims: Mapping[str, object]) -> tuple[bool, str, str]:
    email = normalize_email(claims.get("email"))
    if not email:
        return False, "", "A conta Google não forneceu um endereço de e-mail."
    if not is_verified(claims.get("email_verified")):
        return False, email, "O endereço de e-mail não foi confirmado pelo Google."
    if not is_allowed_email(email):
        return False, email, "O acesso é exclusivo para contas institucionais da UCPel."
    return True, email, ""
