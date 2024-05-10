import streamlit as st
from nameparser import HumanName
import openai
import re
import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth

# Set your OpenAI API key here (use environment variables or Streamlit's secrets for better security)
openai.api_key = st.secrets["OPENAI_API_KEY"]

page_count= None
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
def text_summarizer(value):
     # Define the context for the summary
    context = ('you are a US lawyer that makes summaries according a specific structure. Here are the instructions :'
    'the summary can be characterised as a case digest or a case brief. It is a concise restatement of the essential elements of the court''s decision, including:'
    '1. The procedural context (2 - 4 sentences)'
    '2. The factual background (2 - 4  sentences)'
    '3. The legal arguments presented (2 - 4 sentences )'
    '4. The trial court''s findings  (2 - 4 sentences)'
    '5. The  court''s decision (2 - 4 sentences)' 
    'The summary effectively captures the essence of the decision, highlighting the key legal findings and the rationale for the court''s ruling. It is structured to provide a clear and quick understanding of the outcome and the reasons behind it, which is useful for legal professionals interested into the case. The summary needs to be without the titles of the sections , in one block of text. Also you can roles like : plaintiff, defendent etc... when needed. Also don''t use formulas like : in this case, judgment. Do not need to repeat the name of the case. Don''t need to write out the whole name of the court, however if you have to use it replace it by : the court'
    'Answer in a professional way, don''t invent, stick to the facts.')

    # Call the OpenAI API to generate a summary
    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        temperature=0.0,
        max_tokens=600,
        messages=[
            {"role": "system", "content": context},
            {"role": "user", "content": value}
        ]
    )
    
    return response.choices[0].message.content.strip()

def text_summarizer_alternate(value):
     # Define the context for the summary
    context = ('you are a US lawyer that makes summaries according a specific structure. Here are the instructions :'
    'the summary can be characterised as a case digest or a case brief. It is a concise restatement of the essential elements of the court''s decision, including:'
    '1. The procedural context (2 - 4 sentences)'
    '2. The factual background (2 - 4  sentences)'
    '3. The legal arguments presented (2 - 4 sentences )'
    '4. The trial court''s findings  (2 - 4 sentences)'
    '5. The  court''s decision (2 - 4 sentences)' 
    'The summary effectively captures the essence of the decision, highlighting the key legal findings and the rationale for the court''s ruling. It is structured to provide a clear and quick understanding of the outcome and the reasons behind it, which is useful for legal professionals interested into the case.' 
    'The summary needs to be without the titles of the sections , in one block of text. Also you can roles like : plaintiff, defendent etc... when needed.'
    'Also don''t use formulas like : in this case, judgment. Do not need to repeat the name of the case.'
    'Answer in a professional way, don''t invent, stick to the facts.'
    'if you copy text from the orginal case put into quotes " " .'
    'Keep it between 195-325 tokens.')
    
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
    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        temperature=0.0,
        max_tokens=600,
        messages=[
            {"role": "system", "content": context},
            {"role": "user", "content": value}
        ]
    )
    
    return response.choices[0].message.content.strip()

