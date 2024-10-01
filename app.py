import streamlit as st
from nameparser import HumanName
from openai import OpenAI
import re
import os
import pandas as pd
import pdfplumber
import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth
import nltk
from nltk.tokenize import word_tokenize
from nltk.data import find
import docx2txt
nltk.download('punkt')
from routes import process_row,scrap_web,newsletter,create_docx




def ensure_nltk_data():
    """Check if required NLTK data is present, and download it if necessary."""
    try:
        # Check if 'punkt' tokenizer data is available
        find('tokenizers/punkt')
    except LookupError:
        # Data is not available, so download it
        print("Downloading NLTK 'punkt' data...")
        nltk.download('punkt')
 
# Set your OpenAI API key here (use environment variables or Streamlit's secrets for better security)
client = OpenAI(
    api_key = "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",
)

page_count= None

GPTModelLight = "gpt-4o-mini"
GPTModel = "gpt-4o"

# Complete abbreviation dictionary
abbrev_dict = {
"Academy": "Acad.",
    "Academies": "Acads.",
    "Administration": "Admin.",
    "Administrations": "Admins.",
    "Administrative": "Admin.",
    "Administrator": "Adm'r",
    "Administrators": "Adm'rs",
    "Administratrix": "Adm'x",
    "Administratrixes": "Adm'xs",
    "America": "Am.",
    "Americas": "Ams.",
    "American": "Am.",
    "Americans": "Ams.",
    "and": "&",
    "Associate": "Assoc.",
    "Associates": "Assocs.",
    "Association": "Ass'n",
    "Associations": "Ass'ns",
    "Atlantic": "Atl.",
    "Atlantics": "Atls.",
    "Authority": "Auth.",
    "Authorities": "Auths.",
    "Automobile": "Auto.",
    "Automobiles": "Autos.",
    "Automotive": "Auto.",
    "Automotives": "Autos.",
    "Avenue": "Ave.",
    "Avenues": "Aves.",
    "Board": "Bd.",
    "Boards": "Bds.",
    "Broadcasting": "Broad.",
    "Broadcastings": "Broads.",
    "Brotherhood": "Bhd.",
    "Brotherhoods": "Bhds.",
    "Brothers": "Bros.",
    "Building": "Bldg.",
    "Buildings": "Bldgs.",
    "Business": "Bus.",
    "Businesses": "Bus.",
    "Casualty": "Cas.",
    "Casualties": "Cas.",
    "Center": "Ctr.",
    "Centers": "Ctrs.",
    "Centre": "Ctr.",
    "Centres": "Ctrs.",
    "Central": "Cent.",
    "Centrals": "Cents.",
    "Chemical": "Chem.",
    "Chemicals": "Chems.",
    "Coalition": "Coal.",
    "Coalitions": "Coals.",
    "College": "Coll.",
    "Colleges": "Colls.",
    "Commission": "Comm'n",
    "Commissions": "Comm'ns",
    "Commissioner": "Comm'r",
    "Commissioners": "Comm'rs",
    "Committee": "Comm.",
    "Committees": "Comms.",
    "Communication": "Commc'n",
    "Communications": "Commc'ns",
    "Community": "Cmty.",
    "Communities": "Cmtys.",
    "Company": "Co.",
    "Companies": "Cos.",
    "Compensation": "Comp.",
    "Compensations": "Comps.",
    "Condominium": "Condo.",
    "Condominiums": "Condos.",
    "Congress": "Cong.",
    "Congresses": "Congs.",
    "Congressional": "Cong.",
    "Consolidated": "Consol.",
    "Construction": "Constr.",
    "Constructions": "Constrs.",
    "Continental": "Cont'l",
    "Continentals": "Cont'ls",
    "Cooperative": "Coop.",
    "Cooperatives": "Coops.",
    "Corporation": "Corp.",
    "Corporations": "Corps.",
    "Correction": "Corr.",
    "Corrections": "Corrs.",
    "Correctional": "Corr.",
    "Defense": "Def.",
    "Defenses": "Defs.",
    "Department": "Dep't",
    "Departments": "Dep'ts",
    "Detention": "Det.",
    "Detentions": "Dets.",
    "Development": "Dev.",
    "Developments": "Devs.",
    "Director": "Dir.",
    "Directors": "Dirs.",
    "Distributor": "Distrib.",
    "Distributors": "Distribs.",
    "Distributing": "Distrib.",
    "District": "Dist.",
    "Districts": "Dists.",
    "Division": "Div.",
    "Divisions": "Divs.",
    "East": "E.",
    "Eastern": "E.",
    "Economic": "Econ.",
    "Economics": "Econ.",
    "Economical": "Econ.",
    "Economy": "Econ.",
    "Economies": "Econs.",
    "Education": "Educ.",
    "Educations": "Educs.",
    "Educational": "Educ.",
    "Electric": "Elec.",
    "Electrical": "Elec.",
    "Electricity": "Elec.",
    "Electronic": "Elec.",
    "Electronics": "Elecs.",
    "Engineer": "Eng'r",
    "Engineers": "Eng'rs",
    "Engineering": "Eng'g",
    "Engineerings": "Eng'gs",
    "Enterprise": "Enter.",
    "Enterprises": "Enters.",
    "Entertainment": "Ent.",
    "Entertainments": "Ents.",
    "Environment": "Env't",
    "Environments": "Env'ts",
    "Environmental": "Envtl.",
    "Equality": "Equal.",
    "Equalities": "Equals.",
    "Equipment": "Equip.",
    "Equipments": "Equips.",
    "Examiner": "Exam'r",
    "Examiners": "Exam'rs",
    "Exchange": "Exch.",
    "Exchanges": "Exchs.",
    "Executor": "Ex'r",
    "Executors": "Ex'rs",
    "Executrix": "Ex'x",
    "Executrixes": "Ex'xs",
    "Export": "Exp.",
    "Exports": "Exps.",
    "Exporter": "Exp.",
    "Exporters": "Exps.",
    "Exportation": "Exp.",
    "Exportations": "Exps.",
    "Federal": "Fed.",
    "Federals": "Feds.",
    "Federation": "Fed'n",
    "Federations": "Fed'ns",
    "Fidelity": "Fid.",
    "Fidelities": "Fids.",
    "Finance": "Fin.",
    "Finances": "Fins.",
    "Financial": "Fin.",
    "Financing": "Fin.",
    "Foundation": "Found.",
    "Foundations": "Founds.",
    "General": "Gen.",
    "Generals": "Gens.",
    "Government": "Gov't",
    "Governments": "Gov'ts",
    "Guaranty": "Guar.",
    "Guaranties": "Guars.",
    "Hospital": "Hosp.",
    "Hospitals": "Hosps.",
    "Housing": "Hous.",
    "Housings": "Hous.",
    "Import": "Imp.",
    "Imports": "Imps.",
    "Importer": "Imp.",
    "Importers": "Imps.",
    "Importation": "Imp.",
    "Importations": "Imps.",
    "Incorporated": "Inc.",
    "Indemnity": "Indem.",
    "Indemnities": "Indems.",
    "Independent": "Indep.",
    "Independents": "Indeps.",
    "Industry": "Indus.",
    "Industries": "Indus.",
    "Industrial": "Indus.",
    "Information": "Info.",
    "Informations": "Infos.",
    "Institute": "Inst.",
    "Institutes": "Insts.",
    "Institution": "Inst.",
    "Institutions": "Insts.",
    "Insurance": "Ins.",
    "Insurances": "Ins.",
    "International": "Int'l",
    "Internationals": "Int'ls",
    "Investment": "Inv.",
    "Investments": "Invs.",
    "Laboratory": "Lab.",
    "Laboratories": "Labs.",
    "Liability": "Liab.",
    "Liabilities": "Liabs.",
    "Limited": "Ltd.",
    "Limiteds": "Ltds.",
    "Litigation": "Litig.",
    "Litigations": "Litigs.",
    "Machine": "Mach.",
    "Machines": "Machs.",
    "Machinery": "Mach.",
    "Machineries": "Machs.",
    "Maintenance": "Maint.",
    "Maintenances": "Maints.",
    "Management": "Mgmt.",
    "Managements": "Mgmts.",
    "Manufacturer": "Mfr.",
    "Manufacturers": "Mfrs.",
    "Manufacturing": "Mfg.",
    "Manufacturings": "Mfgs.",
    "Maritime": "Mar.",
    "Maritimes": "Mars.",
    "Market": "Mkt.",
    "Markets": "Mkts.",
    "Marketing": "Mktg.",
    "Marketings": "Mktgs.",
    "Mechanical": "Mech.",
    "Mechanicals": "Mechs.",
    "Medical": "Med.",
    "Medicals": "Meds.",
    "Medicine": "Med.",
    "Medicines": "Meds.",
    "Memorial": "Mem'l",
    "Memorials": "Mem'ls",
    "Merchant": "Merch.",
    "Merchants": "Merchs.",
    "Merchandise": "Merch.",
    "Merchandising": "Merch.",
    "Metropolitan": "Metro.",
    "Metropolitans": "Metros.",
    "Municipal": "Mun.",
    "Municipals": "Muns.",
    "Mutual": "Mut.",
    "Mutuals": "Muts.",
    "National": "Nat'l",
    "Nationals": "Nat'ls",
    "North": "N.",
    "Northern": "N.",
    "Northeast": "Ne.",
    "Northeastern": "Ne.",
    "Northwest": "Nw.",
    "Northwestern": "Nw.",
    "Number": "No.",
    "Numbers": "Nos.",
    "Organization": "Org.",
    "Organizations": "Orgs.",
    "Organizing": "Org.",
    "Pacific": "Pac.",
    "Pacifics": "Pacs.",
    "Partnership": "P'ship",
    "Partnerships": "P'ships",
    "Personal": "Pers.",
    "Personnel": "Pers.",
    "Pharmaceutics": "Pharm.",
    "Pharmaceutical": "Pharm.",
    "Pharmaceuticals": "Pharms.",
    "Preserve": "Pres.",
    "Preserves": "Pres.",
    "Preservation": "Pres.",
    "Preservations": "Pres.",
    "Probation": "Prob.",
    "Probations": "Probs.",
    "Product": "Prod.",
    "Products": "Prods.",
    "Production": "Prod.",
    "Productions": "Prods.",
    "Professional": "Prof'l",
    "Professionals": "Prof'ls",
    "Property": "Prop.",
    "Properties": "Props.",
    "Protection": "Prot.",
    "Protections": "Prots.",
    "Public": "Pub.",
    "Publics": "Pubs.",
    "Publication": "Publ'n",
    "Publications": "Publ'ns",
    "Publishing": "Publ'g",
    "Publishings": "Publ'gs",
    "Railroad": "R.R.",
    "Railroads": "R.Rs.",
    "Railway": "Ry.",
    "Railways": "Rys.",
    "Refining": "Ref.",
    "Refinings": "Refs.",
    "Regional": "Reg'l",
    "Regionals": "Reg'ls",
    "Rehabilitation": "Rehab.",
    "Rehabilitations": "Rehabs.",
    "Reproduction": "Reprod.",
    "Reproductions": "Reprods.",
    "Reproductive": "Reprod.",
    "Resource": "Res.",
    "Resources": "Res.",
    "Restaurant": "Rest.",
    "Restaurants": "Rests.",
    "Retirement": "Ret.",
    "Retirements": "Rets.",
    "Road": "Rd.",
    "Roads": "Rds.",
    "Savings": "Sav.",
    "School": "Sch.",
    "Schools": "Schs.",
    "Science": "Sci.",
    "Sciences": "Scis.",
    "Secretary": "Sec'y",
    "Secretaries": "Sec'ys",
    "Security": "Sec.",
    "Securities": "Secs.",
    "Service": "Serv.",
    "Services": "Servs.",
    "Shareholder": "S'holder",
    "Shareholders": "S'holders",
    "Social": "Soc.",
    "Socials": "Socs.",
    "Society": "Soc'y",
    "Societies": "Soc'ys",
    "South": "S.",
    "Southern": "S.",
    "Southwest": "Sw.",
    "Southwestern": "Sw.",
    "Steamship": "S.S.",
    "Steamships": "S.S.",
    "Street": "St.",
    "Streets": "Sts.",
    "Subcommittee": "Subcomm.",
    "Subcommittees": "Subcomms.",
    "Surety": "Sur.",
    "Sureties": "Surs.",
    "System": "Sys.",
    "Systems": "Sys.",
    "Technology": "Tech.",
    "Technologies": "Techs.",
    "Telecommunication": "Telecomm.",
    "Telecommunications": "Telecomm.",
    "Telephone": "Tel.",
    "Telephones": "Tels.",
    "Telegraph": "Tel.",
    "Telegraphs": "Tels.",
    "Temporary": "Temp.",
    "Temporaries": "Temps.",
    "Township": "Twp.",
    "Townships": "Twps.",
    "Transcontinental": "Transcon.",
    "Transcontinentals": "Transcons.",
    "Transport": "Transp.",
    "Transports": "Transps.",
    "Transportation": "Transp.",
    "Transportations": "Transps.",
    "Trustee": "Tr.",
    "Trustees": "Trs.",
    "Turnpike": "Tpk.",
    "Turnpikes": "Tpks.",
    "Uniform": "Unif.",
    "Uniforms": "Unifs.",
    "University": "Univ.",
    "Universities": "Univs.",
    "Utility": "Util.",
    "Utilities": "Utils.",
    "United States": "U.S.",
    "United States of America": "U.S.",
    "Village": "Vill.",
    "Villages": "Vills.",
    "West": "W.",
    "Western": "W."
}


