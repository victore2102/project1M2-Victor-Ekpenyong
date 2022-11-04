'''Featured Movie Flask App - Victor Ekpenyong'''
import os
import random
import requests
from flask import Flask, render_template, request, redirect, url_for, flash
from dotenv import load_dotenv, find_dotenv
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_required, current_user, login_user, logout_user
from flask_login import UserMixin
#from models import Members


load_dotenv(find_dotenv())

TMDB_API_BASE_URL = 'https://api.themoviedb.org/3/trending/movie/week'
TMBD_API_CONFIG_URL = 'https://api.themoviedb.org/3/configuration'
WIKI_BASE_URL = 'https://en.wikipedia.org/w/api.php'
GENRE_LIST_BASE_URL = 'https://api.themoviedb.org/3/genre/movie/list'
TMDB_API_MOVIE_DATA_BASE_URL = 'https://api.themoviedb.org/3/movie/'

app = Flask(__name__)
app.secret_key = os.getenv('APP_SECRET_KEY')

app.config['SECRET_KEY'] = app.secret_key
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DB_URI')
db = SQLAlchemy(app)

class MovieReviews(db.Model):
    '''Movie Review Table'''
    id = db.Column(db.Integer, primary_key=True)
    movie_ID = db.Column(db.String(6), unique=False, nullable=False)
    user = db.Column(db.String(50), unique=False, nullable=False)
    rating = db.Column(db.String(8), unique=False, nullable=False)
    comments = db.Column(db.String(200), unique=False, nullable=False)

    def __repr__(self) -> str:
        return f"{self.user}-{self.rating}-{self.comments}--END--"

class Member(UserMixin, db.Model):
    '''User DB Table'''
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)

    def __repr__(self) -> str:
        return f"Member with username: {self.username}"

login_manager = LoginManager()
login_manager.login_view = 'log_in'
login_manager.init_app(app)


with app.app_context():
    db.create_all()


@login_manager.user_loader
def load_member(member_id):
    return Member.query.get(int(member_id))


GLOBAL_MOVIE_NUM = 0
trending_json_data = []


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


def movie_review_exists(movie_ID):
    '''Checks to see if review(s) exists for a movie'''
    exists = MovieReviews.query.filter_by(movie_ID=movie_ID).first()
    if exists:
        return True
    return False

def movie_review_list(movie_ID):
    '''Return list of all reviews for movie_ID'''
    reviews_list = []
    reviews = str(MovieReviews.query.filter_by(movie_ID=movie_ID).all())
    filtered_reviews = reviews.lstrip("[")
    filtered_reviews = filtered_reviews.rstrip("]")
    reviews_split = list(filtered_reviews.split("--END--,"))

    for r in reviews_split:
        r_split = list(r.split("-"))
        reviews_list.append(r_split)
    
    return reviews_list

@app.route('/', methods=['GET', 'POST'])
def log_in():
    '''Function which handles HTML form leading to sign up page'''
    return render_template('login.html')

@app.route('/signUp', methods=['GET', 'POST'])
def sign_up():
    '''Function which handles HTML form leading to sign up page'''
    return render_template('signup.html')

@app.route('/validateLogin', methods=['GET', 'POST'])
def validate_login():
    '''Function which handles HTML form leading to sign up page'''
    username = str(request.form.get("UserName"))
    user = Member.query.filter_by(username=username).first()
    if user:
        login_user(user)
        return redirect(url_for('featuring_page'))
    
    flash('User Name does not exist, try again or click below to Sign Up')
    return redirect(url_for('log_in'))
    

@app.route('/validateSignup', methods=['GET', 'POST'])
def validate_signup():
    '''Function which handles HTML form leading to sign up page'''
    username = str(request.form.get("UserName"))
    user = Member.query.filter_by(username=username).first()
    if user:
        flash('User Name already in use, try again or click below to Log In')
        return redirect(url_for('sign_up'))
    
    new_user = Member(username = username)
    db.session.add(new_user)
    db.session.commit()
    return redirect(url_for('log_in'))
    

@app.route('/addReviewMain', methods=['GET', 'POST'])
@login_required
def new_review_main():
    '''Function which handles HTML form leading to sign up page'''
    if request.form.get("rating") == 'empty':
        flash('Rating not selected')
        return redirect(url_for('featuring_page'))
    movie_id = request.form.get("movieID")
    rating = request.form.get("rating")
    comments = request.form.get("comments")

    new_review = MovieReviews(movie_ID=movie_id, user=current_user.username, rating=rating, comments=comments)
    db.session.add(new_review)
    db.session.commit()
    return redirect(url_for('featuring_page'))


@app.route('/featuring')
@login_required
def featuring_page():
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
    movie_reviews = None
    if movie_review_exists(html_elements[9]):
        movie_reviews = movie_review_list(html_elements[9])
    return render_template('index.html', title=html_elements[0], tagline=html_elements[1], 
    image=html_elements[2], backImage=html_elements[3], link=html_elements[4], 
    number=html_elements[5], info=html_elements[6], genres=html_elements[7], movieList=html_elements[8], id=html_elements[9], valid=current_user.username, reviews=movie_reviews)

@app.route('/direct_movie', methods=['GET', 'POST'])
@login_required
def direct():
    '''Function which handles HTML form leading to direction to movie specific page'''
    if request.form.get("movie_rank") == 'empty':
        flash('Movie Was Not Selected Below')
        return redirect(url_for('featuring_page'))
    
    global GLOBAL_MOVIE_NUM
    GLOBAL_MOVIE_NUM = int(request.form.get("movie_rank"))
    return redirect(url_for('show_movie', movie_title=trending_json_data['results'][GLOBAL_MOVIE_NUM]['original_title']))

@app.route('/<movie_title>')
@login_required
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
    movie_reviews = None
    if movie_review_exists(html_elements[9]):
        movie_reviews = movie_review_list(html_elements[9])
    return render_template('movie.html', title=html_elements[0], tagline=html_elements[1], 
    image=html_elements[2], backImage=html_elements[3], link=html_elements[4], 
    number=html_elements[5], info=html_elements[6], genres=html_elements[7], movieList=html_elements[8], id=html_elements[9], valid=current_user.username, reviews=movie_reviews)

@app.route('/logOut', methods=['GET', 'POST'])
@login_required
def log_out():
    '''Function which handles user Log Out'''
    logout_user()
    return redirect(url_for('log_in'))

@app.route('/addReviewSpecific', methods=['GET', 'POST'])
@login_required
def new_review_specific():
    '''Function which handles HTML form leading to sign up page'''
    if request.form.get("rating") == 'empty':
        flash('Rating not selected')
        return redirect(url_for('show_movie', movie_title=trending_json_data['results'][GLOBAL_MOVIE_NUM]['original_title']))
    movie_id = request.form.get("movieID")
    rating = request.form.get("rating")
    comments = request.form.get("comments")

    new_review = MovieReviews(movie_ID=movie_id, user=current_user.username, rating=rating, comments=comments)
    db.session.add(new_review)
    db.session.commit()

    return redirect(url_for('show_movie', movie_title=trending_json_data['results'][GLOBAL_MOVIE_NUM]['original_title']))
