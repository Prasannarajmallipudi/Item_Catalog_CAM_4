## Item_Catalog_CAM_4

By Prasanna Raj Mallipudi
## About the Project
   This is web application build with python framework flask.This is the informative web app
   which gives information about Digital Camera Models in Market and Price and Models and Colors Check the all users.


## Requirements
  - python
  - Flask
  - SQLAlchemy
  - Oauth2client
  - requests
  - Front End Technologies

## Files in this project
  - client_secrets.json -----> File contains oauth2 information.
  - camdatabase.py ----------> is the database setup file which create tables in the sqllite3 database using sqlalchemy
  - camcatalog.db -----------> is the sqllite3 database file.
  - sample_database ---------> Sample Data Stored in database.
  - Static Folder -----------> contains the static files such as
                               css,javascript,images etc.
  - Templates Folder --------> contains the html files only which is used to  rendering data

## Oauth
  This application authenticates users using Google Oauth v2 api and stores user data in database.
  More [about](https://developers.google.com/identity/protocols/OAuth2) Google Oauth

  For this api to work you need to have `client_secrets.json` which can downloaded from
  [Google Api Console](https://console.developers.google.con)
  Then
    - Create a new project
    - Go to credentials page and update your information
    - Download the client_secrets.json file and place it project directory


## How to run server
  In order to run this server you need to install python(2.7) or higher in your machine(linux/windows).

  It is recommended to use vagrant for testing .This will not effect your machine configurations.
  Here is [documentation](https://www.vagrantup.com/docs/) to install vagrant and [virtual box]      (https://www.virtualbox.org/wiki/Documentation)
  
  These instructions assume you have the Udacity-provided Virtual machine
  
  Clone the Udacity Vagrantfile
  
  Go to Vagrant directory and either clone this repo or download and place zip here
  
  `vagrant up`
  `vagrant ssh`

 Connecting vagrant after goto to Shared folders, goto Project Folder
 The entry point for this project is finaldata.py
  run this file using
  ```
  $python finaldata.py

  ```
  After this if all goes well access your web application from [http://localhost:5001](http://localhost:5001)
  
## JSON Endpoint
  - Cam Catalog JSON: /brand/01/JSON - Displays the Brands and Models data
  
  - /brand/<int:brand_id>/JSON

## Content Help
 --- Udacity Videos
 
 --- www.w3schools.com
     
 --- www.stackoverflow.com
 
 --- www.tutorialspoint.com/flask
