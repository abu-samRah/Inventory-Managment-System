import sqlite3
import click
from flask import current_app, g
from flask.cli import with_appcontext


# returns a connection to the database, 
# if there is already a previous one, it just returns it
def get_db():
    if 'db' not in g:
        #establishes a connection to the file pointed at by the database configuration key.
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row #This allows accessing the columns by name

    return g.db

#checks if a connection exisist and if true, it closes the connection
def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()
        
#creates the tabels specified in the schema.sql file
def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

#defines a command line command called init-db 
#that calls the init_db function and shows a success message to the user

@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')
    
#registers the close_db and the init_db_command functions with the application instance
def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)        