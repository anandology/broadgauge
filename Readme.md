BroadGauge
==========

Platform for managing training/workshops by connecting interested trainers and educational institutes interested in conducting trainings for their students. 

This is going to be used for managing Python workshops going to be conducted across India as part of PyCon India 2014.

[![Build Status](https://travis-ci.org/anandology/broadgauge.svg?branch=master)](https://travis-ci.org/anandology/broadgauge)

Requirements
------------

* PostgreSQL
* Python 2.7
* virtualenv

How to setup
------------

* Clone the repo

        git clone git://github.com/anandology/broadgauge.git
        cd broadgauge

* setup virtualenv and install python packages

        virtualenv .
        . bin/activate
        pip install -r requirements.txt

* create a database

        createdb pythonexpress

* add schema 
        
        psql pythonexpress < broadgauge/schema.sql

* run the app

        python run.py
