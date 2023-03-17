#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Blueprint
from flask import Flask, request, render_template, redirect, abort, flash, session

from connexion_db import get_db

client_article = Blueprint('client_article', __name__,
                        template_folder='templates')

@client_article.route('/client/index')
@client_article.route('/client/article/show')              # remplace /client
def client_article_show():                                 # remplace client_index
    mycursor = get_db().cursor()
    id_client = session['id_user']

    list_param = []
    condition_and = ""
    sql = '''
            SELECT id_vetement AS id_article
                   , designation AS nom
                   , quantite AS stock
                   , prix
                   , image
            FROM vetement
            '''

    if "filter_word" in session or "filter_prix_min" in session or "filter_prix_max" in session or "filter_types" in session:
        sql = sql + " WHERE "
    if "filter_word" in session:
        sql = sql + " designation LIKE %s "
        recherche = "%" + session["filter_word"] + "%"
        list_param.append(recherche)
        condition_and = " AND "
    if "filter_prix_min" in session or "filter_prix_max" in session:
        sql = sql + condition_and + " prix BETWEEN %s AND %s "
        list_param.append(session["filter_prix_min"])
        list_param.append(session["filter_prix_max"])
        condition_and = " AND "
    if "filter_types" in session:
        sql = sql + condition_and + "("
        last_item = session["filter_types"][-1]
        for item in session["filter_types"]:
            sql = sql + "type_vetement_id = %s"
            if item != last_item:
                sql = sql + " or "
            list_param.append(item)
        sql = sql + ")"

    tuple_sql = tuple(list_param)
    mycursor.execute(sql, tuple_sql)
    articles = mycursor.fetchall()


    ''' UNION
                    SELECT NULL AS id_article
                        , NULL AS nom
                        , NULL AS stock
                        , NULL AS prix
                        , COUNT(vetement_id) AS liste_envie
                    FROM favoris
                    WHERE utilisateur_id = %s '''
    
    for article in articles:
        id_article = article['id_article']
        sql = ''' SELECT COUNT(vetement_id) AS liste_envie
                    FROM favoris
                    WHERE utilisateur_id = %s 
                    AND vetement_id = %s '''
        mycursor.execute(sql, (id_client, id_article))
        liste_envie = mycursor.fetchone()
        article['liste_envie'] = liste_envie['liste_envie']

    sql = '''
        SELECT id_type_vetement as id
        ,libelle_type_vetement as nom
        FROM type_vetement
        ORDER BY nom;
        '''
    mycursor.execute(sql)
    types_article = mycursor.fetchall()


    sql3=''' prise en compte des commentaires et des notes dans le SQL    '''


    sql = '''SELECT lp.utilisateur_id, lp.vetement_id AS id_article, lp.quantite, lp.prix, lp.date_ajout, v.designation AS nom
        FROM ligne_panier lp
        JOIN vetement v ON lp.vetement_id = v.id_vetement
        WHERE lp.utilisateur_id = %s'''
    mycursor.execute(sql, (id_client,))
    articles_panier = mycursor.fetchall()


    if len(articles_panier) >= 1:
        sql = "SELECT (quantite * prix) as prix_total " \
              "FROM ligne_panier " \
              "WHERE utilisateur_id = %s"
        mycursor.execute(sql, (id_client,))
        prix = mycursor.fetchall()
        prix_total = 0
        for elem in prix:
            prix_total += elem["prix_total"]
    else:
        prix_total = None

    # Count the number of favoris
    #sql = ''' COUNT id_article AS liste_envie FROM favoris WHERE id_client = %s '''
    #mycursor.execute(sql, (id_client,))
    #TODO a finir

    return render_template('client/boutique/panier_article.html'
                           , articles=articles
                           , articles_panier=articles_panier
                           , prix_total=prix_total
                           , items_filtre=types_article
                           )
