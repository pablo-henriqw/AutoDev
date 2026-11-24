import os
from dotenv import load_dotenv

load_dotenv()

def analyze_report(report):
    """
    Fase inicial: classifica o relato e prepara uma análise.
    Ainda NÃO altera arquivos nem publica código.
    """
    description = f"{report['title']} {report['description']}".lower()

    high_risk_terms = [
        "pagamento", "pix", "cartão", "senha", "login", "autenticação",
        "dados pessoais", "banco de dados", "apagou", "perdi meus dados",
        "vazamento", "segurança", "acesso indevido"
    ]
    low_risk_terms = [
        "texto", "ortografia", "cor", "ícone", "icone", "alinhamento",
        "margem", "espaçamento", "espacamento", "tamanho da fonte"
    ]

    if any(term in description for term in high_risk_terms):
        risk = "high"
        severity = "critical"
        analysis = (
            "O relato pode envolver autenticação, pagamento, dados ou segurança. "
            "Requer investigação cuidadosa e aprovação humana antes de qualquer publicação."
        )
    elif any(term in description for term in low_risk_terms):
        risk = "low"
        severity = "minor"
        analysis = (
            "O relato parece relacionado à apresentação visual ou conteúdo. "
            "É candidato a uma correção de baixo risco, mas ainda precisa de reprodução e testes."
        )
    else:
        risk = "medium"
        severity = "moderate"
        analysis = (
            "Não foi possível determinar o risco apenas pelo relato. "
            "É necessário consultar logs, reproduzir o problema e revisar o impacto."
        )

    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=api_key)
            response = client.responses.create(
                model=os.getenv("OPENAI_MODEL", "gpt-5.5"),
                instructions=(
                    "Você é o analista de suporte do AutoDev AI. Analise o relato em português. "
                    "Não invente causa raiz, não peça senhas ou dados sensíveis e não proponha "
                    "alterações diretas em produção. Indique hipóteses, evidências necessárias "
                    "e próximos passos. A classificação de risco determinística do sistema "
                    "continua prevalecendo."
                ),
                input=(
                    f"Título: {report['title']}\\nDescrição: {report['description']}\\n"
                    f"Página: {report.get('page_url') or 'não informada'}\\n"
                    f"Risco preliminar: {risk}"
                ),
                max_output_tokens=450
            )
            analysis = response.output_text.strip() or analysis
        except Exception as exc:
            analysis += f" (Análise por IA indisponível; classificação local utilizada: {type(exc).__name__}.)"

    return {"risk": risk, "severity": severity, "analysis": analysis}
