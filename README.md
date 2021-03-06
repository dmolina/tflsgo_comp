# Task Force on Large Scale Global Optimization comparison website

Website to automatically compare results of algorithms for real and large-scale
global optimization. Initially it was designed by the [Task Force on Large Scale
Global Optimization](http://tflsgo.org/) for its own competitions, like 
for [WCCI'2018](http://tflsgo.org/special_sessions/cec2018.html). 


However, it can be used for each Benchmark competition. The idea of the website
is to allow researchers to compare the results of its algorithms compared with
other algorithms.

## Demo

There is a online demo at [https://tflsgo.herokuapp.com/](https://tflsgo.herokuapp.com/).

[![Usage of benchmarks website comparison](https://i.ytimg.com/vi/Tcb5pscM-bc/hqdefault.jpg)](https://www.youtube.com/watch?v=Tcb5pscM-bc)]


## Structure

The page is compose in two parts:

- A HTML/CSS with JavaScript (using [Vue.js](http://vuejs.org/).

- A Flask application using a REST interface (with Flask_restful) to access the
  database (with SQLAlchemy using SQLite3). 
  
All requests among the website and the Flask application is done using Ajax. 

The website could be in a static server (like github Page or similar) but
currently it is served by the Flask app (because they must run in the same port,
due to security limits of POST methods).

## Requirements

It requires several libraries, indicated in requirements. You can install the
required libraries with:

```shell
pip install -r requirements.txt
```

## Init the database

At the beginning, the app create the initial database, with the CEC'2013
Benchmark. No data algorithms is inserted.

## Run the application

```shell
cd tflsgo_comp
python api.py
```

By default it allows all connections by port 5000. The port can be changed by
the environment variable $PORT.

## Testing the website

To compare, it is required to use a Excel file. In examples/ there are several
examples to test it.
