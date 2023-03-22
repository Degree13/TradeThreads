#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Blueprint
from flask import Flask, request, render_template, redirect, url_for, abort, flash, session, g
from datetime import datetime
from connexion_db import get_db

client_commande = Blueprint('client_commande', __name__,
                        template_folder='templates')


@client_commande.route('/client/commande/valide', methods=['POST'])
def client_commande_valide():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    sql = ''' SELECT ligne_panier.quantite, ligne_panier.prix, designation AS nom 
    FROM vetement, ligne_panier
    WHERE vetement_id = id_vetement 
    AND utilisateur_id = %s '''
    mycursor.execute(sql, id_client)
    articles_panier = mycursor.fetchall()

    if len(articles_panier) >= 1:
        sql = ''' SELECT SUM(ligne_panier.prix) AS total_prix FROM ligne_panier WHERE utilisateur_id = %s'''
        mycursor.execute(sql, (id_client,))
        prix_total = mycursor.fetchone()
        prix_total = prix_total['total_prix']
        print("prix total :", prix_total)
    else:
        prix_total = 0
        print("prix total :", prix_total)
    # etape 2 : selection des adresses
    return render_template('client/boutique/panier_validation_adresses.html'
                           #, adresses=adresses
                           , articles_panier=articles_panier
                           , prix_total=prix_total
                           , validation=1
                           )

@client_commande.route('/client/commande/add', methods=['POST'])
def client_commande_add():
    mycursor = get_db().cursor()

    # choix de(s) (l')adresse(s)

    id_client = session['id_user']
    #selection du contenu du panier de l'utilisateur
    sql = ''' SELECT * FROM ligne_panier WHERE utilisateur_id = %s '''
    items_ligne_panier = []
    mycursor.execute(sql, id_client)
    items_ligne_panier = mycursor.fetchall()
    # if items_ligne_panier is None or len(items_ligne_panier) < 1:
    #     flash(u'Pas d\'articles dans le ligne_panier', 'alert-warning')
    #     return redirect(url_for('client_index'))
                                           # https://pynative.com/python-mysql-transaction-management-using-commit-rollback/
    #a = datetime.strptime('my date', "%b %d %Y %H:%M")

    vetement_id = request.form.get('id_vetement')
    quantite = request.form.get('id_quantite')
    prix = request.form.get('prix')

    # Creation de la commande
    date_achat = datetime.today().strftime('%Y-%m-%d')
    sql = ''' INSERT INTO commande (date_achat, utilisateur_id, etat_id) VALUES (%s, %s, %s)'''
    tuple_update1 = (date_achat, id_client, 1)
    print("this is tupple update :", tuple_update1)
    mycursor.execute(sql, tuple_update1)

    sql = '''SELECT last_insert_id() as last_insert_id'''
    mycursor.execute(sql)
    id_commande = mycursor.fetchone()
    print("this is id_commande :", id_commande)

    # numéro de la dernière commande
    print("this is items ligne panier :", items_ligne_panier)
    for item in items_ligne_panier:
        print("this is item :", item)
        #suppression d'une ligne de panier
        sql = ''' DELETE FROM ligne_panier WHERE vetement_id = %s '''
        print("this is item[vetement_id] :", item['vetement_id'])
        mycursor.execute(sql, item['vetement_id'])

        # ajout d'une ligne de commande
        sql = ''' INSERT INTO ligne_commande VALUES (%s, %s, %s, %s)'''
        tuple_update2 = (id_commande['last_insert_id'], item['vetement_id'], item['prix'], item['quantite'])
        print("this is tupple update2 :", tuple_update2)
        mycursor.execute(sql, tuple_update2)

        # suppression des favoris dans le panier
        sql = ''' DELETE FROM favoris WHERE vetement_id = %s '''
        mycursor.execute(sql, item['vetement_id'])

    get_db().commit()
    flash(u'Commande ajoutée','alert-success')
    return redirect('/client/article/show')




@client_commande.route('/client/commande/show', methods=['get','post'])
def client_commande_show():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    #selection des commandes ordonnées par état puis par date d'achat descendant
    sql = '''
    SELECT c.*, SUM(l.prix * l.quantite) AS prix_total, SUM(l.quantite) AS nbr_articles, etat.libelle_etat AS libelle
    FROM commande c
    JOIN ligne_commande l ON c.id_commande = l.commande_id
    JOIN etat ON c.etat_id = etat.id_etat
    WHERE c.utilisateur_id = %s
    GROUP BY c.id_commande
    ORDER BY c.etat_id DESC, c.date_achat DESC
    '''
    mycursor.execute(sql, id_client)
    commandes = mycursor.fetchall()


    articles_commande = None
    commande_adresses = None
    id_commande = request.args.get('id_commande', None)
    if id_commande != None:
        print(id_commande)
        # partie 1 : selection des articles de la commande selectionnée
        sql = ''' SELECT lc.*, v.designation AS nom, SUM(lc.prix * lc.quantite) AS prix_ligne
        FROM ligne_commande lc
        JOIN vetement v ON lc.vetement_id = v.id_vetement
        WHERE lc.commande_id = %s
        GROUP BY lc.commande_id, lc.vetement_id
        '''
        mycursor.execute(sql, id_commande)
        articles_commande = mycursor.fetchall()

        for article in articles_commande:
            print("this is article :", article)

        # partie 2 : selection de l'adresse de livraison et de facturation de la commande selectionnée
        sql = ''' selection des adressses '''


    return render_template('client/commandes/show.html'
                           , commandes=commandes
                           , articles_commande=articles_commande
                           , commande_adresses=commande_adresses
                           )

