'''Featured Movie Flask App V2 - Victor Ekpenyong (2022)'''
import os
import random
import requests
from flask import Flask, render_template, request, redirect, url_for, flash
from dotenv import load_dotenv, find_dotenv
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_required, current_user, login_user, logout_user
from flask_login import UserMixin

#'''.env initialization'''
load_dotenv(find_dotenv())

#'''URL Constants'''
TMDB_API_BASE_URL = 'https://api.themoviedb.org/3/trending/movie/week'
TMBD_API_CONFIG_URL = 'https://api.themoviedb.org/3/configuration'
WIKI_BASE_URL = 'https://en.wikipedia.org/w/api.php'
GENRE_LIST_BASE_URL = 'https://api.themoviedb.org/3/genre/movie/list'
TMDB_API_MOVIE_DATA_BASE_URL = 'https://api.themoviedb.org/3/movie/'

#'''App Configurations'''
app = Flask(__name__)
app.secret_key = os.getenv('APP_SECRET_KEY')
app.config['SECRET_KEY'] = app.secret_key
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DB_URI')
db = SQLAlchemy(app)

#'''DB MODELS'''
class MovieReviews(db.Model):
    '''Movie Review Table'''
    id = db.Column(db.Integer, primary_key=True)
    movie_ID = db.Column(db.String(6), unique=False, nullable=False)
    user = db.Column(db.String(50), unique=False, nullable=False)
    rating = db.Column(db.String(8), unique=False, nullable=False)
    comments = db.Column(db.String(200), unique=False, nullable=False)
    def __repr__(self) -> str:
        return f"{self.user}-&-{self.rating}-&-{self.comments}-&-{self.movie_ID}--END--"

class Member(UserMixin, db.Model):
    '''User DB Table'''
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), unique=False, nullable=False)

    def __repr__(self) -> str:
        return f"Member with username: {self.username}"


#'''DB Table Initialization'''
with app.app_context():
    db.create_all()


#'''Flask Login Setup'''
login_manager = LoginManager()
login_manager.login_view = 'log_in'
login_manager.init_app(app)
@login_manager.user_loader
def load_member(member_id):
    '''Function which handles loading a user'''
    return Member.query.get(int(member_id))


#'''GLOBAL VARIABLES NEEDED BY MULTIPLE FUNCTIONS'''
GLOBAL_MOVIE_NUM = 0
TRENDING_JSON_DATA = []

#'''App Building Functions'''
def app_logic(movie, TRENDING_JSON_DATA):
    '''Function which returns needed jinja elements for HTML page to render'''
    response2 = requests.get(
        TMBD_API_CONFIG_URL,
        params={
            'api_key': os.getenv('TMDB_API_KEY')
        },
        timeout=10
    )
    response3 = requests.get(
        GENRE_LIST_BASE_URL,
        params={
            'api_key': os.getenv('TMDB_API_KEY')
        },
        timeout=10
    )
    url = response2.json()
    genre = response3.json()
    movie_id_num = str(TRENDING_JSON_DATA['results'][movie]['id'])
    movie_title = TRENDING_JSON_DATA['results'][movie]['original_title']
    movie_poster_url = url['images']['secure_base_url'] + url['images']['poster_sizes'][3] + '/' + TRENDING_JSON_DATA['results'][movie]['poster_path']
    movie_backdrop_url = url['images']['secure_base_url'] + url['images']['backdrop_sizes'][3] + '/' + TRENDING_JSON_DATA['results'][movie]['backdrop_path']
    movie_description = TRENDING_JSON_DATA['results'][movie]['overview']
    response4 = requests.get(
        TMDB_API_MOVIE_DATA_BASE_URL + movie_id_num,
        params={
            'api_key': os.getenv('TMDB_API_KEY')
        },
        timeout=10
    )
    movie_details = response4.json()
    movie_tagline = movie_details['tagline']
    production = movie_details['production_companies'][0]['name']
    genre_set = set(TRENDING_JSON_DATA['results'][movie]['genre_ids'])
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
            'srsearch': movie_title + ' Film (' + TRENDING_JSON_DATA['results'][movie]['release_date'][0:4] + ') released by ' + production
        },
        timeout=10
    )
    wiki = response5.json()
    wiki_link = 'https://en.wikipedia.org/?curid=' + str(wiki['query']['search'][0]['pageid'])
    return [movie_title, movie_tagline, movie_poster_url, movie_backdrop_url, wiki_link, movie+1, movie_description, genre_string, TRENDING_JSON_DATA, movie_id_num]

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
    filtered_reviews = filtered_reviews.rstrip("--END--]")
    reviews_split = list(filtered_reviews.split("--END--, "))
    for r in reviews_split:
        r_split = list(r.split("-&-"))
        reviews_list.append(r_split)
    return reviews_list


