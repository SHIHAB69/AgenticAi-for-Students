import streamlit as st
import requests
from PIL import Image
from io import BytesIO

def fetch_routine_image(batch_section):
    """
    Fetches the routine image for the specified batch and section.

    Args:
        batch_section (str): The batch and section in the format 'batch+section' (e.g., '44c').

    Returns:
        Image: A PIL Image object if the image is fetched successfully.
        str: An error message if the image is not found or fails to load.
    """
    # Construct the URL for the routine image
    url = f"https://diuroutine.com/static/routines/{batch_section.upper()}.jpg"
    
    try:
        response = requests.get(url)

        if response.status_code == 200:
            return Image.open(BytesIO(response.content))
        else:
            return f"No routine found for {batch_section.upper()}."
    except Exception as e:
        return f"Error fetching the routine: {e}"

# Streamlit App
st.title("DIU Class Routine Finder")

# Input for batch and section
batch_section = st.text_input("Enter your batch and section (e.g., '44c'):")

if st.button("Get Routine"):
    if batch_section:
        result = fetch_routine_image(batch_section.strip())

        if isinstance(result, str):
            st.error(result)  # Show error message
        else:
            st.image(result, caption=f"Routine for {batch_section.upper()}", use_container_width=True)
    else:
        st.error("Please enter a valid batch and section.")
