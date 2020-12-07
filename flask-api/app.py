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
        f"/authors<br/>"
        f"/authors/name<br/>"
        f"/tags<br/>"
        f"/tags/tag<br/>"
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

@app.route("/authors")
def author():
    detail = []
    author_details = engine.execute('''select id, name, born, description from author
    ''')
    total_authors = author_details.rowcount
    for row in author_details:
        details = {}
        details['description'] = row.description
        details['born'] = row.born
        details['name'] = row.name
        quote = []
        tags = []
        quote_results = engine.execute(f"select text from quotes where author_name = '{row.name}'")
        tags_result = engine.execute(f'select tag from tags where quote_id=1')
        for tagrow in tags_result:
            tags.append(tagrow.tag)
        details['tags'] = tags
        for quote_row in quote_results:
            quote.append(quote_row.text)
        details['quotes'] = quote
        detail.append(details)
    details['total']=total_authors
    return jsonify(author = detail)

# @app.route("/authors/<author_name>")
# def author_name():
#     return()

@app.route("/tags")
def tag_name():
    result = {}
    tag_query = engine.execute('''select tag, id from tags t inner join quotes q on q.id = t.quote_id 
    order by id''')
    total_tags = tag_query.rowcount
    tags = []
    for t in tag_query:
        details = {}
        details['tag'] = t.tag
        quotes = []
        quote_query = engine.execute(
            f"select text from quotes q inner join tags t on t.quote_id = q.id where t.tag = '{t.tag}'")
        for quote_row in quote_query:
            quotes.append(quote_row.text)
        details['quote text'] = quotes
        tags.append(details)
    result['tags'] = tags
    result['total'] = total_tags
    return jsonify(result)

# @app.route("/tags/<tag>")
# def tags():
#     return()


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