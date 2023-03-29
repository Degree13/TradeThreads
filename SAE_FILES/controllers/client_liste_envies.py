#! /usr/bin/python
# -*- coding:utf-8 -*-
import datetime
from flask import Blueprint
from flask import Flask, request, render_template, redirect, url_for, abort, flash, session, g

from connexion_db import get_db

client_liste_envies = Blueprint('client_liste_envies', __name__,
                        template_folder='templates')


@client_liste_envies.route('/client/envie/add', methods=['get'])
def client_liste_envies_add():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_article = request.args.get('id_article')
    # Verify that the article is not already in the list of wishes
    sql = ''' SELECT COUNT(vetement_id) AS liste_envie
                    FROM favoris
                    WHERE utilisateur_id = %s 
                    AND vetement_id = %s '''
    mycursor.execute(sql, (id_client, id_article))
    fav = mycursor.fetchone()
    if fav['liste_envie'] > 0:
        sql = ''' DELETE FROM favoris WHERE utilisateur_id = %s AND vetement_id = %s '''
        mycursor.execute(sql, (id_client, id_article))
        get_db().commit()
    else :
        # Take the number of the favorite highest fav_order where the user is the same
        sql = ''' SELECT MIN(fav_order) FROM favoris WHERE utilisateur_id = %s '''
        mycursor.execute(sql, (id_client))
        fav_max_int = mycursor.fetchone()
        fav_max_int = fav_max_int['MIN(fav_order)'] - 1
        print(fav_max_int)

        sql = ''' INSERT INTO favoris (utilisateur_id, vetement_id, fav_order) VALUES (%s, %s, %s) '''
        mytuple = (id_client, id_article, fav_max_int)
        mycursor.execute(sql, mytuple)
        get_db().commit()
    return redirect('/client/article/show')

@client_liste_envies.route('/client/envie/delete', methods=['get'])
def client_liste_envies_delete():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_article = request.args.get('id_article')
    sql = ''' DELETE FROM favoris WHERE utilisateur_id = %s AND vetement_id = %s '''
    mycursor.execute(sql, (id_client, id_article))
    get_db().commit()
    return redirect('/client/envies/show')

@client_liste_envies.route('/client/envies/show', methods=['get'])
def client_liste_envies_show():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    articles_liste_envies = []
    articles_historique = []
    nb_liste_envies = 0
    sql = ''' SELECT designation AS nom, id_vetement AS id_article, prix, quantite AS stock, image 
    FROM vetement, favoris 
    WHERE vetement.id_vetement = favoris.vetement_id 
    AND favoris.utilisateur_id = %s 
    ORDER BY fav_order ASC '''
    mycursor.execute(sql, (id_client))
    articles_liste_envies = mycursor.fetchall()

    nb_liste_envies = len(articles_liste_envies)

    #historique
    # Si l'article est dans l'historique depuis plus d'un mois on l'enlève
    sql = ''' DELETE FROM historique WHERE date_achat < DATE_SUB(NOW(), INTERVAL 1 MONTH) '''
    mycursor.execute(sql)
    get_db().commit()
    
    sql = ''' SELECT designation AS nom, id_vetement AS id_article, prix, image, date_achat, nb_consultation
    FROM historique, vetement
    WHERE historique.vetement_id = vetement.id_vetement
    AND historique.utilisateur_id = %s
    ORDER BY date_achat DESC
    '''
    mycursor.execute(sql, (id_client))
    articles_historique = mycursor.fetchall()

    return render_template('client/liste_envies/liste_envies_show.html'
                           , articles_liste_envies=articles_liste_envies
                           , articles_historique=articles_historique
                           , nb_liste_envies= nb_liste_envies
                           )



def client_historique_add(article_id, client_id):
    mycursor = get_db().cursor()
    client_id = session['id_user']
    # rechercher si l'article pour cet utilisateur est dans l'historique
    # si oui mettre
    sql =''' SELECT COUNT(vetement_id), nb_consultation
    FROM historique
    WHERE vetement_id = %s 
    AND utilisateur_id = %s '''
    mycursor.execute(sql, (article_id, client_id))
    historique_produit = mycursor.fetchall()
    #print(historique_produit)

    date_time = datetime.datetime.now()
    if historique_produit[0]['COUNT(vetement_id)'] > 0:
        sql = ''' UPDATE historique 
        SET date_achat = %s, nb_consultation = %s
        WHERE utilisateur_id = %s 
        AND vetement_id = %s '''
        nb_consultation = historique_produit[0]['nb_consultation'] + 1
        mytuple = (date_time, nb_consultation, client_id, article_id)
        mycursor.execute(sql, mytuple)

    if historique_produit[0]['COUNT(vetement_id)'] == 0:
        sql = ''' INSERT INTO historique (utilisateur_id, vetement_id, date_achat, nb_consultation) 
        VALUES (%s, %s, %s, 1) '''
        mytuple = (client_id, article_id, date_time)
        mycursor.execute(sql, mytuple) 
        
    get_db().commit()
    sql =''' SELECT vetement_id, date_achat 
    FROM historique 
    WHERE utilisateur_id = %s '''
    mycursor.execute(sql, (client_id))
    historiques = mycursor.fetchall()

    print("TEST - Historique :", len(historiques))
    while len(historiques) > 6:
        # Select the oldest article
        sql = ''' SELECT vetement_id, date_achat
        FROM historique
        WHERE utilisateur_id = %s
        ORDER BY date_achat ASC
        LIMIT 1 '''
        mycursor.execute(sql, (client_id))
        oldest_article = mycursor.fetchone()
        print(oldest_article)
        # Delete the oldest article
        sql = ''' DELETE FROM historique WHERE utilisateur_id = %s AND vetement_id = %s '''
        mycursor.execute(sql, (client_id, oldest_article['vetement_id']))
        get_db().commit()

        sql =''' SELECT vetement_id, date_achat 
        FROM historique 
        WHERE utilisateur_id = %s '''
        mycursor.execute(sql, (client_id))
        historiques = mycursor.fetchall()
        get_db().commit()


