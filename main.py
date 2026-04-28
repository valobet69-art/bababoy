import time
import requests
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

CPF = "09081684620"
NF = "3306097"

WEBHOOK_URL = os.getenv("WEBHOOK_URL")

URL = "https://www.braspress.com/acesso-rapido/rastreie-sua-encomenda/"

def send_discord(msg):
    requests.post(WEBHOOK_URL, json={"content": msg})

def create_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)
    return driver

def get_status(driver):
    driver.get(URL)
    time.sleep(5)

    cpf_input = driver.find_element(By.NAME, "cpf")
    nf_input = driver.find_element(By.NAME, "nota")

    cpf_input.send_keys(CPF)
    nf_input.send_keys(NF)

    driver.find_element(By.XPATH, "//button").click()

    time.sleep(6)

    return driver.find_element(By.TAG_NAME, "body").text

def main():
    driver = create_driver()
    last = ""

    send_discord("🤖 Bot de rastreio iniciado no Railway!")

    while True:
        try:
            status = get_status(driver)

            if status != last:
                last = status
                send_discord("📦 Atualização:\n" + status)

        except Exception as e:
            send_discord(f"❌ Erro: {e}")

        time.sleep(60)

if __name__ == "__main__":
    main()
