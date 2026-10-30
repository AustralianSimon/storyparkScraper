import os, platform
from playwright.sync_api import sync_playwright


def create_browser_instance(visible, storage_state=None):
    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(
        headless=not visible,
        args=[
            '--disable-dev-shm-usage',
            '--disable-gpu',
        ]
    )
    context = browser.new_context(
        user_agent=build_user_agent(browser.version),
        viewport={'width': 1280, 'height': 900},
        storage_state=storage_state if storage_state and os.path.exists(storage_state) else None,
    )
    return context

def build_user_agent(browser_version):
    """
    Builds a user agent matching the launched Chromium version and host OS, in the reduced
    format real Chrome sends (major version only) so it stays current as Playwright updates.
    """
    major = browser_version.split('.')[0]
    system = platform.system()
    if system == 'Windows':
        os_part = 'Windows NT 10.0; Win64; x64'
    elif system == 'Darwin':
        os_part = 'Macintosh; Intel Mac OS X 10_15_7'
    else:
        os_part = 'X11; Linux x86_64'
    return f"Mozilla/5.0 ({os_part}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{major}.0.0.0 Safari/537.36"

def save_session(browser, path):
    os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
    browser.storage_state(path=path)

def close_instance(browser):
    browser.close()

def create_page_instance(browser):
    page = browser.new_page()
    return page