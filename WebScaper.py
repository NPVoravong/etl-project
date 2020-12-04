# This Activity exactly mirrors the step reuired for part 1 of the project
"""
you will scrape the following information from http://quotes.toscrape.com/

quote text
tags
Author name
Author Details
-born
-description

Store the collected information into MongoDB( you can use Mongo atlas for this)
"""

# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
# Dependencies
from bs4 import BeautifulSoup
import requests
import psycopg2 # for Postgres database connection
import pymongo # for MongoDB database connection
import pandas as pd
from sqlalchemy import create_engine
import time

# %%
# Method Definitions
def getAuthor(url):
    result = {}
    response = requests.get(url)
    #print("author urls good")
    soup = BeautifulSoup(response.text,"lxml")
    result['name'] = soup.h3.text.strip()
    result['born'] = soup.find('span', class_ = 'author-born-date').text.strip()
    result['description'] = soup.find('div', class_ = 'author-description').text.strip()
    return result

def normalize_quotes_data(docs):
    quotes_table = []
    author_names = []
    authors_table = []
    tags_table = []
    id = 1
    for doc in docs.find({}):
#         print(f"normalizing the quote : [{doc['_id']}]")
        quote = {}
#        quote['id'] = doc['_id'].str #psycopg2 had trouble with ObjectId type, so I override it.
        quote['id'] = id
        id += 1
        quote['text'] = doc['text']
        quote['author_name'] = doc['author']['name']
        quotes_table.append(quote)

        author = {}
        author['name'] = doc['author']['name']
        author['born'] =  doc['author']['born']
        author['description'] = doc['author']['description']
        if (author['name'] not in author_names):
            authors_table.append(author)
            author_names.append(author['name'])

        for tag in doc['tags']:
            tags_table.append({'quote_id':quote['id'] , 'tag' : tag})    
            
    return (quotes_table , authors_table ,tags_table) 
# %%    
def migrate():
    mongoQuotes = db.quotes
    print(f' found {mongoQuotes.count_documents({})} documents')
  
    #Separate MongoDB docs into quotes, authors, and tag tables for Postgres
    (quotes , authors ,tags) = normalize_quotes_data(mongoQuotes)
    quotes_df = pd.DataFrame(quotes)
    author_df = pd.DataFrame(authors)
    tags_df = pd.DataFrame(tags)

    #POSTGRES connection settings
    user_name = 'postgres'
    password = 'postgres'
    connection_string = f"{user_name}:{password}@localhost:5432/ETL_Project"
    engine = create_engine(f'postgresql://{connection_string}')  

    quotes_script = '''
        create table quotes(     id INTEGER PRIMARY KEY,    
        author_name varchar(32),    
        text varchar(1500))
    '''

    tags_script = '''
        create table tags(    quote_id INTEGER,    
        tag varchar(32))
    '''

    author_script = '''
        create table author( name varchar(32) PRIMARY KEY,    
        born varchar(32),    
        description varchar(10000))
    '''  
    tables = {'quotes' : quotes_script.strip(), 
            'tags' : tags_script.strip(),
            'author' : author_script.strip()
            } 

    #Design and create in Postgres the three tables needed for quotes, authors, and tags        
    for table in tables.keys():
        print(f'dropping the table {table} if it already exists...')
        engine.execute(f'drop table IF EXISTS {table}') 

    for table , script in tables.items():
        print(f'creating the table {table}...')
        engine.execute(f'{script}')
    
    #Confirm tables are created in Postgress
    print(engine.table_names())  
    
    #Send MongoDB data to Postgres
    quotes_df.to_sql(name='quotes', con=engine, if_exists='append', index=False)  
    tags_df.to_sql(name='tags', con=engine, if_exists='append', index=False)  
    author_df.to_sql(name='author', con=engine, if_exists='append', index=False)
    print("Migration complete")

# %%
# URL of page to be scraped
def scrapeWebsite():
    url = 'http://quotes.toscrape.com/'

    nextPage = True
    pageUrl = url

    while nextPage:

            # Retrieve page with the requests module
        print("Scrapping: " + pageUrl)
        response = requests.get(pageUrl)
        # Create BeautifulSoup object; parse with 'lxml'
        soup = BeautifulSoup(response.text, 'lxml')

        # Examine the results, then determine element that contains sought info
        # results are returned as an iterable list
        results = soup.find_all('div', class_='quote')
        print(f'There are {len(results)} quotes on this page')
        # Loop through returned results
        for result in results:
            # Error handling
            try:
                # Identify and return quote text
                quoteText = result.find('span', class_='text').text.strip()
                #print("quote good")
                # Identify and return list of tags
                tags = [t.text.strip() for t in result.find_all('a', class_='tag')]
                #print("tags good")
                # Identify and return link to listing
                author = getAuthor(url + result.find_all('a')[0]['href'])
                #print("author good")

                # Run only if title, price, and link are available
                if (quoteText and author):
                    print("Quote scraped...")
                    # Dictionary to be inserted as a MongoDB document
                    quote = {
                        'text': quoteText,
                        'author': author,
                        'tags':tags
                    }
                    #Load quote object to collection
                    collection.insert_one(quote)
                    print("Quote inserted to MongoDB.")

            except Exception as e:
                print(e)

        nextButton = soup.find('li',class_='next')
        if(nextButton):
            nextUrl = nextButton.find('a')['href']
            pageUrl = url + nextUrl
        else:
            nextPage = False

# %%
# Main script start
# Initialize PyMongo to work with MongoDBs
conn = 'mongodb://localhost:27017'
client = pymongo.MongoClient(conn)

# Define database and collection
db = client.quote_db
collection = db.quotes

#Scrape Site to MongoDB
#Comment out following line to avoid duplicate Quotes in MongoDB
scrapeWebsite()
# Migrate Mongo DB to Postgres
migrate()

# %%
client.close()
