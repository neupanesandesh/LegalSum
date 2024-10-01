import streamlit as st
import pandas as pd
import json
import re
from docx import Document
from openai import OpenAI
import requests
from bs4 import BeautifulSoup
from browser_detection import browser_detection_engine
from selenium import webdriver
from typing import Optional, Tuple
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.chrome.options import Options as ChromeOptions
from docx.shared import Pt, RGBColor
from docx.oxml.ns import qn
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from selenium.common.exceptions import WebDriverException, TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
import time
from datetime import datetime


client = OpenAI(
    api_key = "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",
)

page_count= None

GPTModelLight = "gpt-4o-mini"
GPTModel = "gpt-4o"

browser_info = browser_detection_engine()
print(f"Browser Info: {browser_info}")  # Debugging line
browser_name = browser_info.get('name', 'none').lower()
print(f"Browser Name: {browser_name}") 


def scrap_web(url):
    # Step 2: Fetch the content of the URL
    try:
        response = requests.get(url, timeout=30)  # Add a timeout to handle long loading pages
        response.raise_for_status()  # Raise an error for bad responses (4xx or 5xx)

        # Step 3: Parse the content using BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')

        # Step 4: Extract all the text content
        text = soup.get_text(separator=' ', strip=True)
        return text
    except requests.exceptions.Timeout:
        print(f"For URL: {url}. Attempting to scrape with Selenium.")
        return scrape_from_selenium(url)
    except requests.exceptions.SSLError:
        print(f"For URL: {url}. Attempting to scrape with Selenium.")
        return scrape_from_selenium(url)
    except requests.exceptions.RequestException as e:
        print(f"For URL: {url}. Error: {e}. Attempting to scrape with Selenium.")
        return scrape_from_selenium(url)

