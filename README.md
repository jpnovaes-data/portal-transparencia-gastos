# Portal da Transparência: gastos públicos federais

Pipeline de ingestão dos arquivos mensais de execução da despesa federal, publicados em dados abertos pela CGU.

**Status:** fase 1, ingestão e validação concluídas. Carga no S3 e análise com Athena vêm nas próximas fases.

## Fonte dos dados

Arquivos mensais em formato CSV, compactados em ZIP, disponíveis em:

```
https://dadosabertos-download.cgu.gov.br/PortalDaTransparencia/saida/despesas-execucao/AAAAMM_Despesas.zip
```

Não é necessária chave de acesso. A descrição das colunas está no dicionário de dados oficial, linkado na página de [download de dados](https://portaldatransparencia.gov.br/download-de-dados/despesas-execucao).

## Como configurar

1. Clone o repositório e entre na pasta:
   ```
   git clone https://github.com/jpnovaes-data/portal-transparencia-gastos.git
   cd portal-transparencia-gastos
   ```
2. Crie e ative o ambiente virtual:
   ```
   python -m venv .venv
   .venv\Scripts\Activate.ps1      # Linux ou macOS: source .venv/bin/activate
   ```
3. Instale as dependências:
   ```
   pip install -r requirements.txt
   ```

## Como rodar

Os comandos abaixo são executados a partir da raiz do projeto.

```
pytest                                      # testes, sem acesso à internet
```

Para baixar, descompactar e validar um mês:

```
python -c "import sys; sys.path.insert(0,'scripts'); import download, tratamento, validacao; csvs = download.ingerir_mes(2024, 1); df = tratamento.ler_csv(csvs[0]); print(validacao.validar(df)); print(validacao.avisos(df))"
```

Os arquivos são salvos em `data/raw/ano=AAAA/mes=MM/`. A pasta `data/` não é versionada.

## Roadmap de desenvolvimento

Projeto em desenvolvimento. A arquitetura-alvo está definida, e cada fase é entregue e testada antes da seguinte.

| Fase | Etapa | Status | Entrega |
|------|-------|--------|---------|
| 1 | Ingestão | Concluída | Download de arquivos mensais, retentativas e descompactação |
| 2 | Tratamento e validação | Concluída | Tipagem correta, checagens de qualidade e avisos (ex.: estornos) |
| 3 | Carga | Não iniciada | Dados tratados em Parquet e envio ao S3 |
| 4 | Consulta | Não iniciada | Catálogo e tabelas no Athena |
| 5 | Modelagem | Não iniciada | Modelos dbt (staging, intermediate e marts) para três perguntas analíticas |
| 6 | Infraestrutura | Não iniciada | Provisionamento com Terraform, desenvolvido junto das fases 3 e 4 |
| 7 | Automação | Não iniciada | Agendamento com EventBridge e disparo com Lambda |
| 8 | Documentação | Em andamento | README final, diagrama de arquitetura e guia de reprodução |

### Perguntas analíticas

1. Onde o dinheiro público é gasto, por órgão e município.
2. Como os gastos evoluem ao longo do tempo.
3. Quais contratos foram feitos por dispensa ou inexigibilidade de licitação.

### Decisões registradas

- **Arquivos em lote em vez da API:** a API do Portal exige filtros por unidade gestora e fase, o que torna a ingestão de um período completo complexa. Os arquivos mensais oficiais são mais simples e completos para este projeto.
- **Validação em dois níveis:** problemas bloqueiam a carga, enquanto avisos (como estornos, que são normais na execução orçamentária) são registrados sem bloquear.
- **Processamento:** a decisão entre Lambda e outro serviço para o processamento será tomada com base no tamanho medido dos arquivos.
- **Custo:** os limites de uso gratuito da AWS são verificados na documentação oficial antes de cada fase que usa um serviço pago.

## Estrutura

```
scripts/
├── config.py       # URL do arquivo, codificação, separador e política de retentativas
├── download.py     # download em streaming, retentativas e descompactação
├── tratamento.py   # leitura do CSV com tipos corretos (códigos como texto, valores como número)
└── validacao.py    # problemas (bloqueiam a carga) e avisos (informativos)
tests/
├── test_download.py
└── test_tratamento.py
docs/
└── NOTAS_API.md    # registro das tentativas com a API e por que a abordagem mudou
```

## Decisões técnicas

- **Arquivos em lote em vez de API.** A API de despesas exige filtros por data de emissão, fase e unidade gestora, o que tornaria a ingestão de um mês inteiro uma sequência de milhares de chamadas. Os arquivos mensais cobrem o mesmo conteúdo com um único download.
- **Leitura com tipos explícitos.** O CSV usa codificação `latin-1`, separador `;` e vírgula como decimal. Os códigos são lidos como texto para preservar zeros à esquerda e valores como `-1`. Os valores monetários são convertidos para número.
- **Problemas e avisos.** Problemas, como colunas ausentes ou arquivo vazio, bloqueiam a carga. Avisos, como estornos (valores pagos negativos), são registrados sem bloquear. No arquivo de janeiro de 2024, há 26 registros negativos, somando cerca de R$ 3,7 milhões, frente a R$ 530 bilhões pagos.
- **Download com retentativas.** Erros de conexão e de servidor são repetidos com espera crescente. O arquivo é gravado em streaming para não ocupar memória com o ZIP inteiro.
- **Reprocessamento seguro.** Cada mês fica em sua própria pasta, então rodar a ingestão de novo sobrescreve apenas aquele mês.

## Resultado do primeiro teste

Janeiro de 2024: 47.964 linhas, sem problemas bloqueantes e 1 aviso (estornos).