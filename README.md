# 📊 Carteira Analyzer

Um programa profissional e completo para análise de carteiras de investimentos com suporte a múltiplas categorias de ativos.

## ✨ Características

### Processamento de Dados
- **Múltiplas Categorias**: Renda Fixa, COE, Renda Variável e Derivativos
- **Detecção Automática**: Identifica automaticamente colunas importantes nas planilhas
- **Limpeza Robusta**: Remove duplicatas, normaliza dados e converte formatos
- **Validação Inteligente**: Valida integridade dos dados antes do processamento

### Análises Avançadas
- **Diversificação**: Score de diversificação (0-100) com Índice de Herfindahl
- **Concentração**: Identifica maior posição e Top 5 ativos
- **Vencimentos**: Análise por período (30, 60, 90 dias) com alertas
- **Risco**: Classificação em níveis crítico, moderado e baixo
- **Estatísticas**: Valor total, médio, máximo, mínimo e quantidade de ativos

### Relatórios e Visualizações
- **Relatório HTML**: Design profissional e responsivo, pronto para impressão
- **Gráficos**: Pizza, barras, vencimentos, risco e top ativos
- **Relatório Excel**: Múltiplas abas com dados consolidados
- **Resumo Executivo**: Cards com principais métricas

## 🚀 Instalação

### Requisitos
- Python 3.8+
- pandas
- numpy
- matplotlib
- seaborn
- openpyxl

### Setup

```bash
# Clonar ou extrair o projeto
cd carteira_analyzer

# Instalar dependências
pip install -r requirements.txt

# Tornar CLI executável (Linux/Mac)
chmod +x cli.py
```

## 📖 Guia de Uso

### Interface de Linha de Comando (CLI)

#### Processamento Básico

```bash
# Processar arquivo de Renda Fixa
python cli.py -c "João Silva" -rf carteira_rf.xlsx

# Processar múltiplas categorias
python cli.py -c "João Silva" -rf rf.xlsx -coe coe.xlsx -rv rv.xlsx

# Processar com todas as opções
python cli.py -c "João Silva" \
  -rf renda_fixa.xlsx \
  -coe coe.xlsx \
  -rv renda_variavel.xlsx \
  -der derivativos.xlsx
```

#### Opções Avançadas

```bash
# Não gerar relatório HTML
python cli.py -c "João Silva" -rf rf.xlsx --no-html

# Não gerar relatório Excel
python cli.py -c "João Silva" -rf rf.xlsx --no-excel

# Exibir resumo no console
python cli.py -c "João Silva" -rf rf.xlsx --resumo

# Combinar opções
python cli.py -c "João Silva" -rf rf.xlsx --resumo --no-html
```

### Uso Programático

```python
from core import ProcessadorCarteira, CategoriaInvestimento, AnalisadorAvancado

# Criar processador
processador = ProcessadorCarteira()

# Carregar dados
processador.carregar_renda_fixa('rf.xlsx')
processador.carregar_coe('coe.xlsx')
processador.carregar_renda_variavel('rv.xlsx')

# Consolidar carteira
carteira = processador.consolidar_carteira()

# Obter análises
alocacao, total = processador.obter_resumo_alocacao()
alertas = processador.obter_alertas_vencimento()

# Análises avançadas
analisador = AnalisadorAvancado(carteira)
diversificacao = analisador.analisar_diversificacao()
vencimentos = analisador.analisar_vencimentos()
risco = analisador.analisar_risco_vencimento()

# Exportar
processador.exportar_para_excel('relatorio.xlsx')
```

## 📁 Estrutura do Projeto

```
carteira_analyzer/
├── core/
│   ├── __init__.py
│   ├── processador_carteira.py      # Núcleo de processamento
│   ├── analisador_avancado.py       # Análises sofisticadas
│   ├── processador_planilhas.py     # Processamento de arquivos
│   ├── gerador_relatorios.py        # Gráficos e relatórios
│   └── utilitarios.py               # Funções auxiliares
├── cli.py                           # Interface de linha de comando
├── requirements.txt                 # Dependências
└── README.md                        # Este arquivo
```

