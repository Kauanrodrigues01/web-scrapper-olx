# src/config.py

# --- Configurações Gerais ---
# URL da OLX que você está usando (conforme seu log)
BASE_URL_OLX = "https://www.olx.com.br/brasil?q=imoveis"

# Número máximo de páginas de resultados a serem percorridas.
# Defina None para tentar percorrer todas ou um número para limitar.
MAX_PAGES_TO_SCRAPE = 1 # Mantenha em 1 para testes iniciais

# Cabeçalhos HTTP para simular um navegador (cloudscraper pode lidar com isso, mas é bom ter)
HTTP_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Language': 'en-US,en;q=0.9,pt-BR;q=0.8,pt;q=0.7',
    'DNT': '1', # Do Not Track
    'Upgrade-Insecure-Requests': '1'
}

# Tempo de espera (em segundos) entre requisições para não sobrecarregar o servidor
REQUEST_DELAY_SECONDS = 5 # Aumente se necessário, especialmente com cloudscraper

# --- Seletores HTML (ATUALIZADOS COM BASE NO SEU INPUT) ---

# Seletores para a página de listagem de anúncios
SELECTORS_LISTING_PAGE = {
    'ad_card': 'section.olx-adcard.olx-adcard__horizontal',
    'ad_link': 'a',
    # 'listing_title': 'h2.olx-adcard__title', # Exemplo de como você nomeou
    # 'listing_price': 'h3.olx-adcard__price',
    # 'listing_location': 'p.olx-adcard__location',
    # 'listing_date': 'p.olx-adcard__date',
    # 'listing_details_summary': 'div.olx-adcard__details',
    # 'listing_detail_item': 'div.olx-adcard__detail',
    # 'listing_image_url': 'div.olx-adcard__media picture img', # Pegue o atributo 'src'
    # 'next_page_link': "a[data-testid='pagination-forward']" # Exemplo, pode ser um botão ou link com texto "Próxima"
}

# Seletores para a página de detalhes de um anúncio individual
SELECTORS_AD_PAGE = {
    'title': 'div#description-title span[data-ds-component="DS-Text"]',
    'price': 'div#price-box-container span.olx-text--title-large',
    'description': 'div[data-section="description"] span[data-ds-component="DS-Text"]',
    'location_neighborhood': 'div#location span.olx-text--body-medium.olx-text--semibold',
    'location_city_state_cep': 'div#location span.olx-text--body-small.olx-color-neutral-110',

    # 'details_section_container': 'div#details div.ad__sc-wuor06-0', # Container da grade de detalhes
    # 'detail_item_container': 'div.ad__sc-2h9gkk-0', # Item individual (label/valor) DENTRO de 'details_section_container'

    # # Dentro de cada 'detail_item_container', use estes para extrair label e valor:
    # 'detail_item_label_relative': 'span.olx-text--overline', # Relativo ao detail_item_container
    # # Lista de seletores possíveis para o valor, relativo ao detail_item_container:
    # 'detail_item_value_relative': ['a.ad__sc-2h9gkk-3', 'span.ad__sc-hj0yqs-0', 'div.ad__sc-1ys3xot-0 > span.olx-text.olx-text--body-medium.olx-text--semibold.olx-color-neutral-120'], # Adicionei uma variação comum

    # 'date_posted': 'div.ad__sc-1oafvmw-0 span.olx-text--caption.olx-color-neutral-100',
    # 'seller_name': 'div.ad__sc-ypp2u2-0 span.olx-text--body-large',
    # 'image_gallery_container': 'div#gallery div.ad__sc-xbkr7e-1',
    # 'image_in_gallery': 'div#gallery div.ad__sc-xbkr7e-1 button.ad__sc-xbkr7e-2 picture img', # para 'src'
    
    
    
    
    'details_section_container': 'html', # Container da grade de detalhes
    'detail_item_container': 'div#description-title span[data-ds-component="DS-Text"]', # Item individual (label/valor) DENTRO de 'details_section_container'

    # Dentro de cada 'detail_item_container', use estes para extrair label e valor:
    'detail_item_label_relative': 'div#description-title span[data-ds-component="DS-Text"]', # Relativo ao detail_item_container
    # Lista de seletores possíveis para o valor, relativo ao detail_item_container:
    'detail_item_value_relative': ['div#description-title span[data-ds-component="DS-Text"]'], # Adicionei uma variação comum

    'date_posted': 'div#description-title span[data-ds-component="DS-Text"]',
    'seller_name': 'div#description-title span[data-ds-component="DS-Text"]',
    'image_gallery_container': 'div#description-title span[data-ds-component="DS-Text"]',
    'image_in_gallery': 'div#description-title span[data-ds-component="DS-Text"]', # para 'src'
}

# --- Configurações de Saída ---
OUTPUT_FILENAME_PREFIX = "olx_imoveis_anuncios"
DATA_FOLDER = "data"