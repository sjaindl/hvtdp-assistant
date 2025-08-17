import subprocess
import sys
from typing import List
from llama_index.tools.playwright.base import PlaywrightToolSpec
from llama_index.core import Document

urls: List[str] = [
    "https://www.hvtdpstainz.at/#/about",
    "https://www.hvtdpstainz.at/#/entenrennen",
    "https://www.hvtdpstainz.at/#/bocciaturnier",
    "https://www.hvtdpstainz.at/#/contact",
]

async def load_web_docs() -> List[Document]:
    subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check = True)

    # spins up browser:
    browser = await PlaywrightToolSpec.create_async_playwright_browser(headless = True)
    tool = PlaywrightToolSpec.from_async_browser(browser)

    docs: List[Document] = []
    try:
        for url in urls:
            await tool.navigate_to(url)
            # Optional: wait for main app content to appear
            try:
                await tool.get_elements("main, [role=main], #app, .app, .content")
            except Exception:
                pass

            text = await tool.extract_text()          # rendered page → plain text
            curr = await tool.get_current_page()      # final URL (after redirects)
            docs.append(Document(text=" ".join(text.split()),
                                 metadata={"source": curr}))

        return docs
    finally:
        await browser.close()
