import numpy as np
from flask import Flask, jsonify
import sqlalchemy
from sqlalchemy import create_engine, func

#Connect to the Postgres Database
engine = create_engine('postgres://zkhlwdmsqfzuhu:9672f3ba7f960cab4d0e96fd60fef1ee18058d7076777bb99e80c53a54e69513@ec2-52-22-238-188.compute-1.amazonaws.com:5432/d87t3tjj770omk')

#Start of Flask
app = Flask(__name__)

@app.route("/")
def home():
    return(
        f"Available Routes:<br/>"
        f"/quotes<br/>"
        f"/top-ten-tags<br/>"
    )

@app.route("/quotes")
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

@app.route("/top-ten-tags")
def top10tags():
    result = []
    tags_result_set = engine.execute('''select tag , count(*) as total from tags
    group by tag
    order by total desc
    limit 10''')
    for row in tags_result_set:
        tag = {}
        tag['tag'] = row.tag
        tag['total'] = row.total
        result.append(tag)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)