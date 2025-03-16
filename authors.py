# Step 1: Import Streamlit and helper functions
import streamlit as st
from helpers import *
from unidecode import unidecode

# Step 2: Function to clear query parameters (unchanged)
def on_click():
    st.query_params.clear()

# Step 3: Update the function to load authors data
def get_authors_data():
    # Updated gsheet_id to use your new Google Sheet
    gsheet_id = "1-aMvoUEzRVhd5Ag1kF-0gZYq7iVnn8taVr_Hjj2Kqi8"
    # Data for the authors (personas) from the "personas" sheet.
    df_authors = read_googlesheet(gsheet_id, "personas", ["Autor"])
    # Add a column with the clean name for easier matching later.
    df_authors["author_clean_name"] = df_authors["Autor"].apply(clean_name)
    # Normalize the column names: convert to lowercase and remove extra spaces.
    df_authors.columns = [unidecode(s.lower().strip()) for s in df_authors.columns]
    return df_authors

# Step 4: Function to check if a given author exists in the authors data.
def is_author_in_authors(df_authors, author):
    author_clean_name = clean_name(author)
    return author_clean_name in df_authors["author_clean_name"].values

# Step 5: Function to display the author's page with their talks (or companies if adapted)
def display_author(df_authors, df_events, author_search_name):
    # Page header for the authors section.
    st.caption('Python Chile: Autores')
    author_clean_name = clean_name(author_search_name)
    # Filter events/talks (or companies) associated with the author.
    df_author_events = df_events.loc[df_events["author_clean_name"] == author_clean_name, :].reset_index()
    if len(df_author_events) == 0:
        display_404_author(author_search_name)
        return
    # Get social media links for the author from df_authors.
    df_author_links = df_authors.loc[df_authors["author_clean_name"] == author_clean_name, :].reset_index()
    if len(df_author_links) > 0:
        companies_list = ["twitter", "linkedin", "github"]
        known_companies_html = []
        for company in companies_list:
            if company in df_author_links.columns:
                link = df_author_links[company].values[0]
                if len(link) > 0:
                    image_link = f"https://github.com/sebastiandres/st_pythonchile/blob/main/images/social_media_icons/{company}.png?raw=true"
                    html = clickable_image_html(link, image_link, style="width:25px;")
                    known_companies_html.append(html)
        html_social_media = "".join(known_companies_html)
    else:
        html_social_media = " "
    # Display the author's name and social media links.
    author_display_name = df_author_events["Autor"].values[0]
    st.title(author_display_name)
    st.components.v1.html(html_social_media, height=50)
    # Display cards for each event/talk/company associated with the author.
    N_cards_per_col = 5
    for n_row, row in df_author_events.iterrows():
        i = n_row % N_cards_per_col
        if i == 0:
            st.write("")
            cols = st.columns(N_cards_per_col, gap="large")
        create_card(row, cols[n_row % N_cards_per_col])
    add_color_to_cards()

# Step 6: Display a 404 message if the author is not found.
def display_404_author(author):
    st.title("404")
    st.write(f"No se encontró el autor {author} entre los autores registrados.")
    st.button("Volver a la página principal", on_click=on_click)
