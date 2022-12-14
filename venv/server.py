import bson
import pymongo
import os
import flask
import json
import redis

from pymongo.collection import Collection, ReturnDocument
from crypto import hash_password, hash_file_name
from datetime import datetime, timedelta, timezone

from flask import Flask, request, url_for, jsonify, make_response
from flask_pymongo import PyMongo
from pymongo.errors import DuplicateKeyError

from flask import session
from flask_session import Session

from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager
from flask_jwt_extended import set_access_cookies
from flask_jwt_extended import unset_jwt_cookies

from model import User, RevokeToken, Film
from objectid import PydanticObjectId
from movie_recommendations import create_cosinus_matrix
from movie_recommendations import get_recommendations

ACCESS_EXPIRES = timedelta(hours=1)

# Configure Flask, Database, JWT:
app = Flask(__name__)

app.secret_key = os.environ.get("APP_SECRET_KEY")
# If true this will only allow the cookies that contain your JWTs to be sent
# over https. In production, this should always be set to True
app.config["JWT_COOKIE_SECURE"] = False
app.config["JWT_COOKIE_CSRF_PROTECT"] = False
app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY")  # Change this in your code!
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)

mongodb_url = "mongodb+srv://Alex:" + os.environ.get("MONGODB_API_KEY") + "@sac.ukrip3m.mongodb.net/SACdb?retryWrites=true&w=majority"
database = pymongo.MongoClient(mongodb_url)
jwt = JWTManager(app)

app.config['SESSION_TYPE'] = 'memcached'

cosinus_matrix = []

# Check Configuration section for more details
# SESSION_TYPE = 'mongodb'
# app.config.from_object(__name__)
# Session(app)

@app.after_request
def refresh_expiring_jwts(response):
    try:
        exp_timestamp = get_jwt()["exp"]
        now = datetime.now(timezone.utc)
        target_timestamp = datetime.timestamp(now + ACCESS_EXPIRES)
        if target_timestamp > exp_timestamp:
            access_token = create_access_token(identity=get_jwt_identity())
            set_access_cookies(response, access_token)
        return response
    except (RuntimeError, KeyError):
        # Case where there is not a valid JWT. Just return the original response
        return response

# Callback function to check if a JWT exists in the redis blocklist
# Callback function to check if a JWT exists in the database blocklist
@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload: dict) -> bool:
    jti = jwt_payload["jti"]
    token = database.SACdb.tokenblocklist.find_one({"jti": jti})

    return token is not None

## Routes

@app.errorhandler(404)
def resource_not_found(e):
    """
    An error-handler to ensure that 404 errors are returned as JSON.
    """
    return jsonify(error=str(e)), 404


@app.errorhandler(DuplicateKeyError)
def resource_not_found(e):
    """
    An error-handler to ensure that MongoDB duplicate key errors are returned as JSON.
    """
    return jsonify(error=f"Duplicate key error."), 400

@app.route("/")
@jwt_required()
def start_page():
    return "<p>Hello, World!</p>"

## variables for register
# Nume ??i prenume
# Adres?? de email
# Parola
# V??rsta
# Gen
# (op??ional) 3 filme preferate
# (op??ional) 3 genuri de filme preferate

@app.route("/signup", methods=["POST"])
def signup():
    raw_user = request.get_json()
    raw_user["password"] = hash_password(str(raw_user["password"]), str(raw_user["email_address"]))
    raw_user["register_date"] = datetime.utcnow()

    user_check = database.SACdb.users.find_one({"email_address": raw_user["email_address"]})

    if not user_check:
        new_user = User(**raw_user)
        insert_result = database.SACdb.users.insert_one(new_user.to_bson())
        new_user.id = PydanticObjectId(insert_result.inserted_id)

        return make_response('Successfully registered.', 201)
    else:
        # returns 202 if user already exists
        return make_response('User already exists. Please Log in.', 202)

@app.route('/login', methods=['POST'])
def login():
    user = request.get_json()

    password_hash = hash_password(str(user["password"]), str(user["email_address"]))

    user_check = database.SACdb.users.find_one({"email_address": user["email_address"], "password": password_hash})
   
    if user_check:
        response = jsonify({"msg": "Login!"})
        access_token = create_access_token(
            identity=user["email_address"]
        )
        set_access_cookies(response, access_token)

        global cosinus_matrix 
        cosinus_matrix = create_cosinus_matrix()

        return response
    else:
        return jsonify('Bad email or Password'), 401

