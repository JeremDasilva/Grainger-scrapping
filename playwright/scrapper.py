from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

def parse_item(html_content):
    results = {}
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Extract category title
    category_title_element = soup.find("p", {"data-category-title": "true"})
    if category_title_element:
        results['category_title'] = category_title_element.text.strip()
    
    return results

def main():
    url = "https://www.grainger.com/category/lighting/light-bulbs-lamps/light-bulb-lamp-accessories-changers?categoryIndex=9"
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        page.goto(url, wait_until="domcontentloaded")
                
        html_content = page.content()
        title = parse_item(html_content)
        
        if title:
            print("Title:", title)
        
        # Assurez-vous de fermer le navigateur après avoir terminé toutes les opérations
        browser.close()

if __name__ == "__main__":
    main()
