# EAN/GTIN Finder Automático para Cosmos Bluesoft

Este projeto automatiza a busca de códigos de barras (EAN/GTIN) de produtos no site cosmos.bluesoft.com.br, preenchendo automaticamente a coluna `codigo` em arquivos CSV de produtos.

Repositório oficial: [https://github.com/sidnei-almeida/bluesoft_code_scraper](https://github.com/sidnei-almeida/bluesoft_code_scraper)

## 🚀 Funcionalidades
- Busca automática do código EAN/GTIN de cada produto usando o campo de busca do Cosmos Bluesoft.
- Atualiza/cria a coluna `codigo` em cada CSV processado.
- **✨ Busca inteligente:** O script verifica automaticamente quais produtos já têm código e pula eles, buscando apenas os necessários desde o início!
- **🔄 Múltiplas tentativas:** Faz até 3 tentativas automaticamente para encontrar códigos de produtos faltantes.
- **📊 Estatísticas detalhadas:** Mostra taxa de sucesso e progresso em tempo real.
- Suporte a múltiplos arquivos CSV na pasta `dados/`.
- Detecção automática do Cloudflare durante o processo, com instruções claras para o usuário.
- Log detalhado do processo em `processar_dados.log`.

## ⚙️ Requisitos
- **Python 3.13** (ou superior)
- **Google Chrome** ou **Mozilla Firefox** instalado
- **pip** para instalar dependências

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
   - **Só aperte ENTER no terminal depois que o site estiver totalmente carregado e a barra de busca aparecer.**
   - **NÃO feche o navegador enquanto o script estiver rodando!**
4. **O script vai:**
   - Verificar automaticamente quais produtos já têm código nos CSVs
   - Mostrar quantos produtos precisam de código
   - Pular produtos que já têm código e buscar apenas os necessários
   - Fazer até 3 tentativas para cada produto sem código
   - Mostrar estatísticas em tempo real e ao final do processo
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

## 🧠 Como funciona a busca inteligente

O script agora trabalha de forma muito mais eficiente:

1. **Análise inicial:** Ao iniciar, verifica todos os CSVs e conta quantos produtos já têm código
2. **Pula produtos completos:** Não perde tempo buscando produtos que já têm código
3. **Múltiplas tentativas:** Para produtos sem código, faz até 3 tentativas automáticas
4. **Estatísticas em tempo real:** Mostra progresso e taxa de sucesso durante o processo
5. **Execução incremental:** Se rodar o script várias vezes, ele sempre continua de onde parou

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
- **Tenha paciência!** O Cloudflare pode aparecer mais de uma vez durante o processo.
- **Às vezes o Cloudflare entra em um loop de carregamento infinito** (fica só "carregando" e não aparece a caixinha para clicar). Isso é normal e acontece por proteção do site. **Nesses casos, espere alguns minutos sem fechar a página**: normalmente, depois de um tempo, o Cloudflare libera e a caixinha volta a aparecer para você clicar. 
- **Vale a pena tentar apertar F5 (atualizar a página)** para ver se o Cloudflare libera, mas **NUNCA feche a página do navegador** enquanto o script estiver rodando! Se fechar, o script vai perder a conexão com o navegador e dará erro.
- **Nunca feche o navegador enquanto o script estiver rodando.**
- **Se o script for interrompido:** Sem problemas! Execute novamente e ele vai pular automaticamente os produtos que já têm código de barras, buscando apenas os faltantes.
- **Busca inteligente:** O script faz múltiplas passagens automaticamente para tentar encontrar todos os códigos de barras possíveis.
- O tempo de espera entre buscas e pausas periódicas são essenciais para evitar bloqueios.

## ❓ Dúvidas ou problemas?
Se tiver qualquer dúvida, problema ou sugestão, abra uma issue ou entre em contato pelo [repositório no GitHub](https://github.com/sidnei-almeida/bluesoft_code_scraper).

---

Feito com ❤️ para automação de catálogos de produtos! 