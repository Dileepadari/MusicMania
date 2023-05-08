import json
import random
from datetime import datetime
from flask import Flask, request, render_template, redirect, session, url_for, jsonify
import sqlite3
connection = sqlite3.connect("Music_Mania.db")
curser = connection.cursor()

query = "SELECT * FROM Artists"
results = curser.execute(query)
all_artists = results.fetchall()



app = Flask(__name__)
app.secret_key = 'DelhiisDelhi'



@app.route('/', methods=['GET', 'POST'])
def index():
    if "user_id" not in session:
        return redirect("/login") 
    connection = sqlite3.connect("Music_Mania.db")
    curser = connection.cursor()

    query = "SELECT * FROM Artists"
    results = curser.execute(query)
    all_artists = results.fetchall()
    query = 'SELECT * FROM Albums ORDER BY rating DESC'
    album_list = curser.execute(query)
    all_albums = album_list.fetchall()
    query = 'SELECT * FROM Albums ORDER BY rating DESC LIMIT 3'
    album_list = curser.execute(query)
    albums = album_list.fetchall()
    query = 'SELECT * FROM Songs ORDER BY rating DESC LIMIT 3'
    songs_list = curser.execute(query)
    songs = songs_list.fetchall()
    user_id = session['user_id']
    query = 'SELECT playlist FROM users WHERE "userid"={0}'.format(user_id)
    play_songs_list = curser.execute(query)
    play_songs = play_songs_list.fetchall()[0][0]
    query = "SELECT * FROM Users where userid = {0}".format(session['user_id'])
    results = curser.execute(query)
    users = results.fetchall()[0]
    return render_template('index.html', data = all_artists, albums = albums, songs = songs, all_albums = all_albums, play_songs = play_songs, users=users)


@app.route('/artists')
def all_artist():
    if "user_id" not in session:
        return redirect("/login")     
    connection = sqlite3.connect("Music_Mania.db")
    curser = connection.cursor()
    query = "SELECT * FROM Users where userid = {0}".format(session['user_id'])
    results = curser.execute(query)
    users = results.fetchall()[0]
    return render_template('artists.html', data = all_artists, users=users)


@app.route('/register_ratiing', methods=['POST','GET'])
def register_rating():
    if "user_id" not in session:
        return redirect("/login") 
    if request.method == 'POST':
        connection = sqlite3.connect("Music_Mania.db")
        curser = connection.cursor()
        rating = request.form['rated']
        review = request.form['comment']
        time = datetime.now()
        current_date = time.strftime("%d/%m/%Y")
        userid = session['user_id']
        query = "INSERT INTO Reviews (userid, review, date,rating) VALUES ({0},'{1}','{2}','{3}');".format(userid, review,current_date,rating)
        curser.execute(query)
        print(query)
        connection.commit()
    return redirect('/spotlight')


@app.route('/about')
def about_page():
    if "user_id" not in session:
        return redirect("/login") 
    connection = sqlite3.connect("Music_Mania.db")
    curser = connection.cursor()
    query = "SELECT * FROM Users where userid = {0}".format(session['user_id'])
    results = curser.execute(query)
    users = results.fetchall()[0]
    return render_template('about.html', users=users)

@app.route('/search')
def search_page():
    if "user_id" not in session:
        return redirect("/login") 
    connection = sqlite3.connect("Music_Mania.db")
    curser = connection.cursor()
    query = "SELECT * FROM Users where userid = {0}".format(session['user_id'])
    results = curser.execute(query)
    users = results.fetchall()[0]
    return render_template('search.html', users=users)

@app.route('/spotlight')
def spotlight_page():
    if "user_id" not in session:
        return redirect("/login") 
    connection = sqlite3.connect("Music_Mania.db")
    curser = connection.cursor()

    query = "SELECT * FROM Artists where uniqid = 12"
    results = curser.execute(query)
    all_artists = results.fetchall()
    query = 'SELECT * FROM Albums WHERE "index" = 12'
    album_list = curser.execute(query)
    albums = album_list.fetchall()
    query = "SELECT * FROM Users where userid = {0}".format(session['user_id'])
    results = curser.execute(query)
    users = results.fetchall()[0]
    query = "SELECT * FROM Reviews"
    results = curser.execute(query)
    reviews = results.fetchall()
    query = "SELECT * FROM Users"
    results = curser.execute(query)
    all_users = results.fetchall()
    return render_template('spotlight.html', artist=all_artists, albums=albums, users=users, reviews=reviews, all_users=all_users)

@app.route('/artist/<artist_name>')
def artist_page(artist_name):
    if "user_id" not in session:
        return redirect("/login") 
    for data_page in all_artists:
        if(data_page[0] == artist_name):
            data_set = data_page
    connection = sqlite3.connect("Music_Mania.db")
    curser = connection.cursor()
    query = 'SELECT * FROM Albums WHERE "index"={0}'.format(data_set[12])
    album_list = curser.execute(query)
    albums = album_list.fetchall()
    query = "SELECT * FROM Users where userid = {0}".format(session['user_id'])
    results = curser.execute(query)
    users = results.fetchall()[0]
    return render_template('artists/ind_artist.html', data_set = data_set, rem_data = all_artists, albums = albums, users=users)


