from datetime import datetime
from random import choices
from flask_wtf import FlaskForm
from flask import flash
import phonenumbers
from wtforms import StringField, SelectField, SelectMultipleField, DateTimeField, BooleanField,ValidationError
from wtforms.validators import DataRequired, AnyOf, URL

genre_choices=[
            ('Alternative', 'Alternative'),
            ('Blues', 'Blues'),
            ('Classical', 'Classical'),
            ('Country', 'Country'),
            ('Electronic', 'Electronic'),
            ('Folk', 'Folk'),
            ('Funk', 'Funk'),
            ('Hip-Hop', 'Hip-Hop'),
            ('Heavy Metal', 'Heavy Metal'),
            ('Instrumental', 'Instrumental'),
            ('Jazz', 'Jazz'),
            ('Musical Theatre', 'Musical Theatre'),
            ('Pop', 'Pop'),
            ('Punk', 'Punk'),
            ('R&B', 'R&B'),
            ('Reggae', 'Reggae'),
            ('Rock n Roll', 'Rock n Roll'),
            ('Soul', 'Soul'),
            ('Other', 'Other'),
        ]

state_choices=[
            ('AL', 'AL'),
            ('AK', 'AK'),
            ('AZ', 'AZ'),
            ('AR', 'AR'),
            ('CA', 'CA'),
            ('CO', 'CO'),
            ('CT', 'CT'),
            ('DE', 'DE'),
            ('DC', 'DC'),
            ('FL', 'FL'),
            ('GA', 'GA'),
            ('HI', 'HI'),
            ('ID', 'ID'),
            ('IL', 'IL'),
            ('IN', 'IN'),
            ('IA', 'IA'),
            ('KS', 'KS'),
            ('KY', 'KY'),
            ('LA', 'LA'),
            ('ME', 'ME'),
            ('MT', 'MT'),
            ('NE', 'NE'),
            ('NV', 'NV'),
            ('NH', 'NH'),
            ('NJ', 'NJ'),
            ('NM', 'NM'),
            ('NY', 'NY'),
            ('NC', 'NC'),
            ('ND', 'ND'),
            ('OH', 'OH'),
            ('OK', 'OK'),
            ('OR', 'OR'),
            ('MD', 'MD'),
            ('MA', 'MA'),
            ('MI', 'MI'),
            ('MN', 'MN'),
            ('MS', 'MS'),
            ('MO', 'MO'),
            ('PA', 'PA'),
            ('RI', 'RI'),
            ('SC', 'SC'),
            ('SD', 'SD'),
            ('TN', 'TN'),
            ('TX', 'TX'),
            ('UT', 'UT'),
            ('VT', 'VT'),
            ('VA', 'VA'),
            ('WA', 'WA'),
            ('WV', 'WV'),
            ('WI', 'WI'),
            ('WY', 'WY'),
        ]



class ShowForm(FlaskForm):
    artist_id = StringField(
        'artist_id'
    )
    venue_id = StringField(
        'venue_id'
    )
    start_time = DateTimeField(
        'start_time',
        validators=[DataRequired()],
        default= datetime.today()
    )

class VenueForm(FlaskForm):
    # Genre validation
    def validate_genres(form, field):
        genres_values = [choice[1] for choice in genre_choices]
        for value in form.genres.data:
            if value not in genres_values:
                raise ValidationError('Invalid genres value.')
    
    def validate_phone(form, field):
        try:
            if len(field.data) < 10:
                print("printed")
                raise ValidationError('Invalid phone number.') 
            else:
                phone_match = phonenumbers.parse("+1"+field.data,form.state.data)
                if not (phonenumbers.is_valid_number(phone_match)):
                    raise ValidationError('Invalid phone number.')
        except:
            raise ValidationError('Invalid phone number.')     
       
    name = StringField(
        'name', validators=[DataRequired()]
    )
    city = StringField(
        'city', validators=[DataRequired()]
    )
    state = SelectField(
        'state', validators=[DataRequired()],
        choices=state_choices
    )
    address = StringField(
        'address', validators=[DataRequired()]
    )
    phone = StringField(
        'phone',validators=[validate_phone]
    )
    image_link = StringField(
        'image_link'
    )
    genres = SelectMultipleField(
        # enum validation
        'genres', validators=[DataRequired(),validate_genres], 
        choices=genre_choices
    )
       
    facebook_link = StringField(
        'facebook_link', validators=[URL()]
    )
    website_link = StringField(
        'website_link'
    )

    seeking_talent = BooleanField( 'seeking_talent' )

    seeking_description = StringField(
        'seeking_description'
    )



class ArtistForm(FlaskForm):
    # facebook link validatation
    def facebook_validation(form,field):
        fb_link = "www.facebook.com"
        if fb_link not in str(form.facebook_link.data):
            flash('Invalid facebook link')
            raise ValidationError('Invalid facebook link')

    # phone validation
    def validate_phone(form, field):
        try:
            if len(field.data) < 10:
                print("printed")
                raise ValidationError('Invalid phone number.') 
            else:
                phone_match = phonenumbers.parse("+1"+field.data,form.state.data)
                if not (phonenumbers.is_valid_number(phone_match)):
                    raise ValidationError('Invalid phone number.')
        except:
            raise ValidationError('Invalid phone number.')     
    
    
    name = StringField(
        'name', validators=[DataRequired()]
    )
    city = StringField(
        'city', validators=[DataRequired()]
    )
    state = SelectField(
        'state', validators=[DataRequired()],
        choices=state_choices
    )
    phone = StringField(
       
        'phone',validators=[validate_phone]
    )
    image_link = StringField(
        'image_link'
    )
    genres = SelectMultipleField(
        'genres', validators=[DataRequired()],
        choices=genre_choices
     )
    facebook_link = StringField(
        # Link validation - facebook_validate
        'facebook_link', validators=[URL(),facebook_validation]
     )

    website_link = StringField(
        'website_link'
     )

    seeking_venue = BooleanField( 'seeking_venue' )

    seeking_description = StringField(
            'seeking_description'
     )

