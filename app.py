#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import collections
import collections.abc
import json
import sys
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from models import db, Artist, Venue, Show
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
migrate = Migrate(app, db)



# SQLALCHEMY_DATABASE_URI = 'postgres://postgres:callONme@postgres/fyyur'
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():

    distint_results = Venue.query.distinct(Venue.city, Venue.state).all() # to limit returning bogos results
    data = []
    
    for result in distint_results:
        city_and_state = {
            'city': result.city,
            'state': result.state,
        }

        venues = Venue.query.filter_by(city=result.city, state=result.state).all()
        
        store_temp = []
        for venue in venues:
            store_temp.append({
                "id": venue.id,
                "name": venue.name,
                "num_upcoming_shows": len(list(filter(lambda x: x.start_time > datetime.now(), venue.shows)))
            })

        city_and_state["venues"] = store_temp
        data.append(city_and_state)
    return render_template('pages/venues.html', areas=data)

# Venue search

@app.route('/venues/search', methods=['POST'])
def search_venues():
    search_term = request.form.get('search_term')
   
    response = {}
    venues = list(Venue.query.filter(
        Venue.name.ilike(f"%{search_term}%") |
        Venue.state.ilike(f"%{search_term}%") |
        Venue.city.ilike(f"%{search_term}%") 
    ).all())
    response["count"] = len(venues)

    data = []
    for venue in venues:
        store_venue = {
            "id" :venue.id,
            "name" :venue.name,
            "num_upcoming_shows" :len(venue.shows)
        }
        data.append(store_venue)
        
        
    response['data'] = data
    return render_template('pages/search_venues.html', results=response, search_term=search_term)


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    
    venue = Venue.query.get(venue_id)
    setattr(venue, "genres", venue.genres.split(","))
    past_shows_data = list(filter(lambda show: show.start_time < datetime.now(), venue.shows))
    upcoming_shows_data = list(filter(lambda show: show.start_time > datetime.now(), venue.shows))
    
    past_shows = []
    for show in past_shows_data:
        artist = Artist.query.get(show.artist_id)
        show_data = {
            "artist_id": artist.id,
            "artist_name": artist.name,
            "artist_image_link": artist.image_link,
            "start_time": str(show.start_time),
        }
        past_shows.append(show_data)
    
    upcoming_shows = []
    for show in upcoming_shows_data:
        artist = Artist.query.get(show.artist_id)
        show_data = {
            "artist_id": artist.id,
            "artist_name": artist.name,
            "artist_image_link": artist.image_link,
            "start_time": str(show.start_time),
        }
        upcoming_shows.append(show_data)

    data = {
            "id": venue.id,
            "name": venue.name,
            "genres": venue.genres,
            "city": venue.city,
            "state": venue.state,
            "phone": venue.phone,
            "address":venue.address,
            "seeking_talent": venue.seeking_talent,
            "facebook_link": venue.facebook_link,
            "image_link": venue.image_link,
            "past_shows": past_shows,
            "upcoming_shows": upcoming_shows,
            "past_shows_count": len(past_shows),
            "upcoming_shows_count": len(upcoming_shows),
        }

    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():

    form = VenueForm(request.form)

    if form.validate():
        try:
            new_venue = Venue(
                name=form.name.data,
                city=form.city.data,
                state=form.state.data,
                address=form.address.data,
                phone=form.phone.data,
                genres=",".join(form.genres.data),
                facebook_link=form.facebook_link.data,
                image_link=form.image_link.data,
                seeking_talent=form.seeking_talent.data,
                seeking_description=form.seeking_description.data,
                website_link=form.website_link.data,
            )
            db.session.add(new_venue)
            db.session.commit()
            flash('Venue ' + form.name.data + ' was successfully listed!')
        except:
            db.session.rollback()
            print("\n", sys.exc_info(), "\n")
            flash('An error occured. Venue ' +
                  form.name.data + ' Could not be listed!')
        finally:
            db.session.close()
    else:
        print("\n",form.errors, "\n")
        flash('An error occurred. Venue ' + form.name.data + ' could not be listed.')
    
    return render_template('pages/home.html')


@app.route('/venues/<venue_id>/delete', methods=['GET'])
def delete_venue(venue_id):

    try:
        venue = Venue.query.get(venue_id)
        db.session.delete(venue)
        db.session.commit()
        flash("Venue " + venue.name + " was deleted successfully!")
    except:
        db.session.rollback()
        print(sys.exc_info())
        flash("Venue was not deleted successfully.")
    finally:
        db.session.close()

    return redirect(url_for("index"))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    
    data = db.session.query(Artist.id, Artist.name).all()
    return render_template('pages/artists.html', artists=data)

# Search Artists

