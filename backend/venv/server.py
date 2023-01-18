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

from flask_cors import CORS, cross_origin

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
from movie_recommendations import get_recommendations, get_recommendations_using_3_factors, get_intralist_similarity

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

CORS(app, supports_credentials=True)

jwt = JWTManager(app)

app.config['SESSION_TYPE'] = 'memcached'

cosinus_matrix = create_cosinus_matrix()

def display_genres(string_genres):
    json_object = json.loads(string_genres)
    genres = ""
    for pair in json_object:
        genres = genres + str(pair["name"]) + " "
    
    return genres

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
#@jwt_required()
def start_page():
    return "<p>Hello World!</p>"

#region ACCESS OPERATIONS

## variables for register
# Nume și prenume
# Adresă de email
# Parola
# Vârsta
# Gen
# (opțional) 3 filme preferate
# (opțional) 3 genuri de filme preferate

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

        return response
    else:
        return jsonify('Bad email or Password'), 401

@app.route("/logout", methods=["DELETE"])
#@jwt_required()
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

#endregion

#region UTILS

@app.route("/deleteuser", methods=["DELETE"])
#@jwt_required()
def delete_user():
    d_user = request.get_json()
    delete_result = database.SACdb.users.delete_one({"email_address": d_user["email_address"]})
    if delete_result.deleted_count == 1:
        return make_response('User successfully deleted.', 203)
    else:
        return make_response('User doesnt exists.', 204)

@app.route("/getallusers", methods=["GET"])
#@jwt_required()
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

#endregion

#region USER BASIC FUNCTIONALITIES

@app.route("/likerblfilm", methods=["POST"])
#@jwt_required()
def like_rbl_film():
    film = request.args
    user_email = film.get("email")
    title = film.get("film")

    user_file = './liked_r_l_films/' + hash_file_name(user_email)
    check = os.path.isfile(user_file)
    if check is not True:
        with open(user_file, 'w') as f:
            f.write(str(title + "\n"))
    else:
        with open(user_file, 'a') as f:
            f.write(str(title + "\n"))
    
    return make_response('Successfully operation.', 201)

@app.route("/likerbwfilm", methods=["POST"])
#@jwt_required()
def like_rbw_film():
    film = request.args
    user_email = film.get("email")
    title = film.get("film")

    user_file = './liked_r_w_films/' + hash_file_name(user_email)
    check = os.path.isfile(user_file)
    if check is not True:
        with open(user_file, 'w') as f:
            f.write(str(title + "\n"))
    else:
        with open(user_file, 'a') as f:
            f.write(str(title + "\n"))
    
    return make_response('Successfully operation.', 201)

@app.route("/likerballfilm", methods=["POST"])
#@jwt_required()
def like_rball_film():
    film = request.args
    user_email = film.get("email")
    title = film.get("film")

    user_file = './liked_r_3_m_films/' + hash_file_name(user_email)
    check = os.path.isfile(user_file)
    if check is not True:
        with open(user_file, 'w') as f:
            f.write(str(title + "\n"))
    else:
        with open(user_file, 'a') as f:
            f.write(str(title + "\n"))
    
    return make_response('Successfully operation.', 201)

@app.route("/likefilm", methods=["POST"])
#@jwt_required()
def like_film():
    film = request.args
    user_email = film.get("email")
    title = film.get("film")

    user_file = './blob_user_films/' + hash_file_name(user_email)
    check = os.path.isfile(user_file)
    if check is not True:
        with open(user_file, 'w') as f:
            f.write(str(title + "\n"))
    else:
        with open(user_file, 'a') as f:
            f.write(str(title + "\n"))
    
    return make_response('Successfully operation.', 201)

@app.route("/unlikefilm", methods=["DELETE"])
#@jwt_required()
def unlike_film():
    film = request.args

    user_email = film.get("email")
    title = film.get("film")
    user_file = './blob_user_films/' + hash_file_name(user_email)
    check = os.path.isfile(user_file)
    if check is True:
        with open(user_file, "r") as f:
            lines = f.readlines()
        with open(user_file, "w") as f:
            for line in lines:
                if line.strip("\n") != title:
                    f.write(line)

    return make_response('Successfully operation.', 201) 

