
# Imports

import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


# Venue Model

class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(120))
    shows = db.relationship("Show", backref="venues", lazy=True, cascade="all, delete-orphan")


# Artist Model

class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    website = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    seeking_description = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, nullable=False, default=False)
    shows = db.relationship("Show", backref="artists", lazy=True, cascade="all, delete-orphan")
    

    def __repr__(self):
        return f"<Venue id={self.id} name={self.name} city={self.city} state={self.city}> \n"


# Show Model and Relationship

class Show(db.Model):
    __tablename__ = "shows"

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey("artists.id"), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey("venues.id"), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    # venue = db.relationship('Venue')
    # artist = db.relationship('Artist')

    def __repr__(self):
        return f"<Show id={self.id} artist_id={self.artist_id} venue_id={self.venue_id} start_time={self.start_time} \n"
