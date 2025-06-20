# --------------------------------------------------------------------------
# Wikipedia Trend Finder (AI-Powered)
#
# This application takes a product description and ideal customer profile,
# uses the OpenAI API to find 10 highly relevant Wikipedia pages, and then
# generates a URL to track their pageview trends.
# --------------------------------------------------------------------------

import streamlit as st
from openai import OpenAI
import urllib.parse  # Used for correctly formatting titles in the URL

# --- Page & API Configuration ---
st.set_page_config(
    page_title="AI-Powered Topic Mining Tool",
    page_icon="📈",
    layout="centered",
    initial_sidebar_state="collapsed",
)

OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]

client = OpenAI(api_key=OPENAI_API_KEY)

# --- AI Function to Find Wikipedia Pages ---
def find_relevant_wiki_pages(api_key, product_desc, customer_profile):
    """
    Uses the GPT model to find 10 relevant Wikipedia page titles based on user input.

    Returns:
        A string of page titles separated by the '|' character, or None on failure.
    """
    if not api_key or "sk-proj" not in api_key:
        st.error("The hardcoded OpenAI API key appears to be invalid. Please check the script.")
        return None

    client = OpenAI(api_key=api_key)

    system_prompt = """
    You are an expert market researcher and SEO strategist. Your task is to identify highly relevant Wikipedia pages that an ideal customer for a given product might be interested in. These pages represent potential content marketing or advertising opportunities.
    """

    user_prompt = f"""
    **Product Description:**
    {product_desc}

    **Ideal Customer Profile:**
    {customer_profile}

    ---
    **Instructions:**
    1.  Analyze the product and customer profile to understand their core interests, problems, and related concepts.
    2.  Generate a list of exactly 10 highly relevant English Wikipedia page titles.
    3.  Format the titles as they appear in a Wikipedia URL (e.g., use underscores `_` instead of spaces, like `Sustainable_living`).
    4.  **CRITICAL:** Your entire response MUST BE ONLY these 10 titles, separated by a single vertical bar `|` character. Do not include any introductory text, explanations, numbers, or bullet points.

    **Example of a perfect response:**
    Sustainable_living|Circular_economy|Minimalism|Zero-waste_movement|Ethical_consumerism|Fair_trade|Slow_food|Community-supported_agriculture|Permaculture|B_Corporation
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.5,
        )
        page_titles_string = response.choices[0].message.content.strip()

        # Basic validation to ensure the AI followed instructions
        if '|' not in page_titles_string or len(page_titles_string.split('|')) < 5:
            raise ValueError("AI model did not return the expected pipe-separated format.")

        return page_titles_string
    except Exception as e:
        st.error(f"An error occurred while contacting the OpenAI API: {e}")
        return None

# --- Main Application ---
def main():
    """
    Renders the Streamlit user interface for the application.
    """
    st.title("📈 AI-Powered Topic Mining Tool")
    st.markdown("Describe your product and ideal customer. The system will find 10 relevant Wikipedia topics and generate a link to track their popularity.")

    with st.form("input_form"):
        product_desc = st.text_area(
            "**1. Enter your Product or Service Description**",
            height=150,
            placeholder="e.g., A subscription box for artisanal, ethically-sourced coffee beans from around the world. We focus on single-origin, specialty grade coffee."
        )
        customer_profile = st.text_area(
            "**2. Describe your Ideal Customer Profile**",
            height=150,
            placeholder="e.g., Environmentally conscious millennials, aged 25-40, living in urban areas. They appreciate quality over quantity, are interested in the story behind their products, and frequent local cafes."
        )
        submitted = st.form_submit_button("🚀 Find Relevant Topics", type="primary", use_container_width=True)

    if submitted:
        if not product_desc or not customer_profile:
            st.warning("⚠️ Please fill out both the product description and customer profile.")
        else:
            with st.spinner("🧠 gpt-4o is analyzing your input and finding relevant topics..."):
                wiki_pages_str = find_relevant_wiki_pages(OPENAI_API_KEY, product_desc, customer_profile)

            if wiki_pages_str:
                st.success("✅ Success! Found relevant topics.")

                # The pipe '|' separator should NOT be URL-encoded, but the page titles themselves should be.
                page_list = wiki_pages_str.split('|')
                encoded_pages = [urllib.parse.quote(page.strip()) for page in page_list]
                encoded_pages_str = '|'.join(encoded_pages)

                # This is the base URL provided in the user request
                base_url = "https://pageviews.wmcloud.org/?project=en.wikipedia.org&platform=all-access&agent=user&redirects=0&range=latest-20&pages="
                final_url = base_url + encoded_pages_str

                st.markdown("---")
                st.subheader("Your Custom Wikipedia Pageview URL")
                st.markdown("Click the button below to see the 20-day pageview trends for these topics. You can bookmark the link to monitor interest over time!")

                # Use a prominent link button for the primary action
                st.link_button("View Wikipedia Trends Now", final_url, use_container_width=True)

                st.markdown("---")
                # Display the topics found for user reference
                st.markdown("#### Topics Found by gpt-4o:")
                readable_pages = [p.replace('_', ' ').strip() for p in page_list]
                st.write(" • " + "\n • ".join(readable_pages))

            else:
                st.error("❌ Could not generate Wikipedia topics. The AI may be experiencing issues or the response was malformed. Please try rephrasing your input or try again in a moment.")

if __name__ == "__main__":
    main()
