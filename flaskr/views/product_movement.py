
from flask import (
    Blueprint, Flask, flash, g, redirect, render_template, request, url_for, send_file
)
from werkzeug.exceptions import abort
from flaskr.db import get_db
from flaskr.helper.saveImages import *

# creating a new blueprint for the product-movement view
bp = Blueprint('product_movement', __name__, url_prefix='/product-movement')



    
"""
The home view of the product-movement 
All the previously created product-movements will be queried and then passed to the view html page to display them
"""    
@bp.route('/')
def index():
    db = get_db() #create a connection with the database
    
    #querying all the previously created product-movements
    movements = db.execute(
        'SELECT m.movement_id, m.from_location, m.to_location, date(m.timestamp) as date, m.qty,p.title'
        ' FROM productMovement m JOIN product p on m.product_id = p.product_id'
    ).fetchall()
    
    
    return render_template('product_movement/product_movement.html', movements=movements)# redirect to the product_movement.html page and passing the queried product-movements


"""
description: this method thakes two locations and check if they are the same or not
arguments: two different locations
returns : a message that conatins the comparison results
"""
def check_same_locations(fromlocation,toLocation):
    message = ""
    if fromlocation == toLocation:
        message="Error: From location and To location cant be the same "
    return message


"""
description: this method thakes a variable called field and check if it matches one of the specified default strings
arguments: a field variable
returns : a message that conatins the comparison results
"""
def check_empty_field(field):
    database_field = field
    if field == "Choose From Location" or field == "Choose To Location" or field == "Choose Product":
        database_field= "Not Specified"
    return database_field

"""
description: this method thakes a product title and checks the quantity availble of that product on the product-table
arguments: product title and a refrence to database connection to excuste the query
returns : a dicationary that conatins the query results
"""
def get_available_quantity(product,db):
    quantity = db.execute(
        'SELECT p.qty'
        ' FROM product p'
        ' WHERE p.title = ?',
        (product,)
        ).fetchone()
    return quantity

"""
description: this method thakes a product title and updates the product quantity by the amount specified in the quantity variable
arguments: product title, product quantity and a refrence to database connection to excuste the query
returns : none
"""
def update_product_quantity(quantity,product,db):
    db.execute(
        'UPDATE product SET qty = ?'
        ' WHERE title = ?',
        (quantity, product)
        )
    db.commit()

"""
description: this method thakes a product title and location name and quiries the quantity productLocation table
arguments: product title, location name and a refrence to database connection to excuste the query
returns : a dicationary that conatins the query results
"""
def check_exisits(product, location,db):
    exitis = db.execute(
        'SELECT pl.qty'
        ' FROM productLocation pl'
        ' WHERE pl.title = ? AND pl.name = ?',
        (product,location)
        ).fetchone()    
    return exitis

"""
description: this method thakes a product title and location name and updates the quantity by the quantity var passed in the productLocation table
arguments: product title, location name, quantity and a refrence to database connection to excuste the query
returns : none
"""
def update_productLocation_quantity(quantity,product,location,db):
    db.execute(
        'UPDATE productLocation SET qty = ?'
        ' WHERE title = ? AND name = ?',
        (quantity, product,location)
        )
    db.commit()

"""
description: this method thakes a product title and location name and quantity  and creates a new record in the productLocation table
arguments: product title, location name, quantity and a refrence to database connection to excuste the query
returns : none
"""
def add_to_productLocation(product,location,quantity,db):
    db.execute(
        'INSERT INTO productLocation (title, name, qty)'
        ' VALUES (?, ?, ?)',
        (product, location, quantity)
        )
    db.commit()

