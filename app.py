import webbrowser
from flask import Flask, render_template, request,redirect,url_for, flash
from flask_sqlalchemy import SQLAlchemy
import secrets
import base64

secret_key = secrets.token_hex(16)


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
                #'postgresql://movie_catalog_db_user:f6uuYwBGN1phyJOAqg8Qu5zq9bHXuAOb@dpg-ckf2vgunpffc73f32i30-a.oregon-postgres.render.com/movie_catalog_db'
                #'sqlite:///database.db'
                #'postgresql://moviecatalog_db_user:ciWkyz7SL86pKtEjePXzz8cUtZBBP6Fj@dpg-cij7vt59aq01qqgpu29g-a.oregon-postgres.render.com/moviecatalog_db'
                #'postgresql://moviecatalog_db_user:ciWkyz7SL86pKtEjePXzz8cUtZBBP6Fj@dpg-cij7vt59aq01qqgpu29g-a/moviecatalog_db'
app.secret_key = secret_key

db = SQLAlchemy(app)

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    year = db.Column(db.Integer)
    industry = db.Column(db.String(100))
    series = db.Column(db.String(100))
    poster_data = db.Column(db.Text)

class WishList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    year = db.Column(db.Integer)
    industry = db.Column(db.String(100))
    series = db.Column(db.String(100))
    poster_data = db.Column(db.Text)
    
    
### All Routing Code Start from Here ##

# index page routing 
@app.route('/')
@app.route("/home")
@app.route("/index", methods=["GET"])
def index():
    msg = ""
    if request.method == "GET" :
        msg = request.args.get("msg")
    movies= Movie.query.all()
    total = len(movies)
    recnt_5 = movies[-5:]
    w_movies= WishList.query.all()
    recnt_wish_10 = w_movies[-10:]
    industries = []
    for movie in movies:
        industries.append(movie.industry)
        
    industries = set(industries)
    return render_template('index.html',msg=msg, total=total,recents = recnt_5, wishlist = recnt_wish_10, industries=industries)


# movie add page show routing 
@app.route("/add")
def add():
    seriesList = []
    movies = []
    db_movies = Movie.query.all()
    for movie in db_movies:
        name = movie.name
        serie = movie.series
        movies.append(name)
        seriesList.append(serie)
    setSeriesList = set(seriesList)
    NewSeriesList = list(setSeriesList)
    return render_template("add.html", movies = movies, series=NewSeriesList)


# new movie add page routing 
@app.route("/added", methods=["POST"])
def added():
    name = request.form["name"]
    year = request.form["year"]
    industry = request.form["industry"]
    series = request.form["series"]

    poster = request.files["poster"]
    poster_file_name = poster.filename
    if poster_file_name:
        poster_data = base64.b64encode(poster.read()).decode('utf-8')
    else:
        poster_data = base64.b64encode(open('static/images/default.jpg', 'rb').read()).decode('utf-8') 
    if not name or not year or not industry:
        flash("Input Required Details ")
    else:
        if request.form["watch"] == "watched":
            movie = Movie(name=name, year=year, industry=industry, series=series, poster_data=poster_data)
            db.session.add(movie)
            db.session.commit()
            flash("New Movie Added to Watched List")
        else:
            w_movie = WishList(name=name, year=year, industry=industry, series=series, poster_data=poster_data)
            db.session.add(w_movie)
            db.session.commit()
            flash("New Movie Added to WishList")
    return redirect(url_for("index"))


# movie update page routing 
@app.route("/update/<int:id>", methods=["GET", "POST"])
def update(id):
    movie = Movie.query.get(id)
    # poster = base64.b64encode(movie.poster_data).decode('utf-8')
    if request.method == "POST":
        movie.name = request.form["name"]
        movie.year = request.form["year"]
        movie.industry = request.form["industry"]
        movie.series = request.form["series"]
        
        poster = request.files["poster"]
        poster_f = poster.filename
        
        if poster_f:
            movie.poster_data = base64.b64encode(poster.read()).decode('utf-8')
            
        db.session.commit()
        flash("Movie details updated")
        return redirect(url_for("index"))
    return render_template("update.html", movie=movie)
    
# movie delete routing 
@app.route("/delete/<int:id>")
def delete(id):
    movie = Movie.query.get(id)
    if movie:
        db.session.delete(movie)
        db.session.commit()
        flash("Movie deleted successfully")
    else:
        flash("Movie not found")
    return redirect(url_for("index"))
   
   
 # movie details show page routing 
@app.route("/show", methods=["POST","GET"])
def show():
    if request.method == "GET":
        id = request.args.get("id")
        movie = Movie.query.get(id)
    return render_template("show.html", movie=movie)


# movie category show page routing 
@app.route("/cat-show", methods=["POST","GET"])
def cat_show():
    if request.method == "GET":
        cat = request.args.get("cat")
        movies = Movie.query.filter(Movie.industry == cat).all()
        total = len(movies)
        
        page = request.args.get('page', 1, type=int)  # Get the page number from the query parameter
        items_per_page = 40
        paginated_movies = movies[(page - 1) * items_per_page: page * items_per_page]
        start_index = (page - 1) * items_per_page + 1
        series = set([])
        for movie in movies:
            if movie.series:
                if movie.series == " ":
                    pass
                else:
                    series.add(movie.series)
                
        return render_template("cat-show.html", title=cat,industry=cat, total= total, movies=paginated_movies, page=page, items_per_page=items_per_page,start_index=start_index, series = series)

		
# movie category show page routing 
@app.route("/series-show", methods=["POST","GET"])
def series_show():
	if request.method == "GET":
		series = request.args.get("series")
		movies = Movie.query.filter(Movie.series == series).all()
		return render_template("series-show.html", title=series, total= len(movies), movies=movies)


@app.route("/autocomplete", methods=["POST"])
def autocomplete():
    search_term = request.form.get("search_term", "")
    movies = Movie.query.filter(Movie.name.contains(search_term)).all()
    suggestions = [movie.name+" ("+str(movie.year)+")" for movie in movies]
    return render_template("autocomplete.html", suggestions=movies)


@app.route("/action", methods=["POST", "GET"])
def do_action():
	if request.method == "GET":
		action = request.args.get("action")
		id = request.args.get("id")
		
		if action == "watched":
			w_movie = WishList.query.get(id)
			
			movie = Movie(name=w_movie.name, year=w_movie.year, industry=w_movie.industry, series=w_movie.series, poster_data=w_movie.poster_data)
			db.session.add(movie)
			db.session.commit()
			
			db.session.delete(w_movie)
			db.session.commit()
			flash("Movie successfully added to watched list")
		elif action == "delete":
			w_movie = WishList.query.get(id)
			db.session.delete(w_movie)
			db.session.commit()
			flash("Movie successfully deleted from  wish list")
	return redirect(url_for("index"))



@app.route("/test")
def test():
	industries = []
	movies = Movie.query.all()
	for movie in movies:
		industries.append(movie.industry)
	industries = set(industries)
	return "testing"

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    # app.run()
    # webbrowser.open("http://127.0.0.1:5000")
    app.run(
        host="0.0.0.0",
        # debug=True
    )
