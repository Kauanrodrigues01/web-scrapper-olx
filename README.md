# Web Scraper OLX Imóveis

Este projeto contém um web scraper desenvolvido em Python para coletar dados de anúncios de imóveis da OLX em uma região específica. Os dados coletados são salvos em arquivos `.csv` e `.xlsx`.

## Aviso Importante

A estrutura dos sites da web, incluindo a OLX, muda frequentemente. Os seletores HTML (classes, IDs, tags) usados neste scraper são baseados em uma análise em um determinado momento e **provavelmente precisarão ser atualizados** para que o scraper funcione corretamente. Você precisará inspecionar o código HTML da OLX na sua região e para os tipos de anúncio desejados para encontrar os seletores corretos.

Este scraper também pode não funcionar se a OLX carregar conteúdo dinamicamente via JavaScript de forma extensiva. Nesses casos, ferramentas como Selenium podem ser necessárias.

## Configuração

1.  **Crie e Ative um Ambiente Virtual:**
    ```bash
    python -m venv venv_olx_scraper
    # Windows
    .\venv_olx_scraper\Scripts\activate
    # macOS/Linux
    source venv_olx_scraper/bin/activate
    ```

2.  **Instale as Dependências:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure a Região e os Seletores:**
    * Abra o arquivo `src/config.py`.
    * Atualize a `BASE_URL_OLX` para a URL da OLX da sua região e categoria de imóveis (ex: imóveis à venda em São Paulo - SP).
    * **CRÍTICO:** Atualize os dicionários `SELECTORS_LISTING_PAGE` e `SELECTORS_AD_PAGE` com os seletores CSS corretos que você encontrar inspecionando o site da OLX.

4.  **Crie a Pasta de Dados:**
    * Crie uma pasta chamada `data` na raiz do projeto. Os arquivos `.csv` e `.xlsx` serão salvos aqui.

## Como Usar

1.  Certifique-se de que o ambiente virtual está ativado e as configurações em `src/config.py` estão corretas.
2.  Execute o script principal:
    ```bash
    python main.py
    ```
3.  Os dados serão salvos na pasta `data/` e um log será gerado em `scraper.log`.

## Estrutura do Projeto

* `main.py`: Script principal para executar o scraper.
* `requirements.txt`: Lista de bibliotecas Python necessárias.
* `scraper.log`: Arquivo de log gerado pela execução.
* `README.md`: Este arquivo.
* `src/`: Contém o código fonte do scraper.
    * `config.py`: Configurações como URL base, seletores e outros parâmetros.
    * `scraper.py`: Lógica principal do web scraping.
    * `data_exporter.py`: Funções para salvar os dados em CSV e Excel.
    * `utils.py`: Funções utilitárias (ex: limpeza de dados).
* `data/`: Pasta onde os dados coletados são armazenados (deve ser criada manualmente).

## Boas Práticas e Ética

* **Respeite o `robots.txt` da OLX.**
* **Não sobrecarregue os servidores:** O script inclui pausas (`time.sleep()`). Ajuste se necessário, mas não as remova.
* **User-Agent:** O script utiliza um User-Agent genérico.
* **Termos de Serviço:** Esteja ciente dos Termos de Serviço da OLX em relação à coleta automatizada de dados. Use por sua conta e risco.
* **LGPD:** Tenha cuidado ao coletar e armazenar dados que possam ser considerados pessoais.