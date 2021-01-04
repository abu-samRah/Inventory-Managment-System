from flask import (
    Blueprint, Flask, flash, g, redirect, render_template, request, url_for, send_file
)
from werkzeug.exceptions import abort
from flaskr.db import get_db
from flaskr.helper.saveImages import *

# creating a new blueprint for the location view
bp = Blueprint('location', __name__, url_prefix='/location')

 
"""
The home view of the location 
All the previously created locations will be queried and then passed to the view html page to display them
"""    
@bp.route('/')
def index():
    db = get_db() #create a connection with the database
    #querying all the previously created locations
    locations = db.execute(
        'SELECT l.location_id, name, date(timestamp) as date, image'
        ' FROM location l'
    ).fetchall()
    
    return render_template('location/view_location.html', locations=locations)


"""
description: this method thakes a location name and search the database for it
arguments: location name
returns : a dicationary that conatins the query results
"""
def check_location_exists(name):
     
        macth = get_db().execute(
                'SELECT l.name'
                ' FROM location l'
                ' WHERE l.name = ?',
                (name,)
                ).fetchone()

        return macth

"""
This is the create view of the location  
"""
@bp.route('/create', methods=('GET', 'POST'))
def create():
    #checks if we are creating a new location or just viewing the create html page, if true then start creating a new location
    if request.method == 'POST':
        # getting the user input from the create.html page
        name = request.form['name']
        error = None
        
        #Checks if the name is empty and if true, flashes the error message and redirects to creat.html page
        if not name:
            error = 'Name is required.'
            flash(error)
  
       
        else:
            #checks if the user attached a picture for the created location, if true it calls the save_image method to save the image   
            if  request.files['file'].filename != '':
                file = request.files['file']
                filename = save_image(file)
                    
            #if the user didnt attach a picture the location will have the default image    
            else:
                filename = "location_default.jpg"
                
            exists = check_location_exists(name)
            #check if another location with the same name is already exists in the database, and if true, it flashes an error message
            if exists is not None:
                flash("*Error: Similar location with the same name Has been already added ")
            
            else:
                db = get_db() #create a connection with the database
                 #inserting the new location to the database
                db.execute(
                    'INSERT INTO location (name, image)'
                    ' VALUES (?, ?)',
                    (name, filename)
                )
                db.commit()
                
                #redirects the user to the home page of the location view
                return redirect(url_for('location.index'))
            
    #redirects the user to the location create.html page
    return render_template('location/create_location.html')


"""
description: this method thakes an id of a location and search the database for it
arguments: location id
returns : a dicationary that conatins the query results
"""
def get_location(id):
    location = get_db().execute(
        'SELECT l.location_id, name, image'
        ' FROM location l'
        ' WHERE l.location_id = ?',
        (id,)
    ).fetchone()
    
    #checks if there are no location with the passed id
    if location is None:
        abort(404, "Location id {0} doesn't exist.".format(id))


    return location

"""
This is the update view of the location 
"""
@bp.route('/<int:id>/update', methods=('GET', 'POST'))
def update(id):
    location = get_location(id) #gets the location information
    #checks if we are updating a location or just viewing the update html page, if true then start updating the location
    if request.method == 'POST':
        # getting the user input from the update.html page
        name = request.form['name']
        error = None

        #Checks if the name is empty and if true, flashes the error message and redirects to update.html page
        if not name:
            error = 'name is required.'
            flash(error)
            
        else:
            #checks if the user attached a picture for the updated location, if true it calls the save_image method to save the image 
            if  request.files['file'].filename != '':
               file = request.files['file']
               filename = save_image(file)
                    
               if filename == "": 
                    filename = "location_default.jpg"
                    
            #if the user didnt attach a new picture the location will have the old image
            else:
                filename = location['image']
                
            exists = check_location_exists(name)
            #check if another location with the same name is already exists in the database, and if true, it flashes an error message
            if exists is not None and exists[0] != location['name']:
                flash("*Error: Similar location with the same name Has been already added")
            else:
                db = get_db()#create a connection with the database
                #updating the location in the productMovement table in database
                db.execute(
                    'UPDATE productMovement SET from_location = ?'
                    ' WHERE from_location = ?',
                    (name,location['name'])
                )
                db.commit()
                
                #updating the location in the productMovement table in database
                db.execute(
                    'UPDATE productMovement SET to_location = ?'
                    ' WHERE to_location = ?',
                    (name, location['name'])
                )
                db.commit()
                #updating the location in the productLocation table in database
                db.execute(
                    'UPDATE productLocation SET name = ?'
                    ' WHERE name = ?',
                    (name, location['name'])
                )
                db.commit()
                
                #updating the location in the location table in database
                db.execute(
                    'UPDATE location SET name = ?, image = ?'
                    ' WHERE location_id = ?',
                    (name, filename,id)
                )
                db.commit()
                
                #redirects the user to the home page of the product view
                return redirect(url_for('location.index'))
    #redirects the user to the product update.html page
    return render_template('location/update_location.html', location=location)


"""
This is the delete view of the product 
"""
@bp.route('/<int:id>/delete', methods=['GET', 'POST'])
def delete(id):
    db = get_db() #create a connection with the database
    
    location = get_location(id) #gets the location information
    #query the location from productMovement table
    location_match = get_db().execute(
        'SELECT m.from_location, to_location'
        ' FROM productMovement m'
        ' WHERE m.from_location = ? OR  m.to_location = ?',
        (location['name'],location['name'])
    ).fetchone()
    
    #checks if location the has been used in the product movement, 
    # if true it flashes an error message and redirects the user to the home view of the location
    if location_match is not None:
        flash("Error: Cant delete this location because its used in the product movement")
        return redirect(url_for('location.index'))
    else:
        db.execute('DELETE FROM location WHERE location_id = ?', (id,)) #delete the location from the database
        db.commit()
        
        #redirects the user to the home page of the location view
        return redirect(url_for('location.index'))