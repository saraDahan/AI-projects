from mcp.server.fastmcp import FastMCP
from playwright.async_api import TimeoutError as PlaywrightTimeout
from playwright.async_api import async_playwright
import asyncio


mcp = FastMCP("weather-Israel")

FORECAST_URL = "https://www.weather2day.co.il/forecast"

browser = None
page = None


@mcp.tool()
async def open_weather_forecast_israel() -> str:
    """Open the Israeli weather forecast website."""

    global browser, page

    playwright = await async_playwright().start()

    browser = await playwright.chromium.launch(headless=False)
    page = await browser.new_page()

    await page.goto("https://www.weather2day.co.il/forecast")

    return "Weather forecast website opened successfully."


@mcp.tool()
async def enter_weather_forecast_city_israel(city: str) -> str:
    """
    Enter an Israeli city name in the weather search field.

    The website is in Hebrew.
    Before calling this tool, convert the city name to Hebrew.
    Example:
    Tel Aviv -> תל אביב
    Jerusalem -> ירושלים
    Haifa -> חיפה
    """

    global page

    print(f"Entering city: {city}")

    search_box = page.locator("#city_search_forecast")

    await search_box.fill(city)

    print("City entered successfully")

    return f"Entered city: {city}"


@mcp.tool()
async def select_weather_forecast_city_israel() -> str:
    """
    Select the first city from the autocomplete list.
    """

    global page

    first_city = page.locator(
        "#city_search_forecastautocomplete-list > div"
    ).first

    await first_city.click()

    return "First city selected"


@mcp.tool()
async def get_weather_forecast_page_content_israel() -> str:
    """
    Read the current weather forecast page content and return it as context for the LLM.
    Call this tool AFTER the city has already been selected via select_weather_forecast_city_israel.
    Does NOT navigate or search again — reads whatever is currently on screen.
    Returns a clean, structured text with the forecast information.
    """

    global page

    # Wait briefly for any dynamic content to settle after city selection
    await asyncio.sleep(1)

    # Extract all visible text from the page body
    raw_text: str = await page.locator("body").inner_text()

    # ── Clean up the raw text ──────────────────────────────────────────────────

    lines = raw_text.splitlines()

    # Known boilerplate / navigation fragments to discard (Hebrew site)
    noise_fragments = [
        "תפריט", "Menu", "עברית", "English", "cookie", "Cookie",
        "פרסומת", "advertisement", "©", "כל הזכויות", "All rights",
        "התחבר", "הרשם", "Sign in", "Register", "Facebook", "Instagram",
        "Twitter", "YouTube", "WhatsApp", "Privacy", "Terms",
        "מדיניות", "תנאי", "צור קשר", "Contact",
    ]

    cleaned_lines: list[str] = []
    prev_blank = False

    for line in lines:
        stripped = line.strip()

        # Skip blank lines that follow another blank line (collapse duplicates)
        if stripped == "":
            if not prev_blank:
                cleaned_lines.append("")
            prev_blank = True
            continue

        prev_blank = False

        # Skip pure-noise lines
        if any(frag in stripped for frag in noise_fragments):
            continue

        # Skip very short lines that are likely UI artefacts (single chars, icons, etc.)
        if len(stripped) <= 2:
            continue

        cleaned_lines.append(stripped)

    # Remove leading/trailing blank lines from the result
    while cleaned_lines and cleaned_lines[0] == "":
        cleaned_lines.pop(0)
    while cleaned_lines and cleaned_lines[-1] == "":
        cleaned_lines.pop()

    cleaned_text = "\n".join(cleaned_lines)

    # ── Format as structured context for the LLM ──────────────────────────────

    structured = (
        "Weather forecast page content:\n"
        "================================\n"
        f"{cleaned_text}\n"
        "================================\n"
        "End of forecast page content."
    )

    await browser.close()

    return structured


def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()

