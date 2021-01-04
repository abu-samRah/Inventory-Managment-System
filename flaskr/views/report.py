
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
        'SELECT pl.title,name,qty'
        ' FROM productLocation pl'
        ' ORDER BY name'
        ).fetchall()
  
    return render_template('main/report.html',report=report)











