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
        st.error(f"Error from Serper API: {response.status_code}")
        return None

# Function to analyze a URL with Jina
def analyze_with_jina(url):
    api_url = f"https://r.jina.ai/{url}"
    headers = {
        "Accept": "application/json"
    }
    response = requests.get(api_url, headers=headers)
    if response.status_code == 200:
        return response.text  # Return raw text from the response
    else:
        st.error(f"Jina Error: HTTP {response.status_code}")
        return None

# Function to preprocess text: remove all after a certain line
def trim_text_at_marker(text, marker="*   some text *"):
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if marker in line:
            return "\n".join(lines[:i+1])  # Return text including the marker line and everything before
    return text

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
        st.error(f"OpenAI Error: HTTP {response.json()}")
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
                # Preprocess to remove text after a specific line
                preprocessed_text = trim_text_at_marker(jina_result)
                result_input ="This is my competitor's LinkedIn profile content, tell me in bullet points after analyzing what all can I learn from it"+ preprocessed_text
                final_result_input=result_input[:16000]
                # Process preprocessed text with OpenAI
                openai_result = process_with_openai(final_result_input, openai_api_key)
                if openai_result:
                    st.write("OpenAI Processed Results:")
                    st.text(openai_result)
                else:
                    st.write("Failed to process text with OpenAI due to API error.")
            else:
                st.write("Failed to get a valid response from Jina.")
        else:
            st.error("No results found or failed to fetch results from Serper.")
    else:
        st.error("Please provide the company name, Serper API key, and OpenAI API key.")









