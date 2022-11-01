'''Featured Movie Flask App - Victor Ekpenyong'''
import os
import random
import requests
from flask import Flask, render_template, request, redirect, url_for, flash
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

TMDB_API_BASE_URL = 'https://api.themoviedb.org/3/trending/movie/week'
TMBD_API_CONFIG_URL = 'https://api.themoviedb.org/3/configuration'
WIKI_BASE_URL = 'https://en.wikipedia.org/w/api.php'
GENRE_LIST_BASE_URL = 'https://api.themoviedb.org/3/genre/movie/list'
TMDB_API_MOVIE_DATA_BASE_URL = 'https://api.themoviedb.org/3/movie/'

app = Flask(__name__)
app.secret_key = os.getenv('APP_SECRET_KEY')


#GLOBAL_MOVIE_NUM used for page direction to specific movie page
GLOBAL_MOVIE_NUM = 0
trending_json_data = []
USER_VALID = None


def app_logic(movie, trending_json_data):
    '''Function which returns needed jinja elements for HTML page to render'''
    response2 = requests.get(
        TMBD_API_CONFIG_URL,
        params={
            'api_key': os.getenv('TMDB_API_KEY')
        }
    )

    response3 = requests.get(
        GENRE_LIST_BASE_URL,
        params={
            'api_key': os.getenv('TMDB_API_KEY')
        }
    )
    url = response2.json()
    genre = response3.json()

    movie_id_num = str(trending_json_data['results'][movie]['id'])
    movie_title = trending_json_data['results'][movie]['original_title']
    movie_poster_url = url['images']['secure_base_url'] + url['images']['poster_sizes'][3] + '/' + trending_json_data['results'][movie]['poster_path']
    movie_backdrop_url = url['images']['secure_base_url'] + url['images']['backdrop_sizes'][3] + '/' + trending_json_data['results'][movie]['backdrop_path']
    movie_description = trending_json_data['results'][movie]['overview']

    response4 = requests.get(
        TMDB_API_MOVIE_DATA_BASE_URL + movie_id_num,
        params={
            'api_key': os.getenv('TMDB_API_KEY')
        }
    )

    movie_details = response4.json()
    movie_tagline = movie_details['tagline']
    production = movie_details['production_companies'][0]['name']

    genre_set = set(trending_json_data['results'][movie]['genre_ids'])
    genre_string = 'Genres: '
    genre_list = ''
    for entry in genre['genres']:
        if entry['id'] in genre_set:
            if genre_list == '':
                genre_list = entry['name']
            else:
                genre_list = genre_list + ', ' + entry['name']
    genre_string = genre_string + genre_list

    response5 = requests.get(
        WIKI_BASE_URL,
        params={
            'action': 'query',
            'format': 'json',
            'list': 'search',
            'srsearch': movie_title + ' Film (' + trending_json_data['results'][movie]['release_date'][0:4] + ') released by ' + production
        }
    )
    wiki = response5.json()
    wiki_link = 'https://en.wikipedia.org/?curid=' + str(wiki['query']['search'][0]['pageid'])

    return [movie_title, movie_tagline, movie_poster_url, movie_backdrop_url, wiki_link, movie+1, movie_description, genre_string, trending_json_data]
@app.route('/')
def hello():
    ''' Opening Function which runs on the first load of application'''
    response1 = requests.get(
        TMDB_API_BASE_URL,
        params={
            'api_key': os.getenv('TMDB_API_KEY')
        }
    )
    global trending_json_data
    trending_json_data = response1.json()
    movie = random.randint(0,19)
    html_elements = app_logic(movie, trending_json_data)
    return render_template('index.html', title=html_elements[0], tagline=html_elements[1], 
    image=html_elements[2], backImage=html_elements[3], link=html_elements[4], 
    number=html_elements[5], info=html_elements[6], genres=html_elements[7], movieList=html_elements[8], valid=USER_VALID)

@app.route('/direct_movie', methods=['GET', 'POST'])
def direct():
    '''Function which handles HTML form leading to direction to movie specific page'''
    if request.form.get("movie_rank") == 'empty':
        flash('Movie Was Not Selected Below')
        return redirect(url_for('hello'))
    
    global GLOBAL_MOVIE_NUM
    GLOBAL_MOVIE_NUM = int(request.form.get("movie_rank"))
    return redirect(url_for('show_movie', movie_title=trending_json_data['results'][GLOBAL_MOVIE_NUM]['original_title']))

@app.route('/<movie_title>')
def show_movie(movie_title= None):
    '''Function which renders movie specific page with ability to redirect back to main page'''
    response1 = requests.get(
        TMDB_API_BASE_URL,
        params={
            'api_key': os.getenv('TMDB_API_KEY')
        }
    )
    global trending_json_data
    trending_json_data = response1.json()
    html_elements = app_logic(GLOBAL_MOVIE_NUM, trending_json_data)
    return render_template('movie.html', title=html_elements[0], tagline=html_elements[1], 
    image=html_elements[2], backImage=html_elements[3], link=html_elements[4], 
    number=html_elements[5], info=html_elements[6], genres=html_elements[7], movieList=html_elements[8])

@app.route('/validate', methods=['GET', 'POST'])
def validate_direction():
    '''Function which handles HTML form leading to sign up page'''
    next_page = str(request.form.get("validate"))
    if next_page == 'log_out':
        global USER_VALID
        USER_VALID = None
        return redirect(url_for('hello'))
    return redirect(url_for(next_page))

@app.route('/signUp', methods=['GET', 'POST'])
def sign_up():
    '''Function which handles HTML form leading to sign up page'''
    return render_template('signup.html')

@app.route('/logIn', methods=['GET', 'POST'])
def log_in():
    '''Function which handles HTML form leading to sign up page'''
    return render_template('login.html')

@app.route('/validateLogin', methods=['GET', 'POST'])
def validate_login():
    '''Function which handles HTML form leading to sign up page'''
    username = str(request.form.get("UserName"))
    if username != 'vbe':
        return redirect(url_for('hello'))
    global USER_VALID
    USER_VALID = username
    return redirect(url_for('hello'))