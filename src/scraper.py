import requests
import cloudscraper
from bs4 import BeautifulSoup
import time
import logging
from urllib.parse import urljoin, urlparse, parse_qs, urlencode

from .config import (
    BASE_URL_OLX,
    HTTP_HEADERS,
    REQUEST_DELAY_SECONDS,
    SELECTORS_LISTING_PAGE,
    SELECTORS_AD_PAGE,
    MAX_PAGES_TO_SCRAPE
)
from .utils import clean_text, extract_price, extract_number # get_detail_value_by_label não será mais usado diretamente assim

# Configuração básica do logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(module)s - %(message)s',
    handlers=[
        logging.FileHandler("scraper.log", mode='w'), # mode='w' para sobrescrever o log a cada execução
        logging.StreamHandler()
    ]
)

# Cria uma instância do scraper do cloudscraper
scraper_instance = cloudscraper.create_scraper(
    browser={ # Simula um navegador mais de perto
        'browser': 'chrome',
        'platform': 'windows',
        'mobile': False
    },
    delay=REQUEST_DELAY_SECONDS # Adiciona um delay entre os desafios JS do cloudflare
)

def fetch_page_content(url):
    """Busca o conteúdo HTML de uma URL usando cloudscraper."""
    try:
        # Usa a instância do cloudscraper para fazer a requisição GET
        response = scraper_instance.get(url, headers=HTTP_HEADERS, timeout=30) # Timeout aumentado
        logging.info(f"Página buscada: {url} (Status: {response.status_code})")
        # Cloudscraper já lida com muitos erros 403 do Cloudflare, mas vamos verificar o status.
        # Se o conteúdo ainda for uma página de bloqueio do Cloudflare, o parsing falhará em encontrar os dados.
        if "cloudflare" in response.text.lower() and "Sorry, you have been blocked" in response.text:
            logging.error(f"Cloudflare ainda está bloqueando o acesso a {url} mesmo com cloudscraper. HTML: {response.text[:500]}")
            return None
        if "Attention Required! | Cloudflare" in response.text:
            logging.error(f"Página de CAPTCHA/desafio do Cloudflare recebida em {url}. HTML: {response.text[:500]}")
            return None

        response.raise_for_status() # Levanta um erro para status ruins (4xx ou 5xx) não pegos acima
        # A pausa principal agora está no construtor do scraper_instance ou será adicionada manualmente entre chamadas se necessário
        # time.sleep(REQUEST_DELAY_SECONDS) # Movido para o construtor do scraper ou usado entre chamadas de alto nível
        return BeautifulSoup(response.content, 'lxml')
    except cloudscraper.exceptions.CloudflareChallengeError as cf_err:
        logging.error(f"Desafio do Cloudflare não resolvido para {url}: {cf_err}. HTML: {cf_err.response.text[:500] if cf_err.response else 'N/A'}")
    except requests.exceptions.HTTPError as http_err: # cloudscraper usa exceções do requests
        logging.error(f"Erro HTTP ao buscar {url}: {http_err}. HTML: {http_err.response.text[:500] if http_err.response else 'N/A'}")
    except requests.exceptions.ConnectionError as conn_err:
        logging.error(f"Erro de conexão ao buscar {url}: {conn_err}")
    except requests.exceptions.Timeout as timeout_err:
        logging.error(f"Timeout ao buscar {url}: {timeout_err}")
    except requests.exceptions.RequestException as req_err:
        logging.error(f"Erro geral de requisição ao buscar {url}: {req_err}")
    time.sleep(REQUEST_DELAY_SECONDS * 2) # Pausa maior em caso de erro persistente
    return None