@app.route('/album/<album_id>')
def album_page(album_id):
    if "user_id" not in session:
        return redirect("/login") 
    connection = sqlite3.connect("Music_Mania.db")
    curser = connection.cursor()
    query = "SELECT * FROM Users where userid = {0}".format(session['user_id'])
    results = curser.execute(query)
    users = results.fetchall()[0]
    query = 'SELECT * FROM Songs WHERE "album_id"={0}'.format(album_id)
    songs_list = curser.execute(query)
    songs = songs_list.fetchall()
    query = 'SELECT * FROM Albums WHERE "uniqid"={0}'.format(album_id)
    album_list = curser.execute(query)
    albums = album_list.fetchone()
    user_id = session['user_id']
    query = 'SELECT playlist FROM users WHERE "userid"={0}'.format(user_id)
    play_songs_list = curser.execute(query)
    play_songs = play_songs_list.fetchall()[0][0]
    return render_template('albums/ind_album.html', play_songs = play_songs ,songs = songs, artists = all_artists, album = albums, users=users)


@app.route('/playlist')
def playlist():
    if "user_id" not in session:
        return redirect("/login") 
    connection = sqlite3.connect("Music_Mania.db")
    curser = connection.cursor()
    query = "SELECT * FROM Users where userid = {0}".format(session['user_id'])
    results = curser.execute(query)
    users = results.fetchall()[0]
    user_id = session['user_id']
    query = 'SELECT playlist FROM users WHERE "userid"={0}'.format(user_id)
    songs_list = curser.execute(query)
    songs = songs_list.fetchall()[0][0]
    query = 'SELECT * FROM Songs'
    all_songs_list = curser.execute(query)
    all_songs = all_songs_list.fetchall()
    return render_template('playlist.html', songs = songs, all_songs = all_songs, users=users)


@app.route('/add_to_playlist', methods=['GET', 'POST'])
def add_to_playlist():
    if "user_id" not in session:
        return redirect("/login") 
    data = request.get_json()
    id = data['id']
    connection = sqlite3.connect("Music_Mania.db")
    curser = connection.cursor()
    user_id = session['user_id']
    query = 'SELECT playlist FROM users WHERE "userid"={0}'.format(user_id)
    songs_list = curser.execute(query)
    songs = songs_list.fetchall()[0][0]
    print(songs)
    if(songs):
        songs = songs+id+","
    else:
        songs=id+","
    update_query = 'UPDATE users SET "playlist"="{0}" WHERE "userid"={1}'.format(songs,user_id)
    songs_list = curser.execute(update_query)
    connection.commit()
    return jsonify({'success': 'True'})


@app.route('/remove_from_playlist', methods=['GET', 'POST'])
def remove_from_playlist():
    if "user_id" not in session:
        return redirect("/login") 
    data = request.get_json()
    id = data['id']
    connection = sqlite3.connect("Music_Mania.db")
    curser = connection.cursor()
    user_id = session['user_id']
    query = 'SELECT playlist FROM users WHERE "userid"={0}'.format(user_id)
    songs_list = curser.execute(query)
    songs = songs_list.fetchall()[0][0]
    songs = songs.replace(id+",","")
    update_query = 'UPDATE users SET "playlist"="{0}" WHERE "userid"={1}'.format(songs,user_id)
    songs_list = curser.execute(update_query)
    connection.commit()
    return jsonify({'success': 'True'})

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        connection = sqlite3.connect("Music_Mania.db")
        curser = connection.cursor()
        username = request.form['username']
        password = request.form['password']
        con_pass = request.form['con-password']
        firstname = request.form['Firstname']
        lastname = request.form['Lastname']

        query = "SELECT * FROM Users WHERE username ='{0}';".format(username) 
        result = curser.execute(query)
        data = result.fetchone()
        if(data):
            return render_template("signup.html",error="Username already exists")
        else:
            query = "INSERT INTO Users (username,img_url,firstname, lastname, password) VALUES (?,?,?,?,?);"
            result = curser.execute(query, (username,"/images/delhi.jpg",firstname,lastname,password))
            connection.commit()
            query = "SELECT * FROM Users WHERE username ='{0}';".format(username) 
            result = curser.execute(query)
            data = result.fetchone()
            session['userid'] = data[0][0]
            return redirect("/")
    return render_template("signup.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        connection = sqlite3.connect("Music_Mania.db")
        curser = connection.cursor()
        query = "SELECT * FROM Users WHERE username ='{0}';".format(username) 
        result = curser.execute(query)
        data = result.fetchone()
        if(data and data[6] == password):
            print(data)
            session['user_id'] = data[0]
            return redirect("/")
        else:
            return render_template("login.html",error=True)
    return render_template("login.html")

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect('/login')



if __name__ == '__main__':
    app.run(debug=True)