# Endpoint for revoking the current users access token. Saved the unique
# identifier (jti) for the JWT into our database.
@app.route("/logout", methods=["DELETE"])
@jwt_required()
def modify_token():
    jti = get_jwt()["jti"]
    now = datetime.utcnow()
    revoke_token = {
        "jti": jti,
        "created_at": now
    }
    new_revoke_token = RevokeToken(**revoke_token)
    insert_result = database.SACdb.tokenblocklist.insert_one(new_revoke_token.to_bson())
    new_revoke_token.id = PydanticObjectId(insert_result.inserted_id)

    response = jsonify({"msg": "Logout!"})
    unset_jwt_cookies(response)
    return response

@app.route("/deleteuser", methods=["DELETE"])
@jwt_required()
def delete_user():
    d_user = request.get_json()
    delete_result = database.SACdb.users.delete_one({"email_address": d_user["email_address"]})
    if delete_result.deleted_count == 1:
        return make_response('User successfully deleted.', 203)
    else:
        return make_response('User doesnt exists.', 204)

@app.route("/getallusers", methods=["GET"])
@jwt_required()
def get_all_users():
    # querying the database
    # for all the entries in it
    users = database.SACdb.users.find({})
    # converting the query objects
    output = []
    for user in users:
        output.append({
            'first_name' : user["first_name"],
            'last_name' : user["last_name"],
            'email_address' : user["email_address"],
            'password' : user["password"],
            'age' : user["age"],
            'gender' : user["gender"],
            'films' : user["films"],
            'film_types' : user["film_types"],
            'register_date' : user["register_date"]
        })
  
    return jsonify({'users': output})

@app.route("/likefilm", methods=["POST"])
@jwt_required()
def like_film():
    film = request.get_json()
    user_file = './blob_user_films/' + hash_file_name(film["email_address"])
    check = os.path.isfile(user_file)
    if check is not True:
        with open(user_file, 'w') as f:
            f.write(str(film["film"] + "\n"))
    else:
        with open(user_file, 'a') as f:
            f.write(str(film["film"] + "\n"))
    
    return make_response('Successfully operation.', 201)

@app.route("/unlikefilm", methods=["DELETE"])
@jwt_required()
def unlike_film():
    film = request.get_json()
    user_file = './blob_user_films/' + hash_file_name(film["email_address"])
    check = os.path.isfile(user_file)
    if check is True:
        with open(user_file, "r") as f:
            lines = f.readlines()
        with open(user_file, "w") as f:
            for line in lines:
                if line.strip("\n") != film["film"]:
                    f.write(line)

    return make_response('Successfully operation.', 201)

@app.route("/getfilmsliked", methods=["GET"])
@jwt_required()
def get_films_liked():
    #code
    user = request.get_json()
    user_file = './blob_user_films/' + hash_file_name(user["email_address"])

    check = os.path.isfile(user_file)
    if check is True:
        file = open(user_file, 'r')
        lines = file.readlines()
        # Strips the newline character
        films = []
        for line in lines:
            films.append(line.strip())
        if len(films) == 0:
            return make_response('You dont have any liked films.', 202)  
        else:
            return jsonify({'films': films}) 
    else:
        return make_response('You dont have any liked films.', 202)    

@app.route("/insertfilms", methods=["POST"])
def insert_films():
    films = request.get_json()
    database.SACdb.films.insert_many([
        {
            "budget": films[i]["budget"],
            "genres": films[i]["genres"],
            "homepage": films[i]["homepage"],
            "keywords": films[i]["keywords"],
            "original_language": films[i]["original_language"],
            "original_title": films[i]["original_title"],
            "overview": films[i]["overview"],
            "popularity": films[i]["popularity"],
            "production_companies": films[i]["production_companies"],
            "production_countries": films[i]["production_countries"],
            "release_date": films[i]["release_date"],
            "revenue": films[i]["revenue"],
            "runtime": films[i]["runtime"],
            "status":films[i]["status"],
            "tagline": films[i]["tagline"],
            "title": films[i]["title"],
            "vote_average": films[i]["vote_average"],
            "vote_count": films[i]["vote_count"],
            "movie_id": films[i]["movie_id"],
            "register_date": datetime.utcnow()
        } for i in range(4800)
    ])
    return make_response('Successfully operation.', 201)

@app.route("/getallfilms", methods=["GET"])
@jwt_required()
def get_all_films():
    # querying the database
    # for all the entries in it
    films = database.SACdb.films.find({})
    # converting the query objects
    output = []
    for film in films:
        output.append({
            "budget": film["budget"],
            "genres": film["genres"],
            "homepage": film["homepage"],
            "keywords": film["keywords"],
            "original_language": film["original_language"],
            "original_title": film["original_title"],
            "overview": film["overview"],
            "popularity": film["popularity"],
            "production_companies": film["production_companies"],
            "production_countries": film["production_countries"],
            "release_date": film["release_date"],
            "revenue": film["revenue"],
            "runtime": film["runtime"],
            "status":film["status"],
            "tagline": film["tagline"],
            "title": film["title"],
            "vote_average": film["vote_average"],
            "vote_count": film["vote_count"],
            "movie_id": film["movie_id"],
            "register_date": film["register_date"]
        })
  
    return jsonify({'films': output})

