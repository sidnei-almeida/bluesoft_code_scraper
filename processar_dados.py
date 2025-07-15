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

def iniciar_driver():
    chrome_options = Options()
    # NÃO usar headless para permitir interação manual
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    driver = webdriver.Chrome(options=chrome_options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver

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