#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Processa todos os CSVs na pasta dados/ usando Selenium, com pausa manual para Cloudflare, busca EAN/GTIN de cada produto, espera 3s entre cada, 10s a cada 5, atualiza coluna 'codigo'.
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
import random
from selenium.webdriver.common.action_chains import ActionChains

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

# Tentar importar undetected_chromedriver
try:
    import undetected_chromedriver as uc
    UC_AVAILABLE = True
except ImportError:
    UC_AVAILABLE = False
    print("[WARN] undetected-chromedriver não instalado. Usando Chrome normal (mais detectável).")


def delay_aleatorio(min_sec, max_sec):
    """
    Espera um tempo aleatório entre min_sec e max_sec segundos.
    """
    time.sleep(random.uniform(min_sec, max_sec))

def scroll_aleatorio(driver):
    """
    Faz scroll aleatório na página para simular comportamento humano.
    """
    try:
        scroll_amount = random.randint(200, 500)
        driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
        delay_aleatorio(0.5, 1.2)
        # Às vezes volta um pouco (comportamento natural)
        if random.random() > 0.7:
            driver.execute_script(f"window.scrollBy(0, -{random.randint(50, 150)});")
            delay_aleatorio(0.3, 0.7)
    except:
        pass

def movimento_mouse_aleatorio(driver):
    """
    Move o mouse aleatoriamente para simular leitura.
    """
    try:
        action = ActionChains(driver)
        # Move para posição aleatória
        x_offset = random.randint(100, 500)
        y_offset = random.randint(100, 400)
        action.move_by_offset(x_offset, y_offset).perform()
        delay_aleatorio(0.2, 0.5)
    except:
        pass

def digitar_como_humano(element, text):
    """
    Digita texto caractere por caractere com delays aleatórios para simular digitação humana.
    """
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(0.05, 0.15))

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
    Tenta iniciar o Chrome com undetected-chromedriver, depois Chromium, depois Firefox.
    Usa undetected-chromedriver quando disponível para evitar detecção de bot.
    """
    # Tentar usar undetected-chromedriver primeiro (melhor anti-detecção)
    if UC_AVAILABLE:
        try:
            options = uc.ChromeOptions()
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            # Não adicionar flags que detectam automação
            driver = uc.Chrome(options=options, version_main=None)
            print(f"\n[INFO] ✅ Navegador Chrome iniciado com undetected-chromedriver (anti-detecção ativada)\n")
            return driver
        except Exception as e:
            print(f"[WARN] undetected-chromedriver falhou: {e}")
            print("[INFO] Tentando Chrome normal...")
    
    # Fallback para Chrome normal
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
        delay_aleatorio(2, 3.5)  # Delay aleatório em vez de fixo
        
        # Simular leitura da página (scroll)
        scroll_aleatorio(driver)
        
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
        
        # Simular movimento do mouse
        movimento_mouse_aleatorio(driver)
        delay_aleatorio(0.5, 1)
        
        # Fazer a busca (copiar e colar é mais rápido e ainda funciona)
        search_field.clear()
        delay_aleatorio(0.3, 0.7)
        search_field.send_keys(produto)  # Copia e cola direto
        delay_aleatorio(0.5, 1.2)
        search_field.send_keys(Keys.RETURN)
        delay_aleatorio(3, 5)  # Espera resultados com delay aleatório
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

def processar_csv_selenium(driver, caminho_csv, apenas_faltantes=False):
    logging.info(f'Processando: {caminho_csv}')
    df = pd.read_csv(caminho_csv)
    nome_column = None
    for col in df.columns:
        if 'nome' in col.lower():
            nome_column = col
            break
    if nome_column is None:
        logging.warning(f"Coluna 'NOME' ou 'nome' não encontrada em {caminho_csv}. Pulando arquivo.")
        return 0
    
    # Se a coluna codigo não existir, criar ela
    if 'codigo' not in df.columns:
        df['codigo'] = ''
    
    produtos_processados = 0
    for idx, row in df.iterrows():
        # Se apenas_faltantes=True, pular produtos que já têm codigo
        if apenas_faltantes and pd.notna(row.get('codigo')) and str(row.get('codigo')).strip():
            continue
        
        produto = str(row[nome_column]).strip()
        if not produto:
            continue
        
        print(f'[{idx+1}/{len(df)}] Buscando: {produto}')
        codigo = buscar_ean_bluesoft_selenium(driver, produto)
        if codigo:
            df.at[idx, 'codigo'] = codigo
            print(f'✅ Código encontrado: {codigo}')
            produtos_processados += 1
        else:
            print(f'❌ Código não encontrado')
        
        # Delay aleatório entre buscas para parecer humano
        delay_aleatorio(3, 5)
        
        # Pausas mais longas periodicamente
        if (idx + 1) % 15 == 0:
            tempo_pausa = random.uniform(10, 15)
            print(f'Aguardando {tempo_pausa:.1f} segundos para evitar bloqueio...')
            time.sleep(tempo_pausa)
    
    df.to_csv(caminho_csv, index=False, encoding='utf-8')
    logging.info(f'Arquivo atualizado: {caminho_csv}')
    return produtos_processados

def contar_produtos_sem_codigo(caminho_csv):
    """
    Conta quantos produtos ainda não têm codigo no CSV.
    """
    df = pd.read_csv(caminho_csv)
    if 'codigo' not in df.columns:
        nome_column = None
        for col in df.columns:
            if 'nome' in col.lower():
                nome_column = col
                break
        if nome_column:
            return len(df[df[nome_column].notna()])
        return 0
    
    # Contar produtos sem codigo (vazios ou NaN)
    sem_codigo = df[df['codigo'].isna() | (df['codigo'] == '')]
    return len(sem_codigo)

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
    print("\n" + "="*80)
    print("""
