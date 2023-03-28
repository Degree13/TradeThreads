#! /usr/bin/python
# -*- coding:utf-8 -*-
from datetime import datetime
from flask import Blueprint
from flask import Flask, request, render_template, redirect, abort, flash, session

from connexion_db import get_db

admin_dataviz = Blueprint('admin_dataviz', __name__,
                        template_folder='templates')

@admin_dataviz.route('/admin/dataviz/etat1')
def show_type_article_stock():
    mycursor = get_db().cursor()
    # Compter le nombre de favoris par vetement
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

    # Compter le nombre de consultation par vetement
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

    # Compter le prix de tous les articles en favoris
    sql = ''' SELECT SUM(v.prix * f.count_favoris) AS prix_total
    FROM vetement v
    JOIN (
        SELECT vetement_id, COUNT(*) AS count_favoris
        FROM favoris
        GROUP BY vetement_id
    ) f ON v.id_vetement = f.vetement_id
    '''
    mycursor.execute(sql)
    datas_show3 = mycursor.fetchall()
    prix_total = [int(row['prix_total']) for row in datas_show3]
    
    # Vérifier si une mesure existe déjà pour la date actuelle
    today = datetime.now().strftime('%Y-%m-%d')
    sql_check = '''SELECT COUNT(*) AS data FROM hist_prix WHERE DATE(date_prix) = %s'''
    mycursor.execute(sql_check, (today,))
    result = mycursor.fetchone()
    print("result: ", result)
    # Ajouter le prix total dans la table hist_prix si aucune mesure n'existe pour la date actuelle
    if result["data"] == 0:
        sql_insert = '''INSERT INTO hist_prix (date_prix, prix) VALUES (%s, %s)'''
        mycursor.execute(sql_insert, (datetime.now(), prix_total[0]))
        get_db().commit()

    # Récuperer le prix total de hist_prix par date pour toute date inférieur a 1 mois
    sql = ''' SELECT date_prix, prix 
    FROM hist_prix 
    WHERE date_prix > DATE_SUB(NOW(), INTERVAL 12 MONTH) '''
    mycursor.execute(sql)
    datas_show3 = mycursor.fetchall()
    labels3 = [str(row['date_prix']) for row in datas_show3]
    values3 = [int(row['prix']) for row in datas_show3]

    return render_template('admin/dataviz/dataviz_etat_1.html'
                           , datas_show=datas_show
                           , datas_show2=datas_show2
                           , labels=labels
                           , values=values
                           , labels2=labels2
                           , values2=values2
                           , labels3=labels3
                           , values3=values3)

