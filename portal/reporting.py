import html
import json


def json_document(result: dict) -> str:
    return json.dumps(result, ensure_ascii=False, indent=2)


def html_report(result: dict) -> str:
    probabilities = "".join(
        f"<tr><td>{html.escape(item['label'])}</td><td>{item['value'] * 100:.1f}%</td></tr>"
        for item in result["probabilities"]
    )
    recommendations = "".join(f"<li>{html.escape(item)}</li>" for item in result["recommendations"])
    symptoms = ", ".join(result.get("symptoms", [])) or "Não informados"
    notice = html.escape(result.get("decisionSupportNotice", "Uso exclusivo para ensino e pesquisa."))
    return f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<title>Relatório {html.escape(result['id'])}</title>
<style>
body{{font-family:Arial,sans-serif;color:#183036;margin:42px;line-height:1.5}}h1,h2{{color:#12333b}}.meta{{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin:20px 0}}.card{{border:1px solid #dce5e3;border-radius:10px;padding:16px}}table{{width:100%;border-collapse:collapse}}td,th{{border-bottom:1px solid #e4eae8;padding:9px;text-align:left}}.notice{{margin-top:28px;padding:15px;background:#edf7f4;border-left:4px solid #0f766e}}
</style>
</head>
<body>
<h1>PET-Saúde Sinais Clínicos</h1>
<p>Relatório acadêmico de pré-análise</p>
<div class="meta">
<div class="card"><strong>Caso</strong><br>{html.escape(result['recordCode'])}</div>
<div class="card"><strong>Modalidade</strong><br>{html.escape(result['modalityName'])}</div>
<div class="card"><strong>Qualidade</strong><br>{result['inspection']['quality']}%</div>
</div>
<h2>Classe priorizada</h2>
<p><strong>{html.escape(result['primaryFinding'])}</strong> com probabilidade de {result['confidence']}% e incerteza {html.escape(result['uncertainty'].lower())}.</p>
<h2>Distribuição das hipóteses</h2>
<table><thead><tr><th>Hipótese</th><th>Probabilidade</th></tr></thead><tbody>{probabilities}</tbody></table>
<h2>Contexto informado</h2>
<p><strong>Sinais e sintomas:</strong> {html.escape(symptoms)}</p>
<p><strong>Observações:</strong> {html.escape(result.get('notes') or 'Não informadas')}</p>
<h2>Próximas verificações</h2>
<ol>{recommendations}</ol>
<div class="notice">{notice}</div>
</body>
</html>"""
