# Daily Status Sender

#### Open windows command line in project directory
#### Run the following commands:

Create a virtual environment using

```
py -m venv venv
```

activate venv using

```
venv\Scripts\activate
```

Install required packages with the following command

```
pip install -r requirements.txt
```

Start the app using (Powershell)

```
$env:FLASK_APP = "flaskr"
$env:FLASK_ENV = "development"
flask run --host=0.0.0.0
```

Then navigate to:

http://127.0.0.1:5000/
