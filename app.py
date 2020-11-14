#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json

import babel
from flask import (
  Flask, 
  render_template, 
  request, 
  Response, 
  flash, 
  redirect, 
  url_for, 
  jsonify
  )
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from sqlalchemy import func
from datetime import datetime
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app,db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    genres = db.Column(db.String(120))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(500), nullable=True)
    seeking_talent = db.Column(db.Boolean, default=True)
    seeking_description= db.Column(db.String(200), nullable=True)
    shows = db.relationship('Shows', backref="Venue",lazy=True)


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    shows = db.relationship('Shows', backref="Artist",lazy=True)


class Shows(db.Model):
    __tablename__ = 'Shows'

    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.Date, nullable=True)
    venue_id = db.Column(db.Integer, db.ForeignKey(Venue.id), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey(Artist.id), nullable=False)

#trying to figure out best way to serialize this since it seems like a redundnacy in
#database to add artise and venue name to show table.  So do I query in the serialize function???
#what's the best practice here???????????????????????????
    def serialize(self):
        artist_name = Artist.query.filter(Artist.id==self.artist_id).first().name
        venue_name = Venue.query.filter(Venue.id==self.venue_id).first().name
        artist_image_link = Artist.query.filter(Artist.id==self.artist_id).first().image_link
        
        return {
            'id':self.id,
            'start_time': self.start_time,
            'venue_id': self.venue_id,
            'artist_id': self.artist_id,
            'artist_name': artist_name,
            'venue_name': venue_name,
            "artist_image_link":artist_image_link
        }

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


#return babel.dates.format_datetime(date, format, locale='en')

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

#db.create_all()

@app.route('/')
def index():
  return render_template('pages/home.html')

#have a theory about it going trhough flask and not being able to directly fetch an image from 
# a file even if a legit route in the folder structure
@app.route('/images/<image_file>')
def image(image_file):
    image_link = '/images/' + str(image_file)
    return render_template(image_link)

@app.route('/venues')
def venues():
  areas = []
  distinct_city_state = Venue.query.distinct(Venue.city, Venue.state).all()
  for dcs in distinct_city_state:
    dcs.venues = Venue.query.filter(Venue.city==dcs.city,Venue.state==dcs.state)
    areas.append(dcs)
  return render_template('pages/venues.html', areas = areas)
 

