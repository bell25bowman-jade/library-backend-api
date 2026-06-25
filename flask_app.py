from app import create_app
from app.models import db

app = create_app("developmentConfig")

@app.route('/hello')
def hello():
    return {'message': 'Hello from Flask!'}

with app.app_context():
        db.create_all()

app.run(debug=True)