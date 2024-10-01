# Blog-Generation
1. Create main.py (Colab/Kaggle) i.e for FASTAPI endpoints which consist of uploading the model, scrapping the text, create endpoint for blog generation which consist of prompt template.
2. Then used ngork (colab/Kaggle) to expose the backend part of the fastapi endpoints and generating URL.
3. Then used streamlit locally on machine to create app.py (http://192.168.204.13:8501) based on the Ngork URL using Requests.

app.py file is the streamlit file for the FastApi, Ngork tunnel of the GPT-neo:2.7B instruct
