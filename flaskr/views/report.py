
from flask import (
    Blueprint, Flask, flash, g, redirect, render_template, request, url_for, send_file
)
from werkzeug.exceptions import abort
from flaskr.db import get_db

# creating a new blueprint for the report view
bp = Blueprint('report', __name__, url_prefix='/report')



    
"""
The home view of the report 
will deisplay all the locations along with the products and thier quantities in that location
"""  
@bp.route('/')
def index():
    db = get_db() #create a connection with the database
    
    #querying all the locations along with the products and thier quantities in that location
    report = db.execute(
        'SELECT pl.title,qty'
        ' FROM productLocation pl'
        ' Group BY title'
        ).fetchall()
    
    for item in report:
        print(item['title']+ " =>"+str(item['qty'])+ " =>"+ str(item['qty']))
    
    
    products = db.execute(
        'SELECT DISTINCT title'
        ' FROM productLocation '
        ).fetchall()
    
   
  
    locations = db.execute(
        'SELECT DISTINCT name'
        ' FROM productLocation '
        ).fetchall()
    
    locationqty = dict()
    
    for location in locations:
        qty = db.execute(
        'SELECT title, qty'
        ' FROM productLocation '
        ' WHERE name = ? ',
        (location['name'],)
        ).fetchall()
        
        locationqty[location['name']] = {p['title']:0 for p in products}
        for q in qty:
            locationqty[location['name']][q['title']] = q['qty']
   
    return render_template('main/report.html',products=products,locations=locations,locationqty=locationqty)


















