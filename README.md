# Elektrisierende Elektrizität


## Start Web App

### setup Flask virtual environment
> python -m venv .venv

> .\\.venv\Scripts\activate

> pip install Flask


### run app
> .\\.venv\Scripts\activate

> flask --app ./webportal/web_server.py run

### use website

visit [localhost:5000/login]

## Start Stromzähler
Similar setup to the Web App


### run app
> .\\.venv\Scripts\activate

> flask -app ./Stromzähler/app.py run
 
### use website
Service-Worker: [localhost:25565/service-worker/]
Order meter: [localhost:25565/meter/order/]
Meter actions: [localhost:25565/meter/<meter-uuid4>/<action>/]



[localhost:5000/login]:<http://localhost:5000/login>
[localhost:25565/service-worker/]:<http://localhost:25565/service-worker/>
[localhost:25565/meter/order/]:<http://localhost:25565/meter/order/>
[localhost:25565/meter/<meter-uuid4>/<action>/]:<http://localhost:25565/meter/<meter-uuid>/<action>/>
