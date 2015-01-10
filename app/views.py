# VIEWS.PY
# Handles routing of views.



from flask import redirect
from app import app


@app.route('/')
def index():
    """
    Index information page.
    """
    return app.send_static_file("index.html")


@app.route('/api')
def api():
    """
    Redirect the user to the API reference
    """
    return redirect('/#usage')