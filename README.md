# EAN/GTIN Finder Automático para Cosmos Bluesoft

Este projeto automatiza a busca de códigos de barras (EAN/GTIN) de produtos no site cosmos.bluesoft.com.br, preenchendo automaticamente a coluna `codigo` em arquivos CSV de produtos.

Repositório oficial: [https://github.com/sidnei-almeida/bluesoft_code_scraper](https://github.com/sidnei-almeida/bluesoft_code_scraper)

## 🚀 Funcionalidades
- Busca automática do código EAN/GTIN de cada produto usando o campo de busca do Cosmos Bluesoft.
- Atualiza/cria a coluna `codigo` em cada CSV processado.
- **🛡️ Anti-detecção de bot:** Usa `undetected-chromedriver` e técnicas de humanização para evitar rate limiting:
  - Scroll e movimentos de mouse aleatórios
  - Delays aleatórios entre ações (3-5s entre buscas)
  - Pausas periódicas a cada 15 produtos
  - Comportamento natural de navegação
- **✨ Busca inteligente:** O script verifica automaticamente quais produtos já têm código e pula eles, buscando apenas os necessários desde o início!
- **🔄 Múltiplas tentativas:** Faz até 3 tentativas automaticamente para encontrar códigos de produtos faltantes.
- **📊 Estatísticas detalhadas:** Mostra taxa de sucesso e progresso em tempo real.
- Suporte a múltiplos arquivos CSV na pasta `dados/`.
- Detecção automática do Cloudflare durante o processo, com instruções claras para o usuário.
- Log detalhado do processo em `processar_dados.log`.

## ⚙️ Requisitos
- **Python 3.9+** (testado em Python 3.12 e 3.13)
- **Google Chrome** (recomendado para melhor evasão de detecção)
- **pip** para instalar dependências

**Nota:** O script usa `undetected-chromedriver` para evitar detecção de bot e rate limiting do Cloudflare. Para Python 3.12+, o `setuptools` é necessário (já incluído no requirements.txt).

## 📦 Instalação
1. Clone o repositório:
   ```bash
   git clone https://github.com/sidnei-almeida/bluesoft_code_scraper.git
   cd bluesoft_code_scraper
   ```
2. Crie e ative um ambiente virtual (opcional, mas recomendado):
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # ou
   venv\Scripts\activate  # Windows
   ```
3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

> **Não é mais necessário baixar o ChromeDriver ou GeckoDriver manualmente!**
> O script usa o [webdriver-manager](https://github.com/SergeyPirogov/webdriver_manager) para instalar e gerenciar o driver automaticamente, tanto no Windows quanto no Linux ou Mac.

## 📂 Como preparar os dados
1. Crie uma pasta chamada `dados` na raiz do projeto (se ainda não existir).
2. Coloque todos os arquivos `.csv` que deseja processar dentro da pasta `dados/`.
3. Cada CSV deve ter uma coluna chamada `NOME` ou `nome` com o nome dos produtos.

## 🏃‍♂️ Como rodar o script
1. Execute o script principal:
   ```bash
   python processar_dados.py
   ```
2. O script tentará abrir o Google Chrome automaticamente. Se não encontrar, tentará o Mozilla Firefox.
   - Certifique-se de ter pelo menos um desses navegadores instalado.
   - O driver será baixado automaticamente na primeira execução.
3. **Leia com atenção o aviso no terminal!**
   - Assim que o navegador abrir, **passe manualmente pela verificação do Cloudflare** (página "Um momento..." ou "Checking your browser...").
   - **IMPORTANTE:** Faça 2-3 buscas MANUAIS no site antes de apertar ENTER:
     - Digite alguns produtos na barra de busca
     - Clique nos resultados, navegue pelas páginas
     - Isso "aquece" a sessão e evita rate limiting
   - **Só aperte ENTER no terminal DEPOIS de fazer essas buscas manuais.**
   - **NÃO feche o navegador enquanto o script estiver rodando!**
4. **O script vai:**
   - Verificar automaticamente quais produtos já têm código nos CSVs
   - Mostrar quantos produtos precisam de código
   - Pular produtos que já têm código e buscar apenas os necessários
   - Usar comportamento humanizado para evitar detecção (delays aleatórios, scroll, etc)
   - Fazer até 3 tentativas para cada produto sem código
   - Mostrar estatísticas em tempo real e ao final do processo
   
   **⚠️ IMPORTANTE:** O processo é MAIS LENTO que antes (3-5s por produto + pausas), mas isso é necessário para evitar rate limiting e bloqueios.
5. **Se o Cloudflare aparecer novamente durante o processo:**
   - O script vai pausar automaticamente e mostrar um aviso super chamativo.
   - Resolva o Cloudflare manualmente no navegador e só então aperte ENTER no terminal para continuar.
   - Pode demorar alguns segundos para o script continuar após o ENTER.
6. **Execuções subsequentes:**
   - Se executar o script novamente, ele detecta automaticamente os produtos que já têm código
   - Busca apenas os produtos que ainda estão faltando
   - Não precisa criar CSV manualmente com dados faltantes!

## 📝 Exemplo de CSV

**Antes (entrada):**
```csv
NOME
Coca-Cola 2L
Arroz Branco Tipo 1 5kg
Leite Integral 1L
```

**Depois (com códigos):**
```csv
NOME,codigo
Coca-Cola 2L,7894900011517
Arroz Branco Tipo 1 5kg,7896005200025
Leite Integral 1L,7891000100103
```

**Se executar novamente com produtos parcialmente preenchidos:**
```csv
NOME,codigo
Coca-Cola 2L,7894900011517
Arroz Branco Tipo 1 5kg,
Leite Integral 1L,7891000100103
```
↓ *O script pula produtos que já têm código e busca apenas o que falta*
```csv
NOME,codigo
Coca-Cola 2L,7894900011517
Arroz Branco Tipo 1 5kg,7896005200025
Leite Integral 1L,7891000100103
```

## 🗂️ Saída
- Os arquivos CSV originais na pasta `dados/` são atualizados com a coluna `codigo` preenchida.
- Um log detalhado é salvo em `processar_dados.log`.

## 🧠 Como funciona a busca inteligente e anti-detecção

O script combina eficiência com segurança:

1. **Análise inicial:** Ao iniciar, verifica todos os CSVs e conta quantos produtos já têm código
2. **Pula produtos completos:** Não perde tempo buscando produtos que já têm código
3. **Comportamento humanizado:** 
   - Faz scroll aleatório nas páginas
   - Move o mouse de forma natural
   - Usa delays aleatórios (não fixos)
   - Pausas estratégicas durante o processo
4. **Múltiplas tentativas:** Para produtos sem código, faz até 3 tentativas automáticas
5. **Estatísticas em tempo real:** Mostra progresso e taxa de sucesso durante o processo
6. **Execução incremental:** Se rodar o script várias vezes, ele sempre continua de onde parou
7. **Anti-detecção:** Usa `undetected-chromedriver` que é muito mais difícil de detectar que Selenium normal

**Exemplo de execução:**
```
📊 Verificando produtos nos CSVs...
📄 alimentos.csv: 45 produtos sem código
📄 bebidas.csv: 23 produtos sem código

🎯 Total de 68 produtos precisam de código

🔍 TENTATIVA 1/3 - Buscando 68 produtos sem código...
📄 Arquivo: alimentos.csv (45 produtos faltantes)
[1/45] Buscando: Coca-Cola 2L
✅ Código encontrado: 7894900011517
...
✅ 60 códigos encontrados nesta tentativa

🔄 TENTATIVA 2/3 - Buscando 8 produtos restantes...
...
```

## 💡 Dicas importantes
- **Compatível com Windows, Linux e Mac!**
- **🛡️ Configurado para segurança contra rate limiting:**
  - 3-5s aleatórios entre cada busca
  - Scroll e movimentos de mouse automáticos
  - 10-15s de pausa a cada 15 produtos
  - Comportamento natural para evitar detecção
- **⏱️ Processo balanceado:** Espere ~5-8s por produto. Rápido o suficiente mas seguro contra bloqueios.
- **🔑 Faça buscas manuais primeiro:** Sempre faça 2-3 buscas manuais no site antes de apertar ENTER.
- **Tenha paciência!** O Cloudflare pode aparecer mais de uma vez durante o processo.
- **Às vezes o Cloudflare entra em um loop de carregamento infinito** (fica só "carregando" e não aparece a caixinha para clicar). Isso é normal e acontece por proteção do site. **Nesses casos, espere alguns minutos sem fechar a página**: normalmente, depois de um tempo, o Cloudflare libera e a caixinha volta a aparecer para você clicar. 
- **Vale a pena tentar apertar F5 (atualizar a página)** para ver se o Cloudflare libera, mas **NUNCA feche a página do navegador** enquanto o script estiver rodando! Se fechar, o script vai perder a conexão com o navegador e dará erro.
- **Nunca feche o navegador enquanto o script estiver rodando.**
- **Se o script for interrompido:** Sem problemas! Execute novamente e ele vai pular automaticamente os produtos que já têm código, buscando apenas os faltantes.
- **Busca inteligente:** O script faz múltiplas passagens automaticamente para tentar encontrar todos os códigos possíveis.

## ❓ Dúvidas ou problemas?
Se tiver qualquer dúvida, problema ou sugestão, abra uma issue ou entre em contato pelo [repositório no GitHub](https://github.com/sidnei-almeida/bluesoft_code_scraper).

---

Feito com ❤️ para automação de catálogos de produtos! 