# Web Scraper OLX Imóveis: Ferramenta de Análise de Mercado Imobiliário!

Este projeto contém um web scraper desenvolvido em Python para coletar dados de anúncios de imóveis da OLX em uma região específica. Os dados coletados são salvos em arquivos `.csv` e `.xlsx`.

## Principais Funcionalidades

- Coleta de Dados: O scraper recolhe dados de anúncios de imóveis na plataforma OLX.
- Exportação de Dados: Os dados coletados são guardados em formatos .csv e .xlsx.
- Configuração Regional: Permite configurar uma URL base da OLX para uma região e categoria de imóveis específica, como "imóveis à venda em São Paulo - SP"

## Tecnologias Utilizadas

O projeto é desenvolvido em Python e utiliza as seguintes bibliotecas:
- cloudscraper
- requests
- beautifulsoup4
- pandas
- openpyxl
- lxml
- 
## Configuração

1.  **Crie e Ative um Ambiente Virtual:**
    ```bash
    python -m venv venv
    # Windows
    .\venv\Scripts\activate
    # macOS/Linux
    source venv/bin/activate
    ```

2.  **Instale as Dependências:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure a Região:**
    * Abra o arquivo `src/config.py`.
    * Atualize a `BASE_URL_OLX` para a URL da OLX da sua região e categoria de imóveis (ex: imóveis à venda em São Paulo - SP).

4.  **Crie a Pasta de Dados:**
    * Crie uma pasta chamada `data` na raiz do projeto. Os arquivos `.csv` e `.xlsx` serão salvos aqui.

## Como Usar

1.  Certifique-se de que o ambiente virtual está ativado e as configurações em `src/config.py` estão corretas.
2.  Execute o script principal:
    ```bash
    python main.py
    ```
3.  Os dados serão salvos na pasta `data/` e um log será gerado em `scraper.log`.
