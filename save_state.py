# save_state.py
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    ctx = browser.new_context()
    page = ctx.new_page()

    # 1) Log in to Google with the same email as in .env
    page.goto("https://accounts.google.com/")
    input("Sign in, wait for your account page to load, then press Enter in the terminal... ")

    # 2) Also open Google Forms so its domain cookies get set
    page.goto("https://docs.google.com/forms")
    input("When the Google Forms page opens, press Enter to save state.json... ")

    ctx.storage_state(path="state.json")
    browser.close()
