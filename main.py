from app import application
from app.apis import *

if __name__ == "__main__":
    application.run(debug=True, port=8000)