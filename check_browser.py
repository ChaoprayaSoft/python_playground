import asyncio
from playwright.async_api import async_playwright
import os

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        page.on("console", lambda msg: print(f"CONSOLE {msg.type}: {msg.text}"))
        page.on("pageerror", lambda err: print(f"PAGE ERROR: {err}"))
        await page.add_init_script("localStorage.setItem('pyplay_user', JSON.stringify({email: 'test@gmail.com'}));")
        
        url = "file:///" + os.path.abspath('datavis_capstone.html').replace('\\', '/')
        await page.goto(url, wait_until="networkidle")
        await page.wait_for_timeout(500)
        print("Clicking Capstone 2 pill...")
        await page.evaluate("currentLessonIndex = 1; loadLesson(1)")
        await page.wait_for_timeout(500)
        
        # Test Capstone 2 solution
        solution_code = "import pandas as pd\\nimport matplotlib.pyplot as plt\\ndf = pd.read_csv('cohorts.csv')\\ndf['Revenue'] = df['Price'] * df['Qty']\\ncohort_rev = df.groupby('Cohort').sum()\\nplt.bar(cohort_rev['Cohort'], cohort_rev['Revenue'])\\nplt.title('Cohort Revenue')\\nplt.show()"
        await page.evaluate(f"editor.setValue(`{solution_code}`)")
        
        print("Clicking RUN...")
        await page.locator('#run-btn').click()
        await page.wait_for_timeout(2000)
        
        btn_text = await page.locator('#run-btn').inner_text()
        print(f"Run Button Text: {btn_text.encode('ascii', 'ignore').decode('ascii')}")
        
        console_text = await page.locator('#terminal-console').inner_text()
        print(f"Terminal Output: {console_text.encode('ascii', 'ignore').decode('ascii')}")
        await browser.close()

asyncio.run(main())
