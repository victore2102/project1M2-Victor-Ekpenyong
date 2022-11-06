### project1-Victor-Ekpenyong
# Top 20 Trending Movies This Week V2
### Created By : Victor Ekpenyong
## Deployed Site - https://tttmthisweekv2.fly.dev/
## Overview
* This project utilizes python flask framework on the backend for the server side of the technology stack. Libraries utilized within this project include:
    * os, dotenv.load_dotenv, and dotenv.find_dotenv used for retrieval of secret variables within .env file. 
    * Python's random library is used within main Feature Page to randomize movie being featured. 
    * The requests library is used in coordination with requesting data through API calls.
    * Finally, flask.Flask, flask.render_template, flask.request, flask.redirect, flask.url_for, flask.flash are used for multiple app functionalities including rendering pages, redirecting and error handling.
* Multiple API calls are used to populate trending movie data, as well as direction to the movie's Wikipedia page. This project utilizes 4 different API requests from TMDB and 1 API request from Wikipedia. The goal of this project and website is to display a random movie out of the top 20 trending movies this week as well as providing the user the ability to view specific movies within that list.
## NEW!
1. User Login / Sign Up 
    * A site viewer must login and/or signup in order to access this application
    * User signup/login includes a username and password field with critea which must be met
2. Reviews
    * Logged in users can post reviews about the movie they are viewing and view previous reviews posted by others
3. Postgresql Database Used
    * Postgresql database used for both user account storage and review storage in order for persistant data to be present
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
* I had an extremly frustrating time in doing the initial steps in setting up the postgresql database through fly.io. I kept having timed out errors and I scoured through the internet looking for a solution with no success. Luckily, running 'fly agent restart' allowed for me to finally set up my database.
* Within my application integrated the delete feature of a review wasn't too dificult, but it wasn't easy either. I had to make sure that the query matched every field which comes from the delete button form.
#### "How did your experience working on this milestone differ from what you pictured while working through the planning process? What was unexpectedly hard? Was anything unexpectedly easy?"
* My experienced differed with this milestone greatly. I would say UI wise, it was easier since I was able to build off of milestone 1 and just add certain sections here and there. Like I mentioned above it was very unexpected to me how much of a problem I had in setting up the database. If it wasn't for the class demo, I probably would've struggled even more. After I was able to set up my database and do local testing, it was not too bad querying the data and adding information to my table models. I would say that this milestone definitely challenged me!

### Thank You for reading, happy coding!