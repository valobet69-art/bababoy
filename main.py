import os
import time
import hashlib
import requests
from playwright.sync_api import sync_playwright

CPF = "71877568600"
NF = "3306097"

WEBHOOK_GENERAL = os.getenv("WEBHOOK_GENERAL")
WEBHOOK_MUDO1 = os.getenv("WEBHOOK_MUDO1")

URL = "https://www.braspress.com/acesso-rapido/rastreie-sua-encomenda/"

def send(webhook, msg):
    if webhook:
        requests.post(webhook, json={"content": msg})

def hash_text(text):
    return hashlib.md5(text.encode()).hexdigest()

def run_check(page):
    page.goto(URL, timeout=60000)
    page.wait_for_timeout(5000)

    try:
        page.fill('input[name="cpf"]', CPF)
        page.fill('input[name="nota"]', NF)
    except:
        return "❌ site mudou (não achou campos)"

    try:
        page.click("button")
    except:
        return "❌ botão de busca não encontrado"

    page.wait_for_timeout(7000)

    content = page.inner_text("body")

    if "não encontrado" in content.lower():
        return "📭 pedido não encontrado"

    return content


def main():
    send(WEBHOOK_GENERAL, "🟢 Bot iniciado e online no Railway")

    last_hash = ""
    last_ping = time.time()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        while True:
            try:
                result = run_check(page)
                h = hash_text(result)

                # 📦 mudança real
                if h != last_hash:
                    last_hash = h
                    send(WEBHOOK_MUDO1, "📦 🔔 ALTERAÇÃO DETECTADA:\n\n" + result)

                # 🟢 heartbeat geral
                if time.time() - last_ping > 300:
                    send(WEBHOOK_GENERAL, "🟢 Bot online e monitorando rastreio...")
                    last_ping = time.time()

            except Exception as e:
                send(WEBHOOK_GENERAL, f"❌ erro: {str(e)}")

            time.sleep(60)


if __name__ == "__main__":
    main()
