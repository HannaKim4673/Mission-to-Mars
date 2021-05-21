# Imports Splinter and BeautifulSoup
from splinter import Browser
from bs4 import BeautifulSoup as soup
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import datetime as dt
import re

# Function establishes communication between code and MongoDB
def scrape_all():
    # Initiates headless driver for deployment
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=True)

    # Sets news title and paragraph variables
    news_title, news_paragraph = mars_news(browser)

    # Runs all scraping functions and stores results in dictionary
    data = {
          "news_title": news_title,
          "news_paragraph": news_paragraph,
          "featured_image": featured_image(browser),
          "facts": mars_facts(),
          "last_modified": dt.datetime.now(),
          "hemispheres": mars_hemispheres(browser)
    }

    # Stops webdriver and returns data
    browser.quit()
    return data

# Function scrapes news title and paragraph summary
def mars_news(browser):
    # Visits the mars nasa news site
    url = 'https://redplanetscience.com'
    browser.visit(url)
    # Optional delay for loading the page
    browser.is_element_present_by_css('div.list_text', wait_time=1)

    # Sets up html parser
    html = browser.html
    news_soup = soup(html, 'html.parser')

    # Adds try/except for error handling
    try:
        slide_elem = news_soup.select_one('div.list_text')
        # Uses the parent element to find the first 'a' tag and save it as 'news_title'
        news_title = slide_elem.find('div', class_='content_title').get_text()
        # Uses the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_='article_teaser_body').get_text()
    except AttributeError:
        return None, None

    return news_title, news_p

# ### Featured Images

# Function scrapes featured image
def featured_image(browser):
    # Visits URL
    url = 'https://spaceimages-mars.com'
    browser.visit(url)

    # Finds and clicks the full image button
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()

    # Parses the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    # Adds try/except for error handling
    try:
        # finds the relative image url
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')
    except AttributeError:
        return None

    # Uses the base URL to create an absolute URL
    img_url = f'https://spaceimages-mars.com/{img_url_rel}'

    return img_url

# ### Mars Facts Table

# Function scrapes facts table
def mars_facts():
    # Adds try/except for error handling
    try:
      # uses 'read_html" to scrape the facts table into a dataframe
      df = pd.read_html('https://galaxyfacts-mars.com')[0]
    except BaseException:
      return None
    
    # Scrapes entire table from website
    df.columns=['description', 'Mars', 'Earth']
    df.set_index('description', inplace=True)

    # Converts dataframe into html-ready code and adds bootstrap
    return df.to_html()

# Function scrapes image urls and titles for mars's hemispheres
def mars_hemispheres(browser):
    # 1. Use browser to visit the URL 
    url = 'https://marshemispheres.com/'

    browser.visit(url)

    # 2. Create a list to hold the images and titles.
    hemisphere_image_urls = []

    # 3. Write code to retrieve the image urls and titles for each hemisphere.
    # List of locations of link tags
    indices = [1, 3, 5, 7]
    for i in indices:
        # Finds and clicks on the hemisphere link
        hemisphere_link = browser.find_by_tag('a.itemLink.product-item')[i]
        hemisphere_link.click()
        # Holds image urls and titles
        hemispheres = {}
        # Parses the resulting html with soup
        html = browser.html
        img_soup = soup(html, 'html.parser')
        # Finds the full-resolution image url
        # Note: info on how to get specific href using regular expressions was found at https://stackoverflow.com/questions/7732694/find-specific-link-w-beautifulsoup
        img_url_rel = img_soup.find('a', href=re.compile('jpg')).get('href')
        # Uses the base URL to create an absolute URL
        img_url = f'https://marshemispheres.com/{img_url_rel}'
        # Finds title 
        title = img_soup.find('h2', class_='title').get_text()
        # Adds image url and title to hemispheres dictionary
        hemispheres['img_url'] = img_url
        hemispheres['title'] = title
        # Adds hemispheres dictionary to list in step 2
        hemisphere_image_urls.append(hemispheres)
        # Navigates back to beginning of browser
        browser.back()

    return hemisphere_image_urls

# Lets Flask konw that script is complete and ready
if __name__ == "__main__":
    # If running as script, print scraped data
    print(scrape_all())