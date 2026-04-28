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
        try:
            requests.post(webhook, json={"content": msg})
        except:
            pass

def hash_text(text):
    return hashlib.md5(text.encode()).hexdigest()

# 🔥 PEGA SÓ O QUE INTERESSA (EVITA MUDANÇA FALSA)
def extract_tracking_text(content):
    lines = content.split("\n")

    filtered = []
    for line in lines:
        line = line.strip().lower()

        # remove lixo do site
        if any(x in line for x in [
            "braspress",
            "cookie",
            "privacidade",
            "menu",
            "login",
            "home"
        ]):
            continue

        if len(line) > 3:
            filtered.append(line)

    return "\n".join(filtered)

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

    return extract_tracking_text(content)


def main():
    send(WEBHOOK_GENERAL, "🟢 Bot iniciado e ONLINE no Railway")
    send(WEBHOOK_MUDO1, "📡 Bot iniciou e está monitorando rastreio...")

    last_hash = ""
    last_ping = time.time()

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu"
            ]
        )

        page = browser.new_page()

        while True:
            try:
                result = run_check(page)
                h = hash_text(result)

                # 📦 SÓ MUDA SE MUDAR O RASTREIO REAL
                if h != last_hash:
                    last_hash = h
                    send(WEBHOOK_MUDO1, "📦 🔔 ALTERAÇÃO DETECTADA:\n\n" + result)

                # 🟢 heartbeat só no geral
                if time.time() - last_ping > 300:
                    send(WEBHOOK_GENERAL, "🟢 Bot ainda ONLINE e monitorando rastreio...")
                    last_ping = time.time()

            except Exception as e:
                send(WEBHOOK_GENERAL, f"❌ erro no bot: {str(e)}")

            time.sleep(60)


if __name__ == "__main__":
    main()
