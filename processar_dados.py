#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Processa todos os CSVs na pasta dados/ usando Selenium, com pausa manual para Cloudflare, busca EAN/GTIN de cada produto, espera 3s entre cada, 10s a cada 5, atualiza BARCODE.
"""

import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import time
import re
import logging
from urllib.parse import quote
import sys
from selenium.common.exceptions import WebDriverException
import shutil
import platform

# Adicionar imports do webdriver-manager
try:
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver.chrome.service import Service as ChromeService
except ImportError:
    ChromeDriverManager = None
    ChromeService = None
try:
    from webdriver_manager.firefox import GeckoDriverManager
    from selenium.webdriver.firefox.service import Service as FirefoxService
except ImportError:
    GeckoDriverManager = None
    FirefoxService = None
try:
    from webdriver_manager.core.utils import ChromeType
except ImportError:
    ChromeType = None


def encontrar_navegador_possiveis(nomes):
    """
    Tenta encontrar o caminho do executável do navegador a partir de uma lista de nomes possíveis.
    """
    for nome in nomes:
        caminho = shutil.which(nome)
        if caminho:
            return caminho
    # Windows: tentar caminhos padrão
    if platform.system() == "Windows":
        possiveis = [
            r"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
            r"C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
            r"C:\\Program Files\\Mozilla Firefox\\firefox.exe",
            r"C:\\Program Files (x86)\\Mozilla Firefox\\firefox.exe",
            r"C:\\Program Files\\Chromium\\Application\\chromium.exe",
            r"C:\\Program Files (x86)\\Chromium\\Application\\chromium.exe",
        ]
        for caminho in possiveis:
            if os.path.exists(caminho):
                return caminho
    return None

def iniciar_driver():
    """
    Tenta iniciar o Chrome, depois Chromium, depois Firefox. Usa webdriver-manager para baixar o driver correto.
    Detecta automaticamente o caminho do navegador no Linux e Windows.
    """
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    # Chrome padrão
    chrome_path = encontrar_navegador_possiveis([
        "google-chrome", "chrome", "chrome.exe"
    ])
    if chrome_path:
        chrome_options.binary_location = chrome_path
    try:
        if ChromeDriverManager is not None and ChromeService is not None:
            driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            print(f"\n[INFO] Navegador Chrome detectado e iniciado em: {chrome_path or 'padrão do sistema'}\n")
            return driver
    except Exception as e:
        print(f"[WARN] Chrome não pôde ser iniciado: {e}")
    # Chromium
    chromium_path = encontrar_navegador_possiveis([
        "chromium", "chromium-browser", "chromium.exe"
    ])
    if chromium_path:
        chrome_options.binary_location = chromium_path
    try:
        if ChromeDriverManager is not None and ChromeService is not None and ChromeType is not None:
            driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install()), options=chrome_options)
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            print(f"\n[INFO] Navegador Chromium detectado e iniciado em: {chromium_path or 'padrão do sistema'}\n")
            return driver
    except Exception as e:
        print(f"[WARN] Chromium não pôde ser iniciado: {e}")
    # Firefox
    firefox_path = encontrar_navegador_possiveis([
        "firefox", "firefox.exe"
    ])
    try:
        if GeckoDriverManager is not None and FirefoxService is not None:
            from selenium.webdriver.firefox.options import Options as FirefoxOptions
            firefox_options = FirefoxOptions()
            if firefox_path:
                firefox_options.binary_location = firefox_path
            driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()), options=firefox_options)
            print(f"\n[INFO] Navegador Firefox detectado e iniciado em: {firefox_path or 'padrão do sistema'}\n")
            return driver
    except Exception as e:
        print(f"[WARN] Firefox não pôde ser iniciado: {e}")
    print("\n[ERRO] Nenhum navegador suportado foi encontrado ou pôde ser iniciado.\n\n" \
          "Certifique-se de ter o Google Chrome, Chromium ou Mozilla Firefox instalado.\n" \
          "Se estiver em ambiente de servidor, instale um navegador gráfico.\n" \
          "Se o erro persistir, consulte o README.md para instruções detalhadas.\n")
    sys.exit(1)

def buscar_ean_bluesoft_selenium(driver, produto):
    try:
        # Garantir que está na home do cosmos
        driver.get("https://cosmos.bluesoft.com.br")
        time.sleep(2)
        # Procurar campo de busca
        search_selectors = [
            "input[type='search']",
            "input[placeholder*='buscar']",
            "input[placeholder*='search']",
            "input[name*='search']",
            "input[id*='search']",
            ".search input",
            "#search input",
            "input[type='text']",
            "form input",
        ]
        search_field = None
        for selector in search_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    search_field = elements[0]
                    break
            except:
                continue
        if not search_field:
            return ''
        # Fazer a busca
        search_field.clear()
        search_field.send_keys(produto)
        search_field.send_keys(Keys.RETURN)
        time.sleep(5)  # Espera resultados
        # Verificar Cloudflare
        if 'um momento' in driver.title.lower() or 'checking' in driver.title.lower():
            print("\n" + "#"*60)
            print("""