def title(value):

    title_case=""
    
    prompt_title = """
            Give the title of the legal case, no need to pull in all of the defendants, just the first one , and if it is a person just his last name. 
            If it is a State of the USA, just mention the State name.
            extract the case name from a legal text similar to the following format:
            
            [Plaintiff Name] v. [Defendent Name]
            Use Capital letter for the first letter of each word when it makes sense, not needed for capitalization preposition words like "of" or standing letter like v.
            

            just return the title as an answer nothing else
            """
            
    title_response = openai.ChatCompletion.create(
    model = "gpt-4-turbo",
    temperature = 0.2,
    max_tokens = 600,
    messages = [
        {"role": "system", "content": prompt_title},
        {"role": "user", "content": value}
        ]
    )
    print (title_response.choices[0].message.content)
    
    title_case = title_response.choices[0].message.content
    
    prompt_abreviation = """
            if needed, use the following abreviation table to abreviate any word of the title :
            A
            Academy	Acad.
            Administrat[ive,ion]	Admin.
            Administrat[or,rix]	Adm'[r,x]
            America[n]	Am.
            and	&
            Associate	Assoc.
            Association	Ass'n
            Atlantic	Atl.
            Authority	Auth.
            Automo[bile, tive]	Auto.
            Avenue	Ave.
            B	
            Board	Bd.
            Broadcast[ing]	Broad.
            Brotherhood	Bhd.
            Brothers	Bros.
            Building	Bldg.
            Business	Bus.
            C	
            Casualty	Cas.
            Cent[er, re]	Ctr.
            Central	Cent.
            Chemical	Chem.
            Coalition	Coal.
            College	Coll.
            Commission	Comm'n
            Commissioner	Comm'r
            Committee	Comm.
            Communication	Commc'n
            Community	Cmty.
            Company	Co.
            Compensation	Comp.
            Condominium	Condo.
            Congress[ional]	Cong.
            Consolidated	Consol.
            Construction	Constr.
            Continental	Cont'l
            Cooperative	Coop.
            Corporation	Corp.
            Correction[s, al]	Corr.
            D	
            Defense	Def.
            Department	Dep't
            Detention	Det.
            Development	Dev.
            Director	Dir.
            Distribut[or, ing]	Distrib.
            District	Dist.
            Division	Div.
            E	
            East[ern]	E.
            Econom[ic, ics, ical, y]	Econ.
            Education[al]	Educ.
            Electric[al, ity]	Elec.
            Electronic	Elec.
            Engineer	Eng'r
            Engineering	Eng'g
            Enterprise	Enter.
            Entertainment	Ent.
            Environment	Env't
            Environmental	Envtl.
            Equality	Equal.
            Equipment	Equip.
            Examiner	Exam'r
            Exchange	Exch.
            Execut[or, rix]	Ex'[r, x]
            Export[er, ation]	Exp.
            F	
            Federal	Fed.
            Federation	Fed'n
            Fidelity	Fid.
            Finance[e, ial, ing]	Fin.
            Foundation	Found.
            G	
            General	Gen.
            Government	Gov't
            Guaranty	Guar.
            H	
            Hospital	Hosp.
            Housing	Hous.
            I	
            Import[er, ation]	Imp.
            Incorporated	Inc.
            Indemnity	Indem.
            Independent	Indep.
            Industr[y, ies, ial]	Indus.
            Information	Info.
            Institut[e, ion]	Inst.
            Insurance	Ins.
            International	Int'l
            Investment	Inv.
            J	
            K	
            L	
            Laboratory	Lab.
            Liability	Liab.
            Limited	Ltd.
            Litigation	Litig.
            M	
            Machine[ry]	Mach.
            Maintenance	Maint.
            Management	Mgmt.
            Manufacturer	Mfr.
            Manufacturing	Mfg.
            Maritime	Mar.
            Market	Mkt.
            Marketing	Mktg.
            Mechanic[al]	Mech.
            Medic[al, ine]	Med.
            Memorial	Mem'l
            Merchan[t, dise, dising]	Merch.
            Metropolitan	Metro.
            Municipal	Mun.
            Mutual	Mut.
            N	
            National	Nat'l
            North[ern]	N.
            Northeast[ern]	Ne.
            Northwest[ern]	Nw.
            Number	No.
            O	
            Organiz[ation, ing]	Org.
            P	
            Pacific	Pac.
            Partnership	P'ship
            Person[al, nel]	Pers.
            Pharmaceutic[s, al]	Pharm.
            Preserv[e, ation]	Pres.
            Probation	Prob.
            Product[ion]	Prod.
            Professional	Prof'l
            Property	Prop.
            Protection	Prot.
            Public	Pub.
            Publication	Publ'n
            Publishing	Publ'g
            Q	
            R	
            Railroad	R.R.
            Railway	Ry.
            Refining	Ref.
            Regional	Reg'l
            Rehabilitation	Rehab.
            Reproduct[ion, ive]	Reprod.
            Resource[s]	Res.
            Restaurant	Rest.
            Retirement	Ret.
            Road	Rd.
            S	
            Savings	Sav.
            School[s]	Sch.
            Science	Sci.
            Secretary	Sec'y
            Securit[y, ies]	Sec.
            Service	Serv.
            Shareholder	S'holder
            Social	Soc.
            Society	Soc'y
            South[ern]	S.
            Southwest[ern]	Sw.
            Steamship[s]	S.S.
            Street	St.
            Subcommittee	Subcomm.
            Surety	Sur.
            System[s]	Sys.
            T	
            Technology	Tech.
            Telecommunication	Telecomm.
            Tele[phone, graph]	Tel.
            Temporary	Temp.
            Township	Twp.
            Transcontinental	Transcon.
            Transport[ation]	Transp.
            Trustee	Tr.
            Turnpike	Tpk.
            U	
            Uniform	Unif.
            University	Univ.
            Utility	Util.
            United States U.S.
            V	
            Village	Vill.
            W	
            West[ern]	W.
            
            ------------------
            Just return the title with the abriviated words (if applicable), nothing else.
    """
    
    abreviated_response = openai.ChatCompletion.create(
    model = "gpt-4-turbo",
    temperature = 0.2,
    max_tokens = 600,
    messages = [
        {"role": "system", "content": prompt_abreviation},
        {"role": "user", "content": title_case}
        ]
    )
    print (abreviated_response.choices[0].message.content)
    
    title_case = abreviated_response.choices[0].message.content
    
    return title_case

