"""
Vasanthi - Company brochure using Ollama instead of OpenAI - WORKS IN VSS
"""

import os
import json
from dotenv import load_dotenv
from scraper import fetch_website_links, fetch_website_contents
from openai import OpenAI
#from IPython.display import Markdown, display, update_display

link_system_prompt = """
You are provided with a list of links found on a webpage.
You are able to decide which of the links would be most relevant to include in a brochure about the company,
such as links to an About page, or a Company page, or Careers/Jobs pages.
You should respond in JSON as in this example:

{
    "links": [
        {"type": "about page", "url": "https://full.url/goes/here/about"},
        {"type": "careers page", "url": "https://another.full.url/careers"}
    ]
}
"""

def get_links_user_prompt(url):
    user_prompt = f"""
Here is the list of links on the website {url} -
Please decide which of these are relevant web links for a brochure about the company, 
respond with the full https URL in JSON format.
Do not include Terms of Service, Privacy, email links.

Links (some might be relative links):

"""
    links = fetch_website_links(url)
    user_prompt += "\n".join(links)
    return user_prompt

OLLAMA_BASE_URL="http://localhost:11434/v1"
OLLAMA_API_KEY="ollama"
MODEL ="llama3.2:1b"
ollama = OpenAI(base_url=OLLAMA_BASE_URL, api_key=OLLAMA_API_KEY)

def select_relevant_links (url):
    print(f"Selecting relevant links for {url} by calling {MODEL}")
    response = ollama.chat.completions.create (
    model=MODEL, 
    messages=[{"role": "system", "content": link_system_prompt},
                {"role" : "user" , "content" : get_links_user_prompt(url)}],
    response_format={"type": "json_object"})
    result = response.choices[0].message.content
    links = json.loads(result) #convers json string to python dictonaries
    print("Links dictionary:", links)
    return links

def fetch_page_and_all_relevant_links(url):
    contents = fetch_website_contents(url)
    relevant_links = select_relevant_links(url)
    print("Links dictionary new:", relevant_links)
    result = f"## Landing Page:\n\n{contents}\n## Relevant Links:\n"
    for link in relevant_links['links']:
        result += f"\n\n### Link: {link['type']}\n"
        result += fetch_website_contents(link["url"])
    return result

brochure_system_prompt = """
You are an assistant that analyzes the contents of several relevant pages from a company website
and creates a short brochure about the company for prospective customers, investors and recruits.
Respond in markdown without code blocks.
Include details of company culture, customers and careers/jobs if you have the information.
"""

def get_brochure_user_prompt(company_name, url):
    user_prompt = f"""
You are looking at a company called: {company_name}
Here are the contents of its landing page and other relevant pages;
use this information to build a short brochure of the company in markdown without code blocks.\n\n
"""
    user_prompt += fetch_page_and_all_relevant_links(url)
    user_prompt = user_prompt[:5_000] # Truncate if more than 5,000 characters
    return user_prompt

def create_brochure(company_name, url):
    response = ollama.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": brochure_system_prompt},
            {"role": "user", "content": get_brochure_user_prompt(company_name, url)}
        ]
    )
    result = response.choices[0].message.content
    print (" /n Results of result of create_brochure:", result)
    return(result)
    #display(Markdown(result))


def Translate_brochure (SourceLangText):
    response = ollama.chat.completions.create (
        model= "mistral", #"deepseek-r1:1.5b",
        messages=[
            {"role":"system", "content": "You are a translator who translates from english to french" },
            {"role":"user", "content": SourceLangText}
        ]
    )
    Translatedresult= response.choices[0].message.content
    return(Translatedresult)

def main():
    ResultEng = create_brochure("ED-train", "https://edwarddonner.com")
    SourceLangText = ResultEng
    #SourceLangText = "I am a bright student who is studying python"
    TranslatedText = Translate_brochure (SourceLangText)
    print ("Results of translated text:", TranslatedText)
    

if __name__ == "__main__":
    main()