def scrape_from_selenium(url: str, timeout: int = 30) -> Tuple[Optional[str], Optional[str]]:
    driver = None
    try:
        if browser_name in ['chrome','google chrome']:
            options = ChromeOptions()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--window-size=1920x1080')
            options.add_argument('--disable-gpu')
            options.add_argument('--ignore-certificate-errors')
            options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
            driver = webdriver.Chrome(options=options)
        
        elif browser_name in ['edge', 'microsoft edge']:
            options = EdgeOptions()
            options.add_argument('--headless')
            options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
            driver = webdriver.Edge(options=options)
            
        elif browser_name in ['firefox', 'mozilla firefox']:
            options = FirefoxOptions()
            options.add_argument('--headless')
            options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0')
            driver = webdriver.Firefox(options=options)
            
        elif browser_name == 'safari':
            driver = webdriver.Safari()
            
        elif browser_name == 'brave':
            options = ChromeOptions()
            options.binary_location = "/usr/bin/brave-browser"
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
            driver = webdriver.Chrome(options=options)
        else:
            print(f"Unsupported browser: {browser_name}. Defaulting to Chrome.")
            options = ChromeOptions()
            options.add_argument('--headless')
            options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
            driver = webdriver.Chrome(options=options)
        
        driver.get(url)
        WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
        
        # Scroll to load lazy-loaded content
        scroll_page(driver)
        
        content = driver.find_element(By.TAG_NAME, 'body').text
        if not content:
            return None, "No visible text found on the page."
        return content, None

    except TimeoutException:
        print(f"Timeout while trying to fetch URL: {url}")
    except WebDriverException as e:
        print(f"WebDriver error occurred while scraping: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if driver:
            driver.quit()

    return None

def scroll_page(driver):
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height



        
        
def process_row(row):
    if pd.isna(row['B']):  # Skip empty rows
        return None
    
    name_role = row['B'].split(', ', 1)
    name = name_role[0]
    role = name_role[1] if len(name_role) > 1 else ''
    
    date_source = row['D'].split(', ', 1)
    date = date_source[0]
    
    return {
        'name': name,
        'role': role,
        'date': date,
        'link': row['E'],
        'info': row['F']
    }

def newsletter(data):
    # Define the context for the summary
    context = f""" you are a newsletter analyzer. you will be provided with extracted contents of a webpage. your role is to thoroughly analyze the contents of that webpage
    and only focus on the part where some people has quoted their view or their words along with their name that lies in the entire web content.
    After getting those names also get the role of those personnel and collectively store in a quoted section of json.
    Also generate a short background referencing that webcontent in no more than 50-100 words. 
    Here is the web content extracted from the webpage: [{data}]. 
    
    Return the results in a JSON format as shown below:
    
    \u0028
    "newsletter": {{
        "people": [
        \u0028
            "name": "Person 1",
            "quote": "This is the quote by Person 1."
        \u0029,
        \u0028
            "name": "Person 2",
            "quote": "This is the quote by Person 2."
        \u0029,
        .
        .
        .
        ]
    }},
    "background": "This is the background information.",
    "quoted": "Person 1 - Role 1, Person 2 - Role 2"
    \u0029
    """

    # Call the OpenAI API to generate a summary
    response = client.chat.completions.create(
        model=GPTModel,
        temperature=0.0,
        max_tokens=600,
        messages=[
            {"role": "system", "content": context},
            # {"role": "user", "content": data}
        ]
    )
    
    response_content = response.choices[0].message.content
    cleaned_response = response_content.replace('```json\n', "").replace('\n```', "")
    

    # Parse the JSON response
    try:
        structured_data = json.loads(cleaned_response)
    except json.JSONDecodeError as e:
        print("Failed to decode JSON:", e)
        return None
    print(structured_data)
    return structured_data

def create_docx(data_list):
    doc = Document()
    
    # Add header "DEA Quotes" with increased font size and centered
    header = doc.add_heading('DEA Quotes', level=1)
    run_header = header.runs[0]
    run_header.font.size = Pt(40)  # Increase font size by 10 times
    run_header.font.name = 'Arial'
    run_header._element.rPr.rFonts.set(qn('w:eastAsia'), 'Arial')
    header.alignment = 1  # Center alignment

    # Add today's date
    doc.add_paragraph(datetime.now().strftime("%B %d, %Y"))

    for item in data_list:
        # Add the topic to the document, bold only the name "Topic"
        topic = item['info']
        p_topic = doc.add_paragraph()
        run_topic_label = p_topic.add_run("Topic: ")
        run_topic_label.bold = True
        run_topic_content = p_topic.add_run(topic)

        # Add quoted information, bold only the name "Quoted"
        quoted = item.get('quoted', 'No quotes available')
        p_quoted = doc.add_paragraph()
        run_quoted_label = p_quoted.add_run("Quoted: ")
        run_quoted_label.bold = True
        run_quoted_content = p_quoted.add_run(quoted)

        # Add background information, bold only the name "Background"
        background = item.get('background', 'No background available')
        p_background = doc.add_paragraph()
        run_background_label = p_background.add_run("Background: ")
        run_background_label.bold = True
        run_background_content = p_background.add_run(background)

        # Add names and their quotes
        people_quotes = item.get('people_quotes', [])
        if not people_quotes:
            doc.add_paragraph("No quotes found in people_quotes.")
        else:
            for entry in people_quotes:
                name = entry.get('name', 'Unknown')
                quote = entry.get('quote', 'No quote available')
                # Add name without bold
                p_name = doc.add_paragraph(name)
                # Add quote in italics and bold
                p_quote = doc.add_paragraph()
                run_quote = p_quote.add_run(f"Quote: {quote}")
                run_quote.bold = True
                run_quote.italic = True

        # Add date
        date = item.get('date', 'No date available')
        doc.add_paragraph(f"Date: {date}")

        # Add link as a simple hyperlink
        link = item.get('link', 'No link available')
        p_link = doc.add_paragraph()
        run_link = p_link.add_run(link)
        run_link.font.color.rgb = RGBColor(0, 0, 255)  # Blue color for hyperlink
        run_link.font.underline = True

        doc.add_paragraph("---")  # Separator between entries

    # Save the document to a file
    doc_path = "newsletter_output.docx"
    doc.save(doc_path)

    return doc_path