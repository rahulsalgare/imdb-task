# imdb-task

Install requirements with  
```pip install -r requirements.txt```

To create DB 
First open python interpreter in main project  
then inside,

```
>>> from api import db, create_app
  
>>> db.create_all(app=create_app())
```

To run server,  
```
set FLASK_APP=api
set FLASK_DEBUG=1
flask run
```

app will be running on http://127.0.0.1:5000