@app.route("/ignorerecommandation", methods=["POST"])
#@jwt_required()
def ignore_recommandation():
    film = request.args

    user_email = film.get("email")
    title = film.get("film")

    user_file = './ignored_user_films/' + hash_file_name(user_email)
    check = os.path.isfile(user_file)
    if check is not True:
        with open(user_file, 'w') as f:
            f.write(str(title + "\n"))
    else:
        with open(user_file, 'a') as f:
            f.write(str(title + "\n"))
    
    return make_response('Successfully operation.', 201)

@app.route("/watchfilm", methods=["POST"])
#@jwt_required()
def watch_film():
    film = request.args

    user_email = film.get("email")
    title = film.get("film")

    file = './watched_films/' + hash_file_name(user_email)
    check = os.path.isfile(file)
    if check is not True:
        with open(file, 'w') as f:
            f.write(str(title + "\n"))
    else:
        with open(file, 'a') as f:
            f.write(str(title + "\n"))
    
    return make_response('Successfully operation.', 201)

@app.route("/getfilmsliked", methods=["GET"])
#@jwt_required()
def get_films_liked():
    user_email = request.args.get('email')
    user_file = './blob_user_films/' + hash_file_name(user_email)

    check = os.path.isfile(user_file)
    if check is True:
        file = open(user_file, 'r')
        lines = file.readlines()
        # Strips the newline character
        films = []
        for line in lines:
            films.append({
                "name": line.strip()
            })
        if len(films) == 0:
            return jsonify({'films': films})   
        else:
            return jsonify({'films': films}) 
    else:
        return jsonify({'films': films}) 

@app.route("/getfilmsignored", methods=["GET"])
#@jwt_required()
def get_films_ignored():
    user_email = request.args.get('email')
    user_file = './ignored_user_films/' + hash_file_name(user_email)

    check = os.path.isfile(user_file)
    if check is True:
        file = open(user_file, 'r')
        lines = file.readlines()
        # Strips the newline character
        films = []
        for line in lines:
            films.append ({
                "name": line.strip()
            })
        if len(films) == 0:
            return jsonify({'films': films})   
        else:
            return jsonify({'films': films}) 
    else:
        return jsonify({'films': films}) 

@app.route("/getfilmswatched", methods=["GET"])
#@jwt_required()
def get_films_watched():
    user_email = request.args.get('email')
    user_file = './watched_films/' + hash_file_name(user_email)

    check = os.path.isfile(user_file)
    if check is True:
        file = open(user_file, 'r')
        lines = file.readlines()
        # Strips the newline character
        films = []
        for line in lines:
            films.append({
                "name": line.strip()
            })
        if len(films) == 0:
            return jsonify({'films': films})   
        else:
            return jsonify({'films': films}) 
    else:
        return jsonify({'films': films})   

@app.route("/getallfilms", methods=["GET"])
#@jwt_required()
def get_all_films():
    # querying the database
    # for all the entries in it
    films = database.SACdb.films.find({})
    # converting the query objects
    output = []
    counter = 0

    for film in films:
        if counter == 100:
            break
        output.append({
            "budget": film["budget"],
            "genres": display_genres(film["genres"]),
            "original_title": film["original_title"],
            "overview": film["overview"],
            "popularity": film["popularity"],
            "release_date": film["release_date"],
            "revenue": film["revenue"],
            "runtime": film["runtime"],
            "title": film["title"],
        })
        counter = counter + 1
  
    return jsonify({'films': output})

#endregion

#region MAKE RECOMMANDATIONS