def extract_first_two_pages(text):
    lines = text.split('\n')
    lines_per_page = 70
    first_two_pages = lines[:lines_per_page*2]

    return '\n'.join(first_two_pages)

def extract_text_from_pdf(pdf_file):
    all_text = ""
    with pdfplumber.open(pdf_file) as pdf:
        for page_num, page in enumerate(pdf.pages):
            page_text = page.extract_text()
            header_text = page.extract_text(x_tolerance=2, y_tolerance=2, layout=True).split('\n')[0] if page_text else ""
            
            if page_num == 0:
                all_text += f"Header: {header_text.strip()}{page_text.strip()}\n\n"

            else:
                all_text += f"Header: {header_text.strip()}{page_text.strip()}\n\n"

    
    return all_text.strip()


def extract_text_from_docx(docx_file):
    """
    Extract text from a DOCX file, removing duplicate headers.

    Parameters:
        docx_file (str): Path to the DOCX file. 

    Returns:
        str: Extracted text with formatting.
    """
    try:
        full_text = docx2txt.process(docx_file)  # Extract text from the document

        # Replace line breaks with spaces and keep page breaks as new lines
        formatted_text = full_text # Replace line breaks with a space
        formatted_text = formatted_text.replace('\f', '\n')  # Replace page breaks with new lines

        # Split into lines and filter out duplicates
        lines = formatted_text.splitlines()
        unique_lines = list(dict.fromkeys(lines))  # Remove duplicates while preserving order

        # Recombine the unique lines
        cleaned_text = '\n'.join(unique_lines) # Join unique lines with new lines

        return cleaned_text
    except Exception as e:
        return f"Error extracting text: {e}"

