# save_state.py
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    ctx = browser.new_context()
    page = ctx.new_page()

    # 1) Логинимся в Google под тем же email, что в .env
    page.goto("https://accounts.google.com/")
    input("Войди в аккаунт, дождись загрузки аккаунт-страницы и только потом жми Enter в терминале... ")

    # 2) Дополнительно заходим на формы, чтобы прогрелись куки домена
    page.goto("https://docs.google.com/forms")
    input("Когда страница Google Forms откроется — жми Enter для сохранения state.json... ")

    ctx.storage_state(path="state.json")
    browser.close()
