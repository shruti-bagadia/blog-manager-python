# Blog Manager Python
A simple FastAPI blog with UUIDs, auth, CRUD & filtering.

--------------Setup Guide ---------------
1. Clone the repo and enter into it.
git clone https://github.com/shruti-bagadia/blog-manager-python.git
cd blog-manager-python
2. Create & activate venv
python -m venv myenv
myenv\scripts\activate.bat 
3. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
4. Start Uvicorn Server
uvicorn app.main:app --host 0.0.0.0 --port 8000 –reload
5. Open API Swagger
[Blog API - Swagger U](http://127.0.0.1:8000/docs#/)