def extract_text(file):
    if file is not None:  # Ensure the file is not None
        if file.name.endswith('.pdf'):
            return extract_text_from_pdf(file)
        elif file.name.endswith('.docx'):
            return extract_text_from_docx(file)
        else:
            return None
    else:
        return None

def remove_suffix(s):
    if s.endswith("CV"):
        return s[:-3]  # Remove last 2 characters
    elif s.endswith("CR"):
        return s[:-3]  # Remove last 2 characters
    return s
def setOptions (role ):
    if role == "admin":
        return ["Reset Password", "Add User", "Update"]
    elif role == "user":
        return ["Reset Password"]

def text_summarizer_alternate(value):
     # Define the context for the summary
    context = """you are a US lawyer that makes summaries according a specific structure. Here are the instructions :
    the summary can be characterised as a case digest or a case brief. It is a concise restatement of the essential elements of the court''s decision, including:
    1. The procedural context (2 - 4 sentences)
    2. The factual background (2 - 4  sentences)
    3. The legal arguments presented (2 - 4 sentences )
    4. The trial court''s findings  (2 - 4 sentences)
    5. The  court''s decision (2 - 4 sentences)
    The summary effectively captures the essence of the decision, highlighting the key legal findings and the rationale for the court''s ruling. It is structured to provide a clear and quick understanding of the outcome and the reasons behind it, which is useful for legal professionals interested into the case.
    The summary needs to be without the titles of the sections , in one block of text. Also you can use roles like : plaintiff, defendant etc... when needed.
    If there is only one plaintiff, defendant or petitioner, then use "defendant" or "plaintiff" or "petitioner" instead of the name.
    
    Also don''t use formulas like : in this case, judgment or things like "In the case before the United States district court for the District of New Jersey" because we already have that information ahead
    Do not need to repeat the name of the case.
    Use "court", instead of "the court", it can be also "family court" etc.., instead of "the family court", basically remove "the" when it is the court or similar.
    Answer in a professional way, don''t invent, stick to the facts.
    if you copy text from the orginal case put into quotes " " .
    Expresion like "filed a motion", can be replaced by "moved to".
    if there are number don''t put them into letters if they are 10 or above, keep them in numbers like 98 or if percentage : 98%.
    if defendant and plaintiff do not start a sentence then they should not be capitalized, even if they are capitlized in the legal decison, don''t capitlize unless it starts a sentence.
    Keep it between 195-375 tokens."""
    
    context = context + """
    In your summary, please ensure the following key aspects are addressed:
    Legal Proceedings Accuracy: Detail the sequence and timing of key legal events, including pre-trial motions, trial proceedings, and post-trial decisions. Highlight any procedural nuances that are critical to understanding the case's context.   
    Detailed Fact Consideration: Include a thorough overview of the factual background of the case. Emphasize key facts that were pivotal in the court's decision-making process, especially those relevant to any summary judgment considerations.

    Clarity and Readability:

    Jurisdictional Clarity: Clearly distinguish between different types of jurisdiction (e.g., subject matter, personal) involved in the case and their implications.
    Legal Standards and Acts: Accurately describe and reference the legal standards and acts applied in the case, ensuring that their relevance and impact on the case are clearly explained.
    Factual vs. Legal Findings: Differentiate between the court's factual findings and legal rulings. Clarify how these findings influenced the case outcome.
    Semantic Precision: Use precise and appropriate legal terminology throughout the summary. Pay close attention to the semantic implications of legal language and ensure that the summary accurately reflects the nuances and complexities of the case.

    Please balance the need for detailed legal analysis with the conciseness expected in a summary, ensuring that the final output is both informative and accessible to legal professionals
    """

    # Call the OpenAI API to generate a summary
    response = client.chat.completions.create(
        model=GPTModel,
        temperature=0.0,
        max_tokens=600,
        messages=[
            {"role": "system", "content": context},
            {"role": "user", "content": value}
        ]
    )
    
    summary_response = response.choices[0].message.content.strip()
    summary_response = ' '.join(summary_response.splitlines())
    
    summary_response = summary_response.replace("$", "&#36;")
    
    return summary_response 

