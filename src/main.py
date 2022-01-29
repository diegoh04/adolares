import os
from project import create_app
from flask import Flask

app = create_app()
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=os.environ.get('PORT',8080))
