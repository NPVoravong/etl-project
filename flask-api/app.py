import numpy as np
from flask import Flask, jsonify
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func


#Connect to the Postgres Database
rds_connection_string = "postgres:postgres@localhost:5432/xxxxxxxxxxxxxxxx"
engine = create_engine(f'postgresql://{rds_connection_string}')

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
a = Base.classes.Author
q = Base.classes.Quotes
t = Base.classes.Tags

# Create a database session object
session = Session(engine)



app = Flask(__name__)

@app.route("/")
def home():
    return(
        f"Available Routes:<br/>"
        f"/api/v1.0/quotes<br/>"
        f"/api/v1.0/authors<br/>"
        f"/api/v1.0/authors/<author_name><br/>"
        f"/api/v1.0/tags<br/>"
        f"/api/v1.0/tags/<tag><br/>"
        f"/api/v1.0/top10tags"
    )

@app.route("/quotes")
def quote():
    total_quotes = session.query(func.count(q.Quotes)).first()[0]
    quote = session.query(q.quote_text,a.name, t.tag,).all()
    return jsonify(total_quotes)

# @app.route("/author")
# def author():
#     return()

# @app.route("/authors/<author_name>")
# def author_name():
#     return()

# @app.route("/tags")
# def tag_name():
#     return()

# @app.route("/tags/<tag>")
# def tags():
#     return()

# @app.route("/top10tags")
# def top_ten():
#     return()

if __name__ == '__main__':
    app.run(debug=True)