def extract_ad_links_from_listing_page(soup):
    """Extrai os links dos anúncios de uma página de listagem."""
    ad_links = []
    if not soup:
        return ad_links

    # ATENÇÃO: VERIFIQUE O SELETOR 'ad_card' EM config.py!
    ad_cards = soup.select(SELECTORS_LISTING_PAGE["ad_card"])
    if not ad_cards:
        logging.warning(f"Nenhum card de anúncio encontrado com o seletor '{SELECTORS_LISTING_PAGE['ad_card']}'. Verifique o seletor e a página HTML.")
        # Logar um trecho do HTML pode ajudar a depurar:
        # logging.debug(f"HTML da página de listagem (início): {soup.prettify()[:2000]}")
        return ad_links

    for card_index, card in enumerate(ad_cards):
        # ATENÇÃO: VERIFIQUE O SELETOR 'ad_link' EM config.py!
        link_tag = card.select_one(SELECTORS_LISTING_PAGE["ad_link"])
        if link_tag and link_tag.has_attr('href'):
            ad_url = urljoin(BASE_URL_OLX, link_tag['href'])
            ad_links.append(ad_url)
        else:
            logging.warning(f"Link do anúncio não encontrado no card #{card_index + 1} usando o seletor '{SELECTORS_LISTING_PAGE['ad_link']}'. Card HTML (início): {str(card)[:300]}...")
    logging.info(f"{len(ad_links)} links de anúncios extraídos desta página.")
    return ad_links

def extract_ad_details(ad_url, soup):
    """Extrai os detalhes de uma página de anúncio individual usando os seletores fornecidos."""
    details = {"url_anuncio": ad_url}
    if not soup:
        logging.warning(f"Não foi possível parsear a página do anúncio (soup vazio): {ad_url}")
        return details

    # Título
    title_tag = soup.select_one(SELECTORS_AD_PAGE["title"])
    details["titulo"] = clean_text(title_tag.get_text()) if title_tag else None

    # Preço
    price_tag = soup.select_one(SELECTORS_AD_PAGE["price"])
    price_text = clean_text(price_tag.get_text()) if price_tag else None
    details["preco_str"] = price_text # Salva o texto original do preço
    details["preco"] = extract_price(price_text)

    # Descrição
    description_tag = soup.select_one(SELECTORS_AD_PAGE["description"])
    details["descricao"] = clean_text(description_tag.get_text(separator=' ', strip=True)) if description_tag else None

    # Localização (Bairro e Cidade/Estado/CEP separados)
    loc_neighborhood_tag = soup.select_one(SELECTORS_AD_PAGE["location_neighborhood"])
    details["local_bairro"] = clean_text(loc_neighborhood_tag.get_text()) if loc_neighborhood_tag else None

    loc_city_state_cep_tag = soup.select_one(SELECTORS_AD_PAGE["location_city_state_cep"])
    details["local_cidade_estado_cep"] = clean_text(loc_city_state_cep_tag.get_text()) if loc_city_state_cep_tag else None

    # Data de Publicação
    date_posted_tag = soup.select_one(SELECTORS_AD_PAGE["date_posted"])
    details["data_publicacao"] = clean_text(date_posted_tag.get_text()) if date_posted_tag else None
    
    # Nome do Vendedor
    seller_name_tag = soup.select_one(SELECTORS_AD_PAGE["seller_name"])
    details["nome_vendedor"] = clean_text(seller_name_tag.get_text()) if seller_name_tag else None

    # Extração de Detalhes da Seção 'details_section_container'
    details_extracted_from_section = {}
    details_section_el = soup.select_one(SELECTORS_AD_PAGE["details_section_container"])
    if details_section_el:
        item_containers = details_section_el.select(SELECTORS_AD_PAGE["detail_item_container"])
        if not item_containers:
            logging.warning(f"Nenhum 'detail_item_container' encontrado dentro de 'details_section_container' para {ad_url} usando seletor '{SELECTORS_AD_PAGE['detail_item_container']}'")

        for item_container in item_containers:
            label_tag = item_container.select_one(SELECTORS_AD_PAGE["detail_item_label_relative"])
            label_text = clean_text(label_tag.get_text().lower()) if label_tag else None # Label em minúsculas para chave

            if label_text:
                value_text = None
                # Tenta cada seletor para o valor
                for value_selector in SELECTORS_AD_PAGE["detail_item_value_relative"]:
                    value_tag = item_container.select_one(value_selector)
                    if value_tag:
                        value_text = clean_text(value_tag.get_text())
                        break # Para no primeiro seletor de valor que funcionar
                
                if value_text:
                    # Tenta converter para número se for um campo numérico conhecido
                    if any(kw in label_text for kw in ["quarto", "banheiro", "vaga", "andar"]):
                        details_extracted_from_section[label_text] = extract_number(value_text)
                    elif "área" in label_text or "tamanho" in label_text:
                        details_extracted_from_section[label_text] = extract_number(value_text) # Poderia ser float também
                    else:
                        details_extracted_from_section[label_text] = value_text
                else:
                    logging.warning(f"Valor não encontrado para a label '{label_text}' no anúncio {ad_url} usando seletores '{SELECTORS_AD_PAGE['detail_item_value_relative']}'")
            else:
                logging.warning(f"Label não encontrada em 'detail_item_container' no anúncio {ad_url} usando seletor '{SELECTORS_AD_PAGE['detail_item_label_relative']}'")
        details.update(details_extracted_from_section) # Adiciona os detalhes extraídos ao dict principal
    else:
        logging.warning(f"Seção de detalhes ('{SELECTORS_AD_PAGE['details_section_container']}') não encontrada para o anúncio: {ad_url}")

    # Imagens (exemplo: coletar a primeira URL de imagem da galeria)
    # Pode-se expandir para coletar todas se necessário
    first_image_tag = soup.select_one(SELECTORS_AD_PAGE["image_in_gallery"])
    if first_image_tag:
        details["imagem_principal_url"] = first_image_tag.get('src') or first_image_tag.get('data-src')
    else:
        details["imagem_principal_url"] = None
        logging.warning(f"Nenhuma imagem encontrada com seletor '{SELECTORS_AD_PAGE['image_in_gallery']}' para {ad_url}")


    logging.info(f"Detalhes extraídos para: {details.get('titulo', ad_url)[:50]}...") # Log do título truncado
    return details

