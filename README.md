**Project overview** 

**DemoVideo : [https://youtu.be/5O-\_yoaGEjQ](https://youtu.be/5O-_yoaGEjQ)** 

**Structural map of files**

├── db.py  
├── index.html  
├── modified\_sms\_v2.xml  
├── process.py  
├── README.md  
├── script.js  
├── server.py  
└── style.css

**1\. Initial Setup and Data Processing**

1. **process.py:**

* This is the first file that needs to be executed (python3 process.py)  
    
* It processes the XML data file (modified\_sms\_v2.xml) containing SMS transaction data  
    
* It performs several key functions:

* Parses the XML file using xml.etree.ElementTree


* Extracts and categorizes transaction types (incoming, payment, transfer, etc.)


* Standardizes names from transaction messages


* Extracts amounts and dates


* Processes all this data into a structured format

* Stores the processed data in SQLite database (corrected\_data.db) using functions from db.py

2. **db.py:**

* Handles all database operations:

* init\_db() \- Creates the SQLite database and table structure


* store\_data() \- Inserts processed transaction data into the database


* get\_unique\_names() \- Retrieves unique names for filtering

**2\. Serving the Web Application**

3. **server.py:**

* This is the Flask web server (python3 server.py)  
    
* Sets up routes and serves the application:

* / \- Serves the main index.html file


* /data \- Provides API endpoint for transaction data (filtered by type/name)


* Other routes serve static files (CSS, JS)

* Handles database queries and returns JSON data for the frontend  
    
* Implements filtering logic based on user selections

**3\. Frontend Components**

4. **index.html:**

* The main HTML structure of the dashboard  
    
* Includes:  
    
* Cards for summary statistics


* Filter controls (type and name dropdowns)


* Chart container for the pie chart


* Table for displaying transactions

* Links to CSS and JavaScript files

5. **style.css:**

* Provides  styling for the dashboard  
    
* Includes responsive design for different screen sizes  
    
* Styles for cards, table, filters, and loading states

6. **script.js:**

* Handles all client-side functionality:

* Fetches data from the /data endpoint


* Updates the chart using Chart.js


* Populates the transactions table


* Updates summary statistics


* Handles filter changes with debouncing


* Implements formatting functions (currency)

**Flow of Execution:**

1. User runs process.py to create/update the database  
     
2. User runs server.py to start the Flask application  
     
3. Browser requests index.html from Flask server  
     
4. HTML loads and requests CSS/JS files  
     
5. JavaScript makes API call to /data endpoint  
     
6. Flask queries database and returns JSON data  
     
7. JavaScript processes data and renders:

* Summary cards (total count/amount)


* Pie chart showing transaction distribution


* Filtered transaction table

8. When filters change, JavaScript makes new API calls and updates the UI

**Key Features:**

* Filtering by transaction type and name  
    
* Interactive pie chart showing transaction distribution  
    
* Detailed transaction table with expandable details  
    
* Responsive design that works on mobile and desktop  
    
* Loading states during data fetching

**Dependencies:**

* Backend: Flask, SQLite  
    
* Frontend: Chart.js (loaded via CDN)  
    
* Python: xml.etree.ElementTree, re, datetime, sqlite3

**DEMO VIDEO AND PROJECT WORK THROUGH**

**DemoVideo** : [https://youtu.be/5O-\_yoaGEjQ](https://youtu.be/5O-_yoaGEjQ) 

**GET THE PROJECT**

* **Zip the project or clone the project:**

**Git clone the project :** 

git clone [https://github.com/josep-prog/momo\_dashboard.git](https://github.com/josep-prog/momo_dashboard.git) 

  **Or zip the file** :   
	  
**sudo apt update**          
**sudo apt install zip**                  *\# make sure that zip is installed*  
**unzip momo\_dashboard-main.zip**        *\# unzip the file to extract all the files* 

**I NSTALL DEPENDENCIES**

1. **Install the dependence** : pip install flask \# we need to make sure that we have flask

* In case it fails :  
    
  * sudo apt install python3-venv         *\# ensure venv is installed*  
  * python3 \-m venv venv  
  * source venv/bin/activate  
  * pip install flask                               *\# Then finally install*  
  * Install sqlite : sudo apt install sqlite2

**HOW TO RUN**

python3 process.py                                         *\# for generating the database*

python3 server.py                                           *\# for running the whole* project  
***Expected output***

**joe@pop-os**:\~/momo\_dashboard-main$ python3 server.py

\* Serving Flask app 'server'  
\* Debug mode: on  
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.  
\* Running on [http://127.0.0.1:5000](http://127.0.0.1:5000)    
Press CTRL+C to quit  
\* Restarting with stat  
\* Debugger is active\!  
\* Debugger PIN: 108-673-974

**Open browser page this url** : [http://127.0.0.1:5000](http://127.0.0.1:5000) 

**NOTE** : please make sure that port 5000 is not in use anywhere else in another opened terminal tab “[http://127.0.0.1:5000](http://127.0.0.1:5000)” 

**If so this is the expected** 

output:joe@pop-os:\~/Downloads/momo\_dashboard$ python3 server.py   
 \* Serving Flask app 'server'  
 \* Debug mode: on  
Address already in use  
Port 5000 is in use by another program. Either identify and stop that program, or start the server with a different port.  
joe@pop-os:\~/Downloads/momo\_dashboard$ 

Authors : 

Joseph Nishimwe ([j.nishimwe@alustudent.com](mailto:j.nishimwe@alustudent.com))

TEDLA Tesfaye Godebo ([t.godebo@alustudent.com](mailto:t.godebo@alustudent.com) )

Justine Neema ([j.neema@alustudent.com](mailto:j.neema@alustudent.com) )

Vestine Umukundwa ([v.umukundwa@alustudent.com](mailto:v.umukundwa@alustudent.com) )