# from playwright.sync_api import sync_playwright

# with sync_playwright() as p:
#     print("Available browsers:")
#     for browser_type in [p.chromium, p.firefox, p.webkit]:
#         print(f"- {browser_type.name}")



async def web_scrapping_tool(url: str):
    """This function tool is used to web scrape, taking the URL as input and outputting
    the final job description which includes all about the job."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url)

        await page.wait_for_timeout(3000)  # allow JS to load
        content = await page.content()  # full rendered HTML
        await browser.close()

    html = content
    soup = BeautifulSoup(html, "html.parser")

    # 1. Remove useless tags
    for tag in soup(["script", "style", "noscript", "header", "footer", "nav", "aside"]):
        tag.decompose()

    # 2. Try to find main content containers
    candidates = []

    for tag in soup.find_all(["main", "article", "section", "div"]):
        text = tag.get_text(separator=" ", strip=True)

        # heuristic: meaningful blocks are long
        if len(text) > 500:
            candidates.append((len(text), tag))

    # 3. Pick the largest meaningful block
    if candidates:
        main_tag = sorted(candidates, key=lambda x: x[0], reverse=True)[0][1]
    else:
        main_tag = soup.body  # fallback

    # 4. Extract structured text (preserve bullets)
    lines = []

    for element in main_tag.descendants:
        if element.name in ["h1", "h2", "h3"]:
            text = element.get_text(strip=True)
            if text:
                lines.append(f"\n{text.upper()}\n")

        elif element.name == "p":
            text = element.get_text(strip=True)
            if text:
                lines.append(text)

        elif element.name == "li":
            text = element.get_text(strip=True)
            if text:
                lines.append(f"- {text}")

    cleaned_text = "\n".join(lines)

    # 5. Final cleanup
    cleaned_text = re.sub(r'\n{2,}', '\n\n', cleaned_text)

    return cleaned_text.strip()