def get_next_page_url(current_url, soup):
    """
    Tenta encontrar o link da próxima página.
    Primeiro tenta usar um seletor CSS de 'next_page_link' do config.py.
    Se falhar ou não estiver definido, tenta a lógica de fallback incrementando o parâmetro 'o' na URL.
    """
    if not soup:
        logging.warning(f"Soup está vazio para {current_url}, não é possível determinar a próxima página.")
        return None

    next_page_selector_str = SELECTORS_LISTING_PAGE.get("next_page_link")
    
    # 1. Tentar encontrar a próxima página usando o seletor CSS
    if next_page_selector_str:  # Apenas tenta se o seletor for uma string não vazia
        logging.info(f"Tentando encontrar próxima página para {current_url} usando seletor: '{next_page_selector_str}'")
        next_page_tag = soup.select_one(next_page_selector_str)
        if next_page_tag and next_page_tag.has_attr('href'):
            potential_next_url = urljoin(current_url, next_page_tag['href'])
            
            # Verifica se a URL encontrada é realmente uma "próxima" página válida
            if potential_next_url != current_url and not potential_next_url.endswith("?o=0") and not (current_url.endswith("?o=1") and potential_next_url.endswith("?o=1")): # Evita loops e voltar para o início
                # Lógica adicional para evitar voltar para a página 1 se a paginação já começou
                current_o_param = parse_qs(urlparse(current_url).query).get('o', [None])[0]
                next_o_param = parse_qs(urlparse(potential_next_url).query).get('o', [None])[0]

                if current_o_param and next_o_param and next_o_param == "1" and current_o_param != "1":
                    logging.info(f"Seletor de próxima página ('{next_page_selector_str}') encontrado, mas aponta para '?o=1' ('{potential_next_url}') vindo de uma página posterior. Ignorando.")
                else:
                    logging.info(f"URL da próxima página (via seletor '{next_page_selector_str}'): {potential_next_url}")
                    return potential_next_url
        else:
            logging.info(f"Seletor '{next_page_selector_str}' para próxima página não encontrou uma tag <a> com href válido.")
    else:
        logging.info(f"Nenhum seletor 'next_page_link' definido em config.py ou o valor é None.")

    # 2. Se o método do seletor falhou ou não foi definido, tentar lógica de fallback com parâmetro 'o'
    logging.info(f"Tentando fallback para próxima página via parâmetro 'o' para: {current_url}")
    parsed_url = urlparse(current_url)
    query_params = parse_qs(parsed_url.query)
    
    current_page_num_o = 0 # Assumir 0 se 'o' não estiver presente, para que a próxima seja 1 (ou 2 se OLX usa o=2 para pag2)
                           # OLX parece usar o=2 para a segunda página se a primeira não tem 'o'.
                           # Se a primeira URL já é ?o=1, a próxima será ?o=2.
    
    is_first_page_without_o = 'o' not in query_params

    if 'o' in query_params:
        try:
            current_page_num_o = int(query_params['o'][0])
        except (ValueError, IndexError):
            logging.warning(f"Não foi possível parsear o parâmetro 'o' da página atual: {query_params.get('o')}. Assumindo 'o'=0.")
            current_page_num_o = 0 # Ou 1, dependendo de como a OLX numera a primeira página com 'o'

    # Se a primeira página (sem parâmetro 'o') deve ir para o=2 (comum na OLX)
    if is_first_page_without_o:
        next_page_num_o = 2
    else:
        next_page_num_o = current_page_num_o + 1
    
    query_params['o'] = [str(next_page_num_o)]
    
    new_query_string = urlencode(query_params, doseq=True)
    next_page_url_by_param = parsed_url._replace(query=new_query_string).geturl()
    
    if next_page_url_by_param != current_url:
        logging.info(f"URL da próxima página (via parâmetro 'o'): {next_page_url_by_param}")
        return next_page_url_by_param
    else:
        logging.warning(f"URL da próxima página via parâmetro 'o' ('{next_page_url_by_param}') é a mesma que a atual ('{current_url}'). Isso pode indicar o fim das páginas.")

    logging.warning(f"Não foi possível determinar a próxima página para {current_url} por nenhum método.")
    return None


