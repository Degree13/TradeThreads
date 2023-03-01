from flask import Flask, request, render_template, redirect, url_for, abort, flash, session, g

import pymysql.cursors


app = Flask(__name__)
app.config["DEBUG"] = True

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = pymysql.connect(
            user="root",
            host="localhost",
            #passwd="",
            database="bdd_nnicolas",
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
    return db