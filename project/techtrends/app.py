import sqlite3

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort

import logging

logging.basicConfig(level=logging.DEBUG)
db_connections = 0

# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    global db_connections
    db_connections +=1
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    return connection

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()

    app.logger.info(post[2]+' retrieved!')
    return post

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

# Define the main route of the web application 
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
      app.logger.info('No Post Found.')
      return render_template('404.html'), 404
    else:
      return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    app.logger.info('It was always About Us <3')
    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()
            app.logger.info(title+' created!')
            return redirect(url_for('index'))

    return render_template('create.html')

@app.route('/healthz')
def healthz():

    try:
        db = get_db_connection()
        db.execute('SELECT * FROM posts').fetchall()

        response = app.response_class(
            response=json.dumps({'result':'OK - healthy'}),
            status=200,
            mimetype='application/json'
    )
    except:
        response = app.response_class(
            response=json.dumps({'result':'ERROR - unhealthy'}),
            status=500,
            mimetype='application/json'
        )
    return response

@app.route('/metrics')
def metrics():

    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()

    json_data = {
        'db_connection_count': db_connections,
        'post_count': len(posts)
    }
    response = app.response_class(
            response=json.dumps(json_data),
            status=200,
            mimetype='application/json'
    )
    return response
# start the application on port 3111
if __name__ == '__main__':
    app.run(host='0.0.0.0', port='3111')
