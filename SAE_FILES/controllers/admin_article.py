#! /usr/bin/python
# -*- coding:utf-8 -*-
import math
import os.path
from random import random

from flask import Blueprint
from flask import request, render_template, redirect, flash
#from werkzeug.utils import secure_filename

from connexion_db import get_db

admin_article = Blueprint('admin_article', __name__,
                          template_folder='templates')


@admin_article.route('/admin/article/show')
def show_article():
    mycursor = get_db().cursor()
    sql = ''' SELECT id_vetement AS id_article, designation AS nom, prix, fournisseur, image, marque, quantite AS stock, couleur_id, taille_id , type_vetement_id AS type_article_id , libelle_type_vetement AS libelle
    FROM vetement
    JOIN type_vetement ON vetement.type_vetement_id = type_vetement.id_type_vetement
    '''
    mycursor.execute(sql)
    articles = mycursor.fetchall()
    return render_template('admin/article/show_article.html', articles=articles)

@admin_article.route('/admin/article/add', methods=['GET'])
def add_article():
    mycursor = get_db().cursor()

    sql=''' SELECT id_type_vetement AS id_type_article , libelle_type_vetement AS libelle FROM type_vetement'''
    mycursor.execute(sql)
    type_article= mycursor.fetchall()


    return render_template('admin/article/add_article.html'
                           ,types_article=type_article,
                           #,couleurs=colors
                           #,tailles=tailles
                            )


@admin_article.route('/admin/article/add', methods=['POST'])
def valid_add_article():
    mycursor = get_db().cursor()

    nom = request.form.get('nom', '')
    type_article_id = request.form.get('type_article_id', '')
    prix = request.form.get('prix', '')
    stock = request.form.get('stock', '')
    image = request.files.get('image', '')

    if image:
        filename = 'img_upload'+ str(int(2147483647 * random())) + '.png'
        image.save(os.path.join('static/images/', filename))
    else:
        print("erreur")
        filename=None

    sql = '''  INSERT INTO vetement(designation , image , prix, type_vetement_id , quantite )
    VALUES(%s, %s, %s, %s, %s)
    '''

    tuple_add = (nom, filename, prix, type_article_id, stock)
    print(tuple_add)
    mycursor.execute(sql, tuple_add)
    get_db().commit()

    print(u'article ajouté , nom: ', nom, ' - type_article:', type_article_id, ' - prix:', prix,
          ' - stock:', stock, ' - image:', image)
    message = u'article ajouté , nom:' + nom + '- type_article:' + type_article_id + ' - prix:' + prix + ' - stock:' + stock + ' - image:' + str(
        image)
    flash(message, 'alert-success')
    return redirect('/admin/article/show')


@admin_article.route('/admin/article/delete', methods=['GET'])
def delete_article():
    id_article=request.args.get('id_article')
    mycursor = get_db().cursor()
    # sql = ''' DELETE  * FROM vetement WHERE id_vetement = %s  '''
    # mycursor.execute(sql, id_article)
    # nb_declinaison = mycursor.fetchone()
    # if nb_declinaison['nb_declinaison'] > 0:
    #     message= u'il y a des declinaisons dans cet article : vous ne pouvez pas le supprimer'
    #     flash(message, 'alert-warning')
    # else:
    sql = ''' SELECT image FROM vetement WHERE id_vetement = %s '''
    mycursor.execute(sql, id_article)
    article = mycursor.fetchone()
    print(article)
    image = article['image']

    sql = ''' DELETE FROM vetement WHERE id_vetement = %s  '''
    mycursor.execute(sql, id_article)
    get_db().commit()
    if image != None:
        #os.remove('static/images/' + image)
        pass

    print("un article supprimé, id :", id_article)
    message = u'un article supprimé, id : ' + id_article
    flash(message, 'alert-success')

    return redirect('/admin/article/show')


@admin_article.route('/admin/article/edit', methods=['GET'])
def edit_article():
    id_article=request.args.get('id_article')

    mycursor = get_db().cursor()
    sql = ''' SELECT id_vetement AS id_article, designation AS nom, prix, fournisseur, image, marque, quantite AS stock, couleur_id, taille_id , type_vetement_id AS type_article_id , libelle_type_vetement AS libelle FROM vetement JOIN type_vetement ON vetement.type_vetement_id = type_vetement.id_type_vetement WHERE id_vetement = %s
    '''
    mycursor.execute(sql, id_article)
    article = mycursor.fetchone()
    print(article)
    sql = ''' SELECT id_type_vetement AS id_type_article, libelle_type_vetement AS libelle FROM type_vetement
    '''
    mycursor.execute(sql)
    types_article = mycursor.fetchall()
    print(types_article, u"----------------------------------------------")


    # sql = '''
    # requête admin_article_6
    # '''
    # mycursor.execute(sql, id_article)
    # declinaisons_article = mycursor.fetchall()

    return render_template('admin/article/edit_article.html'
                           ,article=article
                           ,types_article=types_article
                         #  ,declinaisons_article=declinaisons_article
                           )


@admin_article.route('/admin/article/edit', methods=['POST'])
def valid_edit_article():
    mycursor = get_db().cursor()
    nom = request.form.get('nom')
    id_article = request.form.get('id_article')
    image = request.files.get('image', '')
    type_article_id = request.form.get('type_article_id','')
    prix = request.form.get('prix', '')
    image = request.files.get('image')
    stock = request.form.get('stock', '')
    sql = ''' SELECT image, type_vetement_id FROM vetement WHERE id_vetement = %s
       '''
    mycursor.execute(sql, id_article)
    image_nom = mycursor.fetchone()
    image_nom = image_nom['image']
    if image:
        if image_nom != "" and image_nom is not None and os.path.exists(
                os.path.join(os.getcwd() + "/static/images/", image_nom)):
            os.remove(os.path.join(os.getcwd() + "/static/images/", image_nom))
        # filename = secure_filename(image.filename)
        if image:
            filename = 'img_upload_' + str(int(2147483647 * random())) + '.png'
            image.save(os.path.join('static/images/', filename))
            image_nom = filename

    sql = '''  UPDATE vetement SET designation = %s, image = %s, prix = %s, quantite = %s, type_vetement_id = %s 
    WHERE id_vetement = %s '''
    tuple_add = (nom, image_nom, prix, stock, type_article_id, id_article)
    mycursor.execute(sql, tuple_add)
    get_db().commit()
    if image_nom is None:
        image_nom = ''
    message = u'article modifié , nom:' + nom + '- type_article :' + type_article_id + ' - prix:' + prix  + ' - image:' + image_nom + ' - stock: ' + stock
    flash(message, 'alert-success')
    return redirect('/admin/article/show')






@admin_article.route('/admin/article/avis/<int:id>', methods=['GET'])
def admin_avis(id):
    mycursor = get_db().cursor()
    article=[]
    commentaires = {}
    return render_template('admin/article/show_avis.html'
                           , article=article
                           , commentaires=commentaires
                           )


@admin_article.route('/admin/comment/delete', methods=['POST'])
def admin_avis_delete():
    mycursor = get_db().cursor()
    article_id = request.form.get('idArticle', None)
    userId = request.form.get('idUser', None)

    return admin_avis(article_id)