@app.route("/getuserrecommendedfilms", methods=["GET"])
@jwt_required()
def get_user_recommended_films():
    user = request.get_json()

    films = []
    informations = database.SACdb.users.find_one({'email_address': user["email_address"]})
    for i in informations["films"]:
        films.append(i)

    # liked films
    user_file = './blob_user_films/' + hash_file_name(user["email_address"])
    check = os.path.isfile(user_file)
    if check is True:
        file = open(user_file, 'r')
        lines = file.readlines()
        # Strips the newline character
        for line in lines:
            films.append(line.strip())
    
    # watched films
    watched_films_file = './watched_films/' + hash_file_name(user["email_address"])
    check = os.path.isfile(watched_films_file)
    if check is True:
        file = open(watched_films_file, 'r')
        lines = file.readlines()
        for line in lines:
            films.append(line.strip())

    # create film array with what user had watched or liked
    id_array = []

    for film in films:
        aux = database.SACdb.films.find_one({"title": film})
        id_array.append(int(aux["movie_id"]))

    global cosinus_matrix
    recommandations = get_recommendations(id_array, cosinus_matrix)

    ignored_films_file = './ignored_user_films/' + hash_file_name(user["email_address"])
    check = os.path.isfile(ignored_films_file)
    ignored_films = []
    if check is True:
        file = open(ignored_films_file, 'r')
        lines = file.readlines()
        for line in lines:
            ignored_films.append(line.strip())
    
    ignored_films_id = []
    for i in ignored_films:
        aux = database.SACdb.films.find_one({"title": i})
        ignored_films_id.append(int(aux["movie_id"]))

    watched_films_file = './watched_films/' + hash_file_name(user["email_address"])
    check = os.path.isfile(watched_films_file)
    watched_films = []
    if check is True:
        file = open(watched_films_file, 'r')
        lines = file.readlines()
        for line in lines:
            watched_films.append(line.strip())
    
    watched_films_id = []
    for i in watched_films:
        aux = database.SACdb.films.find_one({"title": i})
        watched_films_id.append(int(aux["movie_id"]))

    # first filter
    recommandations = [x for x in recommandations if x not in ignored_films_id]

    # second filter
    recommandations = [x for x in recommandations if x not in watched_films_id]

    recommended_films = []
    for r in recommandations:
        aux = database.SACdb.films.find_one({"movie_id": str(r)})
        recommended_films.append({
            "budget": aux["budget"],
            "genres": aux["genres"],
            "homepage": aux["homepage"],
            "keywords": aux["keywords"],
            "original_language": aux["original_language"],
            "original_title": aux["original_title"],
            "overview": aux["overview"],
            "popularity": aux["popularity"],
            "production_companies": aux["production_companies"],
            "production_countries": aux["production_countries"],
            "release_date": aux["release_date"],
            "revenue": aux["revenue"],
            "runtime": aux["runtime"],
            "status":aux["status"],
            "tagline": aux["tagline"],
            "title": aux["title"],
            "vote_average": aux["vote_average"],
            "vote_count": aux["vote_count"],
            "movie_id": aux["movie_id"],
            "register_date": aux["register_date"]
        })
  
    return jsonify({'films': recommended_films})

@app.route("/ignorerecommandation", methods=["POST"])
@jwt_required()
def ignore_recommandation():
    film = request.get_json()
    user_file = './ignored_user_films/' + hash_file_name(film["email_address"])
    check = os.path.isfile(user_file)
    if check is not True:
        with open(user_file, 'w') as f:
            f.write(str(film["film"] + "\n"))
    else:
        with open(user_file, 'a') as f:
            f.write(str(film["film"] + "\n"))
    
    return make_response('Successfully operation.', 201)

@app.route("/watchfilm", methods=["POST"])
@jwt_required()
def watch_film():
    film = request.get_json()
    file = './watched_films/' + hash_file_name(film["email_address"])
    check = os.path.isfile(file)
    if check is not True:
        with open(file, 'w') as f:
            f.write(str(film["film"] + "\n"))
    else:
        with open(file, 'a') as f:
            f.write(str(film["film"] + "\n"))
    
    return make_response('Successfully operation.', 201)