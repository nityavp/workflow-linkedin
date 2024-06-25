import streamlit as st
import requests
import json
import re

# Function to make search request to Serper API
def serper_search(query, api_key):
    url = "https://google.serper.dev/search"
    headers = {
        'X-API-KEY': api_key,
        'Content-Type': 'application/json'
    }
    payload = json.dumps({"q": query})
    response = requests.post(url, headers=headers, data=payload)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Error: {response.status_code}")
        return None

# Function to analyze a URL with Jina
def analyze_with_jina(url):
    api_url = f"https://r.jina.ai/{url}"
    headers = {
        'X-With-Links-Summary': 'true',
        'Accept': 'application/json'
    }
    response = requests.get(api_url, headers=headers)
    if response.status_code == 200:
        jina_results = response.json()
        
        # Remove specific URLs from Jina results
        cleaned_results = remove_specific_urls_from_jina_response(jina_results)
        
        return cleaned_results
    else:
        st.error(f"Jina Error: HTTP {response.status_code}")
        return None

# Function to remove specific URLs from Jina AI response
def remove_specific_urls_from_jina_response(jina_results):
    try:
        # List of URLs to remove
        urls_to_remove = [
            "https://in.linkedin.com/in/amit-sunderiyal-b486766?trk=org-employees",
            "https://www.linkedin.com/signup?session_redirect=https%3A%2F%2Fwww%2Elinkedin%2Ecom%2Fsearch%2Fresults%2Fpeople%2F%3FfacetCurrentCompany%3D%255B74912%255D&trk=public_biz_employees-join",
            "https://in.linkedin.com/company/force-motors?trk=organization_guest_main-feed-card_feed-actor-name",
            "https://www.linkedin.com/uas/login?fromSignIn=true&session_redirect=https%3A%2F%2Fin.linkedin.com%2Fcompany%2Fforce-motors&trk=organization_guest_main-feed-card_ellipsis-menu-semaphore-sign-in-redirect&guestReportContentType=POST&_f=guest-reporting"
        ]
        
        # Regular expression pattern to match URLs
        url_pattern = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+'
        
        # Check if 'data' key exists in the response
        if 'data' in jina_results:
            # Iterate through 'data' fields to remove specific URLs
            for key, value in jina_results['data'].items():
                if isinstance(value, str):
                    # Remove specific URLs from string fields
                    jina_results['data'][key] = re.sub("|".join(map(re.escape, urls_to_remove)), '', value)
                elif isinstance(value, list):
                    # Remove specific URLs from list of strings
                    jina_results['data'][key] = [re.sub("|".join(map(re.escape, urls_to_remove)), '', item) if isinstance(item, str) else item for item in value]
        
        return jina_results
    except KeyError as e:
        st.error(f"KeyError: {e}")
        return None

# Function to process text with OpenAI
def process_with_openai(text, openai_api_key):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {openai_api_key}'
    }
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "Analyze the following content:"},
            {"role": "user", "content": text}
        ]
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content']
    else:
        st.error(f"OpenAI Error: HTTP {response.status_code}")
        return None

# Streamlit app setup
st.title("Advanced Company Analysis with LinkedIn, Jina, and OpenAI")

# User inputs
company_name = st.text_input("Enter the company name")
serper_api_key = st.text_input("Enter your Serper API key", type="password")
openai_api_key = st.text_input("Enter your OpenAI API key", type="password")

if st.button("Analyze Company LinkedIn Page"):
    if company_name and serper_api_key and openai_api_key:
        # Perform search on LinkedIn via Serper API
        linkedin_query = f"LinkedIn {company_name}"
        search_results = serper_search(linkedin_query, serper_api_key)
        if search_results and search_results['organic']:
            # Extract the first URL
            first_url = search_results['organic'][0]['link']
            st.write("First LinkedIn URL:", first_url)
            
            # Analyze the URL with Jina
            jina_result = analyze_with_jina(first_url)
            if jina_result:
                st.write("Jina Analysis Results:")
                st.json(jina_result)  # Display Jina results as JSON
                
                # Process Jina results with OpenAI
                if 'data' in jina_result:
                    jina_text = extract_text_from_jina_results(jina_result)
                    openai_result = process_with_openai(jina_text, openai_api_key)
                    if openai_result:
                        st.write("OpenAI Processed Results:")
                        st.text(openai_result)
                else:
                    st.error("No 'data' found in Jina results.")
        else:
            st.error("No results found or failed to fetch results.")
    else:
        st.error("Please provide the company name, Serper API key, and OpenAI API key.")

# Function to extract text from Jina results
def extract_text_from_jina_results(jina_results):
    text = ""
    try:
        if 'data' in jina_results:
            for key, value in jina_results['data'].items():
                if isinstance(value, str):
                    text += value + "\n"
                elif isinstance(value, list):
                    text += ' '.join(value) + "\n"
    except KeyError as e:
        st.error(f"KeyError: {e}")
    return text.strip()