@app.route("/getuserrecommendedfilms", methods=["GET"])
#@jwt_required()
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
            "original_title": aux["original_title"],
            "overview": aux["overview"],
            "popularity": aux["popularity"],
            "release_date": aux["release_date"],
            "revenue": aux["revenue"],
            "runtime": aux["runtime"],
            "status":aux["status"],
            "title": aux["title"]
        })
  
    return jsonify({'films': recommended_films})

@app.route("/getuserrecommendedfilms3factors", methods=["GET"])
#@jwt_required()
def get_user_recommended_films_using_3_factors():
    user_email = request.args.get('email')

    preffered_films = []
    informations = database.SACdb.users.find_one({'email_address': user_email})
    for i in informations["films"]:
        preffered_films.append(i)
    
    preffered_films_id = []
    for i in preffered_films:
        aux = database.SACdb.films.find_one({"title": i})
        preffered_films_id.append(int(aux["movie_id"]))

    user_file = './blob_user_films/' + hash_file_name(user_email)
    check = os.path.isfile(user_file)
    films_liked = []
    if check is True:
        file = open(user_file, 'r')
        lines = file.readlines()
        for line in lines:
            films_liked.append(line.strip())
    
    liked_films_id = []
    for i in films_liked:
        aux = database.SACdb.films.find_one({"title": i})
        liked_films_id.append(int(aux["movie_id"]))

    watched_films_file = './watched_films/' + hash_file_name(user_email)
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

    recommandations = get_recommendations_using_3_factors(preffered_films_id, liked_films_id, watched_films_id, cosinus_matrix)

    # filter

    ignored_films_file = './ignored_user_films/' + hash_file_name(user_email)
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

    recommandations = [x for x in recommandations if x not in ignored_films_id]

    recommended_films = []
    for r in recommandations:
        aux = database.SACdb.films.find_one({"movie_id": str(r)})
        recommended_films.append({
            "budget": aux["budget"],
            "genres": display_genres(aux["genres"]),
            "original_title": aux["original_title"],
            "overview": aux["overview"],
            "popularity": aux["popularity"],
            "release_date": aux["release_date"],
            "revenue": aux["revenue"],
            "runtime": aux["runtime"],
            "status":aux["status"],
            "title": aux["title"]
        })
  
    return jsonify({'films': recommended_films})

@app.route("/getuserrecommendedbasedonmovieswatched", methods=["GET"])
#@jwt_required()
def get_user_recommended_based_on_movies_watched():
    user_email = request.args.get('email')

    watched_films_file = './watched_films/' + hash_file_name(user_email)
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

    recommandations = get_recommendations(watched_films_id, cosinus_matrix)

    # filter

    ignored_films_file = './ignored_user_films/' + hash_file_name(user_email)
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

    recommandations = [x for x in recommandations if x not in ignored_films_id]

    recommended_films = []
    for r in recommandations:
        aux = database.SACdb.films.find_one({"movie_id": str(r)})
        recommended_films.append({
            "budget": aux["budget"],
            "genres": display_genres(aux["genres"]),
            "original_title": aux["original_title"],
            "overview": aux["overview"],
            "popularity": aux["popularity"],
            "release_date": aux["release_date"],
            "revenue": aux["revenue"],
            "runtime": aux["runtime"],
            "status":aux["status"],
            "title": aux["title"]
        })
  
    return jsonify({'films': recommended_films})

@app.route("/getuserrecommendedbasedonmoviesliked", methods=["GET"])
#@jwt_required()
def get_user_recommended_based_on_movies_liked():
    user_email = request.args.get('email')

    user_file = './blob_user_films/' + hash_file_name(user_email)
    check = os.path.isfile(user_file)
    films_liked = []
    if check is True:
        file = open(user_file, 'r')
        lines = file.readlines()
        for line in lines:
            films_liked.append(line.strip())
    
    liked_films_id = []
    for i in films_liked:
        aux = database.SACdb.films.find_one({"title": i})
        liked_films_id.append(int(aux["movie_id"]))

    recommandations = get_recommendations(liked_films_id, cosinus_matrix)

    # filter

    ignored_films_file = './ignored_user_films/' + hash_file_name(user_email)
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

    recommandations = [x for x in recommandations if x not in ignored_films_id]

    recommended_films = []
    for r in recommandations:
        aux = database.SACdb.films.find_one({"movie_id": str(r)})
        recommended_films.append({
            "budget": aux["budget"],
            "genres": display_genres(aux["genres"]),
            "original_title": aux["original_title"],
            "overview": aux["overview"],
            "popularity": aux["popularity"],
            "release_date": aux["release_date"],
            "revenue": aux["revenue"],
            "runtime": aux["runtime"],
            "status":aux["status"],
            "title": aux["title"]
        })
  
    return jsonify({'films': recommended_films})