"""
This is the create view of the product-movement 
"""
@bp.route('/create', methods=('GET', 'POST'))
def create():
    #querying all the availble products on the product table 
    # and pass it as the products to be displayed on the add_movement.html page 
    products = get_db().execute(
                'SELECT p.title'
                ' FROM product p').fetchall()
    
    #querying all the availble locations on the productLocation table
    # and pass it as the from-locations to be displayed on the add_movement.html page 
    fromLocations = get_db().execute(
                'SELECT DISTINCT pl.name'
                ' FROM productLocation pl').fetchall()
    
    #querying all the availble locations on the location table
    # and pass it as the to-locations to be displayed on the add_movement.html page 
    toLocations = get_db().execute(
                'SELECT l.name'
                ' FROM location l').fetchall()
    
    #checks if we are creating a new product-movement or just viewing the add_movement.html page, if true then start creating a new product-movement
    if request.method == 'POST':
        # getting the user input from the add_movement.html page
        product = request.form['product']
        fromLocation = request.form['fromLocation']
        toLocation = request.form['toLocation']
        quantity = int(request.form['quantity'])
        error = None

        #checks if the user didnt enter a product title, if true flashes the error message and redirects to add_movement.html page
        product = check_empty_field(product)
        if product == "Not Specified" :
            error = 'You must choose a product.'
            flash(error)
       
        else:
            
            # checks if the from and to location are the same,if true flashes the error message and redirects to add_movement.html page
            error = check_same_locations(fromLocation,toLocation)
            if error != "":
                flash(error)
                
            else:
                fromLocation = check_empty_field(fromLocation)
                toLocation = check_empty_field(toLocation)
                
                # checks if the user didnt specify both from and to location ,if true flashes the error message and redirects to add_movement.html page
                if fromLocation == toLocation:
                    flash("You must at least fill From location or to location ")
                    
                else:
                    db = get_db() #create a connection with the database
                    
                    available_qty =  get_available_quantity(product,db) # gets the availble quantity of the current product
                    
                    # if the user didnt choose a from location:
                    if fromLocation == "Not Specified" :
                        
                        #checks if the quntity given by the user is larger than the available_qty, if true flashes the error message and redirects to add_movement.html page
                        if quantity > available_qty['qty'] :
                            flash(f"Error: The quantity you tried to move of {product} is more than the availble quantity which is {available_qty['qty']}")
                            return render_template('product_movement/add_movement.html', products=products, from_locations =fromLocations, to_locations=toLocations)
                       
                        # if the quantity given by the user is smaller than or equal to available_qty, then it deducts this quantity from
                        # the available_qty and updates the product quantity in the product-table
                        else:
                            update_product_quantity(available_qty['qty'] - quantity,product,db)
                            
                        exitis = check_exisits(product,toLocation,db)  
                        
                        #checks if the product exitis in the productLocation-table, if true it updates the quantity 
                        if exitis is not None:
                             update_productLocation_quantity(exitis['qty'] + quantity,product,toLocation,db)
                             
                        #if the product doesnt exitis in the productLocation-table, it creates a new record in the table and add the quantity and location
                        else:
                            add_to_productLocation(product,toLocation,quantity,db)
                            
                            
                    # if the user didnt choose a from location:        
                    elif toLocation == "Not Specified" :
                        exitis = check_exisits(product,fromLocation,db)
                        #checks if the product doesnt exitis in the productLocation-table, 
                        # if true flashes the error message and redirects to add_movement.html page
                        if exitis is None:
                            flash(f"Error: {fromLocation} doesnt have any available quantity of {product}")
                            return render_template('product_movement/add_movement.html', products=products, from_locations =fromLocations, to_locations=toLocations)
                       
                        #checks if the user given quantity is larger than the quantity available of the product in that location, 
                        # if if true flashes the error message and redirects to add_movement.html page
                        if quantity > exitis['qty']:
                            flash(f"Error: The quantity you tried to move of {product} form {fromLocation} is more than the availble quantity which is {exitis['qty']}")
                            return render_template('product_movement/add_movement.html', products=products, from_locations =fromLocations, to_locations=toLocations)
                        
                        # if the quantity given by the user is smaller than or equal to available_qty(exitis['qty']), then it deducts this quantity from
                        # the available_qty and updates the product quantity in the productLocation-table 
                        # and updates the product quantity in the product-table with the addition of the user given quantity and the older quantity
                        else:
                            update_productLocation_quantity(exitis['qty'] - quantity,product,fromLocation,db)
                            update_product_quantity(available_qty['qty'] + quantity,product,db)
                            
                        #checks if the product exitis in the productLocation-table, if true it updates the quantity     
                        if exitis is not None:
                            update_productLocation_quantity(exitis['qty'] - quantity,product,fromLocation,db)
                            
                        #if the product doesnt exitis in the productLocation-table, it creates a new record in the table and add the quantity and location
                        else:
                            add_to_productLocation(product,fromLocation,quantity,db)
                            
                    # if the user specified both from and to locations:        
                    else :
                        fromLocationExisists = check_exisits(product, fromLocation,db)
                        
                        #checks if the product doesnt exitis in the productLocation-table, 
                        # if true flashes the error message and redirects to add_movement.html page
                        if fromLocationExisists is None:
                            flash(f"{fromLocation} doesnt have any availble quantity of {product}")
                            return render_template('product_movement/add_movement.html', products=products, from_locations =fromLocations, to_locations=toLocations)

                        #checks if the user given quantity is larger than the quantity available of the product in that location, 
                        # if if true flashes the error message and redirects to add_movement.html page
                        if quantity > fromLocationExisists['qty']:
                            flash(f"Error: The quantity you tried to move of {product} form {fromLocation} is more than the availble quantity which is {fromLocationExisists['qty']}")
                            return render_template('product_movement/add_movement.html', products=products, from_locations =fromLocations, to_locations=toLocations)
                        
                        
                        update_productLocation_quantity(fromLocationExisists['qty'] - quantity,product,fromLocation,db)
                        
                        
                        exitis = check_exisits(product,toLocation,db)
                        
                        #checks if the product exitis in the productLocation-table, if true it updates the quantity 
                        if exitis is not None:
                             update_productLocation_quantity(exitis['qty'] + quantity,product,toLocation,db)
                             
                        #if the product doesnt exitis in the productLocation-table, it creates a new record in the table and add the quantity and location     
                        else:
                            add_to_productLocation(product,toLocation,quantity,db)
                            
                    #querying the id of the user selected product      
                    product_id = db.execute(
                    'SELECT p.product_id'
                    ' FROM product p'
                    ' WHERE p.title = ?',
                    (product,)
                    ).fetchone()
                    
                    #insterts the new product-movement into the productMovement-table
                    db.execute(
                        'INSERT INTO productMovement (from_location, to_location, product_id, qty)'
                        ' VALUES (?, ?, ?, ?)',
                        (fromLocation, toLocation, product_id['product_id'] , quantity)
                    )
                    db.commit()
                    return redirect(url_for('product_movement.index'))
        
    #redirects the user to the add_movement.html page
    return render_template('product_movement/add_movement.html', products=products, from_locations =fromLocations, to_locations=toLocations)