@client_liste_envies.route('/client/envies/up', methods=['get'])
@client_liste_envies.route('/client/envies/down', methods=['get'])
@client_liste_envies.route('/client/envies/last', methods=['get'])
@client_liste_envies.route('/client/envies/first', methods=['get'])
def client_liste_envies_article_move():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_article = request.args.get('id_article')
    # get fav_order of the article
    sql = ''' SELECT fav_order 
    FROM favoris 
    WHERE utilisateur_id = %s 
    AND vetement_id = %s '''
    mycursor.execute(sql, (id_client, id_article))
    fav_order = mycursor.fetchone()
    fav_order = fav_order['fav_order']
    print(fav_order)
    # if client route is up
    if request.path == '/client/envies/up':
        # select article that has the previous fav_order
        sql = ''' SELECT MAX(fav_order) 
        FROM favoris 
        WHERE utilisateur_id = %s 
        AND fav_order < %s '''
        mycursor.execute(sql, (id_client, fav_order))
        fav_order_before = mycursor.fetchone()
        sql = ''' SELECT vetement_id 
        FROM favoris 
        WHERE utilisateur_id = %s 
        AND fav_order = %s '''
        mycursor.execute(sql, (id_client, fav_order_before['MAX(fav_order)']))
        fav_order_before = mycursor.fetchone()
                
        # update fav_order of the article
        sql = ''' UPDATE favoris 
        SET fav_order = %s 
        WHERE utilisateur_id = %s 
        AND vetement_id = %s '''
        mycursor.execute(sql, (fav_order - 1, id_client, id_article))

        # update fav_order of the article before
        sql = ''' UPDATE favoris 
        SET fav_order = %s 
        WHERE utilisateur_id = %s 
        AND vetement_id = %s '''
        mycursor.execute(sql, (fav_order, id_client, fav_order_before['vetement_id']))
    
    if request.path == '/client/envies/down':
        # select article that has the next fav_order
        sql = ''' SELECT MIN(fav_order) 
        FROM favoris 
        WHERE utilisateur_id = %s 
        AND fav_order > %s '''
        mycursor.execute(sql, (id_client, fav_order))
        fav_order_after = mycursor.fetchone()
        sql = ''' SELECT vetement_id 
        FROM favoris 
        WHERE utilisateur_id = %s 
        AND fav_order = %s '''
        mycursor.execute(sql, (id_client, fav_order_after['MIN(fav_order)']))
        fav_order_after = mycursor.fetchone()
                
        # update fav_order of the article
        sql = ''' UPDATE favoris 
        SET fav_order = %s 
        WHERE utilisateur_id = %s 
        AND vetement_id = %s '''
        mycursor.execute(sql, (fav_order + 1, id_client, id_article))

        # update fav_order of the article next
        sql = ''' UPDATE favoris 
        SET fav_order = %s 
        WHERE utilisateur_id = %s 
        AND vetement_id = %s '''
        mycursor.execute(sql, (fav_order, id_client, fav_order_after['vetement_id']))

    if request.path == '/client/envies/last':
        # get max fav_order
        sql = ''' SELECT MAX(fav_order) 
        FROM favoris 
        WHERE utilisateur_id = %s '''
        mycursor.execute(sql, (id_client))
        fav_order_max = mycursor.fetchone()
        fav_order_max = fav_order_max['MAX(fav_order)']
        # update fav_order of the article
        sql = ''' UPDATE favoris 
        SET fav_order = %s 
        WHERE utilisateur_id = %s 
        AND vetement_id = %s '''
        mycursor.execute(sql, (fav_order_max + 1, id_client, id_article))
    
    if request.path == '/client/envies/first':
        # get min fav_order
        sql = ''' SELECT MIN(fav_order) 
        FROM favoris 
        WHERE utilisateur_id = %s '''
        mycursor.execute(sql, (id_client))
        fav_order_min = mycursor.fetchone()
        fav_order_min = fav_order_min['MIN(fav_order)']
        # update fav_order of the article
        sql = ''' UPDATE favoris 
        SET fav_order = %s 
        WHERE utilisateur_id = %s 
        AND vetement_id = %s '''
        mycursor.execute(sql, (fav_order_min - 1, id_client, id_article))

    
    get_db().commit()
    return redirect('/client/envies/show')
