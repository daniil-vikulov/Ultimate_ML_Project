from app import data, app

with app.app_context():
    data.create_all()