"""
description: this method thakes a movement id and returns all that movement data from the database 
arguments: movement id
returns : a dicationary that conatins the query results
"""
def get_movement(id):
    movement = get_db().execute(
        'SELECT m.movement_id, from_location, to_location, product_id, qty'
        ' FROM productMovement m'
        ' WHERE m.movement_id = ?',
        (id,)
    ).fetchone()

    #checks if there are no movements with the passed id
    if movement is None:
        abort(404, "Product id {0} doesn't exist.".format(id))
        
    return movement

"""
description: this method thakes an id of a product and search the database for it
arguments: product id and a refrence to database connection to excuste the query
returns : a dicationary that conatins the query results
"""
def get_product(id,db):
    product = db.execute(
        'SELECT p.title'
        ' FROM product p'
        ' WHERE p.product_id = ?',
        ( id,)
        ).fetchone()
    
    return product

"""
description: this method thakes a movement id  and updates the movement quantity by the amount specified in the quantity variable
arguments: movement id, product quantity and a refrence to database connection to excuste the query
returns : none
"""
def update_productMovement_quantity(quantity,id,db):
    db.execute(
        'UPDATE productMovement SET qty = ?'
        ' WHERE movement_id = ?',
        (quantity, id)
        )
    db.commit()


"""
description: this method thakes a product id  and updates the product quantity by the amount specified in the quantity variable
arguments: product id, product quantity and a refrence to database connection to excuste the query
returns : none
"""
def update_productID_quantity(quantity,id,db):
    db.execute(
        'UPDATE product SET qty = ?'
        ' WHERE product_id = ?',
        (quantity, id)
        )
    db.commit()
    
