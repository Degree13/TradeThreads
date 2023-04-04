#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Blueprint
from flask import request, render_template, redirect, abort, flash, session

from connexion_db import get_db

client_panier = Blueprint('client_panier', __name__,
                        template_folder='templates')


@client_panier.route('/client/panier/add', methods=['POST'])
def client_panier_add():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_article = request.form.get('id_article')
    quantite = request.form.get('quantite', '')
    print("quantite : ", quantite)
    # ---------
    #id_declinaison_article=request.form.get('id_declinaison_article',None)
    #id_declinaison_article = 1

# ajout dans le panier d'une déclinaison d'un article (si 1 declinaison : immédiat sinon => vu pour faire un choix

    sql = '''   SELECT * FROM ligne_panier
                WHERE vetement_id = %s
                AND utilisateur_id = %s '''
    mycursor.execute(sql, (id_article, id_client))
    article_panier = mycursor.fetchone()

    mycursor.execute("SELECT * FROM vetement WHERE id_vetement =%s", id_article)
    article = mycursor.fetchone()
    prix = article["prix"]


    sql2 = "UPDATE vetement v SET v.quantite = v.quantite-%s " \
           "WHERE v.id_vetement = %s"
    tuple_update = (quantite, id_article)
    mycursor.execute(sql2, tuple_update)

    if not (article_panier is None) and article_panier["quantite"] >= 1:
        tuple_update = (quantite, id_client, id_article)
        sql = "UPDATE ligne_panier SET quantite = %s+1 " \
              "WHERE utilisateur_id = %s " \
              "AND vetement_id = %s"
        mycursor.execute(sql, tuple_update)
    else:
        tuple_insert = (id_client, id_article, quantite, prix)
        sql = "INSERT INTO ligne_panier(utilisateur_id, vetement_id, quantite, prix, date_ajout)" \
              "VALUES (%s, %s, %s, %s, current_timestamp)"
        mycursor.execute(sql, tuple_insert)
    get_db().commit()
    return redirect("/client/article/show")

@client_panier.route('/client/panier/delete', methods=['POST'])
def client_panier_delete():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_article = request.form.get('id_article', '')


    quantite = request.form.get('quantite', '')

    # ---------
    # partie 2 : on supprime une déclinaison de l'article
    # id_declinaison_article = request.form.get('id_declinaison_article', None)

    sql = "SELECT l.* FROM ligne_panier l " \
          "JOIN utilisateur u ON u.id_utilisateur = l.utilisateur_id " \
          "JOIN vetement v ON v.id_vetement = l.vetement_id " \
          "WHERE u.id_utilisateur=%s AND v.id_vetement=%s"
    tuple_select = (id_client, id_article)
    mycursor.execute(sql, tuple_select)
    article_panier= []
    article_panier = mycursor.fetchone()
    print("article_panier:", article_panier)

    if not(article_panier is None) and article_panier['quantite'] > 1:
        # mise à jour de la quantité dans le panier => -1 article
        sql = ''' UPDATE ligne_panier SET quantite = %s-1 WHERE utilisateur_id = %s AND vetement_id = %s '''
        tuple_update = (quantite, id_client, id_article)
        mycursor.execute(sql, tuple_update)
    else:
        # suppression de la ligne de panier
        sql = ''' DELETE FROM ligne_panier WHERE utilisateur_id = %s AND vetement_id = %s '''
        tuple_delete = (id_client, id_article)
        mycursor.execute(sql, tuple_delete)
    
    # get the quantity of the article in the database
    sql = "SELECT v.quantite FROM vetement v WHERE v.id_vetement = %s"
    mycursor.execute(sql, (id_article,))
    quantite = mycursor.fetchone()
    quantite = quantite['quantite']
    # mise à jour du stock de l'article disponible
    sql2 = "UPDATE vetement v SET v.quantite = %s+1 " \
            "WHERE v.id_vetement = %s"
    tuple_update = (quantite, id_article,)
    mycursor.execute(sql2, tuple_update)


    # mise à jour du stock de l'article disponible
    get_db().commit()
    return redirect('/client/article/show')


