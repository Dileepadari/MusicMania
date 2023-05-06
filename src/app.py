import json
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
    user_id = 1
    query = 'SELECT playlist FROM users WHERE "userid"={0}'.format(user_id)
    play_songs_list = curser.execute(query)
    play_songs = play_songs_list.fetchall()[0][0]
    return render_template('index.html', data = all_artists, albums = albums, songs = songs, all_albums = all_albums, play_songs = play_songs)


@app.route('/artists')
def all_artist():
    return render_template('artists.html', data = all_artists)

@app.route('/about')
def about_page():
    return render_template('about.html')

@app.route('/search')
def search_page():
    return render_template('search.html')

@app.route('/spotlight')
def spotlight_page():
    connection = sqlite3.connect("Music_Mania.db")
    curser = connection.cursor()

    query = "SELECT * FROM Artists where uniqid = 12"
    results = curser.execute(query)
    all_artists = results.fetchone()
    connection = sqlite3.connect("Music_Mania.db")
    curser = connection.cursor()
    query = 'SELECT * FROM Albums WHERE "index"= 12'
    album_list = curser.execute(query)
    albums = album_list.fetchall()
    return render_template('spotlight.html', artist=all_artists , albums=albums )

@app.route('/artist/<artist_name>')
def artist_page(artist_name):
    for data_page in all_artists:
        if(data_page[0] == artist_name):
            data_set = data_page
    connection = sqlite3.connect("Music_Mania.db")
    curser = connection.cursor()
    query = 'SELECT * FROM Albums WHERE "index"={0}'.format(data_set[12])
    album_list = curser.execute(query)
    albums = album_list.fetchall()
    return render_template('artists/ind_artist.html', data_set = data_set, rem_data = all_artists, albums = albums)


@app.route('/album/<album_id>')
def album_page(album_id):
    connection = sqlite3.connect("Music_Mania.db")
    curser = connection.cursor()
    query = 'SELECT * FROM Songs WHERE "album_id"={0}'.format(album_id)
    songs_list = curser.execute(query)
    songs = songs_list.fetchall()
    query = 'SELECT * FROM Albums WHERE "uniqid"={0}'.format(album_id)
    album_list = curser.execute(query)
    albums = album_list.fetchone()
    user_id = 1
    query = 'SELECT playlist FROM users WHERE "userid"={0}'.format(user_id)
    play_songs_list = curser.execute(query)
    play_songs = play_songs_list.fetchall()[0][0]
    return render_template('albums/ind_album.html', play_songs = play_songs ,songs = songs, artists = all_artists, album = albums)


@app.route('/playlist')
def playlist():
    connection = sqlite3.connect("Music_Mania.db")
    curser = connection.cursor()
    user_id = 1
    query = 'SELECT playlist FROM users WHERE "userid"={0}'.format(user_id)
    songs_list = curser.execute(query)
    songs = songs_list.fetchall()[0][0]
    query = 'SELECT * FROM Songs'
    all_songs_list = curser.execute(query)
    all_songs = all_songs_list.fetchall()
    return render_template('playlist.html', songs = songs, all_songs = all_songs)


@app.route('/add_to_playlist', methods=['GET', 'POST'])
def add_to_playlist():
    data = request.get_json()
    id = data['id']
    connection = sqlite3.connect("Music_Mania.db")
    curser = connection.cursor()
    user_id = 1
    query = 'SELECT playlist FROM users WHERE "userid"={0}'.format(user_id)
    songs_list = curser.execute(query)
    songs = songs_list.fetchall()[0][0]
    print(songs)
    songs = songs+id+","
    update_query = 'UPDATE users SET "playlist"="{0}" WHERE "userid"={1}'.format(songs,user_id)
    songs_list = curser.execute(update_query)
    connection.commit()
    return jsonify({'success': 'True'})


@app.route('/remove_from_playlist', methods=['GET', 'POST'])
def remove_from_playlist():
    data = request.get_json()
    id = data['id']
    connection = sqlite3.connect("Music_Mania.db")
    curser = connection.cursor()
    user_id = 1
    query = 'SELECT playlist FROM users WHERE "userid"={0}'.format(user_id)
    songs_list = curser.execute(query)
    songs = songs_list.fetchall()[0][0]
    songs = songs.replace(id+",","")
    update_query = 'UPDATE users SET "playlist"="{0}" WHERE "userid"={1}'.format(songs,user_id)
    songs_list = curser.execute(update_query)
    connection.commit()
    return jsonify({'success': 'True'})

if __name__ == '__main__':
    app.run(debug=True)