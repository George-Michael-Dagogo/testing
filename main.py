from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time

def setup_chrome_driver():
    """Setup Chrome driver with options suitable for Gitpod"""
    chrome_options = Options()
    
    # Essential options for headless environment
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--remote-debugging-port=9222')
    
    # Additional stability options
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--disable-web-security')
    chrome_options.add_argument('--disable-features=VizDisplayCompositor')
    chrome_options.add_argument('--window-size=1920,1080')
    
    # User agent
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36')
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        return driver
    except Exception as e:
        print(f"Error setting up Chrome driver: {e}")
        return None

def scrape_premium_times_search(query="rape"):
    """Scrape Premium Times search results"""
    driver = setup_chrome_driver()
    if not driver:
        return []
    
    try:
        # Navigate to search page
        url = f'https://www.premiumtimesng.com/search_gcse?q={query}'
        print(f"Navigating to: {url}")
        driver.get(url)
        
        # Wait for page to load
        time.sleep(5)
        
        # Wait for search results to appear
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".gs-webResult, .gsc-webResult"))
            )
        except:
            print("Search results didn't load in time, continuing anyway...")
        
        # Get page source and parse with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Try multiple selectors for search results
        selectors = [
            '.gs-webResult',
            '.gsc-webResult', 
            '.gs-result',
            '.gsc-result',
            'div[class*="webResult"]',
            'div[class*="result"]'
        ]
        
        news_cards = []
        for selector in selectors:
            cards = soup.select(selector)
            if cards:
                news_cards = cards
                print(f"Found {len(cards)} results with selector: {selector}")
                break
        
        if not news_cards:
            print("No results found with any selector. Checking page content...")
            print("Page title:", soup.title.text if soup.title else "No title")
            print("Body length:", len(soup.body.text) if soup.body else 0)
            
            # Debug: Print some div classes to see what's available
            divs_with_classes = soup.find_all('div', class_=True)[:10]
            for div in divs_with_classes:
                print(f"Div class: {div.get('class')}")
        
        return news_cards
        
    except Exception as e:
        print(f"Error during scraping: {e}")
        return []
    
    finally:
        driver.quit()

def extract_article_info(news_cards):
    """Extract information from news cards"""
    articles = []
    
    for card in news_cards:
        try:
            # Try to find title
            title_elem = card.find('h3') or card.find('a') or card.find(class_='gs-title')
            title = title_elem.get_text().strip() if title_elem else "No title"
            
            # Try to find link
            link_elem = card.find('a')
            link = link_elem.get('href') if link_elem else None
            
            # Try to find snippet/description
            snippet_elem = card.find(class_='gs-snippet') or card.find('p')
            snippet = snippet_elem.get_text().strip() if snippet_elem else "No description"
            
            articles.append({
                'title': title,
                'link': link,
                'snippet': snippet
            })
            
        except Exception as e:
            print(f"Error extracting info from card: {e}")
            continue
    
    return articles

# Main execution
if __name__ == "__main__":
    print("Starting Premium Times scraping...")
    
    # Scrape the search results
    news_cards = scrape_premium_times_search("rape")
    
    if news_cards:
        print(f"\nFound {len(news_cards)} news articles")
        
        # Extract article information
        articles = extract_article_info(news_cards)
        
        # Print results
        for i, article in enumerate(articles, 1):
            print(f"\n--- Article {i} ---")
            print(f"Title: {article['title']}")
            print(f"Link: {article['link']}")
            print(f"Snippet: {article['snippet'][:200]}...")
    else:
        print("No articles found")