@app.route("/getuserrecommendedbasedonmoviespreffered", methods=["GET"])
#@jwt_required()
def get_user_recommended_based_on_movies_preffered():
    user_email = request.args.get('email')

    preffered_films = []
    informations = database.SACdb.users.find_one({'email_address': user_email})
    for i in informations["films"]:
        preffered_films.append(i)
    
    preffered_films_id = []
    for i in preffered_films:
        aux = database.SACdb.films.find_one({"title": i})
        preffered_films_id.append(int(aux["movie_id"]))

    recommandations = get_recommendations(preffered_films_id, cosinus_matrix)

    # filter

    ignored_films_file = './ignored_user_films/' + hash_file_name(user_email)
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

    recommandations = [x for x in recommandations if x not in ignored_films_id]

    recommended_films = []
    for r in recommandations:
        aux = database.SACdb.films.find_one({"movie_id": str(r)})
        recommended_films.append({
            "budget": aux["budget"],
            "genres": display_genres(aux["genres"]),
            "original_title": aux["original_title"],
            "overview": aux["overview"],
            "popularity": aux["popularity"],
            "release_date": aux["release_date"],
            "revenue": aux["revenue"],
            "runtime": aux["runtime"],
            "status":aux["status"],
            "title": aux["title"]
        })
  
    return jsonify({'films': recommended_films})

#endregion

def get_file_lines(filename):
    try:
        file1 = open(filename, 'r')
        lines = file1.readlines()
        return len(lines)
    except IOError:
        return 0

@app.route("/getstatistics", methods=["GET"])
#@jwt_required()
def get_statistics():
    user_email = request.args.get('email')

    preffered_films = []
    informations = database.SACdb.users.find_one({'email_address': user_email})
    for i in informations["films"]:
        preffered_films.append(i)
    
    preffered_films_id = []
    for i in preffered_films:
        aux = database.SACdb.films.find_one({"title": i})
        preffered_films_id.append(int(aux["movie_id"]))

    user_file = './blob_user_films/' + hash_file_name(user_email)
    check = os.path.isfile(user_file)
    films_liked = []
    if check is True:
        file = open(user_file, 'r')
        lines = file.readlines()
        for line in lines:
            films_liked.append(line.strip())
    
    liked_films_id = []
    for i in films_liked:
        aux = database.SACdb.films.find_one({"title": i})
        liked_films_id.append(int(aux["movie_id"]))

    watched_films_file = './watched_films/' + hash_file_name(user_email)
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

    intralist_similarity = get_intralist_similarity(preffered_films_id, liked_films_id, watched_films_id, cosinus_matrix)

    statistics = [{
        "is": intralist_similarity,
        "bl": int(get_file_lines('./liked_r_l_films/' + hash_file_name(user_email))) / int(get_file_lines('./blob_user_films/' + hash_file_name(user_email))),
        "bw": int(get_file_lines('./liked_r_w_films/' + hash_file_name(user_email))) / int(get_file_lines('./blob_user_films/' + hash_file_name(user_email))),
        "ba": int(get_file_lines('./liked_r_3_m_films/' + hash_file_name(user_email))) / int(get_file_lines('./blob_user_films/' + hash_file_name(user_email)))
    }]
    return jsonify({'statistics': statistics})