def Connecticut_summarizer(value):
    summary =""
    
    name_case = title(value)
    
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
    court_response = openai.ChatCompletion.create(
    model = "gpt-4-turbo",
    temperature = 0.2,
    max_tokens = 600,
    messages = [
        {"role": "system", "content": prompt_court_option},
        {"role": "user", "content": value}
        ]
    )
    
    print (court_response.choices[0].message.content)
    court_case = court_response.choices[0].message.content
    
    prompt_num = """
            Give the number of the legal case, 
            just return the number as an answer nothing else
            """
            
    num_response = openai.ChatCompletion.create(
    model = "gpt-4-turbo",
    temperature = 0.2,
    max_tokens = 600,
    messages = [
        {"role": "system", "content": prompt_num},
        {"role": "user", "content": value}
        ]
    )
    print (num_response.choices[0].message.content)
    
    num_case = num_response.choices[0].message.content
    
    prompt_judge = "you are a US lawyer, and will read a legal decision and return the name of the judge, only the name, nothing else, in the format : Lastname, Firstname (only first letter of the Firstname). If the case is PER CURIAM, just return : per curiam. If it 's a federal case and district case, replace the first name by : U.S.D.J. Else if it 's a federal case and magistrate case, replace the first name by : U.S.M.J."

    judge_response = openai.ChatCompletion.create(
    model = "gpt-4-turbo",
    temperature = 0.2,
    max_tokens = 600,
    messages = [
        {"role": "system", "content": prompt_judge},
        {"role": "user", "content": value}
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
    date_response = openai.ChatCompletion.create(
                model="gpt-4-turbo",
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
    taxonomy_response = openai.ChatCompletion.create(
    model = "gpt-4-turbo",
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
                 
    practice_response = openai.ChatCompletion.create(
    model = "gpt-4-turbo",
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

    title_response = openai.ChatCompletion.create(
    model = "gpt-4-turbo",
    temperature = 0.2,
    max_tokens = 600,
    messages = [
        {"role": "system", "content": prompt_title},
        {"role": "user", "content": value}
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
    
    print(summary)
    
    summary = summary.replace("$", "&#36;") # avoiding issues
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
    taxonomy_response = openai.ChatCompletion.create(
    model = "gpt-4-turbo",
    temperature = 0.2,
    max_tokens = 600,
    messages = [
        {"role": "system", "content": prompt_taxonomy},
        {"role": "user", "content": value}
        ]
    )
    print (taxonomy_response.choices[0].message.content)
    
    summary = taxonomy_response.choices[0].message.content + "  \n" + summary
    summary = summary + "  \n" + title(value)
    
    
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
    court_response = openai.ChatCompletion.create(
    model = "gpt-4-turbo",
    temperature = 0.2,
    max_tokens = 600,
    messages = [
        {"role": "system", "content": prompt_court_option},
        {"role": "user", "content": value}
        ]
    )
    print (court_response.choices[0].message.content)
    summary = summary + ", " + court_response.choices[0].message.content
    
    case_number = ('I will send you a legal decision and you will detect the case number and return it, just the case number nothing else ')
            
    case_number_response = openai.ChatCompletion.create(
    model = "gpt-4-turbo",
    temperature = 0.2,
    max_tokens = 600,
    messages = [
        {"role": "system", "content": case_number},
        {"role": "user", "content": value}
        ]
    )
    print (case_number_response.choices[0].message.content)
    
    case_num = remove_suffix(case_number_response.choices[0].message.content)
    summary = summary + ", " + case_num
    
    # Extract the court date
    date_response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
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
    global page_count
    st.image('MESJ.jpg')
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

            # Create a text input field for the legal decision
            user_input = st.text_area("Enter legal decision:", height=150) 
            
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
                    
                    summary = summary.replace("$", "&#36;") # avoiding issues
                    summary = summary.replace("District Court", "district court")
                    st.subheader("Summary:")

                    # Type of case federal or State
                    federal_response = openai.ChatCompletion.create(
                        model="gpt-4-turbo",
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
                    date_response = openai.ChatCompletion.create(
                        model="gpt-4-turbo",
                        temperature=0.2,
                        max_tokens=16,
                        messages=[
                            {"role": "system", "content": "When did the judgment happen, if you can't find, look for decided date, also answer with the date only, nothing else, no additional text, just the date, and abreviate the month like this Jan. Feb. March April May June July Aug. Sept. Oct. Nov. Dec."},
                            {"role": "user", "content": user_input}
                        ]
                    )

                    # Append the court date to the summary
                    court_date = date_response.choices[0].message.content.strip()
                    
                    if court_type =="Federal":
                        summary = summary + " [Filled " + court_date + "]"
                    else:
                        summary = summary + " [" + court_date + "]"    
                    
                    # judge
                    prompt_judge = "you are a US lawyer, and will read a legal decision and return the name of the judge, only the name, nothing else, in the format : Lastname, Firstname (only first letter of the Firstname). If the case is PER CURIAM, just return : per curiam. If it 's a federal case and district case, replace the first name by : U.S.D.J. Else if it 's a federal case and magistrate case, replace the first name by : U.S.M.J."

                    judge_response = openai.ChatCompletion.create(
                    model = "gpt-4-turbo",
                    temperature = 0.2,
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
                    
                    court_response = openai.ChatCompletion.create(
                    model = "gpt-4-turbo",
                    temperature = 0.2,
                    max_tokens = 600,
                    messages = [
                        {"role": "system", "content": prompt_court_option},
                        {"role": "user", "content": user_input}
                        ]
                    )
                    print (court_response.choices[0].message.content)
                    summary = courts_inverted[int(court_response.choices[0].message.content)] + " "  + summary
                    
                    title_case = (f"*{title(user_input)}*")
                    
                    
                    summary = title_case + ", "  + summary 
                    
                    # taxonomy
                    prompt_taxonomy = """ I will give you a table with taxonomy , just return the corresponding number , nothing else. here is the table :
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
                        62	Employment Compliance; Employment Litigation
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

                    taxonomy_response = openai.ChatCompletion.create(
                    model = "gpt-4-turbo",
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
                        "62": "Employment Compliance; Employment Litigation",
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

if __name__ == "__main__":
    main()
