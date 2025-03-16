"""
This module uses a Large Language Model (via LangChain and OpenAI)
to allow a more flexible search engine for your companies cheat sheet.
It returns the indices of the most relevant companies (from your sheet)
for a given query. For example, queries like:
- "tech"
- "high quality growth"
- "finance, strong moat"
will be processed to return a list of company indices sorted from most to least relevant.
"""

# Import necessary LangChain and helper functions
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import ResponseSchema
from langchain.output_parsers import StructuredOutputParser

# IMPORTANT: Update the import to use the companies data function
from helpers import get_companies_data

def get_most_relevant_companies(user_query, df, openai_api_key):
    """
    This function takes a user query and a dataframe (your companies cheat sheet),
    and returns a list of indices corresponding to the most relevant companies for that query.
    """
    # Convert the dataframe to a markdown table only for columns of interest.
    # Updated to use new headers: "Company", "Sector", and "Notes".
    df_md = df[["Company", "Sector", "Notes"]].to_csv()
    
    # Create a prompt template adjusted for companies.
    prompt_template_str = """
    Using the table provided in markdown format, find the most relevant companies 
    for the user query provided below. 
    You must return a list of indices of the companies in the dataframe that are
    relevant to the query. Do not return more indices than are necessary.
    Do not return more than a maximum of 10 indices.
    The list must be sorted and provided as a Python list of integers.
    The values of the integers correspond to the indices of the companies in the dataframe.
    The output should be a Python list of integers as a comma-separated string, 
    from the most relevant to the least relevant. For example, if the most relevant
    company is the 12th, then the second is the 0th, then the third is the 4th, then:
    ```
    [12, 0, 4]
    ```
    The query will be provided by the user, delimited by triple backticks like ```this```.

    Dataframe:
    {data}

    Query:
    ```
    {query}
    ```
    """

    # Create the prompt template from the string above.
    prompt_template = ChatPromptTemplate.from_template(prompt_template_str)
    
    # Initialize the LLM using OpenAI with zero temperature for deterministic results.
    llm = ChatOpenAI(openai_api_key=openai_api_key, temperature=0.0)
    
    # Format the prompt with the dataframe markdown and the user query.
    query_prompt = prompt_template.format_messages(
                            data=df_md,
                            query=user_query)
    
    # Send the prompt to the LLM and get the response.
    full_answer = llm(query_prompt)
    
    # Clean the answer by removing backticks and extra text.
    answer = full_answer.content.replace("```", "").replace("python", "").strip()
    
    # Evaluate the answer string to a Python list.
    indexes_str = eval(answer)
    indexes_list = list(indexes_str)
    return indexes_list

if __name__ == "__main__":
    # Load the OpenAI API key from Streamlit secrets (ensure your .streamlit/secrets.toml is updated).
    import toml
    openai_api_key = toml.load(".streamlit/secrets.toml")["OPENAI_KEY"]
    
    # Load the companies dataframe instead of events
    df = get_companies_data()
    
    # Example user query; adjust as needed.
    user_query = "tech companies with high growth and strong moat"
    
    # Get the sorted list of indices for the companies most relevant to the query.
    indexes = get_most_relevant_companies(user_query, df, openai_api_key)
    
    # Filter the dataframe to only show the relevant companies and print the result.
    df_search = df.loc[indexes]
    print(df_search)
