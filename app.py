import streamlit as st
import requests
import json

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
        "X-With-Links-Summary": "true"
    }
    response = requests.get(api_url, headers=headers)
    if response.status_code == 200:
        return response.text  # Return raw text from the response
    else:
        st.error(f"Jina Error: HTTP {response.status_code}")
        return None

# Streamlit app setup
st.title("Company LinkedIn Page Analyzer")

# User inputs
company_name = st.text_input("Enter the company name")
serper_api_key = st.text_input("Enter your Serper API key", type="password")

if st.button("Analyze Company LinkedIn Page"):
    if company_name and serper_api_key:
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
                # Display Jina analysis results
                st.write("Jina Analysis Results:")
                st.text(jina_result)
        else:
            st.error("No results found or failed to fetch results.")
    else:
        st.error("Please provide the company name and Serper API key.")