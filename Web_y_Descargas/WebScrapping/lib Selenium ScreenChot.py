from playwright.sync_api import sync_playwright

urls = [
    "https://esiima.uaa.mx/exsiima/xwglhorarioaula.jsp?vps_Aula=116-A",
]

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    for i, url in enumerate(urls):
        page.goto(url)
        page.screenshot(path=f"screenshot_{i+1}.png", full_page=True)

    browser.close()
