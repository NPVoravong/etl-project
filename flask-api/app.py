import numpy as np
from flask import Flask, jsonify
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import psycopg2


#Connect to the Postgres Database
engine = create_engine('postgres://zkhlwdmsqfzuhu:9672f3ba7f960cab4d0e96fd60fef1ee18058d7076777bb99e80c53a54e69513@ec2-52-22-238-188.compute-1.amazonaws.com:5432/d87t3tjj770omk')

#Start of Flask
app = Flask(__name__)

@app.route("/")
def home():
    return(
        f"Available Routes:<br/>"
        f"/info/quotes<br/>"
        f"/api/v1.0/authors<br/>"
        f"/api/v1.0/authors/<author_name><br/>"
        f"/api/v1.0/tags<br/>"
        f"/api/v1.0/tags/<tag><br/>"
        f"/info/top10tags"
    )

@app.route("/info/quotes")
def quotes():
    result = {}
    result_set = engine.execute('''select id, author_name, text
    from quotes q inner join author a on q.author_name = a.name
    order by id''')
    total_quotes = result_set.rowcount
    quotes = []
    for row in result_set:
        quote = {}
        quote['text'] = row.text
        quote['author'] = row.author_name
        tags = []
        tags_result = engine.execute(
            f'select tag  from tags where quote_id= {row.id}')
        for tagrow in tags_result:
            tags.append(tagrow.tag)
        quote['tags'] = tags
        quotes.append(quote)
    result['quotes'] = quotes
    result['total'] = total_quotes
    return jsonify(result)

@app.route("/author")
def author():

      
# @app.route("/authors/<author_name>")
# def author_name():
#     return()

# @app.route("/tags")
# def tag_name():
#     return()

# @app.route("/tags/<tag>")
# def tags():
#     return()

@app.route("/info/top10tags")
def top_ten():

    top_tags = engine.execute('select tag from quotes as q inner join tags as t on t.quote_id = q.id group by tag order by count(text) desc limit 10').fetchall()


    return jsonify(
        {"Top 10 Tags" : list(np.ravel(top_tags))}
    )

if __name__ == '__main__':
    app.run(debug=True)