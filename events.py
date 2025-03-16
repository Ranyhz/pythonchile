# Step 1: Import necessary modules and functions from helpers and llm
import streamlit as st
import numpy as np
import random
from unidecode import unidecode

# Import our helper functions – note that get_companies_data() is the new function to read your sheet
from helpers import get_companies_data, get_mask_for_keyword_list, create_card, add_color_to_cards
from llm import get_most_relevant_videos  # Keeping this if needed for flexible search

# Step 2: Define the display_search function to show companies from your cheat sheet
def display_search(df):
    """
    Displays the search bar interface for your Companies Cheat Sheet.
    This version uses your new headers:
    "Company", "Growth Rate (10% CAGR)", "FCF Yield (Exit Period)", "Predictability",
    "Sector", "Current Price", "Quality Level", "Past 5 Y Growth", "Notes", "Phase", "Moat", "5 year eps growth"
    """
    # Make a lowercase copy of the dataframe's columns for easy searching.
    df_lower = df.copy()
    df_lower.columns = [unidecode(s.lower().strip()) for s in df_lower.columns]
    for col in df_lower.columns:
        df_lower[col] = df_lower[col].apply(lambda x: unidecode(x.lower().strip()))
    
    # Choose the columns we want to display in the search results.
    # You can adjust this list as desired.
    show_cols = [
        "Company", 
        "Sector", 
        "Quality Level", 
        "Growth Rate (10% CAGR)", 
        "FCF Yield (Exit Period)", 
        "Notes"
    ]
    
    # Step 3: Update the page title and caption
    st.title('Companies Cheat Sheet')
    st.caption(f"Discover and analyze among the **{df.shape[0]}** companies in your cheat sheet.")
    
    # Step 4: Define search type options and set up search input.
    search_types = ["Exact Search", "Flexible Search"]
    search_type_sel = st.radio("How would you like to search?", search_types, horizontal=True)
    
    # Set up a placeholder example for search terms.
    ejemplos = ["tech", "finance", "growth", "high quality"]
    if "ejemplo" not in st.session_state:
        st.session_state.ejemplo = ejemplos[random.randint(0, len(ejemplos)-1)]
    
    # Depending on the search type, set up the appropriate search input.
    if search_type_sel == search_types[0]:
        c1, c2 = st.columns([5, 1])
        text_search = c1.text_input(
            "Search by company name, sector, quality, or notes. Separate terms with a semicolon (;)",
            placeholder=st.session_state.ejemplo
        )
        text_search = unidecode(text_search.lower())
        # Split search text into keywords.
        keyword_list = [keyword.strip() for keyword in text_search.split(";") if keyword.strip() != ""]
    else:
        # Flexible search uses a single text input.
        text_search = st.text_input(
            "Type what you would like to learn about companies",
            placeholder=st.session_state.ejemplo
        )
    
    # Step 5: Set up layout parameters for displaying cards.
    N_cards_per_col = 5

    # Step 6: Perform search and display results if there is search input.
    if text_search:
        if search_type_sel == search_types[0]:
            # Get a mask for keywords using helper function.
            mask = get_mask_for_keyword_list(df_lower, keyword_list, search_cols=["company", "sector", "quality level", "notes"])
            df_search = df.loc[mask, show_cols].reset_index(drop=True)
        else:
            # For flexible search, use the LLM-based search method.
            index_list = get_most_relevant_videos(text_search, df, openai_api_key=st.secrets["OPENAI_API_KEY"])
            df_search = df.loc[index_list, show_cols].reset_index(drop=True)
        
        # Display the search results as cards.
        for n_row, row in df_search.iterrows():
            i = n_row % N_cards_per_col
            if i == 0:
                st.write("")
                cols = st.columns(N_cards_per_col, gap="large")
            # Using create_card to display each company card.
            create_card(row, cols[n_row % N_cards_per_col])
    else:
        # If no search text is provided, show a default selection.
        N_cards = N_cards_per_col * 1
        st.write("#### Latest Companies")
        df_latest = df[show_cols].head(N_cards).reset_index(drop=True)
        for n_row, row in df_latest.iterrows():
            i = n_row % N_cards_per_col
            if i == 0:
                st.write("")
                cols = st.columns(N_cards_per_col, gap="large")
            create_card(row, cols[n_row % N_cards_per_col])
        st.write("")
        st.write("#### Random Companies")
        df_random = df[show_cols].sample(N_cards).reset_index(drop=True)
        for n_row, row in df_random.iterrows():
            i = n_row % N_cards_per_col
            if i == 0:
                st.write("")
                cols = st.columns(N_cards_per_col, gap="large")
            create_card(row, cols[i])
    
    # Step 7: Apply additional styling to the cards.
    add_color_to_cards()

# If this file is run directly, use get_companies_data() to display the search interface.
if __name__ == "__main__":
    # Call the new function from helpers.py to get your companies data.
    df = get_companies_data()
    display_search(df)
