import pandas as pd
import os
import json
from docx import Document
from openai import OpenAI
from docx.shared import Pt, RGBColor
from docx.oxml.ns import qn
from selenium.webdriver.support import expected_conditions as EC
import time
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()
OPENAI_API_KEY= os.getenv("OPENAI_API_KEY")

client = OpenAI(
    api_key = OPENAI_API_KEY,
)

page_count= None

GPTModelLight = "gpt-4o-mini"
GPTModel = "gpt-4o"



def format_date_and_info(date_str):
    try:
        date_part, info_part = date_str.split("; ", 1)
        # Parse the date with the format MM/DD/YY
        date_obj = datetime.strptime(date_part, "%m/%d/%y")
        # Format the date as 'Month Day, Year'
        formatted_date = date_obj.strftime("%B %d, %Y")  # For example: 'September 07, 2024'
        
        # Extract the location part within parentheses
        if "(" in info_part and ")" in info_part:
            info_main, location = info_part.split("(", 1)
            location = location.rstrip(")")
            formatted_info = f"{info_main.strip()} ({location.strip()})"
        else:
            formatted_info = info_part.strip()
        
        return f"{formatted_date}; {formatted_info}"
    except ValueError as e:
        return date_str
    
    except Exception as e:
        # Handle any error that occurs during date parsing or formatting
        # print(f"Error formatting date: {e}")
        return date_str

        
def process_row(row):
    if pd.isna(row['B']):  # Skip empty rows
        return None
    
    name_role = row['B'].split(', ', 1)
    name = name_role[0]
    role = name_role[1] if len(name_role) > 1 else ''
    branch_head = row['C']
    date_source = row['D'].split(', ', 1)
    date = date_source[0]
    
    return {
        'name': name,
        'role': role,
        'branch_head':branch_head,
        'date': date,
        'link': row['E'],
        'info': row['F']
    }

def newsletter(data):
    # Define the context for the summary
    context = f""" you are a newsletter analyzer. you will be provided with extracted contents of a webpage. your role is to thoroughly analyze the contents of that webpage
    and only focus on the part where some people has quoted their view or their words along with their name that lies in the entire web content.
    After getting those names also get the role of those personnel and collectively store in a "quoted" section of json.
    Here is the web content extracted from the webpage: {data}. 
    
    Return the results in a proper JSON format directly like this:
    
    {{
        "newsletter": \u0028
            "people": [
            \u0028
                "name": "Person 1",
                "quote": [
                "Quote by person 1",
                "another quote by same person (if any)"
                ]
            \u0029,
            \u0028
                "name": "Person 2",
                "quote": [
                "Quote by person 2",
                "another quote by same person (if any)"
                ]
            \u0029
            // more if any...
            ]
        \u0029,
        "quoted": "Person 1 - Role 1, Person 2 - Role 2, Person 3 - Role 3,......"
    }}

    """

    # Call the OpenAI API to generate a summary
    response = client.chat.completions.create(
        model=GPTModel,
        temperature=0.3,
        max_tokens=1000,
        messages=[
            {"role": "system", "content": context},
            # {"role": "user", "content": data}
        ]
    )
    
    response_content = response.choices[0].message.content
    print({"response_content":response_content})
    cleaned_response = response_content.replace('```json\n', "").replace('\n```', "")
    print({"cleaned":cleaned_response})
    # Parse the JSON response
    try:
        structured_data = json.loads(cleaned_response)
    except json.JSONDecodeError as e:
        print("Failed to decode JSON:", e)
        return None
    print(structured_data)
    return structured_data


def get_topic_newsletter(data):
    context = f"""
    I have an article related to drugs. Please generate a topic following this structure: [Main Subject]: [Key Elements]: [Location/Context].
    Here is an example :
    **Topic:** "Xylazine: Danger Warning: Pennsylvania"
    **Article Summary:** "Pennsylvania's Department of Health Secretary Bogen unveils a new wound care initiative aimed at addressing injuries associated with the use of xylazine, an emerging and dangerous drug."
    
    Here is the article summary: [{data}]
    
    Directly return topic in str in json format:
    {{
    "topic": "topic related to article."
    }}
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


def get_newsletter_background(data):
    context = f"""  you will be provided with extracted contents of a webpage. your role is to return first two paragraph as background with very little 
    or no modification at all.
    here is the web content:({data})
    Return background in json format directly:
    {{
    "background": "First two paragraphs of the web content for background."
    }}

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
    # Define the order of major heads
    branch_order = {
        'E': 'EXECUTIVE BRANCH',
        'L': 'LEGISLATIVE BRANCH',
        'S': 'STATE OFFICIALS',
        'O': 'OTHERS'
    }

    # Sort data_list based on branch_head order
    data_list.sort(key=lambda x: list(branch_order.keys()).index(x['branch_head']))

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

    for branch, branch_name in branch_order.items():
        # Filter items by branch_head
        branch_items = [item for item in data_list if item['branch_head'] == branch]

        if branch_items:
            # Add branch name as a heading
            branch_heading = doc.add_heading(level=2)
            run_branch_heading = branch_heading.add_run(branch_name)
            run_branch_heading.bold = True
            run_branch_heading.font.size = Pt(16)

            for item in branch_items:
                # Add the topic to the document, bold only the name "Topic"
                topic = item['topic']
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
                        p_name = doc.add_paragraph()
                        run_name = p_name.add_run(name)
                        run_name.bold = True  # Make the name bold

                        # Add quote in italics
                        p_quote = doc.add_paragraph()
                        run_quote = p_quote.add_run("Quote \n")
                        run_quote.bold = True  # Make the quote italic
                        run_quotes = p_quote.add_run(quote)
                        run_quotes.italic = True

                # Add date
                date = item.get('date', 'No date available')
                doc.add_paragraph(f" {date}")

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
