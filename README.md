### project1-Victor-Ekpenyong
# Top 20 Trending Movies This Week
### Created By : Victor Ekpenyong
## Deployed Site - https://tttmthisweek.fly.dev/
## Overview
* This project utilizes python flask framework on the backend for the server side of the technology stack. Libraries utilized within this project include:
    * os, dotenv.load_dotenv, and dotenv.find_dotenv used for retrieval of secret variables within .env file. 
    * Python's random library is used within main Feature Page to randomize movie being featured. 
    * The requests library is used in coordination with requesting data through API calls.
    * Finally, flask.Flask, flask.render_template, flask.request, flask.redirect, flask.url_for, flask.flash are used for multiple app functionalities including rendering pages, redirecting and error handling.
* Multiple API calls are used to populate trending movie data, as well as direction to the movie's Wikipedia page. This project utilizes 4 different API requests from TMDB and 1 API request from Wikipedia. The goal of this project and website is to display a random movie out of the top 20 trending movies this week as well as providing the user the ability to view specific movies within that list.
## Initial Set Up
1. Make Sure that you have a functioning TMDB API Key
    * Create an account and register for an API key for free at https://www.themoviedb.org/
    * Within your .env file, have your TMDB API Key set to the variable name 'TMDB_API_KEY'
2. Create an app_secret_key
    * Make your own app_secret_key and store it within your .env file set to the variable name 'APP_SECRET_KEY'
## How To Run
1. Ensure you have python or python3 installed
2. Ensure you have flask installed, if not [Install Flask Here](https://flask.palletsprojects.com/en/1.1.x/installation/#virtual-environments)
3. There are multiple ways to run within the terminal, choose one you're most comfortable with
    * FLASK_APP=featured_movie flask run
    * python3 featured_movie.py or python featured_movie.py
## Follow Up Questions
#### "What are at least 2 technical issues you encountered with your project? How did you fix them?"
* I had a pretty hard time pulling the url for the movie backdrop image and passing it in as the background of a div container. This was difficult to do since the url is a variable which needed to be passed into the html through jinja. I solved this by having the styling of that specific div 'inline' instead of 'external' and through this I was able to add the faded look I was looking for.
* I had a really difficult time and process in figuring out the redirection of the application based on the specific movie the user selects. How I solved this was through research and listening to class lecture on how redirects and flashes work. This new understanding led me to implement this feature.
#### "What are at least 2 known problems (still existing), if any, with your project? (If none, what are two things you would improve about your project if given more time?)"
* One existing problem is that the queried Wikipedia link is not 100%, meaning that there are rare times where the link will not be the actually page of the movie. 9 times out of 10, the correct link is present.
* If I had more time, I would implement a feature where the user could search for an actor and if they are present in one of the trending movies the application will direct them to that movie specific page.

### Thank You for reading, happy coding!