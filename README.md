# Portal da Transparência: gastos públicos federais

Pipeline de ingestão dos dados de despesas do governo federal, a partir da API do Portal da Transparência (CGU).

**Status:** fase 1, ingestão. Tratamento, carga no S3 e análise com Athena vêm nas próximas fases.

## Como configurar

1. Obtenha uma chave em portaldatransparencia.gov.br/api-de-dados/cadastrar-email (exige conta gov.br Prata ou Ouro).
2. Crie o ambiente e instale as dependências:
   ```
   python -m venv .venv
   source .venv/bin/activate   # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. Copie `.env.example` para `.env` e preencha `TRANSPARENCIA_API_KEY`.

## Como rodar

```
cd scripts
python teste_api.py                 # primeira chamada, salva data/raw/teste.json
python ingestao.py --mes 202401     # baixa todas as páginas do mês
cd .. && pytest                     # testes sem chamadas reais à API
```

## Decisões técnicas

- **Retentativas com espera crescente** para erros 429 e 5xx, com número máximo de tentativas. Respostas que não são JSON de lista também contam como erro.
- **Saída particionada** em `data/raw/ano=AAAA/mes=MM/`, para que cada mês possa ser reprocessado isoladamente.
- **Pausa entre páginas** para ficar bem abaixo do limite de requisições por minuto da API.

## Notas da API

Preencher após a primeira resposta real: campos principais, formato de datas e valores, número de registros por página.