def abbreviate_title(title):
    words = word_tokenize(title)
    abbreviated_words = []
    for word in words:
        if word in abbrev_dict:
            abbreviated_words.append(abbrev_dict[word])
        elif word.capitalize() in abbrev_dict:
            abbreviated_words.append(abbrev_dict[word.capitalize()])
        else:
            abbreviated_words.append(word)
    return ' '.join(abbreviated_words)

def title(value):

    title_case=""
    
    prompt_title = """
            Give the title of the legal case, take the current title first, then here are the rules : 
            If there are several defendants, just take the first one.
            If it is a person just keep his last name and don't put his first name. 
            If it is a company or organization, it needs to keep the whole name, don't abbreviate anything.
            If it is a State of the USA, just mention the State name.
            
            If the title has the following format plaintiff vs defendant, ONLY if it has that format, then extract the case name from a legal text similar to the following format:
            [Plaintiff Lastname] v. [Defendant Lastname]
            Use Capital letter for the first letter of each word when it makes sense, not needed for capitalization preposition words like "of" or standing letter like v.
            
            If the title has a different format, keep the same format, remove any code or reference, that is not part of the title case and use the previous rules.

            just return the title as an answer nothing else.
    
            """
    title_response = client.chat.completions.create(
    model = GPTModel,
    temperature = 0.0,
    max_tokens = 600,
    messages = [
        {"role": "system", "content": prompt_title},
        {"role": "user", "content": value}
        ]
    )
    print("new2")
    print (title_response.choices[0].message.content)
    
    title_case = title_response.choices[0].message.content
    
    title_case = abbreviate_title(title_case)
    
    print(title_case + ' : NLP')
    return title_case

def Connecticut_summarizer(value):
    summary =""
    first_two_pages = extract_first_two_pages(value)
    name_case = title(first_two_pages)
    
    summary = "CASE: " +  name_case + "  \n"
    prompt_court_option = ("""I will send you a legal decision and you will detect the court that ruled and return it according to a table, just the court name nothing else.
            Here is the structure of table :
            Connecticut Supreme Court
            Connecticut Appellate Court
            Connecticut Superior Court
            District Courts
            Probate Courts
            Family Courts
            Small Claims Courts
            Housing Courts
            Workers' Compensation Commission
            Tax Court
            Juvenile Courts
            Traffic Courts
            Administrative Agencies
            """)
    court_response = client.chat.completions.create(
    model = GPTModel,
    temperature = 0.2,
    max_tokens = 600,
    messages = [
        {"role": "system", "content": prompt_court_option},
        {"role": "user", "content": first_two_pages}
        ]
    )
    
    print (court_response.choices[0].message.content)
    court_case = court_response.choices[0].message.content
    
    prompt_num = """
            Give the number of the legal case, 
            just return the number as an answer nothing else
            """
            
    num_response = client.chat.completions.create(
    model = GPTModel,
    temperature = 0.2,
    max_tokens = 600,
    messages = [
        {"role": "system", "content": prompt_num},
        {"role": "user", "content": first_two_pages}
        ]
    )
    print (num_response.choices[0].message.content)
    
    num_case = num_response.choices[0].message.content
    
    prompt_judge = "you are a US lawyer, and will read a legal decision and return the name of the judge, only the name, nothing else, in the format : Lastname, Firstname (only first letter of the Firstname). If the case is PER CURIAM, just return : per curiam. If it 's a federal case and district case, replace the first name by : U.S.D.J. Else if it 's a federal case and magistrate case, replace the first name by : U.S.M.J."

    judge_response = client.chat.completions.create(
    model = GPTModel,
    temperature = 0.2,
    max_tokens = 600,
    messages = [
        {"role": "system", "content": prompt_judge},
        {"role": "user", "content": first_two_pages}
        ]
    )
            
    judge_name ="" 
            
    if judge_response.choices[0].message.content =="per curiam" :
        judge_name = "per curiam"
    elif "U.S.D.J." in judge_response.choices[0].message.content:
        name = HumanName(judge_response.choices[0].message.content)
        judge_name = name.last + ", U.S.D.J."
        
    elif "U.S.M.J." in judge_response.choices[0].message.content:
        name = HumanName(judge_response.choices[0].message.content)
        judge_name = name.last + ", U.S.M.J."
                
    else:
        name = HumanName(judge_response.choices[0].message.content)
        judge_name = name.last + ", J."  #.capitalize()
            
    
    print (judge_response.choices[0].message.content)
    date_response = client.chat.completions.create(
                model=GPTModel,
                temperature=0.2,
                max_tokens=16,
                messages=[
                    {"role": "system", "content": "When did the judgment happen, if you can't find, look for decided date, also answer with the date only, nothing else, no additional text, just the date, and abreviate the month like this Jan. Feb. March April May June July Aug. Sept. Oct. Nov. Dec."},
                    {"role": "user", "content": value}
                ]
            )

            # Append the court date to the summary
    court_date = date_response.choices[0].message.content.strip()


    prompt_taxonomy = """ I will give you a table with taxonomy , read the legal case, You can use up to three taxonomies. The last topic is usually Civil Appeals or Criminal Appeals. The format is caps and lower case. Just return up to 3 taxonomies, separated by ",", example :  Wrongful Death, Civil Rights, Civil Appeals. Here is the table of taxonomy :
            Administrative Law
            Admiralty
            Antitrust
            Banking and Finance Laws
            Bankruptcy
            Civil Procedure
            Civil Rights
            Commercial Law
            Constitutional Law
            Consumer Protection
            Contracts
            Contractual Disputes
            Corporate Entities
            Corporate Governance
            Creditors' and Debtors' Rights
            Criminal Law
            Damages
            Personal Injury
            Dispute Resolution
            Education Law
            Elder Law
            Employment Benefits
            Employment Litigation
            Employment Compliance
            Employment Litigation
            Entertainment and Sports Law
            Environmental Law
            Evidence
            Family Law
            Government
            Health Care Law
            Immigration Law
            Insurance Law
            Intellectual Property
            Internet Law
            Judges
            Legal Ethics and Attorney Discipline
            Legal Malpractice
            Labor Law
            Employment Benefits
            Employment Compliance
            Employment Litigation
            Land Use and Planning
            Landlord/Tenant
            Mass Tort Claims
            Motor Vehicle Torts
            Toxic Torts
            Business Torts
            Damages
            Medical Malpractice
            Motor Vehicle Torts
            Products Liability
            Public Records
            Public Utilities
            Real Estate
            Securities
            Tax
            Telecommunications
            Transportation
            Trusts and Estates
            Wrongful Death
            Civil Appeals
            Criminal Appeals
            """
    taxonomy_response = client.chat.completions.create(
    model = GPTModel,
    temperature = 0.2,
    max_tokens = 600,
    messages = [
        {"role": "system", "content": prompt_taxonomy},
        {"role": "user", "content": value}
        ]
    )
    print (taxonomy_response.choices[0].message.content)
    practice_area = taxonomy_response.choices[0].message.content
    
    
    prompt_practice = """
            I will give you a table with industries, read the legal case, give the industry of the legal case, just return the industry as an answer nothing else. Here is the table of industries:
            Accounting		
            Advertising		
            Aerospace		
            Agriculture 		
            Autokotive		
            Biotechnology		
            Brokerage		
            Call Centers		
            Cargo and Shipping		
            Chemicals and Materials		
            Construction		
            Consumer Products		
            Defense		
            Ditribution and Wholesale		
            E-Commerce		
            Education		
            Electronics		
            Energy		
            Entertainment and Leisure		
            Executive Search		
            Federal Government		
            Food and Beverage		
            Hardware (Computer)		
            Health Care		
            Hospitatlity and Lodging		
            Insurance		
            Investments and Investment Advisory		
            Legal Services		
            Manufacturing		
            Mining and Resources		
            Non-Profit		
            Pharmaceuticals		
            Real Estate		
            Revruitment and Staffing		
            Retail		
            Software		
            State and Local Government		
            Technology Media Telecom		
            Transportation		
            Travel and Tourism		
            """
                 
    practice_response = client.chat.completions.create(
    model = GPTModel,
    temperature = 0.2,
    max_tokens = 600,
    messages = [
        {"role": "system", "content": prompt_practice},
        {"role": "user", "content": value}
        ]
    )
    print (practice_response.choices[0].message.content)
    
    practice_case = practice_response.choices[0].message.content
    prompt_title = "you are a US lawyer, and will read a legal decision and return the title of the case, only the title, nothing else, the title should describe in a sentence the case without mentioning the plaintiff and the defendants."

    title_response = client.chat.completions.create(
    model = GPTModel,
    temperature = 0.2,
    max_tokens = 600,
    messages = [
        {"role": "system", "content": prompt_title},
        {"role": "user", "content": first_two_pages}
        ]
    )
    print (title_response.choices[0].message.content)
    title_case = title_response.choices[0].message.content
    summary = f"""
CASE: {name_case} \n
COURT: {court_case} \n
DOC NO: {num_case} \n
COURT OPINION BY: {judge_name} \n
DATE: {court_date} \n
PAGES: {page_count} \n

{text_summarizer_alternate(value)}

TITLE: {title_case}               \n
LITIGATION: Yes  \n
PRACTICE AREA: {practice_area} \n
INDUSTRY: {practice_case} \n
ROLE:  


"""
    return summary