@client_panier.route('/client/panier/vider', methods=['POST'])
def client_panier_vider():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    sql = "SELECT l.* from ligne_panier l " \
          "JOIN utilisateur u ON u.id_utilisateur = l.utilisateur_id " \
          "WHERE u.id_utilisateur = %s"
    mycursor.execute(sql, (id_client,))
    items_panier = mycursor.fetchall()
    for item in items_panier:
        id_client = item["utilisateur_id"]
        id_article = item["vetement_id"]
        quantite = item["quantite"]

        sql = "DELETE FROM ligne_panier " \
              "WHERE utilisateur_id=%s " \
              "AND vetement_id=%s"
        tuple_delete = (id_client, id_article)
        mycursor.execute(sql, tuple_delete)

        sql2= "UPDATE vetement SET quantite = quantite+%s " \
              "WHERE id_vetement = %s"
        tuple_update = (quantite, id_article)
        mycursor.execute(sql2, tuple_update)
        get_db().commit()
    return redirect('/client/article/show')


@client_panier.route('/client/panier/delete/line', methods=['POST'])
def client_panier_delete_line():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_article = request.form.get('id_article')
    #id_declinaison_article = request.form.get('id_declinaison_article')

    sql = "SELECT l.* FROM ligne_panier l " \
          "JOIN utilisateur u ON u.id_utilisateur = l.utilisateur_id " \
          "JOIN vetement v ON v.id_vetement = l.vetement_id " \
          "WHERE u.id_utilisateur=%s " \
          "AND v.id_vetement=%s"
    mycursor.execute(sql, (id_client, id_article))
    ligne = mycursor.fetchone()
    id_utilisateur = ligne["utilisateur_id"]
    id_article = ligne["vetement_id"]
    quantite = ligne["quantite"]
    prix = ligne["prix"]

    sql = "DELETE FROM ligne_panier " \
          "WHERE utilisateur_id=%s " \
          "AND vetement_id=%s"
    tuple_delete = (id_utilisateur, id_article)
    mycursor.execute(sql, tuple_delete)

    sql2="UPDATE vetement v SET v.quantite = v.quantite+%s " \
         "WHERE v.id_vetement = %s"
    tuple_update = (quantite, id_article)
    mycursor.execute(sql2, tuple_update)

    get_db().commit()
    return redirect('/client/article/show')


@client_panier.route('/client/panier/filtre', methods=['POST'])
def client_panier_filtre():
    filter_word = request.form.get('filter_word', None)
    filter_prix_min = request.form.get('filter_prix_min', None)
    filter_prix_max = request.form.get('filter_prix_max', None)
    filter_types = request.form.getlist('filter_types', None)
    if filter_word or filter_word == "":
        if len(filter_word) > 1:
            if filter_word.isalpha():
                session["filter_word"] = filter_word
            else:
                flash(u"votre mot recherché oit uniquement contenir des lettres")
        else:
            if len(filter_word) == 1:
                flash(u"votre mot recherch doit être composé de au moins 2 lettres")
            else:
                session.pop("filter_word", None)
    if filter_prix_min or filter_prix_max:
        if filter_prix_min.isdecimal() and filter_prix_max.isdecimal():
            if int(filter_prix_min) < int(filter_prix_max):
                session["filter_prix_min"] = filter_prix_min
                session["filter_prix_max"] = filter_prix_max
            else:
                flash(u"min > max")
        else:
            flash(u"Les prix doivent être des numériques")
    if filter_types and filter_types != []:
        session["filter_types"] = filter_types

    return redirect('/client/article/show')


@client_panier.route('/client/panier/filtre/suppr', methods=['POST'])
def client_panier_filtre_suppr():
    session.pop("filter_word", None)
    session.pop("filter_prix_min", None)
    session.pop("filter_prix_max", None)
    session.pop("filter_types", None)
    return redirect('/client/article/show')
