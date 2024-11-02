import sqlite3
from flask import Flask, render_template, request, url_for, flash, redirect, abort

# make a Flask application object called app
app = Flask(__name__)
app.config["DEBUG"] = True
app.config['SECRET_KEY'] = 'your secret key'



# Function to open a connection to the database.db file
def get_db_connection():
    # create connection to the database
    conn = sqlite3.connect('database.db')
    
    # allows us to have name-based access to columns
    # the database connection will return rows we can access like regular Python dictionaries
    conn.row_factory = sqlite3.Row

    #return the connection object
    return conn

#Function to retrieve a post from the database
def get_post(post_id):
    conn = get_db_connection()
    post = conn.execute('SELECT * FROM posts WHERE id = ?', (post_id,)).fetchone()
    conn.close()

    if post is None:
        abort(404)

    return post

# use the app.route() decorator to create a Flask view function called index()
@app.route('/')
def index():
    #get connection
    conn = get_db_connection()
    #execute query
    posts = conn.execute('SELECT * FROM posts').fetchall()
    #close connection
    conn.close()
    #send posts to index

    return render_template('index.html', posts=posts)


# route to create a post
@app.route('/create/', methods=('GET', 'POST'))
def create():
    #determine if the page is being requested with a POST or GET request
    if request.method == 'POST':
        #get title and content submitted
        title = request.form['title']
        content = request.form['content']
        #display error message if not submitted
        #else make a database connection
        if not title:
            flash("Title is required")
        elif not content:
            flash('Content is required')
        else:
            conn = get_db_connection()
            #insert dada
            conn.execute('INSERT INTO posts (title, content) VALUES (?, ?)', (title,content))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))
    return render_template('create.html')

#create a route to edit a post
#pass post id as url parameter
@app.route('/<int:id>/edit/', methods=('GET', 'POST'))
def edit(id):
    #get the post from the databse with select query for post with id
    post = get_post(id)
    #determine if the page was arequest with GET or POST
    #IF POST, process the form data. Get the data and validate it. Update the post and redirect to homepage
    if request.method == 'POST':
        #get title and content
        title = request.form['title']
        content = request.form['content']
        
        if not title:
            flash('Title is required')
        elif not content:
            flash('Content is required')
        else:
            conn = get_db_connection()
            conn.execute('UPDATE posts SET title = ?, content = ? WHERE id = ?', (title, content, id))
            conn.commit()
            conn.close()

            return redirect(url_for('index'))
        
    #If GET then display page
    return render_template('edit.html', post=post)
#create route to delete post
@app.route('/<int:id>/delete', methods=('POST',))
def delete(id):
    #get the post
    post = get_post(id)

    #Connect tot he database
    conn = get_db_connection()
    #execute a delete query
    conn.execute('DELETE from posts WHERE id = ?', (id,))
    #commit and close the connection
    conn.commit()
    conn.close()
    #flash a success message
    flash('"{}" was successfully deleted!'.format(post['title']))
    #redirect to the homepage
    return redirect(url_for('index'))
app.run()