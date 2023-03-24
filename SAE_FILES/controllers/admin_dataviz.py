#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Blueprint
from flask import Flask, request, render_template, redirect, abort, flash, session

from connexion_db import get_db

admin_dataviz = Blueprint('admin_dataviz', __name__,
                        template_folder='templates')

@admin_dataviz.route('/admin/dataviz/etat1')
def show_type_article_stock():
    mycursor = get_db().cursor()
    sql = ''' SELECT v.designation AS libelle, COALESCE(COUNT(f.vetement_id), 0) AS nbr_articles, v.id_vetement
    FROM vetement v
    LEFT JOIN favoris f ON v.id_vetement = f.vetement_id
    GROUP BY v.id_vetement
    ORDER BY nbr_articles ASC
    '''
    mycursor.execute(sql)
    datas_show = mycursor.fetchall()
    labels = [str(row['libelle']) for row in datas_show]
    values = [int(row['nbr_articles']) for row in datas_show]


    sql = ''' SELECT v.designation AS libelle, COALESCE(SUM(h.nb_consultation), 0) AS nbr_articles, v.id_vetement
    FROM vetement v
    LEFT JOIN historique h ON h.vetement_id = v.id_vetement
    GROUP BY v.id_vetement
    ORDER BY nbr_articles ASC 
    '''
    mycursor.execute(sql)
    datas_show2 = mycursor.fetchall()
    labels2 = [str(row['libelle']) for row in datas_show2]
    values2 = [int(row['nbr_articles']) for row in datas_show2]

    return render_template('admin/dataviz/dataviz_etat_1.html'
                           , datas_show=datas_show
                           , datas_show2=datas_show2
                           , labels=labels
                           , values=values
                           , labels2=labels2
                           , values2=values2)

