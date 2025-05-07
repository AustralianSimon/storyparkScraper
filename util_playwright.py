from playwright.sync_api import sync_playwright


def create_browser_instance(visible):
    playwright = sync_playwright().start()
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.9999.99 Safari/537.36"
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context(user_agent=user_agent)
    return context

def close_instance(browser):
    browser.close()

def create_page_instance(browser):
    page = browser.new_page()
    return page