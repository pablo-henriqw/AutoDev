# AutoDev AI — MVP

Primeira versão funcional do sistema de suporte:
- widget incorporável em sites;
- API Flask para receber relatos;
- dashboard protegido por senha;
- persistência local em SQLite;
- análise preliminar de risco e análise textual opcional pela OpenAI API.

## O que esta versão ainda NÃO faz
Ela não lê o repositório do site, não modifica arquivos, não cria Pull Requests e não publica correções. A análise é apenas diagnóstica. Isso é intencional: primeiro validamos o fluxo de relatos e a classificação de risco.

## Executar localmente

Requer Python 3.10 ou superior.

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt
```

Copie `.env.example` para `.env`, defina `FLASK_SECRET_KEY` e `ADMIN_PASSWORD`.

```bash
python backend/app.py
```

Abra `http://localhost:5000/login`, entre com a senha definida e acesse o dashboard.

## Incorporar o widget em outro site

Adicione antes de fechar a tag `</body>`:

```html
<script
  src="http://localhost:5000/widget/support.js"
  data-api="http://localhost:5000">
</script>
```

Em produção, substitua `http://localhost:5000` pelo domínio HTTPS onde o AutoDev estiver hospedado.

Configure `ALLOWED_ORIGINS` com os domínios dos sites autorizados. Para produção, não use `*`.

## Segurança e próxima fase

- Use HTTPS.
- Nunca coloque a chave da OpenAI no JavaScript do navegador.
- Não envie senhas, tokens, cookies ou dados pessoais nos relatos/logs.
- Restrinja origens e adicione rate limiting, verificação de domínio e proteção anti-spam antes de abrir ao público.
- Próxima fase: integração com Sentry/logs e GitHub em branch isolada, testes automatizados e Pull Request. Deploy automático só após regras de risco, testes e rollback.