████████████████████████████████████████████████████████████████████████████
⚠️  ATENÇÃO! PASSO OBRIGATÓRIO PARA O USUÁRIO ⚠️

1️⃣  Passe pela verificação do Cloudflare (página 'Um momento...' ou 'Checking...')

2️⃣  IMPORTANTE - Para evitar rate limit, faça 2-3 buscas MANUAIS no site:
    • Digite alguns nomes de produtos na barra de busca
    • Clique nos resultados, navegue pelas páginas
    • Isso ajuda a "aquecer" a sessão e evita bloqueios

3️⃣  Só APERTE ENTER aqui DEPOIS de fazer essas buscas manuais!

4️⃣  O Cloudflare pode aparecer durante o processo - se acontecer, o script
    pausará automaticamente. Resolva e aperte ENTER para continuar.

5️⃣  O script usa comportamento humanizado (delays aleatórios, scroll, etc)
    para evitar detecção. O processo será mais LENTO mas SEGURO.

NÃO FECHE O NAVEGADOR enquanto o script estiver rodando!

████████████████████████████████████████████████████████████████████████████
""")
    print("="*80 + "\n")
    input("Aperte ENTER aqui APÓS fazer 2-3 buscas manuais no navegador!")
    
    # Aguardar um pouco mais após o usuário apertar ENTER
    print("\n✅ ENTER reconhecido! Aguardando alguns segundos antes de iniciar...\n")
    delay_aleatorio(3, 5)
    
    # Número máximo de tentativas para buscar produtos faltantes
    max_tentativas = 3
    
    # Verificar quantos produtos precisam ser processados no total
    print("\n" + "="*80)
    print("📊 Verificando produtos nos CSVs...")
    print("="*80 + "\n")
    
    total_inicial_faltantes = 0
    faltantes_inicial = {}
    for arquivo in arquivos:
        caminho_csv = os.path.join(pasta_dados, arquivo)
        faltantes = contar_produtos_sem_codigo(caminho_csv)
        if faltantes > 0:
            faltantes_inicial[arquivo] = faltantes
            total_inicial_faltantes += faltantes
            print(f"📄 {arquivo}: {faltantes} produtos sem código")
    
    if total_inicial_faltantes == 0:
        print("\n✅ Todos os produtos já têm código! Nada a fazer.")
        driver.quit()
        return
    
    print(f"\n🎯 Total de {total_inicial_faltantes} produtos precisam de código")
    print("="*80 + "\n")
    
    # PASSAGENS - Buscar apenas produtos sem codigo
    for tentativa in range(0, max_tentativas):
        # Verificar quantos produtos ainda estão sem codigo
        total_faltantes = 0
        faltantes_por_arquivo = {}
        
        for arquivo in arquivos:
            caminho_csv = os.path.join(pasta_dados, arquivo)
            faltantes = contar_produtos_sem_codigo(caminho_csv)
            if faltantes > 0:
                faltantes_por_arquivo[arquivo] = faltantes
                total_faltantes += faltantes
        
        if total_faltantes == 0:
            print("\n" + "="*80)
            print("✅ SUCESSO! Todos os produtos têm código!")
            print("="*80 + "\n")
            break
        
        print("\n" + "="*80)
        if tentativa == 0:
            print(f"🔍 TENTATIVA {tentativa + 1}/{max_tentativas} - Buscando {total_faltantes} produtos sem código...")
        else:
            print(f"🔄 TENTATIVA {tentativa + 1}/{max_tentativas} - Buscando {total_faltantes} produtos restantes...")
        print("="*80 + "\n")
        
        for arquivo, faltantes in faltantes_por_arquivo.items():
            caminho_csv = os.path.join(pasta_dados, arquivo)
            print(f"\n📄 Arquivo: {arquivo} ({faltantes} produtos faltantes)")
            produtos_encontrados = processar_csv_selenium(driver, caminho_csv, apenas_faltantes=True)
            print(f"✅ {produtos_encontrados} códigos encontrados nesta tentativa")
        
        # Se for a última tentativa, mostrar estatísticas finais
        if tentativa == max_tentativas - 1:
            # Contar quantos ainda faltam após todas as tentativas
            total_final_faltantes = 0
            faltantes_finais = {}
            for arquivo in arquivos:
                caminho_csv = os.path.join(pasta_dados, arquivo)
                faltantes = contar_produtos_sem_codigo(caminho_csv)
                if faltantes > 0:
                    total_final_faltantes += faltantes
                    faltantes_finais[arquivo] = faltantes
            
            if total_final_faltantes > 0:
                print("\n" + "="*80)
                print(f"⚠️  Atingido o limite de {max_tentativas} tentativas")
                print("="*80 + "\n")
                
                for arquivo, faltantes in faltantes_finais.items():
                    print(f"📄 {arquivo}: {faltantes} produtos sem código")
                
                print(f"\n⚠️  Total de {total_final_faltantes} produtos ainda sem código.")
                print("💡 Isso pode acontecer por limitações do Cloudflare ou produtos não cadastrados.")
                print("💡 Você pode executar o script novamente mais tarde para tentar buscar os restantes.")
                print("💡 O script vai pular automaticamente os que já têm código e buscar apenas os faltantes.")
    
    driver.quit()
    
    # Estatísticas finais
    print('\n' + "="*80)
    print('🎉 PROCESSAMENTO CONCLUÍDO!')
    print("="*80 + "\n")
    
    # Contar quantos foram encontrados vs quantos faltavam
    total_final_faltantes = 0
    for arquivo in arquivos:
        caminho_csv = os.path.join(pasta_dados, arquivo)
        faltantes = contar_produtos_sem_codigo(caminho_csv)
        total_final_faltantes += faltantes
    
    total_encontrados = total_inicial_faltantes - total_final_faltantes
    
    if total_final_faltantes == 0:
        print(f"✅ {total_encontrados}/{total_inicial_faltantes} códigos encontrados com sucesso!")
    else:
        print(f"📊 Estatísticas:")
        print(f"   ✅ Encontrados: {total_encontrados}/{total_inicial_faltantes}")
        print(f"   ❌ Não encontrados: {total_final_faltantes}/{total_inicial_faltantes}")
        taxa_sucesso = (total_encontrados / total_inicial_faltantes) * 100
        print(f"   📈 Taxa de sucesso: {taxa_sucesso:.1f}%")
    
    print("="*80 + "\n")

if __name__ == "__main__":
    main() 