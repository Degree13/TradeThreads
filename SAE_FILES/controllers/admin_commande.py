#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Blueprint
from flask import Flask, request, render_template, redirect, flash, session

from connexion_db import get_db

admin_commande = Blueprint('admin_commande', __name__,
                        template_folder='templates')

@admin_commande.route('/admin')
@admin_commande.route('/admin/commande/index')
def admin_index():
    return render_template('admin/layout_admin.html')


@admin_commande.route('/admin/commande/show', methods=['get','post'])
def admin_commande_show():
    mycursor = get_db().cursor()
    admin_id = session['id_user']
    sql = '''
    SELECT c.id_commande, c.date_achat, c.utilisateur_id, c.etat_id, COUNT(lc.commande_id) AS nbr_articles, e.libelle_etat AS libelle, SUM(lc.prix*lc.quantite) AS prix_total 
    FROM commande c
    JOIN etat e ON c.etat_id = e.id_etat
    JOIN ligne_commande lc ON c.id_commande = lc.commande_id
    GROUP BY c.id_commande
    ORDER BY c.date_achat DESC
    '''

    mycursor.execute(sql)
    commandes = mycursor.fetchall()

    articles_commande = None
    commande_adresses = None
    id_commande = request.args.get('id_commande', None)
    print(id_commande)
    if id_commande != None:
        sql = ''' SELECT vetement.designation AS nom, ligne_commande.quantite, ligne_commande.prix, (ligne_commande.quantite*ligne_commande.prix) AS prix_ligne
        FROM ligne_commande
        JOIN vetement ON ligne_commande.vetement_id= vetement.id_vetement
        WHERE commande_id = %s   '''
        mycursor.execute(sql, id_commande)
        articles_commande = mycursor.fetchall()
        commande_adresses = []
    return render_template('admin/commandes/show.html'
                           , commandes=commandes
                           , articles_commande=articles_commande
                           , commande_adresses=commande_adresses
                           )


@admin_commande.route('/admin/commande/valider', methods=['get','post'])
def admin_commande_valider():
    mycursor = get_db().cursor()
    commande_id = request.form.get('id_commande', None)
    if commande_id != None:
        print(commande_id)
        sql = '''
        UPDATE commande SET etat_id = 2
        WHERE id_commande = %s
        '''
        mycursor.execute(sql, commande_id)
        get_db().commit()
    return redirect('/admin/commande/show')