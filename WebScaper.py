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
import pymongo


# %%
# Initialize PyMongo to work with MongoDBs
conn = 'mongodb://localhost:27017'
client = pymongo.MongoClient(conn)


# %%
# Define database and collection
db = client.quote_db
collection = db.quotes


# %%
# URL of page to be scraped
url = 'http://quotes.toscrape.com/page/'

for page in range(1, 11):

        # Retrieve page with the requests module
    response = requests.get(url + str(page))
    # Create BeautifulSoup object; parse with 'lxml'
    soup = BeautifulSoup(response.text, 'html')

    # %%
    # Examine the results, then determine element that contains sought info
    # results are returned as an iterable list
    results = soup.find_all('div', class_='quote')

    # Loop through returned results
    for result in results:
        # Error handling
        try:
            # Identify and return title of listing
            quoteText = result.find('span', class_='text').text.strip()
            # Identify and return price of listing
            tags = [t.text.strip() for t in result.find_all('a', class='tag')]
            # Identify and return link to listing
            authorName = result.find('small', class='author').text.strip()

            # Run only if title, price, and link are available
            if (title and price and link):
                # Print results
                print('-------------')
                print(title)
                print(price)
                print(link)

                # Dictionary to be inserted as a MongoDB document
                post = {
                    'title': title,
                    'price': price,
                    'url': link
                }

                collection.insert_one(post)

        except Exception as e:
            print(e)


# %%
# Display items in MongoDB collection
listings = db.items.find()

for listing in listings:
    print(listing)
