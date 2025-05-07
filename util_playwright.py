from playwright.sync_api import sync_playwright


def create_browser_instance(visible):
    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(headless=True)
    return browser

def close_instance(browser):
    browser.close()

def create_page_instance(browser):
    page = browser.new_page()
    return page