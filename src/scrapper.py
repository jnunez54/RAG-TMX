import requests

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

from config.config import URL
from config.logger_config import setup_logger

logger = setup_logger(__name__, f"logs/{__name__}.log")

class Scrapper():
    def __init__(self):
        self.urls = []
        self.content = {}
        
    def get_urls(self):
        """
        Get the urls of the processes.
        """
        logger.info("Getting the urls of the processes")
        with sync_playwright() as p:
            # Open the browser
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            
            # Load the page
            page.goto(URL)
            html = page.content()
            soup = BeautifulSoup(html, "html.parser")
            
            # Iterate over the buttons
            menu_buttons = soup.find_all("button", class_ = "menu")
            for button in menu_buttons:
                div = button.find("div", class_="justify-content-start")
                if div:
                    category = div.get_text()
                    if category == "Aguascalientes": # Break at State buttons
                        break
                    flag = True
                    try:
                        # Load the content by clicking the button
                        page.click(f"button:has-text('{category}')", timeout=1000)
                    except:
                        logger.error(f"Error clicking the button: {category}")
                        flag = False
                        continue
                    
                    if flag:
                        # Get the content
                        html = page.content()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        # Find the hrefs of the processes
                        items = soup.find_all("a", href=True)
                        for item in items:
                            p = item.find("p", class_ = "mx-auto")
                            name = item.get_text()
                            href = item.get("href")
                            if p and "www.gob" in href and "Consulta requisitos" != name:
                                process = {"name": name, "href": href}
                                if process not in self.urls:
                                    self.urls.append(process)
                                    logger.info(f"Process found: {name}")
            page.close()
            browser.close()
            
    def get_content(self):
        """
        Extract the content of the processes.
        """
        if not self.urls:
            self.get_urls()
        
        for url in self.urls:
            response = requests.get(url["href"])
            soup = BeautifulSoup(response.text, "html.parser")
            paragraphs = soup.find_all("p")
            tables = soup.find_all("table")
            process_name = url["name"]
            self.content[process_name] = {"url": url["href"], "segments": []}
            
            for p in paragraphs:
                text = p.get_text()
                if text:
                 self.content[process_name]["segments"].append(text)
                
            for table in tables:
                table_name = " ".join(table.get("class"))
                table_text = table.get_text().strip().replace("\n", " ")
                text = f"{table_name}: {table_text}"
                self.content[process_name]["segments"].append(text)
                