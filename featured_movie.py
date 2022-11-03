'''Featured Movie Flask App - Victor Ekpenyong'''
import os
import random
import requests
from flask import Flask, render_template, request, redirect, url_for, flash
from dotenv import load_dotenv, find_dotenv
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_sqlalchemy_session import flask_scoped_session
#from models import Members

load_dotenv(find_dotenv())

TMDB_API_BASE_URL = 'https://api.themoviedb.org/3/trending/movie/week'
TMBD_API_CONFIG_URL = 'https://api.themoviedb.org/3/configuration'
WIKI_BASE_URL = 'https://en.wikipedia.org/w/api.php'
GENRE_LIST_BASE_URL = 'https://api.themoviedb.org/3/genre/movie/list'
TMDB_API_MOVIE_DATA_BASE_URL = 'https://api.themoviedb.org/3/movie/'

app = Flask(__name__)
app.secret_key = os.getenv('APP_SECRET_KEY')

#app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DB_URI')
#db = SQLAlchemy(app)
#db.init_app(app)
#session = flask_scoped_session(session_factory, app)

#GLOBAL_MOVIE_NUM used for page direction to specific movie page
GLOBAL_MOVIE_NUM = 0
trending_json_data = []
#Global vars which will be replaced once database is figured out
USER_VALID = None
USERS_SET = set()
MOVIE_REVIEWS = dict()


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

    return [movie_title, movie_tagline, movie_poster_url, movie_backdrop_url, wiki_link, movie+1, movie_description, genre_string, trending_json_data, movie_id_num]

#def add_user(username):
    #user = Members(username=username)
    #db.add(user)
    #db.commit()

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
    movieReviews = None
    global MOVIE_REVIEWS
    if MOVIE_REVIEWS.get(html_elements[9]):
        movieReviews = MOVIE_REVIEWS.get(html_elements[9])
    return render_template('index.html', title=html_elements[0], tagline=html_elements[1], 
    image=html_elements[2], backImage=html_elements[3], link=html_elements[4], 
    number=html_elements[5], info=html_elements[6], genres=html_elements[7], movieList=html_elements[8], id=html_elements[9], valid=USER_VALID, reviews=movieReviews)

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
    movieReviews = None
    global MOVIE_REVIEWS
    if MOVIE_REVIEWS.get(html_elements[9]):
        movieReviews = MOVIE_REVIEWS.get(html_elements[9])
    return render_template('movie.html', title=html_elements[0], tagline=html_elements[1], 
    image=html_elements[2], backImage=html_elements[3], link=html_elements[4], 
    number=html_elements[5], info=html_elements[6], genres=html_elements[7], movieList=html_elements[8], id=html_elements[9], valid=USER_VALID, reviews=movieReviews)

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
    global USERS_SET
    if not username in USERS_SET:
        flash('User Name does not exist, try again')
        return redirect(url_for('log_in'))
    global USER_VALID
    USER_VALID = username
    return redirect(url_for('hello'))

@app.route('/validateSignup', methods=['GET', 'POST'])
def validate_signup():
    '''Function which handles HTML form leading to sign up page'''
    username = str(request.form.get("UserName"))
    global USERS_SET
    if not username in USERS_SET:
        USERS_SET.add(username)
        #add_user(username)
        #print([str(u) for u in Members.query.all()])
        global USER_VALID
        USER_VALID = username
        return redirect(url_for('hello'))
    flash('User Name already in use, try again')
    return redirect(url_for('sign_up'))

@app.route('/addReviewMain', methods=['GET', 'POST'])
def new_review_main():
    '''Function which handles HTML form leading to sign up page'''
    movie_id = request.form.get("movieID")
    rating = request.form.get("rating")
    comments = request.form.get("comments")

    review = [USER_VALID, rating, comments]
    global MOVIE_REVIEWS
    if not movie_id in MOVIE_REVIEWS:
        MOVIE_REVIEWS.update({movie_id: []})
    MOVIE_REVIEWS[movie_id].append(review)
    return redirect(url_for('hello'))
@app.route('/addReviewSpecific', methods=['GET', 'POST'])
def new_review_specific():
    '''Function which handles HTML form leading to sign up page'''
    movie_id = request.form.get("movieID")
    rating = request.form.get("rating")
    comments = request.form.get("comments")

    review = [USER_VALID, rating, comments]
    global MOVIE_REVIEWS
    if MOVIE_REVIEWS.get(movie_id):
        MOVIE_REVIEWS[movie_id].append(review)
    else:
        MOVIE_REVIEWS.update({movie_id: []})
        MOVIE_REVIEWS[movie_id].append(review)
    return redirect(url_for('show_movie', movie_title=trending_json_data['results'][GLOBAL_MOVIE_NUM]['original_title']))