## 🔧 Módulos Principais

### ProcessadorCarteira
Classe principal para processamento de carteiras.

```python
processador = ProcessadorCarteira()
processador.carregar_renda_fixa(arquivo)
processador.consolidar_carteira()
```

**Métodos principais:**
- `carregar_categoria(arquivo, categoria)`: Carrega arquivo de uma categoria
- `consolidar_carteira()`: Consolida todos os dados
- `obter_resumo_alocacao()`: Retorna alocação por categoria
- `obter_alertas_vencimento()`: Retorna ativos com vencimento próximo
- `exportar_para_excel(caminho)`: Exporta relatório completo

### AnalisadorAvancado
Análises sofisticadas da carteira.

```python
analisador = AnalisadorAvancado(carteira_consolidada)
diversificacao = analisador.analisar_diversificacao()
```

**Métodos principais:**
- `analisar_diversificacao()`: Score e métricas de diversificação
- `analisar_vencimentos()`: Análise por período de vencimento
- `analisar_risco_vencimento()`: Classificação de risco
- `obter_top_ativos(n)`: Top N ativos por valor
- `gerar_relatorio_completo()`: Relatório integrado

### ProcessadorPlanilhas
Processamento robusto de arquivos.

```python
processador = ProcessadorPlanilhas()
sucesso, df, msg = processador.carregar_planilha('arquivo.xlsx')
sucesso, df_proc, msg = processador.processar_planilha(df)
```

**Características:**
- Detecção automática de colunas
- Limpeza e normalização de dados
- Conversão de valores e datas
- Remoção de duplicatas
- Validação de integridade

### GeradorGraficos
Geração de visualizações.

```python
from core.gerador_relatorios import GeradorGraficos

sucesso, caminho = GeradorGraficos.criar_grafico_pizza_alocacao(alocacao)
sucesso, caminho = GeradorGraficos.criar_grafico_vencimentos(analise_vencimentos)
```

**Gráficos disponíveis:**
- Pizza de alocação
- Barras de alocação
- Vencimentos (valor e percentual)
- Risco (valor e percentual)
- Top ativos

## 📊 Formato de Entrada

### Estrutura de Planilhas Esperada

As planilhas devem conter as seguintes colunas (nomes podem variar):

#### Renda Fixa
- **Ativo**: Identificação do ativo (obrigatório)
- **Valor Bruto - Opção Cliente**: Valor do investimento
- **Data Vencimento**: Data de vencimento
- **Sub Mercado**: Classificação/classe do ativo

#### COE
- **Ativo**: Identificação do ativo
- **Valor Bruto - Opção Cliente**: Valor do investimento
- **Data Vencimento**: Data de vencimento
- **Tipo**: Classificação do COE

#### Renda Variável
- **Ativo**: Identificação do ativo
- **Valor Atual**: Valor atual do investimento
- **Tipo**: Classificação (Ação, Fundo, etc.)

#### Derivativos
- **Ativo**: Identificação do ativo
- **Valor**: Valor do derivativo
- **Data Vencimento**: Data de vencimento
- **Tipo**: Tipo de derivativo

**Nota**: O sistema detecta automaticamente as colunas, então nomes ligeiramente diferentes são aceitos.

## 📈 Métricas e Indicadores

### Diversificação
- **Score (0-100)**: Combinação de número de ativos e HHI
- **HHI (Índice de Herfindahl)**: Mede concentração (0-10000)
  - < 1500: Baixa concentração
  - 1500-2500: Concentração moderada
  - > 2500: Alta concentração
- **Maior Posição**: Percentual do maior ativo
- **Top 5**: Percentual dos 5 maiores ativos

### Vencimentos
- **Próximos 30 dias**: Valor e percentual
- **Próximos 60 dias**: Valor e percentual
- **Próximos 90 dias**: Valor e percentual
- **Vencidos**: Valor e percentual
- **Sem Vencimento**: Valor e percentual

