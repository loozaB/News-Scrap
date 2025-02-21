import pandas as pd
import streamlit as st
import requests
from bs4 import BeautifulSoup
import re

def fetch_link(portal_name):
    if portal_name == "Select":
        return "None"
    elif portal_name == "OnlineKhabar":
        url = "https://www.onlinekhabar.com/latest"
    elif portal_name == "CNN":
        url = "https://edition.cnn.com/world"
    elif portal_name == "Reuters":
        url = "https://www.reuters.com/world"
    else:
        return "Portal not available."

    response = requests.get(url)

    # Check if the response is successful
    if response.status_code == 200:
        # Parsing the page content with BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extraction
        if portal_name == "OnlineKhabar":
            extract = soup.find_all(class_="ok-news-post")
        elif portal_name == "CNN":
            extract = soup.find_all('span', class_="cd__headline-text")
        elif portal_name == "Reuters":
            extract = soup.find_all('h3')

        news_link = []
        for x in extract:
            k=x.find('a')
            news_link.append(k['href'])

        # Extracting text from the link
        title_list=[]
        for link in news_link[:10]:
            response = requests.get(link)
            #if response.status_code == 200:
            response.encoding = 'utf-8'
            soup=BeautifulSoup(response.text, 'html.parser')
            title = soup.find('h1', class_="entry-title")
            if title is not None:
                title_list.append(title.text.strip())
            #else:
                #print("Failed!")  
        
        df = pd.DataFrame(title_list, columns=['Title'])
        return news_link, df
    else:
        return "Failed to retrieve data."

def fetch_news(portal_name , news_link):
    all_files = []
    for link in news_link[:10]: 
            response=requests.get(link)
            if response.status_code==200:
                response.encoding = 'utf-8'
                soup=BeautifulSoup(response.text,'html.parser')
                if portal_name == "OnlineKhabar":
                    title = soup.find('h1', class_="entry-title")
                    if title is not None:
                        title = title.get_text()
                        filename=f"{title}.txt"
                        valid_filename = re.sub(r'[<>:"/\\|?*]', '', filename)
                        content = soup.find(class_="ok18-single-post-content-wrap")

                if content:
                    with open(valid_filename, 'w', errors='ignore', encoding='utf-8') as file:
                        file.write(content.get_text())
                        file.write('\n')

                    with open(valid_filename, 'r', encoding='utf-8') as file:
                        file_data = file.read()
                
                    all_files.append({
                    'filename': valid_filename,
                    'file_data': file_data
                    })
                else:
                    st.write(f"Content not found for {title}")
            else:
                st.write("Failed!")
    
    return all_files

# Streamlit UI elements
st.title('News Scrapping Nepal')

# Dropdown to select news portal
portal_name = st.selectbox("Select a news portal:", ["Select","OnlineKhabar", "CNN", "Reuters"])

news_link = None
titles = None


    
news_link, titles = fetch_link(portal_name)
st.write(f"Displaying top news from {portal_name}:")
if isinstance(titles, pd.DataFrame):
        st.dataframe(titles)  
else:
        st.write(titles)  
    
st.write("If you want to scrap news contents as seperate files for all above news headlines, Click below.")
if st.button("Scrap News Content"):
        if news_link is not None:
            contents =  fetch_news(portal_name, news_link)
            if contents:
                st.write("Download completed! Check the folder location of this file.")
                # for file in contents:
                #     st.download_button(
                #     label=f"Download {file['filename']}",
                #     data=file['file_data'],
                #     file_name=file['filename'],
                #     mime="text/plain"
                #     )   
            else:
                st.write("No content to download.")
        else:
            st.write("Failed scrapping titles!")