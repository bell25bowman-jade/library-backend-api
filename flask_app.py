from app import create_app

app = create_app("ProductionConfig")  # Use the ProductionConfig for production environment

@app.route('/hello')
def hello():
    return {'message': 'Hello from Flask!'}


if __name__ == "__main__":
    app.run(debug=True)