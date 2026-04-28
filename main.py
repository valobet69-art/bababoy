import os
import time
import hashlib
import requests
from playwright.sync_api import sync_playwright

CPF = "71877568600"
NF = "3306097"

WEBHOOK_URL = os.getenv("WEBHOOK_URL")

URL = "https://www.braspress.com/acesso-rapido/rastreie-sua-encomenda/"

def send(msg):
    if WEBHOOK_URL:
        requests.post(WEBHOOK_URL, json={"content": msg})

def hash_text(text):
    return hashlib.md5(text.encode()).hexdigest()

def run_check(page):
    page.goto(URL, timeout=60000)
    page.wait_for_timeout(5000)

    # tenta preencher campos
    try:
        page.fill('input[name="cpf"]', CPF)
        page.fill('input[name="nota"]', NF)
    except:
        return "❌ Não conseguiu encontrar campos de CPF/NF (site mudou layout)"

    # clicar buscar
    try:
        page.click("button")
    except:
        return "❌ Botão de busca não encontrado"

    page.wait_for_timeout(7000)

    content = page.inner_text("body")

    # valida se realmente pesquisou certo
    if CPF not in content and NF not in content:
        return "⚠️ Página carregou, mas não parece ter processado a busca corretamente"

    # detecta erro comum
    if "não encontrado" in content.lower():
        return "📭 Pedido não encontrado no sistema"

    return content


def main():
    send("🤖 Bot Braspress iniciado (monitoramento ativo)")

    last_hash = ""

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        while True:
            try:
                result = run_check(page)
                h = hash_text(result)

                if h != last_hash:
                    last_hash = h

                    send("📦 🔔 Atualização detectada no rastreio:\n\n" + result)

                else:
                    print("Sem mudanças...")

            except Exception as e:
                send(f"❌ Erro no bot: {str(e)}")

            time.sleep(60)


if __name__ == "__main__":
    main()
