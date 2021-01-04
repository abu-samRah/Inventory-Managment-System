
from flask import (
    Blueprint, Flask, flash, g, redirect, render_template, request, url_for, send_file
)
from werkzeug.exceptions import abort
from flaskr.db import get_db
from flaskr.helper.saveImages import *


# creating a new blueprint for the product view
bp = Blueprint('product', __name__, url_prefix='/product')


"""
The home view of the product 
All the previously created products will be queried and then passed to the view html page to display them
"""  
@bp.route('/')
def index():
    db = get_db() #create a connection with the database
    
    #querying all the previously created products  
    products = db.execute(
        'SELECT p.product_id, date(timestamp) as date, title, image, qty'
        ' FROM product p'
    ).fetchall()
    
    return render_template('product/view.html', products=products) # redirect to the view.html page and passing the queried products


"""
description: this method thakes a product title and search the database for it
arguments: product title
returns : a dicationary that conatins the query results
"""
def check_product_exists(title):
     
        macth = get_db().execute(
                'SELECT p.title'
                ' FROM product p'
                ' WHERE p.title = ?',
                (title,)
                ).fetchone()

        return macth


"""
This is the create view of the product 
"""
@bp.route('/create', methods=('GET', 'POST'))
def create():
    #checks if we are creating a new product or just viewing the create html page, if true then start creating a new product
    if request.method == 'POST':
        # getting the user input from the create.html page
        title = request.form['title'] 
        qty = request.form['quantity']
        error = None

        #Checks if the title is empty and if true, flashes the error message and redirects to creat.html page
        if not title:
            error = 'Title is required.'
            flash(error)
        
        else:
            #checks if the user attached a picture for the created product, if true it calls the save_image method to save the image 
            if  request.files['file'].filename != '':
                file = request.files['file']
                filename = save_image(file)
            #if the user didnt attach a picture the product will have the default image
            else: 
                filename = "default_image.jpg"
                
            exists = check_product_exists(title)
            
            #check if another product with the same name is already exists in the database, and if true, it flashes an error message
            if exists is not None:
                flash("*Error: Similar product with the same title Has been already added ")
            else:
                db = get_db() #create a connection with the database
                
                #inserting the new product to the database
                db.execute(
                    'INSERT INTO product (title, image, qty)'
                    ' VALUES (?, ?, ?)',
                    (title, filename, qty)
                )
                db.commit()
                
                #redirects the user to the home page of the product view
                return redirect(url_for('product.index'))

    #redirects the user to the product create.html page
    return render_template('product/create.html')


"""
description: this method thakes an id of a product and search the database for it
arguments: product id
returns : a dicationary that conatins the query results
"""
def get_product(id):
    product = get_db().execute(
        'SELECT p.product_id, title, image, qty'
        ' FROM product p'
        ' WHERE p.product_id = ?',
        (id,)
    ).fetchone()

    #checks if there are no products with the passed id
    if product is None:
        abort(404, "Product id {0} doesn't exist.".format(id))


    return product

"""
This is the update view of the product 
"""
@bp.route('/<int:id>/update', methods=('GET', 'POST'))
def update(id):
    product = get_product(id) #gets the product information
    
    #checks if we are updating a product or just viewing the update html page, if true then start updating the product
    if request.method == 'POST':
        # getting the user input from the update.html page
        title = request.form['title']
        quantity = request.form['quantity']
        error = None
        
        #Checks if the title is empty and if true, flashes the error message and redirects to update.html page
        if not title:
            error = 'Title is required.'
            flash(error)
        
        else:
            #checks if the user attached a picture for the updated product, if true it calls the save_image method to save the image 
            if  request.files['file'].filename != '':
               file = request.files['file']
               filename = save_image(file)
               
               if filename == "": 
                    filename = "default_image.jpg"
        
            #if the user didnt attach a new picture the product will have the old image
            else:
                filename = product['image']
                
            exists = check_product_exists(title)
            
            #check if another product with the same name is already exists in the database, and if true, it flashes an error message
            if exists is not None and exists[0] != product['title']:
                flash("*Error: Similar product with the same title Has been already added")
            else:
                db = get_db() #create a connection with the database
                
                #updating the product in the database
                db.execute(
                    'UPDATE product SET title = ?, image = ?, qty = ?'
                    ' WHERE product_id = ?',
                    (title, filename, quantity, id)
                )
                db.commit()
                
                #redirects the user to the home page of the product view
                return redirect(url_for('product.index'))
            
    #redirects the user to the product update.html page
    return render_template('product/update.html', product=product)


"""
This is the delete view of the product 
"""
@bp.route('/<int:id>/delete', methods=['GET', 'POST'])
def delete(id):
    db = get_db() #create a connection with the database
    
    #query the product from productMovement table
    product = get_db().execute(
        'SELECT m.product_id'
        ' FROM productMovement m'
        ' WHERE m.product_id = ?',
        (id,)
    ).fetchone()
    
    #checks if the product has been used in the product movement, 
    # if true it flashes an error message and redirects the user to the home view of the product
    if product is not None:
        flash("Error: Cant delete this product because its used in the product movement")
        return redirect(url_for('product.index'))
    else:
        db.execute('DELETE FROM product WHERE product_id = ?', (id,)) #delete the product from the database
        db.commit()
        
        #redirects the user to the home page of the product view
        return redirect(url_for('product.index')) 