"""
This is the update view of the product-movement 
"""               
@bp.route('/<int:id>/update', methods=('GET', 'POST'))
def update(id):
    movement = get_movement(id) #gets the movement information
    
    db = get_db() #create a connection with the database
    
    product = get_product(movement['product_id'],db) #gets the user specified product information
    
    #checks if we are updating a product-movement or just viewing the update_movement.html page, if true then start updating the product-movement
    if request.method == 'POST':
        # getting the user input quantity from the update_movement.html page
        quantity = int(request.form['quantity'])
        
        # if the movement from_location queried from database equals to "not specified":
        if movement['from_location'] == "Not Specified" :
            
            #querying the availble quantity of the product from the product-table
            available_qty =  db.execute(
                        'SELECT p.qty'
                        ' FROM product p'
                        ' WHERE p.product_id = ?',
                        ( movement['product_id'],)
                        ).fetchone()
            
            #checks if the quantity given by the user is smaller than the the older quantity:
            if movement['qty'] > quantity:
                new_qty = movement['qty'] - quantity #calculates the diffrence between the older quantity and the quantity given by the user
                
                update_productID_quantity(available_qty['qty'] + new_qty,movement['product_id'],db)
                
                update_productMovement_quantity(quantity,movement['movement_id'],db)
                

                current_qty = check_exisits(product['title'], movement['to_location'],db) #gets the current quantity from the productLocation-table
                
                #updates the current quantity of the product in the productLocation-table
                update_productLocation_quantity(current_qty['qty'] - new_qty, product['title'],movement['to_location'],db) #updates the current quantity from the productLocation-table
                return redirect(url_for('product_movement.index'))
            
            #checks if the quantity given by the user is larger than the the older quantity:
            elif  movement['qty'] < quantity:    
                new_qty = quantity - movement['qty'] #calculates the diffrence between the older quantity and the quantity given by the user
                
                #checks if there are enoough quantity of the product to move it to the new location
                if new_qty > available_qty['qty']:
                    flash(f"Error: The quantity you tried to move is more than the availble quantity in {movement['to_location']} which is {available_qty['qty']}")
                    return render_template('product_movement/update_movement.html', movement=movement, product=product)
                
                else: 
                    update_productID_quantity(available_qty['qty'] - new_qty,movement['product_id'],db) #updates the product quantity in the product-table

                    update_productMovement_quantity(quantity,movement['movement_id'],db) #updates the product quantity in the productMovement-table
                    
                    current_qty = check_exisits(product['title'], movement['to_location'],db) #gets the current quantity from the productLocation-table
                    
                    update_productLocation_quantity(current_qty['qty'] + new_qty, product['title'], movement['to_location'],db) #updates the product quantity in the productLocation-table
                    return redirect(url_for('product_movement.index'))
                
            # if the user didnt change the quantity and just clicked the submit button
            else:
                return redirect(url_for('product_movement.index'))
            
        # if the movement to_location queried from database equals to "not specified":        
        elif movement['to_location'] == "Not Specified" :
            
            #gets the current quantity from the productLocation-table
            exitis = check_exisits(product['title'],movement['from_Location'],db)
            
            #checks if the quantity given by the user is smaller than the the older quantity: 
            if movement['qty'] > quantity:
                new_qty = movement['qty'] - quantity #calculates the diffrence between the older quantity and the quantity given by the user
                
                #updates the current quantity from the productLocation-table
                update_productLocation_quantity(exitis['qty'] + new_qty, product['title'], movement['from_Location'],db)     
                
                available_qty = get_available_quantity(product['title'],db) #gets the avaialbe quantity of the product from the product-table

                update_product_quantity(available_qty['qty'] - new_qty,product['title'],db) #updates the product quantity in the product-table
                
                update_productMovement_quantity(quantity,movement['movement_id'],db) #updates the product quantity in the productMovement-table
        
                return redirect(url_for('product_movement.index'))
            
            #checks if the quantity given by the user is larger than the the older quantity:
            elif quantity > movement['qty']:
                new_qty = quantity - movement['qty'] #calculates the diffrence between the older quantity and the quantity given by the user
                
                #gets the current quantity from the productLocation-table
                current_qty = check_exisits(product['title'], movement['from_location'],db) 
                   
                #checks if we have enough quantity to move it out 
                if current_qty['qty'] >= new_qty:
                    
                     #updates the current quantity from the productLocation-table
                    update_productLocation_quantity(current_qty['qty'] - new_qty, product['title'], movement['from_Location'],db) 
                    
                    available_qty = get_available_quantity(product['title'],db) #gets the avaialbe quantity of the product from the product-table
                    
                    update_product_quantity(available_qty['qty'] + new_qty,product['title'],db) #updates the product quantity in the product-table
                    
                    update_productMovement_quantity(quantity,movement['movement_id'],db) #updates the product quantity in the productMovement-table
                       
                    return redirect(url_for('product_movement.index'))  
                
                #if we dont have enough quantity in the specified location to move it out              
                else:
                    flash(f"Error: The quantity you tried to move is more than the availble quantity in {movement['from_location']} which is {current_qty['qty']}")
                    return render_template('product_movement/update_movement.html', movement=movement, product=product)
            
            else:    
                return redirect(url_for('product_movement.index'))
        
        # if the user specified both from and to locations:
        else:
            
            #checks if the quantity given by the user is smaller than the the older quantity: 
            if movement['qty'] > quantity:
                new_qty = movement['qty'] - quantity #calculates the diffrence between the older quantity and the quantity given by the user
                
                #gets the current quantity available on the from_location from the productLocation-table
                fromLocationQty = check_exisits(product['title'], movement['from_location'],db) 

                #updates the current quantity from the productLocation-table
                update_productLocation_quantity(fromLocationQty['qty'] + new_qty, product['title'], movement['from_Location'],db) 
                
                #gets the current quantity available on the from_location from the productLocation-table
                toLocationQty = check_exisits(product['title'], movement['to_Location'],db)
               
                #updates the current quantity from the productLocation-table
                update_productLocation_quantity(toLocationQty['qty'] - new_qty, product['title'], movement['to_Location'],db)
                
                #updates the product quantity in the productMovement-table
                update_productMovement_quantity(quantity,movement['movement_id'],db)
               
                return redirect(url_for('product_movement.index'))
            
            #checks if the quantity given by the user is larger than the the older quantity:
            elif movement['qty'] < quantity:
                new_qty = quantity - movement['qty'] #calculates the diffrence between the older quantity and the quantity given by the user
                
                #gets the current quantity available on the from_location from the productLocation-table
                fromLocationQty = check_exisits(product['title'], movement['from_Location'],db)
                
                #checks if we have enough quantity in the from_location to move it out
                if fromLocationQty['qty'] >= new_qty:
                    
                    #updates the current quantity from the productLocation-table
                    update_productLocation_quantity(fromLocationQty['qty'] - new_qty, product['title'], movement['from_Location'],db)
                    #gets the current quantity available on the from_location from the productLocation-table
                    toLocationQty = check_exisits(product['title'], movement['to_Location'],db)
                    
                    #updates the current quantity from the productLocation-table
                    update_productLocation_quantity(toLocationQty['qty'] + new_qty, product['title'], movement['to_Location'],db)
                    
                    #updates the product quantity in the productMovement-table
                    update_productMovement_quantity(quantity,movement['movement_id'],db)
                    
                    return redirect(url_for('product_movement.index'))
                #
                else: 
                    flash(f"Error: The quantity you tried to move is more than the availble quantity in {movement['from_location']} which is {fromLocationQty['qty']}")
                    return render_template('product_movement/update_movement.html', movement=movement, product=product)
            
            # if the user didnt change the quantity and just clicked the submit button
            else:     
                 return redirect(url_for('product_movement.index'))
            
            
                

    return render_template('product_movement/update_movement.html', movement=movement, product=product)