def Texas_summarizer(value):
    summary =""
    
    # Display the generated summary
    summary = text_summarizer_alternate(value)
    first_two_pages = extract_first_two_pages(value)
    print(summary)
    
    summary = summary.replace("District Court", "district court")
    
    prompt_taxonomy = """ I will give you a table with taxonomy , read the legal case, You can use up to three taxonomies. The last topic is usually Civil Appeals or Criminal Appeals. The format is caps and lower case. Just return up to 3 taxonomies, separated by "│", example :  Wrongful Death│Civil Rights│Civil Appeals. Here is the table of taxonomy :
            Administrative Law
            Admiralty
            Antitrust
            Banking and Finance Laws
            Bankruptcy
            Civil Procedure
            Civil Rights
            Commercial Law
            Constitutional Law
            Consumer Protection
            Contracts
            Contractual Disputes
            Corporate Entities
            Corporate Governance
            Creditors' and Debtors' Rights
            Criminal Law
            Damages
            Personal Injury
            Dispute Resolution
            Education Law
            Elder Law
            Employment Benefits
            Employment Litigation
            Employment Compliance
            Employment Litigation
            Entertainment and Sports Law
            Environmental Law
            Evidence
            Family Law
            Government
            Health Care Law
            Immigration Law
            Insurance Law
            Intellectual Property
            Internet Law
            Judges
            Legal Ethics and Attorney Discipline
            Legal Malpractice
            Labor Law
            Employment Benefits
            Employment Compliance
            Employment Litigation
            Land Use and Planning
            Landlord/Tenant
            Mass Tort Claims
            Motor Vehicle Torts
            Toxic Torts
            Business Torts
            Damages
            Medical Malpractice
            Motor Vehicle Torts
            Products Liability
            Public Records
            Public Utilities
            Real Estate
            Securities
            Tax
            Telecommunications
            Transportation
            Trusts and Estates
            Wrongful Death
            Civil Appeals
            Criminal Appeals
            """
    taxonomy_response = client.chat.completions.create(
    model = GPTModel,
    temperature = 0.2,
    max_tokens = 600,
    messages = [
        {"role": "system", "content": prompt_taxonomy},
        {"role": "user", "content": value}
        ]
    )
    print (taxonomy_response.choices[0].message.content)
    
    summary = taxonomy_response.choices[0].message.content + "  \n" + summary
    summary = summary + "  \n" + title(first_two_pages)
    
    
    prompt_court_option = ("""I will send you a legal decision and you will detect the court that ruled and return it according to a table, just the court name nothing else.
            Here is the structure of table :
            Fifth Circuit
            Supreme Court of Texas
            Court of Criminal Appeals
            First Court of Appeals
            Second Court of Appeals 
            ...
            Fourteenth Court of Appeals
            [District number] Court of Appeals                
            """)
    court_response = client.chat.completions.create(
    model = GPTModel,
    temperature = 0.2,
    max_tokens = 600,
    messages = [
        {"role": "system", "content": prompt_court_option},
        {"role": "user", "content": first_two_pages}
        ]
    )
    print (court_response.choices[0].message.content)
    summary = summary + ", " + court_response.choices[0].message.content
    
    case_number = ('I will send you a legal decision and you will detect the case number and return it, just the case number nothing else ')
            
    case_number_response = client.chat.completions.create(
    model = GPTModel,
    temperature = 0.2,
    max_tokens = 600,
    messages = [
        {"role": "system", "content": case_number},
        {"role": "user", "content": first_two_pages}
        ]
    )
    print (case_number_response.choices[0].message.content)
    
    case_num = remove_suffix(case_number_response.choices[0].message.content)
    summary = summary + ", " + case_num
    
    # Extract the court date
    date_response = client.chat.completions.create(
        model=GPTModel,
        temperature=0.2,
        max_tokens=16,
        messages=[
            {"role": "system", "content": "When did the judgment happen, if you can't find, look for decided date, also answer with the date only, nothing else, no additional text, just the date, with this format 01/17/2021"},
            {"role": "user", "content": value}
        ]
    )

    # Append the court date to the summary
    court_date = date_response.choices[0].message.content.strip()
    summary = summary + ", " + court_date
               
        
    return summary
    

