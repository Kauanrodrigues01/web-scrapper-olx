import pandas as pd
import os
import logging
from datetime import datetime
from .config import OUTPUT_FILENAME_PREFIX, DATA_FOLDER

def save_data(data_list):
    """
    Salva a lista de dicionários de dados em arquivos CSV e XLSX.
    Retorna os nomes dos arquivos salvos ou None em caso de erro.
    """
    if not data_list:
        logging.warning("Nenhum dado para salvar.")
        return None, None

    try:
        df = pd.DataFrame(data_list)

        # Garante que a pasta de dados existe
        if not os.path.exists(DATA_FOLDER):
            os.makedirs(DATA_FOLDER)
            logging.info(f"Pasta '{DATA_FOLDER}' criada.")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = f"{OUTPUT_FILENAME_PREFIX}_{timestamp}"

        csv_filename = os.path.join(DATA_FOLDER, f"{base_filename}.csv")
        xlsx_filename = os.path.join(DATA_FOLDER, f"{base_filename}.xlsx")

        # Salvar em CSV
        df.to_csv(csv_filename, index=False, encoding='utf-8-sig')
        logging.info(f"Dados salvos em: {csv_filename}")

        # Salvar em XLSX
        df.to_excel(xlsx_filename, index=False, engine='openpyxl')
        logging.info(f"Dados salvos em: {xlsx_filename}")

        return csv_filename, xlsx_filename

    except Exception as e:
        logging.error(f"Erro ao salvar os dados: {e}", exc_info=True)
        return None, None

if __name__ == '__main__':
    # Exemplo de uso (para teste)
    logging.basicConfig(level=logging.INFO)
    test_data = [
        {'titulo': 'Casa 1', 'preco': 100000, 'quartos': 3},
        {'titulo': 'Apto 2', 'preco': 200000, 'quartos': 2, 'area': 70},
    ]
    save_data(test_data)