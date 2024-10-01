import os
import streamlit as st
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
from huggingface_hub import login
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get Hugging Face API key from environment variables
huggingface_key = os.getenv('HUGGINGFACE_API_KEY')

# Log in to Hugging Face with the API key
login(huggingface_key)

st.write("Logged in to Hugging Face successfully!")

# Load the model and tokenizer
tokenizer = AutoTokenizer.from_pretrained("EleutherAI/gpt-neo-2.7B")
model = AutoModelForCausalLM.from_pretrained("EleutherAI/gpt-neo-2.7B")

# Streamlit app
st.title("Blog Generator")

st.write("Input multiple URLs, multiple paragraph indices, and specify the desired word count to generate blogs.")

# Function to scrape specific paragraphs from a webpage
def scrape_specific_paragraphs(url, indices):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    paragraphs = soup.find_all('p')

    selected_paragraphs = []
    for index in indices:
        if index < len(paragraphs):
            selected_paragraphs.append(paragraphs[index].get_text())
        else:
            selected_paragraphs.append(f"Paragraph index {index} out of range.")

    return selected_paragraphs

# Function to generate blog using GPT-Neo
def get_gpt2_response(specific_paragraphs, no_words):
    template = f"""
    You are a blog writer. Generate a blog within {no_words} words based on the following content: {' '.join(specific_paragraphs)}
    
    Structure:
    1. **Introduction**: Briefly introduce the topic.
    2. **Main Points**:
       - Discuss the significance.
       - Discuss various perspectives.
       - Discuss practical applications.
    3. **Conclusion**: Summarize the main ideas.

    Make sure the blog is engaging, informative, and easy to read, avoiding any repetition and ensuring a coherent flow of ideas.
    """

    inputs = tokenizer(template, return_tensors="pt", max_length=700, truncation=True)
    with torch.no_grad():
        output = model.generate(**inputs,
                                max_length=700, 
                                num_return_sequences=1, 
                                temperature=1, 
                                top_k=50, 
                                do_sample=True,
                                top_p=0.95)

    response = tokenizer.decode(output[0], skip_special_tokens=True)
    return response

# Function to scrape and generate blogs
def generate_blogs_from_urls(urls_and_indices, no_words):
    results = []

    def generate_blog(url, indices):
        specific_paragraphs = scrape_specific_paragraphs(url, indices)
        blog_response = get_gpt2_response(specific_paragraphs, no_words)
        results.append(blog_response)

    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(generate_blog, url, indices) for url, indices in urls_and_indices]
        for future in futures:
            future.result()

    return results

# User input
urls = st.text_area("Enter the URLs (one per line)", 'https://byjus.com/cbse/essay-on-constitution-of-india/\nhttps://byjus.com/physics/renewable-energy/')
indices_input = st.text_area("Enter the corresponding paragraph indices for each URL (comma-separated, one set per line)", "0,1,2\n1,2,3")
no_words = st.number_input("Enter the number of words for each blog", value=400)

# Process inputs
urls_list = urls.splitlines()
indices_list = [list(map(int, indices.split(','))) for indices in indices_input.splitlines()]

# Ensure the number of URLs and indices match
if len(urls_list) != len(indices_list):
    st.error("The number of URLs and the number of indices sets must match.")
else:
    # Start blog generation on button click
    if st.button("Generate Blogs"):
        urls_and_indices = list(zip(urls_list, indices_list))
        
        with st.spinner("Generating blogs..."):
            generated_blogs = generate_blogs_from_urls(urls_and_indices, no_words)
        
        # Display each blog
        for i, blog in enumerate(generated_blogs):
            st.subheader(f"Blog {i + 1}")
            st.write(blog)
