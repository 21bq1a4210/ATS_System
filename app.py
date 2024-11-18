from dotenv import load_dotenv
import base64
import streamlit as st
import os
import io
from PIL import Image 
import pdf2image
import google.generativeai as genai

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function to get the response from Gemini model
def get_gemini_response(input, pdf_content, prompt):
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content([input, pdf_content[0], prompt])
    return response.text

# Function to process uploaded PDF
def input_pdf_setup(uploaded_file):
    if uploaded_file is not None:
        # Convert PDF to images
        images = pdf2image.convert_from_bytes(uploaded_file.read())
        num_pages = len(images)

        # Take the first two pages (or less if single page)
        pages_to_process = images[:2]

        # Convert to bytes
        pdf_parts = []
        for page in pages_to_process:
            img_byte_arr = io.BytesIO()
            page.save(img_byte_arr, format='JPEG')
            img_byte_arr = img_byte_arr.getvalue()
            pdf_parts.append({
                "mime_type": "image/jpeg",
                "data": base64.b64encode(img_byte_arr).decode()  # encode to base64
            })

        return pdf_parts, num_pages
    else:
        raise FileNotFoundError("No file uploaded")

# Streamlit App
st.set_page_config(page_title="ATS Resume Expert")
st.header("ATS Tracking System")
input_text = st.text_area("Job Description: ", key="input")
uploaded_file = st.file_uploader("Upload your resume (PDF)...", type=["pdf"])

if uploaded_file is not None:
    st.write("PDF Uploaded Successfully")

submit1 = st.button("Tell Me About the Resume")
submit3 = st.button("Percentage Match")

# Updated prompts
input_prompt1 = """
You are an experienced Technical Human Resource Manager. 
Evaluate the provided resume against the given job description. Your analysis should:
1. Assess the alignment of the candidate's profile with the role.
2. Highlight strengths and weaknesses in relation to the job requirements.
3. Offer actionable suggestions to improve the resume for better suitability.
"""

input_prompt3 = """
You are a highly skilled ATS (Applicant Tracking System) scanner with expertise in data science and recruitment processes. 
Evaluate the resume against the provided job description and:
1. Provide a percentage match between the resume and the job description.
2. List critical missing keywords.
3. Offer a concise summary with recommendations for improving the match.
"""

if submit1:
    if uploaded_file is not None:
        pdf_content, num_pages = input_pdf_setup(uploaded_file)
        response = get_gemini_response(input_text, pdf_content, input_prompt1)
        st.subheader("The Response is")
        st.write(response)
    else:
        st.write("Please upload the resume.")

elif submit3:
    if uploaded_file is not None:
        pdf_content, num_pages = input_pdf_setup(uploaded_file)
        response = get_gemini_response(input_text, pdf_content, input_prompt3)
        st.subheader("The Response is")
        st.write(response)
    else:
        st.write("Please upload the resume.")