████████████████████████████████████████████████████████████████████████████
⚠️  ATENÇÃO! CLOUDFLARE DETECTADO NOVAMENTE! ⚠️

O Cloudflare apareceu no meio do processo. Isso é NORMAL!

➡️  Resolva manualmente no navegador (página 'Um momento...' ou 'Checking your browser...').
➡️  Só APERTE ENTER aqui no terminal DEPOIS que o site estiver totalmente carregado e a barra de busca aparecer.
➡️  Tenha PACIÊNCIA! Pode demorar alguns segundos para o script continuar após apertar ENTER.

NÃO FECHE O NAVEGADOR!
████████████████████████████████████████████████████████████████████████████
""")
            print("#"*60 + "\n")
            input("Aperte ENTER aqui no terminal APÓS passar pelo Cloudflare no navegador!")
            print("\n✅ ENTER reconhecido! Continuando o processamento...\n")
            time.sleep(2)
        page_source = driver.page_source
        # Extrair EAN/GTIN dos links dos produtos
        ean_pattern = r'/produtos/(\d{8,14})'
        matches = re.findall(ean_pattern, page_source)
        if matches:
            return matches[0]  # Pega o primeiro código encontrado
        return ''
    except Exception as e:
        logging.error(f'Erro ao buscar "{produto}": {e}')
        return ''

def processar_csv_selenium(driver, caminho_csv):
    logging.info(f'Processando: {caminho_csv}')
    df = pd.read_csv(caminho_csv)
    nome_column = None
    for col in df.columns:
        if 'nome' in col.lower():
            nome_column = col
            break
    if nome_column is None:
        logging.warning(f"Coluna 'NOME' ou 'nome' não encontrada em {caminho_csv}. Pulando arquivo.")
        return
    barcodes = []
    for idx, row in df.iterrows():
        produto = str(row[nome_column]).strip()
        if not produto:
            barcodes.append('')
            continue
        codigo = buscar_ean_bluesoft_selenium(driver, produto)
        barcodes.append(codigo)
        time.sleep(3)  # Espera entre buscas
        if (idx + 1) % 20 == 0:
            print('Aguardando 10 segundos para evitar bloqueio...')
            time.sleep(10)
    df['BARCODE'] = barcodes
    df.to_csv(caminho_csv, index=False, encoding='utf-8')
    logging.info(f'Arquivo atualizado: {caminho_csv}')

def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('processar_dados.log'),
            logging.StreamHandler()
        ]
    )
    pasta_dados = 'dados'
    if not os.path.exists(pasta_dados):
        print(f'Pasta {pasta_dados} não encontrada!')
        return
    arquivos = [f for f in os.listdir(pasta_dados) if f.endswith('.csv')]
    if not arquivos:
        print('Nenhum arquivo CSV encontrado na pasta dados/')
        return
    driver = iniciar_driver()
    # Abrir direto no site do Cosmos Bluesoft
    try:
        driver.get("https://cosmos.bluesoft.com.br")
    except Exception as e:
        print(f"[ERRO] Não foi possível acessar o site do Cosmos Bluesoft: {e}")
    print("\n" + "="*60)
    print("""
████████████████████████████████████████████████████████████████████████████
⚠️  ATENÇÃO! PASSO OBRIGATÓRIO PARA O USUÁRIO ⚠️

1️⃣  Assim que o navegador abrir, você PRECISA passar manualmente pela verificação do Cloudflare (página 'Um momento...' ou 'Checking your browser...').

2️⃣  Só APERTE ENTER aqui no terminal DEPOIS que o site cosmos.bluesoft.com.br estiver totalmente carregado e você conseguir ver a barra de busca normalmente.

3️⃣  IMPORTANTE: O Cloudflare pode aparecer NOVAMENTE no meio do processo! Se isso acontecer, o script vai PAUSAR AUTOMATICAMENTE e pedir para você resolver de novo. Tenha PACIÊNCIA, aguarde o Cloudflare liberar e só então aperte ENTER para continuar.

4️⃣  Se alguns produtos não encontrarem o código de barras, isso é NORMAL e geralmente é culpa do Cloudflare. Você pode rodar o script novamente só com esses produtos em um novo CSV para tentar buscar os códigos que faltaram.

NÃO FECHE O NAVEGADOR enquanto o script estiver rodando!

████████████████████████████████████████████████████████████████████████████
""")
    print("="*60 + "\n")
    input("Aperte ENTER aqui no terminal APÓS passar pelo Cloudflare no navegador!")
    for arquivo in arquivos:
        caminho_csv = os.path.join(pasta_dados, arquivo)
        processar_csv_selenium(driver, caminho_csv)
    driver.quit()
    print('\nProcessamento concluído de todos os CSVs!')

if __name__ == "__main__":
    main() 