# Function to validate if the input is a positive integer
def is_positive_integer(value):
    try:
        value = int(value)
        return value > 0
    except ValueError:
        return False
    
# Define the Streamlit app
def main():
    
    ensure_nltk_data()
    global page_count
    st.image('MESJ.jpg')
    app_mode = st.sidebar.selectbox("Choose your preference:", ["Legal Decision Summarizer", "Newsletter Quotes"])
    if app_mode == "Legal Decision Summarizer":
        st.title("Legal Decision Summarizer")

        with open('config.YAML') as file:
            config = yaml.load(file, Loader=SafeLoader)
        with open('cfg1.YAML') as file:
            roles_config = yaml.load(file, Loader=SafeLoader)

        if 'pre-authorized' in config.keys():
            authenticator = stauth.Authenticate(
            config['credentials'],
            config['cookie']['name'],
            config['cookie']['key'],
            config['cookie']['expiry_days'],
            
            config['pre-authorized']
        )
            if 'authentication_status' not in st.session_state:
                st.session_state.authentication_status = None
            name, authentication_status, username = authenticator.login()
            if username : 
                role = roles_config["usernames"][username]["role"]
                
            else : role = "user"

            if authentication_status == False:
                st.error("Username/password is incorrect")

            if authentication_status == None:
                st.warning("Please enter your username and password")

            if authentication_status:
                authenticator.logout("Logout", "sidebar")
                st.sidebar.title(f"Welcome {name}")
                # Create a text input field for the legal decision

                selected_option = st.sidebar.selectbox("Options", setOptions(role))

                with st.expander(f"{selected_option}"):

            # Perform actions based on the selected option
                    if selected_option == "Reset Password":
                        if st.session_state["authentication_status"]:
                            try:
                                if authenticator.reset_password(st.session_state["username"]):
                                    st.success('Password modified successfully')
                            except Exception as e:
                                st.error(e)
                            with open('config.YAML', 'w') as file:
                                yaml.dump(config, file, default_flow_style=False)
                    elif selected_option == "Add User":
                        try:
                            email_of_registered_user, username_of_registered_user, name_of_registered_user = authenticator.register_user(
                                fields={
                                    'Form name':'Register user', 
                                    'Email':'Email', 
                                    'Username':'Username', 
                                    'Password':'Password', 
                                    'Repeat password':'Repeat password',
                                    'Register':'Register'},
                                pre_authorization=False)
                            if username_of_registered_user : 
                                st.session_state["username_of_registered_user"] = username_of_registered_user
                            if email_of_registered_user:
                                    
                                with open('config.YAML', 'w') as file:
                                    yaml.dump(config, file, default_flow_style=False)
                                st.success('User registered successfully')
                            if "username_of_registered_user" in st.session_state.keys() and st.session_state["username_of_registered_user"]:
                                role='admin'
                                role = st.selectbox("select a role", options=["admin", "user"])
                                if role =='user':
                                    chosen_states = st.multiselect ("select the states" , options = ["New Jersey", "Texas", "Connecticut"])
                                    if role and chosen_states:
                                        with open('cfg1.YAML', 'r') as file:
                                            role_data = yaml.safe_load(file)
                                            if st.session_state["username_of_registered_user"] not in role_data['usernames'].keys() or role_data["usernames"][st.session_state["username_of_registered_user"]]==None :
                                                role_data["usernames"][st.session_state["username_of_registered_user"]]= dict()
                                            role_data["usernames"][st.session_state["username_of_registered_user"]]["role"] = role
                                            role_data["usernames"][st.session_state["username_of_registered_user"]]["states"] = chosen_states
                                        with open('cfg1.YAML', 'w') as file:
                                            yaml.dump(role_data, file)
                                            file.close()
                                
                        except Exception as e:
                            st.error(e)
                        with open('config.YAML', 'w') as file:
                                yaml.dump(config, file, default_flow_style=False)
                        
                    elif selected_option == "Update":
                        if st.session_state["authentication_status"]:   
                            try:
                                with open('config.YAML', 'r') as file:
                                        usernames_data = yaml.safe_load(file)["credentials"]["usernames"]
                                        usernames_= usernames_data.keys()
                                username_updated= st.selectbox('username',usernames_)
                                if username_updated : 
                                    st.session_state["username_updated"] = username_updated
                                if authenticator.update_user_details(username_updated):
                                    st.success('Entries updated successfully')
                                with open('cfg1.YAML', 'r') as file:
                                    role_data = yaml.safe_load(file)
                                if "username_updated" in st.session_state.keys() and st.session_state["username_updated"] and role_data["usernames"][st.session_state["username_updated"]]['role']== 'user':                            
                                        chosen_states = st.multiselect ("select the states" , options = ["New Jersey", "Texas", "Connecticut"])
                                        if chosen_states:
                                            
                                            if st.session_state["username_updated"] not in role_data['usernames'].keys() or role_data["usernames"][st.session_state["username_updated"]]==None :
                                                role_data["usernames"][st.session_state["username_updated"]]= dict()
                                            role_data["usernames"][st.session_state["username_updated"]]["states"] = chosen_states
                                            with open('cfg1.YAML', 'w') as file:
                                                yaml.dump(role_data, file)
                                                file.close()
                            except Exception as e:
                                st.error(e)
                            with open('config.YAML', 'w') as file:
                                yaml.dump(config, file, default_flow_style=False)
                                            
                choice1 = st.radio("How would you like to provide the legal decision?", ('Copy-Paste Text', 'Upload Document'))
                
                if choice1 == 'Copy-Paste Text':
                # Create a text input field for the legal decision
                    user_input = st.text_area("Enter legal decision:", height=150) 
                    first_two_pages = extract_first_two_pages(user_input)
                
                elif choice1 == 'Upload Document':
                    user_file_input = st.file_uploader("Upload your document", type=["pdf", "docx"])  
                    if user_file_input is not None:  # Check if a file was uploaded
                        combined_text = extract_text(user_file_input)
                        if combined_text:
                            first_two_pages = extract_first_two_pages(combined_text)
                            user_input = combined_text  # Assign extracted text to user_input
                        else:
                            st.error("Could not extract text from the file. Please upload a valid document.")
                    else:
                        st.error("No file uploaded. Please upload a document.")
                        first_two_pages = None
                
                # Create a numeric input for the page count
                #page_count = st.number_input("Page count:", min_value=1, value=1, step=1)
                
                # Create a text input for the page count
                #page_count_input = st.text_input("Page count:", value="1")
    
                # # Validate the input
                # if is_positive_integer(page_count_input):
                #     page_count = int(page_count_input)
                #     # Continue with your logic using page_count
                # else:
                #     st.error("Please enter a valid positive integer for the page count.")
                
                # Create a dropdown to select the US State
                        
                if role =="user" :
                    try:
                        states = roles_config["usernames"][username]["states"]
                    except : states=[]
                else : states = ["New Jersey", "Texas","Connecticut"]
                state = st.selectbox("Select a US State:", states)  
                
                # Only show the page count option if the selected state is not Texas
                if state != "Texas":
                    # Create a text input for the page count
                    page_count_input = st.text_input("Page count:", value="1")

                    # Validate the input
                    if is_positive_integer(page_count_input):
                        page_count = int(page_count_input)
                        # Continue with your logic using page_count
                    else:
                        st.error("Please enter a valid positive integer for the page count.")
                else:
                    # If Texas is selected, you can set a default value for page_count or handle it as needed
                    page_count = None  # Or any default/fallback value you prefer


                if st.button("Summarize"):
                    if state == "New Jersey":

                        # Display the generated summary
                        summary = text_summarizer_alternate(user_input) #
                    
                        
                        print(summary)
                        
                        summary = summary.replace("District Court", "district court")
                        st.subheader("Summary:")

                        # Type of case federal or State
                        federal_response = client.chat.completions.create(
                            model=GPTModel,
                            temperature=0.2,
                            max_tokens=16,
                            messages=[
                                {"role": "system", "content": """
                                
                                Determine if the legal case, if related to a state or federal case, the federal cases are these 
                                Bankr. D.N.J. (U.S Bankruptcy Court) 6
                                D.N.J. (U.S. District Court) - 7
                                3d Cir. (Third Circuit) – 8
                                
                                If that's a federal case just return Federal, nothing else, if it's a state just retrun State nothing else.
                                """},
                                {"role": "user", "content": user_input}
                            ]
                        )

                        # Append the court date to the summary
                        court_type = federal_response.choices[0].message.content.strip()


                        # Extract the court date
                        date_response = client.chat.completions.create(
                            model=GPTModel,
                            temperature=0.2,
                            max_tokens=16,
                            messages=[
                                {"role": "system", "content": "Check filed date, usually it is at the top of the document, American date format, also answer with the date only, nothing else, no additional text, just the date, and abreviate the month like this Jan. Feb. March April May June July Aug. Sept. Oct. Nov. Dec."},
                                {"role": "user", "content": user_input}
                            ]
                        )

                        # Append the court date to the summary
                        court_date = date_response.choices[0].message.content.strip()
                        
                        if court_type =="Federal":
                            summary = summary + " [Filed " + court_date + "]"
                        
                        # judge
                        prompt_judge = "you are a US lawyer, and will read a legal decision and return the name of the judge, only the name, nothing else, in the format : Lastname, Firstname (only first letter of the Firstname). If the case is PER CURIAM, just return : per curiam. If it 's a federal case and district case, replace the first name by : U.S.D.J. Else if it 's a federal case and magistrate case, replace the first name by : U.S.M.J."

                        judge_response = client.chat.completions.create(
                        model = GPTModel,
                        temperature = 0.0,
                        max_tokens = 600,
                        messages = [
                            {"role": "system", "content": prompt_judge},
                            {"role": "user", "content": user_input}
                            ]
                        )
                        
                        judge_name ="" 
                        
                        if judge_response.choices[0].message.content =="per curiam" :
                            judge_name = "per curiam"
                        elif "U.S.D.J." in judge_response.choices[0].message.content:
                            name = HumanName(judge_response.choices[0].message.content)
                            judge_name = name.last + ", U.S.D.J."
                            
                        elif "U.S.M.J." in judge_response.choices[0].message.content:
                            name = HumanName(judge_response.choices[0].message.content)
                            judge_name = name.last + ", U.S.M.J."
                            
                        else:
                            name = HumanName(judge_response.choices[0].message.content)
                            judge_name = name.last + ", J."  #.capitalize()
                        
                        summary = " (" + judge_name + ") (" + str(page_count) + " pp.) "  + summary 
                        print (judge_response.choices[0].message.content)
                        
                        # court option
                        
                        courts = {
                                'N.J.': 1,
                                'N.J. Super. App. Div.': 2,
                                'N.J. Super. Law Div.': 3,
                                'N.J. Super. Ch. Div.': 4,
                                'Tax Ct.': 5,
                                'Bankr. D.N.J.': 6,
                                'D.N.J.': 7,
                                '3d Cir.': 8
                                }
                        courts_inverted = {value: key for key, value in courts.items()}

                        
                        prompt_court_option = ('I will send you a legal decision and you have to select one of these court option, just return the corresponding number, nothing else, here are the court option :' 
                            'N.J. Sup. Ct. (Supreme Court) - 1 '
                            'N.J. Super. App. Div. (Appellate Division) 2 '
                            'N.J. Super. Law Div. – (Law Division) (Civil and Criminal) 3 '
                            'N.J. Super. Ch. Div. (Chancery Division) (General Equity and Family) -4 '
                            'Tax Ct. – (Tax Court) - 5 '
                            'Bankr. D.N.J. (U.S Bankruptcy Court 6 '
                            'D.N.J. (U.S. District Court) - 7 '
                            '3d Cir. (Third Circuit) - 8 ')
                        
                        court_response = client.chat.completions.create(
                        model = GPTModel,
                        temperature = 0.2,
                        max_tokens = 600,
                        messages = [
                            {"role": "system", "content": prompt_court_option},
                            {"role": "user", "content": first_two_pages}
                            ]
                        )
                        print (court_response.choices[0].message.content)
                        summary = courts_inverted[int(court_response.choices[0].message.content)] + " "  + summary
                        
                        title_case = (f"*{title(first_two_pages)}*")
                        
                        
                        summary = title_case + ", "  + summary 
                        
                        # taxonomy
                        prompt_taxonomy = """ I will give you a table with taxonomy , read the legal case, just return the corresponding number , nothing else. here is the table :
                            NJ topic #	NJ Taxonomy Topics
                            01	Administrative Law
                            54	Admiralty
                            59	Antitrust
                            06	Banking and Finance Laws
                            42	Bankruptcy
                            07	Civil Procedure
                            46	Civil Rights
                            08	Commercial Law
                            10	Constitutional Law
                            09	Consumer Protection
                            11	Contracts; Contractual Disputes
                            12	Corporate Entities; Corporate Governance
                            15	Creditors' and Debtors' Rights
                            14	Criminal Law
                            31	Damages; Personal Injury
                            03	Dispute Resolution
                            16	Education Law
                            60	Elder Law
                            39	Employment Benefits; Employment Litigation
                            55	Entertainment and Sports Law
                            17	Environmental Law
                            19	Evidence
                            20	Family Law
                            21	Government
                            22	Health Care Law
                            51	Immigration Law
                            23	Insurance Law
                            53	Intellectual Property
                            61	Internet Law
                            48	Judges
                            04	Judges; Legal Ethics and Attorney Discipline; Legal Malpractice
                            56	Labor Law; Employment Benefits
                            25	Labor Law; Employment Compliance; Employment Litigation
                            26	Land Use and Planning
                            27	Landlord/Tenant
                            36	Mass Tort Claims; Motor Vehicle Torts; Toxic Torts; Business Torts; Damages
                            29	Medical Malpractice
                            05	Motor Vehicle Torts
                            32	Products Liability
                            52	Public Records
                            37	Public Utilities
                            34	Real Estate
                            50	Securities
                            35	Tax
                            57	Telecommunications
                            49	Transportation
                            38	Trusts and Estates
                            40	Wrongful Death
                            """

                        taxonomy_response = client.chat.completions.create(
                        model = GPTModel,
                        temperature = 0.2,
                        max_tokens = 600,
                        messages = [
                            {"role": "system", "content": prompt_taxonomy},
                            {"role": "user", "content": user_input}
                            ]
                        )
                        print (taxonomy_response.choices[0].message.content)
                        summary = taxonomy_response.choices[0].message.content + "-" + court_response.choices[0].message.content + "-XXXX " + summary
                        
                        hash_table = {
                            "01": "Administrative Law",
                            "54": "Admiralty",
                            "59": "Antitrust",
                            "06": "Banking and Finance Laws",
                            "42": "Bankruptcy",
                            "07": "Civil Procedure",
                            "46": "Civil Rights",
                            "08": "Commercial Law",
                            "10": "Constitutional Law",
                            "09": "Consumer Protection",
                            "11": "Contracts; Contractual Disputes",
                            "12": "Corporate Entities; Corporate Governance",
                            "15": "Creditors' and Debtors' Rights",
                            "14": "Criminal Law",
                            "31": "Damages; Personal Injury",
                            "03": "Dispute Resolution",
                            "16": "Education Law",
                            "60": "Elder Law",
                            "39": "Employment Benefits; Employment Litigation",
                            "55": "Entertainment and Sports Law",
                            "17": "Environmental Law",
                            "19": "Evidence",
                            "20": "Family Law",
                            "21": "Government",
                            "22": "Health Care Law",
                            "51": "Immigration Law",
                            "23": "Insurance Law",
                            "53": "Intellectual Property",
                            "61": "Internet Law",
                            "48": "Judges",
                            "04": "Judges; Legal Ethics and Attorney Discipline; Legal Malpractice",
                            "56": "Labor Law; Employment Benefits",
                            "25": "Labor Law; Employment Compliance; Employment Litigation",
                            "26": "Land Use and Planning",
                            "27": "Landlord/Tenant",
                            "36": "Mass Tort Claims; Motor Vehicle Torts; Toxic Torts; Business Torts; Damages",
                            "29": "Medical Malpractice",
                            "05": "Motor Vehicle Torts",
                            "32": "Products Liability",
                            "52": "Public Records",
                            "37": "Public Utilities",
                            "34": "Real Estate",
                            "50": "Securities",
                            "35": "Tax",
                            "57": "Telecommunications",
                            "49": "Transportation",
                            "38": "Trusts and Estates",
                            "40": "Wrongful Death"
                        }
                        
                        legal_category = hash_table.get(taxonomy_response.choices[0].message.content, "Unknown code").upper()
                        
                        st.markdown(f"**{legal_category}**")
                        st.write(summary)
                    elif state =="Connecticut":
                        st.subheader("Summary:")
                        st.write(Connecticut_summarizer(user_input))
                    elif state == "Texas":
                        st.subheader("Summary:")
                        st.write(Texas_summarizer(user_input))
                    else:
                        st.warning("Please select a state before clicking 'Summarize'.")
                        
    elif app_mode == "Newsletter Quotes":
        def process_data(uploaded_file):
            df = pd.read_excel(uploaded_file, header=None)
            df.columns = ['A', 'B', 'C', 'D', 'E', 'F']
            results = list(filter(None, df.apply(process_row, axis=1)))

            all_items = []
            for idx, item in enumerate(results):
                web_content = scrap_web(item['link'])
                item['web_content'] = web_content
                newsletter_data = newsletter(item['web_content'])

                if newsletter_data is None:
                    continue

                try:
                    people_quotes = newsletter_data['newsletter']['people']
                    background = newsletter_data.get('background', 'No background available')  
                    quoted = newsletter_data.get('quoted', 'No quotes available')
                    extracted_people_quotes = [{'name': person['name'], 'quote': person['quote']} for person in people_quotes]

                    data = {
                        'info': item['info'],
                        'background': background,
                        'people_quotes': extracted_people_quotes,
                        'quoted': quoted,
                        'link': item['link'],
                        'date': item['date']
                    }

                    all_items.append(data)

                except KeyError as e:
                    st.error(f"Error processing data for {item['info']}: Missing key {e}")
                except Exception as e:
                    st.error(f"Unexpected error processing data for {item['info']}: {e}")

            return all_items

        # Title of the app
        st.title('Newsletter Quotes')

        # Uploading the file
        uploaded_file = st.file_uploader("Choose an Excel file", type="xlsx")

        # Check if we already have the processed data in session state
        if 'processed_data' not in st.session_state:
            st.session_state['processed_data'] = None

        # If a file is uploaded and not already processed
        if uploaded_file is not None and st.session_state['processed_data'] is None:
            with st.spinner("Processing..."):
                st.session_state['processed_data'] = process_data(uploaded_file)

        # If the data is processed
        if st.session_state['processed_data']:
            docx_path = create_docx(st.session_state['processed_data'])
            with open(docx_path, "rb") as file:
                docx_data = file.read()

            # Display the download button
            st.download_button(
                label="Download DOCX File",
                data=docx_data,
                file_name="newsletter_output.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
                


if __name__ == "__main__":
    main()
