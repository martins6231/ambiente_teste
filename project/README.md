# Dashboard de Análise de Eficiência de Máquinas

Este aplicativo web fornece uma análise detalhada da eficiência de máquinas com base em dados de paradas. O dashboard permite identificar tendências, áreas problemáticas e oportunidades de melhoria na operação industrial.

## Funcionalidades

- Upload de arquivos Excel contendo dados de paradas de máquinas
- Análise de métricas-chave (disponibilidade, eficiência operacional, tempo médio de paradas)
- Visualizações interativas (gráficos de Pareto, pizza, barras e linhas)
- Filtros por máquina, período e mês/ano
- Análise temporal com tendências e sazonalidades
- Conclusões e recomendações automáticas baseadas nos dados
- Exportação dos dados filtrados em formato Excel

## Estrutura de Dados Esperada

O aplicativo espera que o arquivo Excel tenha as seguintes colunas:

- **Máquina**: identificador da máquina
- **Parada**: descrição do tipo de parada
- **Área Responsável**: área responsável pela parada
- **Inicio**: data/hora de início da parada
- **Fim**: data/hora de fim da parada
- **Duração**: tempo de duração da parada (formato HH:MM:SS)

## Como Executar o Aplicativo

1. Instale as dependências:
   ```
   pip install -r requirements.txt
   ```

2. Execute o aplicativo:
   ```
   streamlit run app.py
   ```

3. Acesse o aplicativo em seu navegador (geralmente em http://localhost:8501)

4. Faça o upload do arquivo Excel com os dados de paradas

## Visualizações Disponíveis

- **Pareto de Causas de Paradas**: identifica as principais causas de paradas por duração
- **Índice de Paradas por Área Responsável**: distribuição de paradas por área
- **Taxa de Ocorrência de Paradas por Mês**: tendência de quantidade de paradas ao longo do tempo
- **Tempo Total de Paradas por Área**: ranking de áreas por tempo total de parada
- **Distribuição de Paradas por Dia da Semana**: análise de padrões semanais
- **Acumulação de Horas de Parada por Hora do Dia**: identificação de horários críticos

## Suporte

Para qualquer dúvida ou sugestão, entre em contato com o desenvolvedor.