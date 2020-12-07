import numpy as np
from flask import Flask, jsonify
import sqlalchemy
from sqlalchemy import create_engine, func, text


#Connect to the Postgres Database
engine = create_engine('postgres://zkhlwdmsqfzuhu:9672f3ba7f960cab4d0e96fd60fef1ee18058d7076777bb99e80c53a54e69513@ec2-52-22-238-188.compute-1.amazonaws.com:5432/d87t3tjj770omk')

#Start of Flask
app = Flask(__name__)
#################################################
# Flask Routes
#################################################
def tags_for_the_quote(quote_id):
    tags = []
    print(f'getting tags for {quote_id}')
    tags_result = engine.execute(
        f'select tag  from tags where quote_id= {quote_id}')
    for tagrow in tags_result:
        tags.append(tagrow.tag)
    return tags

#################################################


def quotes_for_author(author_name):
    result = []
    print(f'getting quotes for {author_name}')
    query = text("select id , text from quotes where author_name = :name")
    quotes_result_set = engine.execute(query, {'name': author_name})
    for row in quotes_result_set:
        this_quote = {}
        this_quote['text'] = row.text
        this_quote['tags'] = tags_for_the_quote(row.id)
        result.append(this_quote)
    return result

#################################################


def quotes_for_tag(tag):
    result = []
    print(f'getting quotes for {tag}')

    query = text('''select id, text
            from quotes q inner join tags t on q.id=t.quote_id
            where t.tag = :tag ''')
    quotes_result_set = engine.execute(query, {'tag': tag})
    for row in quotes_result_set:
        this_quote = {}
        this_quote['text'] = row.text
        this_quote['tags'] = tags_for_the_quote(row.id)
        result.append(this_quote)
    return result

#################################################


@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/quotes<br/>"
        f"/authors<br/>"
        f"/authors/&ltauthor_name&gt<br/>"
        f"/tags<br/>"
        f"/tags/&lttag&gt<br/>"
        f"/top-ten-tags"
    )


@app.route("/authors")
def authors():
    result = {}
    authors = []
    author_resuletset = engine.execute(
        'select name , born , description from author')
    result['count'] = author_resuletset.rowcount

    for author_row in author_resuletset:
        this_author = {}
        quotes = []
        this_author['name'] = author_row.name
        this_author['description'] = author_row.description
        this_author['born'] = author_row.born
        quotes = quotes_for_author(author_row.name)
        this_author['count'] = len(quotes)
        this_author['quotes'] = quotes
        authors.append(this_author)

    result['details'] = authors

    return jsonify(result)


@app.route("/authors/<author_name>")
def oneauthor(author_name):
    result = {}
    query = text(
        "select name , born , description from author where name = :name")
    author_result = engine.execute(query, {'name': author_name})
    # if we found the author, return the details, otherwise return Author not found
    if(author_result.rowcount == 1):
        author = author_result.fetchone()
        result['name'] = author.name
        result['description'] = author.description
        quotes = quotes_for_author(author_name)
        result['quotes'] = quotes
        result['number_of_quotes'] = len(quotes)
    else:  # authro not found
        result['name'] = author_name
        result['description'] = 'Author not found'

    return jsonify(result)

@app.route("/tags")
def tags():
    result = {}
    tags_result_set = engine.execute('''select tag , count(*) as total from tags
        group by tag
        order by total desc''')
    result['count'] = tags_result_set.rowcount
    tags = []
    for row in tags_result_set:
        this_tag = {}
        this_tag['name'] = row.tag
        this_tag['number_of_quotes'] = row.total
        this_tag['quotes'] = quotes_for_tag(row.tag)
        tags.append(this_tag)
    result['details'] = tags
    return jsonify(result)

@app.route("/tags/<tag_name>")
def onetag(tag_name):
    result = {}
    result['tag'] = tag_name
    quotes = quotes_for_tag(tag_name)
    result['quotes'] = quotes
    result['count'] = len(quotes)
    return jsonify(result)

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