### Risco
- **Crítico**: Vencidos + próximos 30 dias
- **Moderado**: 31-90 dias
- **Baixo**: > 90 dias ou sem vencimento
- **Nível Geral**: Classificação baseada em percentual crítico

## 🎨 Saídas Geradas

### Relatório HTML
- Resumo executivo com cards de estatísticas
- Tabelas formatadas e responsivas
- Gráficos integrados
- Design profissional
- Pronto para impressão (PDF)

### Relatório Excel
- **Aba 1**: Resumo de Alocação
- **Aba 2**: Resumo por Classe
- **Aba 3**: Carteira Detalhada
- **Aba 4**: Alertas de Vencimento
- **Aba 5**: Ativos Vencidos
- **Aba 6**: Estatísticas

### Gráficos (PNG)
- Pizza de alocação
- Barras de alocação
- Vencimentos (duplo)
- Risco (duplo)
- Top 10 ativos

## 🔍 Validações Realizadas

O sistema realiza validações em múltiplos níveis:

1. **Validação de Arquivo**: Extensão, tamanho, existência
2. **Validação de Dados**: Estrutura, colunas obrigatórias
3. **Validação de Valores**: Conversão numérica, datas
4. **Validação de Integridade**: Duplicatas, valores ausentes
5. **Validação de Saída**: Dados processados corretamente

## 📝 Exemplos Práticos

### Exemplo 1: Análise Completa

```bash
python cli.py -c "Empresa XYZ" \
  -rf carteira_rf.xlsx \
  -coe carteira_coe.xlsx \
  -rv carteira_rv.xlsx \
  --resumo
```

### Exemplo 2: Apenas Renda Fixa

```bash
python cli.py -c "Cliente ABC" -rf renda_fixa.xlsx
```

### Exemplo 3: Múltiplos Clientes (Script)

```bash
#!/bin/bash
for cliente in "Cliente1" "Cliente2" "Cliente3"; do
  python cli.py -c "$cliente" -rf "dados/${cliente}_rf.xlsx"
done
```

## 🐛 Troubleshooting

### Erro: "Coluna não encontrada"
- Verifique se o nome da coluna está correto
- O sistema tenta detectar automaticamente, mas pode precisar de ajustes
- Use `--resumo` para ver os dados carregados

### Erro: "Arquivo vazio"
- Verifique se o arquivo Excel contém dados
- Remova linhas/colunas vazias
- Certifique-se de que há pelo menos uma coluna "Ativo"

### Erro: "Valores inválidos"
- Verifique o formato dos valores (moeda, separadores)
- Remova símbolos especiais desnecessários
- Certifique-se de que as datas estão em formato válido

## 📞 Suporte

Para dúvidas ou problemas:
1. Verifique a documentação acima
2. Consulte os exemplos de uso
3. Verifique os logs de erro (arquivo de log)

## 📄 Licença

Este projeto é fornecido como está para uso interno.

## ✅ Checklist de Funcionalidades

- [x] Processamento de múltiplas categorias
- [x] Detecção automática de colunas
- [x] Validação robusta de dados
- [x] Análise de diversificação
- [x] Análise de vencimentos
- [x] Análise de risco
- [x] Geração de gráficos
- [x] Relatório HTML profissional
- [x] Relatório Excel completo
- [x] Interface CLI intuitiva
- [x] Documentação completa
- [x] Tratamento de erros
- [x] Logging detalhado

## 🚀 Roadmap Futuro

- [ ] Interface Web (Flask/FastAPI)
- [ ] Banco de dados para histórico
- [ ] Análise de rentabilidade
- [ ] Comparação com benchmarks
- [ ] Alertas automáticos por email
- [ ] Dashboard interativo
- [ ] Suporte a múltiplos idiomas
- [ ] Exportação para PDF
- [ ] API REST

---

**Desenvolvido com ❤️ para análise profissional de carteiras**
