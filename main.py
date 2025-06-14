import logging
from src.scraper import run_scraper
from src.data_exporter import save_data
from src.config import BASE_URL_OLX

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("scraper.log", mode='a'),
        logging.StreamHandler()
    ]
)

def main():
    logging.info("--- INICIANDO PROCESSO DE WEB SCRAPING DA OLX ---")
    logging.info(f"URL Base configurada: {BASE_URL_OLX}")
    logging.info("Certifique-se de que os seletores em 'src/config.py' estão ATUALIZADOS para a sua região e para o layout atual da OLX.")

    try:
        collected_ads = run_scraper()

        if collected_ads:
            logging.info(f"Total de {len(collected_ads)} anúncios coletados.")
            csv_file, xlsx_file = save_data(collected_ads)
            if csv_file and xlsx_file:
                logging.info(f"Dados exportados com sucesso para '{csv_file}' e '{xlsx_file}'.")
            else:
                logging.error("Falha ao exportar os dados.")
        else:
            logging.warning("Nenhum anúncio foi coletado. Verifique os logs e as configurações.")

    except Exception as e:
        logging.critical(f"Ocorreu um erro crítico no processo principal: {e}", exc_info=True)
    finally:
        logging.info("--- PROCESSO DE WEB SCRAPING FINALIZADO ---")

if __name__ == "__main__":
    main()