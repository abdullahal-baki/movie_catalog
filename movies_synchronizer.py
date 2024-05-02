from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import warnings
from sqlalchemy.ext.declarative import declarative_base
warnings.filterwarnings("ignore", category=DeprecationWarning)


def main():
    Base = declarative_base()

    class Movie(Base):
        __tablename__ = 'movie'
        
        id = Column(Integer, primary_key=True)
        name = Column(String(100))
        year = Column(Integer)
        industry = Column(String(100))
        series = Column(String(100))
        poster_data = Column(Text)

    class WishList(Base):
        __tablename__ = 'wish_list'

        id = Column(Integer, primary_key=True)
        name = Column(String(100))
        year = Column(Integer)
        industry = Column(String(100))
        series = Column(String(100))
        poster_data = Column(Text)


    engine_remote = create_engine('postgresql://root:gRKzW8ZrIUc3@ep-solitary-bread-a2vfxx8b.eu-central-1.pg.koyeb.app/koyebdb')
    engine_local = create_engine('sqlite:///instance/database.db')

    Session_remote = sessionmaker(bind=engine_remote)
    Session_local = sessionmaker(bind=engine_local)

    Base.metadata.create_all(engine_remote)
    Base.metadata.create_all(engine_local)



    #------------------updating watched movies---------------
    #--show tables
    session_local = Session_local()
    movies_local = session_local.query(Movie).all()
    session_local.close()
    
    #--show tables
    session_remote = Session_remote()
    total_number_of_movies = session_remote.query(Movie).count()
    session_remote.close()
    remote_movies_list = []
    print("[+] Total in RemoteDB: ",total_number_of_movies)
    for movie_id in range(1, total_number_of_movies + 1): 
        print("[+] Fatching Movies from RemoteDB with ID: ",movie_id)
        try:
            session_remote = Session_remote()
            movie_remote = session_remote.query(Movie).get(movie_id)
            session_remote.close()
            if movie_remote is not None:
                remote_movies_list.append(movie_remote)
            else:
                print(f"No movie found with ID: {movie_id}")
        except:
            pass
    print("[+] RemoteDB Movies Fetched")
    
    # # Compare and update local movies
    print("[+] Upadating Local Watched Movies Database...")
    for movie_remote in remote_movies_list:
        movie_exists = False
        for movie_local in movies_local:
            if (movie_local.name == movie_remote.name and
                movie_local.year == movie_remote.year and
                movie_local.industry == movie_remote.industry):
                movie_exists = True
                print('[+] Already existed movie: ',movie_remote.name)
                break
        if not movie_exists:
            print('\n[+] New Movie Found at Remote Database.\n[+] Name: ',movie_remote.name)
            print('[+] Adding New Movie at Local Database.')
            session_local = Session_local()
            new_movie = Movie(
                                    name=movie_remote.name,
                                    year=movie_remote.year,
                                    industry=movie_remote.industry,
                                    series=movie_remote.series,
                                    poster_data=movie_remote.poster_data
                                )
            session_local.add(new_movie)
            session_local.commit()
            session_local.close()
            print('[+] New movie successfully added.\n\n')
            
            
    # Compare and update remote movies
    print("[+] Updating Remote Watched Movies Database...")
    for movie_local in movies_local:
        movie_exists = False
        for movie_remote in remote_movies_list:
            if (movie_local.name == movie_remote.name and
                movie_local.year == movie_remote.year and
                movie_local.industry == movie_remote.industry):
                movie_exists = True
                print('[+] Already existed movie: ', movie_remote.name)
                break
        if not movie_exists:
            print('\n[+] New Movie Found in Local Database.\n[+] Name: ', movie_local.name)
            print('[+] Adding New Movie to Remote Database.')
            session_remote = Session_remote()
            new_movie = Movie(
                name=movie_local.name,
                year=movie_local.year,
                industry=movie_local.industry,
                series=movie_local.series,
                poster_data=movie_local.poster_data
            )
            session_remote.add(new_movie)
            session_remote.commit()
            session_remote.close()
            print('[+] New movie successfully added.\n\n')

    #------------------E-N-D updating watched movies---------------



    #------------------Updating wishlist Movies---------------
    session_remote = Session_remote()
    wishlist_remote = session_remote.query(WishList).all()
    session_remote.close()

    session_local = Session_local()
    wishlist_local = session_local.query(WishList).all()
    session_local.close()

    print("[+] Updating Local WishList Database...")
    for movie_remote in wishlist_remote:
        movie_exists = False
        for movie_local in wishlist_local:
            if (movie_local.name == movie_remote.name and
                movie_local.year == movie_remote.year and
                movie_local.industry == movie_remote.industry):
                movie_exists = True
                print('[+] Already existed movie in wishlist: ', movie_remote.name)
                break
        if not movie_exists:
            print('\n[+] New Movie Found in Remote Wishlist.\n[+] Name: ', movie_remote.name)
            print('[+] Adding New Movie to Local Wishlist.')
            session_local = Session_local()
            new_movie = WishList(
                name=movie_remote.name,
                year=movie_remote.year,
                industry=movie_remote.industry,
                series=movie_remote.series,
                poster_data=movie_remote.poster_data
            )
            session_local.add(new_movie)
            session_local.commit()
            session_local.close()
            print('[+] New movie successfully added to local wishlist.\n\n')

    # Compare and update remote wishlist
    print("[+] Updating Remote WishList Database...")
    for movie_local in wishlist_local:
        movie_exists = False
        for movie_remote in wishlist_remote:
            if (movie_local.name == movie_remote.name and
                movie_local.year == movie_remote.year and
                movie_local.industry == movie_remote.industry):
                movie_exists = True
                print('[+] Already existed movie in remote wishlist: ', movie_remote.name)
                break
        if not movie_exists:
            print('\n[+] New Movie Found in Local Wishlist.\n[+] Name: ', movie_local.name)
            print('[+] Adding New Movie to Remote Wishlist.')
            session_remote = Session_remote()
            new_movie = WishList(
                name=movie_local.name,
                year=movie_local.year,
                industry=movie_local.industry,
                series=movie_local.series,
                poster_data=movie_local.poster_data
            )
            session_remote.add(new_movie)
            session_remote.commit()
            session_remote.close()
            print('[+] New movie successfully added to remote wishlist.\n\n')

    #------------------E-N-D updating wishlist movies---------------

main()