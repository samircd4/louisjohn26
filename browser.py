from playwright.sync_api import sync_playwright
from rich import print

user_data_dir = r"C:\Users\samir\AppData\Roaming\Mozilla\Firefox\Profiles\xyz123.default-release"

with sync_playwright() as p:
    context = p.firefox.launch_persistent_context(
        user_data_dir=user_data_dir,
        headless=True
    )
    
    # launch_persistent_context opens a page automatically
    page = context.pages[0] if context.pages else context.new_page()
    page.goto("https://www.arket.com/en-gb/product/desert-kick-flare-jeans-white-1360778002/")
    # page.wait_for_load_state('documentloaded')  # Wait for the page to load completely
    print(page.title())
    cookies = page.context.cookies()
    print(cookies)
    context.close()