from app import app

if __name__ == '__main__':
     web: gunicorn app:app
