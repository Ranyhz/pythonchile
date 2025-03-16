# This are shared functions used in the app and the dashboard   
import streamlit as st
import pandas as pd
import numpy as np
from unidecode import unidecode
import random
from collections import defaultdict
#from IPython import embed

# Image dictionary remains unchanged
image_dict = defaultdict(lambda: "https://github.com/sebastiandres/st_pythonchile/blob/main/images/python_chile.png?raw=true")
image_dict["Pycon 2022"] = "https://github.com/sebastiandres/st_pythonchile/blob/main/images/pycon_2022.png?raw=true"
image_dict["Pyday 2020"] = "https://github.com/sebastiandres/st_pythonchile/blob/main/images/pyday_2020.png?raw=true"
image_dict["Sin registro"] = "https://github.com/sebastiandres/st_pythonchile/blob/main/images/sin_registro.png?raw=true"

# -------------------------------------------------------------------------
# STEP 1: NEW FUNCTION TO READ YOUR COMPANIES CHEAT SHEET DATA
# -------------------------------------------------------------------------
def get_companies_data():
    # Updated gsheet_id: new spreadsheet for your cheat sheet data
    gsheet_id = "1-aMvoUEzRVhd5Ag1kF-0gZYq7iVnn8taVr_Hjj2Kqi8"
    # Update the sheet name: adjust "Sheet1" if your sheet is named differently.
    # Also, update the sort_columns as needed – here we sort by "Company".
    df = read_googlesheet(gsheet_id, "Sheet1", ["Company"])
    # Clean up column names (this will convert headers like "Growth Rate (10% CAGR)" correctly)
    df.columns = [unidecode(s.strip()) for s in df.columns]
    # Filter out rows with empty "Company" values – adjust as necessary for your data.
    df = df.loc[df["Company"] != "", :]
    return df

# -------------------------------------------------------------------------
# ORIGINAL FUNCTION (for events/talks) remains here in case you need it.
# If not used, you can eventually remove or comment it out.
# -------------------------------------------------------------------------
def get_events_data():
    # Shared gsheet_id for events data (old sheet)
    gsheet_id = "15iKaOhNSVoX6xb2zRDi-oPl0Bd9Dz2RuJFFfD5JDzw4"
    # Data for the talks (charlas)
    df = read_googlesheet(gsheet_id, "charlas", ["Fecha", "Orden", "Track"])
    df.columns = [ unidecode(s.strip()) for s in df.columns]
    df["author_clean_name"] = df["Autor"].apply(clean_name)
    df = df.loc[df["Autor"] != "", :] # Filter out empty rows
    df = df.loc[df["Titulo"] != "", :] # Filter out empty rows
    return df

# -------------------------------------------------------------------------
# Utility functions remain unchanged
# -------------------------------------------------------------------------
def clean_name(name):
    """
    Cleans up the author's name by removing spaces and special characters.
    """
    return unidecode(name.strip().replace(" ", "").replace(r"%20","").lower())

def read_googlesheet(sheet_id, sheet_name, sort_columns):
    """
    Reads a Google Sheet and returns a dataframe sorted by the columns in sort_columns.
    If the public Google Sheet URL is "https://docs.google.com/spreadsheets/d/1nctiWcQFaB5UlIs6z8d1O6ZgMHFDMAoo3twVxYnBUws/edit?usp=sharing",
    then the sheet_id is "1nctiWcQFaB5UlIs6z8d1O6ZgMHFDMAoo3twVxYnBUws".
    The sheet_name is the name of the sheet in the Google Sheet.
    """
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    df = pd.read_csv(url, dtype=str).fillna("")
    df = df.sort_values(sort_columns, ascending=False, ignore_index=True)
    return df

def html_link(text, link, blank=True):
    # Returns an HTML anchor tag with target set to _blank if desired.
    if blank:
        return f'<a target="_blank" href="{link}">{text}</a>'
    else:
        return f'<a target="_top" href="{link}">{text}</a>'

def get_mask_for_keyword(df, keyword, search_cols=["autor", "titulo"]):
    """
    Returns a boolean mask from a dataframe based on the presence of a keyword in specified columns.
    """
    m = False
    for col in search_cols:
        m = np.logical_or(df[col].str.contains(keyword), m)
    return m

def clickable_image_html(link, image_link, style="width:100%;"):
    html = f'<a href="{link}" target="_blank"><img src="{image_link}" style="{style}"></a>'
    return html

def get_mask_for_keyword_list(df, keyword_list, search_cols=["autor", "titulo"]):
    """
    Returns a boolean mask from a dataframe based on a list of keywords.
    """
    m = False
    for keyword in keyword_list:
        m = np.logical_or(get_mask_for_keyword(df, keyword, search_cols), m)
    return m

def create_card(row, c):
    """
    Creates a card with the information of a row, using Streamlit elements.
    (Note: This function is designed for event data. If not used in your new app, you may eventually remove or modify it.)
    """
    link = row["Video"].strip()
    evento = row["Evento"].strip()
    if link != "Sin registro":
        image_link = image_dict[evento]
        clickable_image = f'<a href="{link}" target="_blank"> <img src="{image_link}" style="width:100%;"> </a>'
    else:
        image_link = image_dict["Sin registro"]
        clickable_image = f'<img src="{image_link}" style="width:100%;">'
    with c:
        st.caption(f"{row['Evento'].strip()} - {row['Lugar'].strip()} - {row['Fecha'].strip()} ")
        authors_html_list = []
        for author in row["Autor"].split(";"):
            authors_html_list.append(html_link(author, f"/?author={author}", blank=True))
        authors_html = " | ".join(authors_html_list)
        st.markdown(authors_html + clickable_image, unsafe_allow_html=True)
        st.markdown(f"{row['Tipo'].strip()}: {row['Titulo'].strip()}")

def add_style():
    """
    Adds CSS style so links are not blue.
    """
    style = """
    a:link {
    color: inherit;
    text-decoration: none;
    }

    a:visited {
    color: inherit;
    text-decoration: none;
    }

    a:hover {
    color: red;
    text-decoration: underline;
    }

    a:active {
    color: red;
    text-decoration: underline;
    }
    """
    my_html = f"""
                <style>
                {style} 
                </style>
                """
    st.components.v1.html(my_html, height=0, width=0)

def add_color_to_cards():
    """
    Adds color styling to the expanders/cards.
    """
    my_js = """
    var cards = window.parent.document.getElementsByClassName("css-vhjbnf");
    for (var i = 0; i < cards.length; i++) {
        let card = cards[i];
        N_chars_in_cards = String(card.firstChild.innerHTML).length;
        if (N_chars_in_cards > 100){
            card.style.border = "solid";
            card.style.borderColor = "#E4F6F8";
            card.style.borderWidth = "2px";
            card.style.padding = "10px";
            card.style.borderRadius = "10px";
            card.addEventListener("mouseover", function(event){card.style.borderColor = "red"})
            card.addEventListener("mouseout",  function(event){card.style.borderColor = "#E4F6F8"})
        }
    }    
    """
    my_html = f"""
                <script>
                {my_js}
                </script>
                """
    st.components.v1.html(my_html, height=0, width=0)
    return