#'''Routing Functions (Login, SignUp, Logout)'''
@app.route('/', methods=['GET', 'POST'])
def log_in():
    '''Function which handles user login, landing page'''
    return render_template('login.html')

@app.route('/signUp', methods=['GET', 'POST'])
def sign_up():
    '''Function which handles user signup'''
    return render_template('signup.html')

@app.route('/validateLogin', methods=['GET', 'POST'])
def validate_login():
    '''Function which handles login validation'''
    username = str(request.form.get("UserName"))
    password = str(request.form.get("PassWord"))
    user = Member.query.filter_by(username=username, password=password).first()
    if user:
        login_user(user)
        return redirect(url_for('featuring_page'))
    flash('Username and/or Passeword invalid, try again or click below to Sign Up')
    return redirect(url_for('log_in'))
    
@app.route('/validateSignup', methods=['GET', 'POST'])
def validate_signup():
    '''Function which handles signup validation'''
    username = str(request.form.get("UserName"))
    password = str(request.form.get("PassWord"))
    print("Password Valid? - ", request.form.get("passwordValid"))
    user = Member.query.filter_by(username=username).first()
    if user:
        flash('User Name already in use, try again or click below to Log In')
        return redirect(url_for('sign_up'))
    new_user = Member(username = username, password=password)
    db.session.add(new_user)
    db.session.commit()
    return redirect(url_for('log_in'))

@app.route('/logOut', methods=['GET', 'POST'])
@login_required
def log_out():
    '''Function which handles user Log Out'''
    logout_user()
    return redirect(url_for('log_in'))
    

#'''Routing Functions (Featured Page, Specific Page, Add Review, Delete Review)'''
@app.route('/featuring')
@login_required
def featuring_page():
    ''' Opening Function which runs after user has logged in'''
    response1 = requests.get(
        TMDB_API_BASE_URL,
        params={
            'api_key': os.getenv('TMDB_API_KEY')
        },
        timeout=10
    )
    global TRENDING_JSON_DATA
    TRENDING_JSON_DATA = response1.json()
    movie = random.randint(0,19)
    html_elements = app_logic(movie, TRENDING_JSON_DATA)
    movie_reviews = None
    if movie_review_exists(html_elements[9]):
        movie_reviews = movie_review_list(html_elements[9])
    return render_template('index.html', title=html_elements[0], tagline=html_elements[1], 
    image=html_elements[2], backImage=html_elements[3], link=html_elements[4], 
    number=html_elements[5], info=html_elements[6], genres=html_elements[7], movieList=html_elements[8], id=html_elements[9], valid=str(current_user.username), reviews=movie_reviews)

@app.route('/direct_movie', methods=['GET', 'POST'])
@login_required
def direct():
    '''Function which handles HTML form leading to direction to movie specific page'''
    if request.form.get("movie_rank") == 'empty':
        flash('Movie Was Not Selected Below')
        return redirect(url_for('featuring_page'))
    global GLOBAL_MOVIE_NUM
    GLOBAL_MOVIE_NUM = int(request.form.get("movie_rank"))
    return redirect(url_for('show_movie', movie_title=TRENDING_JSON_DATA['results'][GLOBAL_MOVIE_NUM]['original_title']))

