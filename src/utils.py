import re
import logging

def clean_text(text):
    """Remove espaços extras e quebras de linha de um texto."""
    if text:
        return " ".join(text.split()).strip()
    return None

def extract_price(price_text):
    """Extrai um valor numérico de um texto de preço (ex: 'R$ 150.000')."""
    if not price_text:
        return None
    # Remove 'R$', pontos de milhar e substitui vírgula decimal por ponto.
    match = re.search(r'[\d\.,]+', price_text)
    if match:
        try:
            # Remove pontos de milhar, substitui vírgula decimal por ponto
            cleaned_price = match.group(0).replace('.', '').replace(',', '.')
            return float(cleaned_price)
        except ValueError:
            logging.warning(f"Não foi possível converter o preço: {price_text}")
            return None
    return None

def extract_number(text_with_number):
    """Extrai o primeiro número encontrado em um texto (ex: '2 quartos')."""
    if not text_with_number:
        return None
    match = re.search(r'\d+', text_with_number)
    if match:
        return int(match.group(0))
    return None

def get_detail_value_by_label(details_elements, label_keyword):
    """
    Tenta encontrar um elemento de detalhe que contenha a 'label_keyword' (ex: 'Quartos')
    e retorna o texto do seu valor.
    Assume que os 'details_elements' são tags BeautifulSoup.
    Esta função é um exemplo e pode precisar de muita adaptação.
    """
    if not details_elements:
        return None
    for el in details_elements:
        # Tenta encontrar o texto da label e o texto do valor
        # A estrutura exata dependerá do HTML da OLX
        # Exemplo: <span><strong>Quartos</strong> 2</span>
        # Ou: <div><span>Quartos</span><span>2</span></div>
        text_content = clean_text(el.get_text(separator=' ', strip=True))
        if label_keyword.lower() in text_content.lower():
            # Tentar extrair o número ou o texto após a label
            # Isto é muito dependente da estrutura e precisará de ajuste
            parts = text_content.split(label_keyword, 1) # Divide pelo keyword ignorando case
            if len(parts) > 1:
                value_part = parts[1].strip()
                # Tentar extrair número se for relevante
                num_match = re.search(r'\d+', value_part)
                if num_match:
                    return int(num_match.group(0))
                return clean_text(value_part) # Retorna o texto se não for um número claro
            # Se a label e o valor estiverem no mesmo texto mas sem separador claro:
            num_match_direct = re.search(r'\d+', text_content) # Ex: "2 Quartos"
            if num_match_direct:
                 return int(num_match_direct.group(0))
    return None


if __name__ == '__main__':
    # Testes simples
    print(f"Preço: {extract_price('R$ 1.250,50')}")
    print(f"Preço: {extract_price('Sob Consulta')}")
    print(f"Número: {extract_number('Área útil 120 m²')}")
    print(f"Texto limpo: {clean_text('  Olá   mundo  \n  teste ')}")