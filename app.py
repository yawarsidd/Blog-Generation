import streamlit as st
import requests

st.title("Blog Generator")

st.write("Input multiple URLs, multiple paragraph indices, and specify the desired word count to generate blogs.")

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
            # Send request to the FastAPI backend
            response = requests.post("https://9205-34-123-190-61.ngrok-free.app/generate_blog",  # Replace with your ngrok URL
                                     json={"urls_and_indices": urls_and_indices, "no_words": no_words})

            if response.status_code == 200:
                generated_blogs = response.json().get("blogs", [])
                # Display each blog
                for i, blog in enumerate(generated_blogs):
                    st.subheader(f"Blog {i + 1}")
                    st.write(blog)

                    # Create a download button for the blog
                    st.download_button(
                        label="Download Blog Post",
                        data=blog,
                        file_name=f"blog_post_{i + 1}.txt",
                        mime="text/plain"
                    )
            else:
                st.error("Error generating blogs.")

# http://192.168.204.13:8501