@app.route('/artists/search', methods=['POST'])
def search_artists():
    
    search_term = request.form.get('search_term')
    search_results = Artist.query.filter(
            Artist.name.ilike('%{}%'.format(search_term))).all()

    
    response = {}
    response['count'] = len(search_results)
    response['data'] = []

    for artist in search_results:
        temp = {}
        upcoming_shows = 0
        temp["name"] = artist.name
        temp["id"] = artist.id

        for show in artist.shows:
            if show.start_time > datetime.now():
                upcoming_shows = upcoming_shows + 1
        
        temp["upcoming_shows"] = upcoming_shows
        response["data"].append(temp)
    
    return render_template('pages/search_artists.html', results=response, search_term=search_term)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    
    clicked_artist = Artist.query.get(artist_id)
    setattr(clicked_artist, "genres", clicked_artist.genres.split(","))

    # past shows

    past_shows_data = list(filter(lambda x: x.start_time < datetime.now(), clicked_artist.shows))
    past_shows = []
    for show in past_shows_data:
        temp = {}
        temp["venue_name"] = show.venues.name
        temp["venue_id"] = show.venues.id
        temp["venue_image_link"] = show.venues.image_link
        temp["start_time"] = show.start_time.strftime("%m/%d/%Y, %H:%M:%S")

        past_shows.append(temp)

    past_shows_count = len(past_shows)

    # upcoming shows

    upcoming_shows_data = list(filter(lambda x: x.start_time > datetime.now(), clicked_artist.shows))
    upcoming_shows = []
    for show in upcoming_shows_data:
        temp = {}
        temp["venue_name"] = show.venues.name
        temp["venue_id"] = show.venues.id
        temp["venue_image_link"] = show.venues.image_link
        temp["start_time"] = show.start_time.strftime("%m/%d/%Y, %H:%M:%S")

        upcoming_shows.append(temp)

    upcoming_shows_count = len(upcoming_shows)

    # data to render

    data = {
            "id": clicked_artist.id,
            "name": clicked_artist.name,
            "genres": clicked_artist.genres,
            "city": clicked_artist.city,
            "state": clicked_artist.state,
            "phone": clicked_artist.phone,
            "seeking_venue": clicked_artist.seeking_venue,
            "facebook_link": clicked_artist.facebook_link,
            "image_link": clicked_artist.image_link,
            "past_shows": past_shows,
            "upcoming_shows": upcoming_shows,
            "past_shows_count": past_shows_count,
            "upcoming_shows_count": upcoming_shows_count,
        }
    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------

@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  form.genres.data = artist.genres.split(",")

  
  return render_template('forms/edit_artist.html', form=form, artist=artist)

# Edit artist

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    
    form = ArtistForm(request.form)
    artist = Artist.query.get(artist_id)

    if form.validate():
        try:
            
            artist.name = form.name.data
            artist.city=form.city.data
            artist.state=form.state.data
            artist.phone=form.phone.data
            artist.genres=",".join(form.genres.data) 
            artist.facebook_link=form.facebook_link.data
            artist.image_link=form.image_link.data
            artist.seeking_venue=form.seeking_venue.data
            artist.seeking_description=form.seeking_description.data
            artist.website_link=form.website_link.data

            db.session.add(artist)
            db.session.commit()
            flash("Artist " + artist.name + " was successfully edited!")
        except:
            db.session.rollback()
            print("\n", sys.exc_info() , "\n")
            flash("Artist: " + artist.name + " was not edited successfully.")
        finally:
            db.session.close()
    else:
        print("\n", form.errors , "\n")
        flash("Artist: " + artist.name + " was not edited successfully.")

    return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue = Venue.query.get(venue_id)
    form.genres.data = venue.genres.split(",")
 
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  
    form = VenueForm(request.form)
    venue = Venue.query.get(venue_id)
    if form.validate():
        try:
            venue.name = form.name.data
            venue.city=form.city.data
            venue.state=form.state.data
            venue.address=form.address.data
            venue.phone=form.phone.data
            venue.genres=",".join(form.genres.data) 
            venue.facebook_link=form.facebook_link.data
            venue.image_link=form.image_link.data
            venue.seeking_talent=form.seeking_talent.data
            venue.seeking_description=form.seeking_description.data
            venue.website_link=form.website_link.data

            db.session.add(venue)
            db.session.commit()
            flash("Venue " + venue.name  + " edited successfully")
        except:
            db.session.rollback()
            print("\n", sys.exc_info(), "\n")
            flash("Venue: " + venue.name + " was not edited successfully.")
        finally:
            db.session.close()
    else: 
        print("\n", form.errors , "\n")
        flash("Venue: " + venue.name + " was not edited successfully.")
                
    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    form = ArtistForm(request.form)
   
    if form.validate():
        try:
            new_artist = Artist(
                name=form.name.data,
                city=form.city.data,
                state=form.state.data,
                phone=form.phone.data,
                genres=",".join(form.genres.data), 
                image_link=form.image_link.data,
                facebook_link=form.facebook_link.data,
                website_link=form.website_link.data,
                seeking_venue=form.seeking_venue.data,
                seeking_description=form.seeking_description.data,
            )
            db.session.add(new_artist)
            db.session.commit()
            # on successful db insert, flash succes
            flash("Artist " + form.name.data + " was successfully listed!")
        except:
            db.session.rollback()
            # on failure db insert, flash error
            flash("Artist was not successfully listed.")
        finally:
            db.session.close()
    else:
        print("\n", form.errors, "\n")
        flash("Artist was not successfully listed.")
    
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
   
    data = []
    shows = Show.query.all()
    print(shows)
    for show in shows:
        temp_show = {}
        temp_show["venue_id"] = show.venues.id
        temp_show["venue_name"] = show.venues.name
        temp_show["artist_id"] = show.artists.id
        temp_show["artist_name"] = show.artists.name
        temp_show["artist_image_link"] = show.artists.image_link
        temp_show["start_time"] = show.start_time.strftime("%m/%d/%Y, %H:%M:%S")
        data.append(temp_show)
        print(data)
    
    return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    
    form = ShowForm(request.form)
    
    if form.validate():
        try:
            new_show = Show(
                artist_id=form.artist_id.data,
                venue_id=form.venue_id.data,
                start_time=form.start_time.data
            )
            db.session.add(new_show)
            db.session.commit()
            flash('Show was successfully listed!')
        except:
            db.session.rollback()
            print("\n",sys.exc_info(),"\n")
            flash('Show was not successfully listed.')
        finally:
            db.session.close()
    else:
        print("\n", form.errors,"\n")
        flash('Show was not successfully listed.')

    return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run(host="127.0.0.1",debug=True,port=5000)

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