@app.route('/venues/search', methods=['POST'])
def search_venues():
    search_term = request.form.get('search_term')
    likeSearch = '%' + search_term + '%'
    response_results = Venue.query.filter(Venue.name.like(likeSearch))
    response={
    "results": response_results
    }
    #jsoned_response= jsonify(response)
    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    venue = Venue.query.get(venue_id)
    showData = []    
    for show in venue.shows:
        showData.append(show.serialize())

    today = datetime.today().date()
    futureShows = []
    pastShows = []
    #find the shows that were past vs upcoming
    #datetime.datetime to datetime.date
    
    for show in showData:
        if show['start_time'] > today:
            futureShows.append(show)
        else:
            pastShows.append(show)

    data = {
    "id": venue_id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    #"website": venue.website,
    "facebook_link": venue.facebook_link,
    #"seeking_talent": venue.seeking_talent,
    #"seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": pastShows,
    "upcoming_shows": futureShows,
    "past_shows_count": len(pastShows),
    "upcoming_shows_count": len(futureShows)
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
  name = request.form['name']
  address = request.form['address']
  phone = request.form['phone']
  genres = request.form['genres']
  city = request.form['city']
  state = request.form['state']
  image_link=request.form['image_link']

  try:
      newVenue = Venue()
      newVenue.name = name
      newVenue.address = address
      newVenue.phone = phone
      newVenue.genres = genres
      newVenue.city = city
      newVenue.state = state
      newVenue.image_link = image_link
      db.session.add(newVenue)
      db.session.commit()
      flash('Venue ' + request.form['name'] + ' was successfully listed!')

  except:
      print("something went wrong")
      db.session.rollback()
      flash('An error occured! Venue ' + request.form['name'] + ' could not be listed')
  finally:
      db.session.close()

  return render_template('pages/home.html')



@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  try:
      venueToDelete = Venue.query.filter(Venue.id == venue_id)
      venueToDelete.delete()
      db.session.commit()
      flash("deleted Venue!")    
  except:
      flash("Something went wrong!  Couldn't delete Venue {}".format(venue_id))
      db.session.rollback()
  finally:
      db.session.close()
 
  return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  return render_template('pages/artists.html', artists = Artist.query.all())
  #       num_show


@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_term = request.form.get('search_term')
  likeSearch = '%' + search_term + '%'
  artist_results = Artist.query.filter(Artist.name.like(likeSearch))

  count = 0
  for item in artist_results:
      count+=1

  data = []
  for item in artist_results:
      data.append(item)

  response= {
  "count":count,
  "data": data
  }

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>', methods=['GET'])
def show_artist(artist_id):
    artist_data = Artist.query.get(artist_id)

    showData = []    
    for show in artist_data.shows:
        showData.append(show.serialize())

    today = datetime.today().date()
    futureShows = []
    pastShows = []
    
    for show in showData:
        if show['start_time'] > today:
            futureShows.append(show)
        else:
            pastShows.append(show)

    
    data={
    "id": artist_data.id,
    "name": artist_data.name,
    "genres": artist_data.genres,
    "city": artist_data.city,
    "state": artist_data.state,
    "phone": artist_data.phone,
    #website": artist_data.website,
    "facebook_link": artist_data.facebook_link,
    #"seeking_venue": artist_data.seeking_venue,
    #"seeking_description": artist_data.seeking_description,
    "image_link": artist_data.image_link,
    "past_shows": pastShows,
    "upcoming_shows": futureShows,
    "past_shows_count": len(pastShows),
    "upcoming_shows_count": len(futureShows)
    }

    return render_template('pages/show_artist.html', artist=data)



#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artistToEdit = Artist.query.get(artist_id)

  artist={
    "id": artistToEdit.id,
    "name": artistToEdit.name,
    "genres": artistToEdit.genres,
    "city": artistToEdit.city,
    "state": artistToEdit.state,
    "phone": artistToEdit.phone,
    #"website": artistToEdit.website,
    "facebook_link": artistToEdit.facebook_link,
    #"seeking_venue": True,
    #"seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": artistToEdit.image_link
  }
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    name = request.form['name']
    genres = request.form['genres']
    city = request.form['city']
    state = request.form['state']
    image_link = request.form['image_link']  

    try:
        artistToEdit = Artist.query.get(artist_id)
        artistToEdit.name = name
        artistToEdit.genres = genres
        artistToEdit.city = city
        artistToEdit.state = state
        artistToEdit.image_link = image_link
        db.session.add(artistToEdit)
        db.session.commit()
        flash('Artist ' + request.form['name'] + ' was successfully edited!')
    except:
        print("something went wrong")
        db.session.rollback()
        flash('An error occured! Artist ' + request.form['name'] + ' could not be edited')
    finally:
        db.session.close()

    return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):

  name = request.form['name']
  address = request.form['address']
  phone = request.form['phone']
  genres = request.form['genres']
  city = request.form['city']
  state = request.form['state']
  image_link = request.form['image_link']

  try:
      venueToEdit = Venue.query.get(venue_id)
      venueToEdit.name = name
      venueToEdit.address = address
      venueToEdit.phone = phone
      venueToEdit.genres = genres
      venueToEdit.city = city
      venueToEdit.state = state
      venueToEdit.image_link = image_link
      db.session.add(venueToEdit)
      db.session.commit()
      flash('Venue ' + request.form['name'] + ' was successfully listed!')

  except:
      print("something went wrong")
      db.session.rollback()
      flash('An error occured! Venue ' + request.form['name'] + ' could not be listed')
  finally:
      db.session.close()

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    name = request.form['name']
    genres = request.form['genres']
    city = request.form['city']
    state = request.form['state']
    image_link = request.form['image_link']

    try:
        newArtist = Artist()
        newArtist.name = name
        newArtist.genres = genres
        newArtist.city = city
        newArtist.state = state
        newArtist.image_link = image_link
        db.session.add(newArtist)
        db.session.commit()
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
    except:
        print("something went wrong")
        db.session.rollback()
        flash('An error occured! Artist ' + request.form['name'] + ' could not be listed')
    finally:
        db.session.close()

    return render_template('pages/home.html')



#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    showData = Shows.query.all()
    data = []
    for show in showData:
        data.append(show.serialize())
    return render_template('pages/shows.html', shows=data)



@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()

  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    artist_id = request.form['artist_id']
    venue_id = request.form['venue_id']
    start_time = request.form['start_time']

    try:
        newShow = Shows()
        newShow.artist_id = artist_id
        newShow.venue_id = venue_id
        newShow.start_time = start_time
        db.session.add(newShow)
        db.session.commit()
        print("Successfully added!")
    except:
        print("an error occured!")
        db.session.rollback()
    finally:
        db.session.close()

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
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
