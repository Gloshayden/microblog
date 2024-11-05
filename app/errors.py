from flask import render_template
from app import app, db

# when error 404 apperars it shows a different web page (error 404 = web page not found)
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

# when error 500 apperars it shows a different web page (error 500 = internal server error)
@app.errorhandler(500)
def not_found_error(error):
    db.session.rollback() # resets the session to not risk errors
    return render_template('500.html'), 500