@app.route('/<movie_title>')
@login_required
def show_movie(movie_title= None):
    '''Function which renders movie specific page with ability to redirect back to main page'''
    response1 = requests.get(
        TMDB_API_BASE_URL,
        params={
            'api_key': os.getenv('TMDB_API_KEY')
        },
        timeout=10
    )
    global TRENDING_JSON_DATA
    TRENDING_JSON_DATA = response1.json()
    html_elements = app_logic(GLOBAL_MOVIE_NUM, TRENDING_JSON_DATA)
    movie_reviews = None
    if movie_review_exists(html_elements[9]):
        movie_reviews = movie_review_list(html_elements[9])
    return render_template('movie.html', title=html_elements[0], tagline=html_elements[1], 
    image=html_elements[2], backImage=html_elements[3], link=html_elements[4], 
    number=html_elements[5], info=html_elements[6], genres=html_elements[7], movieList=html_elements[8], id=html_elements[9], valid=str(current_user.username), reviews=movie_reviews)

@app.route('/addReviewMain', methods=['GET', 'POST'])
@login_required
def new_review_main():
    '''Function which handles adding of a new review from the featuring page'''
    if request.form.get("rating") == 'empty':
        flash('Rating not selected')
        return redirect(url_for('featuring_page'))
    movie_id = request.form.get("movieID")
    rating = request.form.get("rating")
    comments = request.form.get("comments")
    new_review = MovieReviews(movie_ID=movie_id, user=str(current_user.username), rating=rating, comments=comments)
    db.session.add(new_review)
    db.session.commit()
    return redirect(url_for('featuring_page'))

@app.route('/addReviewSpecific', methods=['GET', 'POST'])
@login_required
def new_review_specific():
    '''Function which handles adding of a new review from the movie specific page'''
    if request.form.get("rating") == 'empty':
        flash('Rating not selected')
        return redirect(url_for('show_movie', movie_title=TRENDING_JSON_DATA['results'][GLOBAL_MOVIE_NUM]['original_title']))
    movie_id = request.form.get("movieID")
    rating = request.form.get("rating")
    comments = request.form.get("comments")
    new_review = MovieReviews(movie_ID=movie_id, user=str(current_user.username), rating=rating, comments=comments)
    db.session.add(new_review)
    db.session.commit()
    return redirect(url_for('show_movie', movie_title=TRENDING_JSON_DATA['results'][GLOBAL_MOVIE_NUM]['original_title']))

@app.route('/deleteReviewMain', methods=['GET', 'POST'])
@login_required
def delete_review_main():
    '''Function which handles the deletion of a review from featuring page'''
    review = request.form.get("reviewToDelete")
    filtered_review = review.lstrip("['")
    filtered_review = filtered_review.rstrip("']")
    review_to_delete = list(filtered_review.split("', '"))
    MovieReviews.query.filter_by(movie_ID=str(review_to_delete[3]), user=str(review_to_delete[0]), rating=str(review_to_delete[1]), comments=str(review_to_delete[2])).delete()
    db.session.commit()
    flash('Review Deleted...')
    return redirect(url_for('featuring_page'))

@app.route('/deleteReviewSpecific', methods=['GET', 'POST'])
@login_required
def delete_review_specific():
    '''Function which handles the deletion of a review from featuring page'''
    review = request.form.get("reviewToDelete")
    filtered_review = review.lstrip("['")
    filtered_review = filtered_review.rstrip("']")
    review_to_delete = list(filtered_review.split("', '"))
    MovieReviews.query.filter_by(movie_ID=str(review_to_delete[3]), user=str(review_to_delete[0]), rating=str(review_to_delete[1]), comments=str(review_to_delete[2])).delete()
    db.session.commit()
    flash('Review Deleted...')
    return redirect(url_for('show_movie', movie_title=TRENDING_JSON_DATA['results'][GLOBAL_MOVIE_NUM]['original_title']))