def run_scraper():
    """Orquestra o processo de scraping."""
    all_ads_data = []
    current_page_url = BASE_URL_OLX
    page_count = 0

    while current_page_url and (MAX_PAGES_TO_SCRAPE is None or page_count < MAX_PAGES_TO_SCRAPE):
        page_count += 1
        logging.info(f"--- Raspando Página {page_count} / {MAX_PAGES_TO_SCRAPE if MAX_PAGES_TO_SCRAPE else 'N/A'}: {current_page_url} ---")

        listing_soup = fetch_page_content(current_page_url)

        if not listing_soup:
            logging.error(f"Falha ao obter conteúdo da página de listagem: {current_page_url}. Tentando próxima página se houver.")
            # Mesmo com falha, tenta obter a próxima página para não parar tudo se for um erro temporário
            # Mas se MAX_PAGES_TO_SCRAPE for 1, isso vai parar.
            if page_count >= (MAX_PAGES_TO_SCRAPE or float('inf')): #  Se atingiu o limite, para
                 break
            next_page_candidate_after_fail = get_next_page_url(current_page_url, listing_soup) # listing_soup será None aqui
            if next_page_candidate_after_fail == current_page_url: break
            current_page_url = next_page_candidate_after_fail
            time.sleep(REQUEST_DELAY_SECONDS * 2) # Pausa extra após falha
            continue


        ad_links_on_page = extract_ad_links_from_listing_page(listing_soup)
        if not ad_links_on_page:
            logging.info(f"Nenhum link de anúncio encontrado na página {current_page_url}. Verifique os seletores ou pode ser o fim das listagens.")
            break 

        for ad_link_index, ad_link in enumerate(ad_links_on_page):
            logging.info(f"Processando anúncio {ad_link_index + 1}/{len(ad_links_on_page)}: {ad_link}")
            ad_soup = fetch_page_content(ad_link)
            if ad_soup:
                ad_data = extract_ad_details(ad_link, ad_soup)
                all_ads_data.append(ad_data)
            else:
                logging.warning(f"Não foi possível obter/processar detalhes do anúncio: {ad_link}")
            time.sleep(REQUEST_DELAY_SECONDS / 2) # Pequena pausa entre anúncios individuais

        next_page_candidate = get_next_page_url(current_page_url, listing_soup)
        if next_page_candidate == current_page_url:
            logging.info("URL da próxima página é a mesma da atual. Encerrando paginação.")
            break
        current_page_url = next_page_candidate
        
        if not current_page_url:
            logging.info("Nenhuma URL de próxima página encontrada. Encerrando.")
            break
        time.sleep(REQUEST_DELAY_SECONDS) # Pausa entre páginas de listagem

    if not all_ads_data:
        logging.warning("Nenhum dado de anúncio foi coletado.")
    else:
        logging.info(f"Coleta finalizada. Total de {len(all_ads_data)} anúncios processados.")

    return all_ads_data

if __name__ == '__main__':
    logging.info("Iniciando teste direto do scraper.py...")
    collected_data = run_scraper()
    # ... (resto do bloco if __name__ == '__main__' como antes)