#Import Dependencies
from splinter import Browser
from bs4 import BeautifulSoup
import pandas as pd
import datetime as dt
import time

#Define scrape all and initiate headless driver for deployment
def scrape_all():
    browser = Browser("chrome", executable_path='chromedriver', headless=True)

    #Set news title and paragraph variables
    news_title, news_paragraph = mars_news(browser)

    #Run all scraping functions and store results in dictionary
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "last_modified": dt.datetime.now(),
        "mars_hemispheres": mars_hemispheres(browser)
    }

    browser.quit()
    return data


# Set the executable path and initialize the chrome browser in splinter
executable_path = {'executable_path': '/usr/local/bin/chromedriver'}
browser = Browser('chrome', **executable_path)

def mars_news(browser):

    #Visit the mars nasa news site
    url = 'https://mars.nasa.gov/news/'
    browser.visit(url)

    #Optional delay for loading the page
    browser.is_element_present_by_css("ul.item_list li.slide", wait_time=1)


    #Set up the html parser
    html = browser.html
    news_soup = BeautifulSoup(html, 'html.parser')

    # Add try/except for error handling
    try:
        slide_elem = news_soup.select_one("ul.item_list li.slide")

        #Use the parent element to find the first 'a' tag and save it as 'news_title'
        news_title = slide_elem.find("div", class_="content_title").get_text()

        #USe the parent element to find the paragraph text
        news_p = slide_elem.find("div", class_="article_teaser_body").get_text()

    except AttributeError:
        return None, None

    return news_title, news_p


### Featured Images
def featured_image(browser):

    # Visit URL
    url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(url)


    # Find and click the full image button
    full_image_elem = browser.find_by_id('full_image')
    full_image_elem.click()

    # Find the more info button and click that
    browser.is_element_present_by_text('more info', wait_time=1)
    more_info_elem = browser.find_link_by_partial_text('more info')
    more_info_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = BeautifulSoup(html, 'html.parser')

    #Add error handling for Attribute Error
    try:
        # Find the relative image url
        img_url_rel = img_soup.select_one('figure.lede a img').get("src")

    except AttributeError:
        return None

    img_url = f'https://www.jpl.nasa.gov{img_url_rel}'

    return img_url

### Scraping the Table
def mars_facts():
    # Add try/except for error handling
    try:
        # Use 'read_html' to scrape the facts table into a dataframe
        df = pd.read_html('http://space-facts.com/mars/')[0]

    except BaseException:
        return None
    
    # Assign columns and set index of dataframe
    df.columns=['Description', 'Mars']
    df.set_index('Description', inplace=True)
    
    # Convert dataframe into HTML format, add bootstrap
    return df.to_html()

def mars_hemispheres(browser):

    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url)

    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')

    hemispheres = soup.find_all('div', class_='description')

    #Iterate through the various hemispheres
    for hemisphere in hemispheres:
    
        #Sort through the html code to pull the title and href
        link = hemisphere.find('a')
        href = link['href']
        h3 = link.find('h3')
        hemi_string = h3.text
        title = hemi_string.replace(' Enhanced', '')
        
        #Create the url for each hemi and visit the link
        hemi_url = f'https://astrogeology.usgs.gov{href}'
        browser.visit(hemi_url)
        
        html = browser.html
        soup = BeautifulSoup(html, 'html.parser')
        
        #Use select one to pick the first full sized image and get the src
        mars_img_ending = soup.select_one('img.wide-image').get('src')
        
        #Attach the src to the base url for the full sized image
        hemi_img_url = f'https://astrogeology.usgs.gov{mars_img_ending}'
        
        #Create a dictionary for each hemisphere that has img_url and title
        hemi_image = {"image": hemi_img_url, "title": title}
        
        return hemi_image
        

browser.quit()

if __name__ == "__main__":
    # If running as script, print scraped data
    print(scrape_all())

