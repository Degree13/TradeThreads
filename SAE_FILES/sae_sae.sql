# Suppression tables
DROP TABLE IF EXISTS  ligne_panier, ligne_commande, vetement, couleur, type_vetement, taille, commande, etat, utilisateur;

# enlevez marque et fournisseur
# Creation tables
CREATE TABLE utilisateur(
    id_utilisateur INT AUTO_INCREMENT,
    login VARCHAR(255),
    email VARCHAR(255),
    nom VARCHAR(255),
    password VARCHAR(255),
    role VARCHAR(255),
    est_actif tinyint(1), #boolean
    PRIMARY KEY (id_utilisateur)
) ENGINE = InnoDB DEFAULT CHARSET utf8mb4;

CREATE TABLE etat(
    id_etat INT AUTO_INCREMENT,
    libelle_etat VARCHAR(255),
    PRIMARY KEY (id_etat)
);

CREATE TABLE commande(
    id_commande INT AUTO_INCREMENT,
    date_achat DATE,
    utilisateur_id INT,
    etat_id INT,
    PRIMARY KEY (id_commande),
    CONSTRAINT fk_utilisateur_commande FOREIGN KEY (utilisateur_id) REFERENCES utilisateur(id_utilisateur),
    CONSTRAINT fk_etat FOREIGN KEY  (etat_id) REFERENCES etat(id_etat)
);

CREATE TABLE taille(
    id_taille INT AUTO_INCREMENT,
    libelle_taille VARCHAR(255),
    PRIMARY KEY (id_taille)
);

CREATE TABLE type_vetement(
    id_type_vetement INT AUTO_INCREMENT,
    libelle_type_vetement VARCHAR(255),
    PRIMARY KEY (id_type_vetement)
);

CREATE TABLE couleur(
    id_couleur INT AUTO_INCREMENT,
    libelle_couleur VARCHAR(255),
    PRIMARY KEY (id_couleur)
);

CREATE TABLE vetement(
    id_vetement INT AUTO_INCREMENT,
    designation VARCHAR(255),
    prix NUMERIC(7,2),
    fournisseur VARCHAR(255),
    image VARCHAR(255),
    marque VARCHAR(255),
    quantite INT,
    couleur_id INT,
    taille_id INT,
    type_vetement_id INT,
    PRIMARY KEY (id_vetement),
    CONSTRAINT fk_couleur FOREIGN KEY (couleur_id) REFERENCES couleur(id_couleur),
    CONSTRAINT fk_taille FOREIGN KEY (taille_id) REFERENCES taille(id_taille),
    CONSTRAINT fk_type_vetement FOREIGN KEY (type_vetement_id) REFERENCES type_vetement(id_type_vetement)
);
# ajout stocks

CREATE TABLE ligne_commande(
    commande_id INT,
    vetement_id INT,
    prix NUMERIC(7,2),
    quantite INT,
    PRIMARY KEY (commande_id, vetement_id),
    CONSTRAINT fk_vetement_commande FOREIGN KEY (vetement_id) REFERENCES vetement(id_vetement),
    CONSTRAINT  fk_commande FOREIGN KEY (commande_id) REFERENCES commande(id_commande)
);

CREATE TABLE ligne_panier(
    utilisateur_id INT,
    vetement_id INT,
    quantite INT,
    prix NUMERIC(7,2),
    date_ajout DATE,
    PRIMARY KEY (utilisateur_id, vetement_id),
    CONSTRAINT fk_utilisateur_panier FOREIGN KEY (utilisateur_id) REFERENCES utilisateur(id_utilisateur),
    CONSTRAINT fk_vetement_panier FOREIGN KEY (vetement_id) REFERENCES vetement(id_vetement)
);

# table panier à faire pour une sauvegarde permanente
# table facturation à faire

# Insert

INSERT INTO utilisateur(id_utilisateur,login,email,password,role,nom,est_actif) VALUES
(1,'admin','admin@admin.fr',
    'sha256$dPL3oH9ug1wjJqva$2b341da75a4257607c841eb0dbbacb76e780f4015f0499bb1a164de2a893fdbf',
    'ROLE_admin','admin','1'),
(2,'client','client@client.fr',
    'sha256$1GAmexw1DkXqlTKK$31d359e9adeea1154f24491edaa55000ee248f290b49b7420ced542c1bf4cf7d',
    'ROLE_client','client','1'),
(3,'client2','client2@client2.fr',
    'sha256$MjhdGuDELhI82lKY$2161be4a68a9f236a27781a7f981a531d11fdc50e4112d912a7754de2dfa0422',
    'ROLE_client','client2','1'),
(4, 'Romain', 'romain.meyer.fkpt@gmail.com',
    'sha256$fNr1sj4gBPxAlnpI$5b0242df0c3559cb66c1d29ec72bc9ead6f13a32fdd9cac7216761123dbf3e10',
    'ROLE_client', 'client3', '1');

INSERT INTO etat(id_etat, libelle_etat) VALUES
(1,'en attente'),
(2,'expédié'),
(3,'validé'),
(4,'confirmé');

INSERT INTO commande(id_commande, date_achat, utilisateur_id, etat_id) VALUES
(1,'2023-01-07', 1, 3),
(2,'2023-01-19', 1, 1),
(3,'2023-01-07', 2, 2),
(4,'2023-01-19', 2, 1),
(5,'2023-01-07', 3, 4);

INSERT INTO taille(id_taille, libelle_taille) VALUES
(1, 'taille unique'),
(2, 'XS'),
(3, 'S'),
(4, 'M'),
(5, 'XL');

INSERT INTO type_vetement(id_type_vetement, libelle_type_vetement) VALUES
(1, 'T-shirt'),
(2, 'Pull'),
(3, 'Sweatshirt'),
(4, 'Pantalon'),
(5, 'Jogging'),
(6, 'Robe'),
(7, 'Jeans'),
(8, 'Veste'),
(9, 'Top');

INSERT INTO couleur(id_couleur, libelle_couleur) VALUES
(1, 'rouge'),
(2, 'blanc'),
(3, 'vert'),
(4, 'marron'),
(5, 'noir'),
(6, 'bleu'),
(7, 'gris'),
(8, 'multicolore'),
(9, 'beige'),
(10, 'rose'),
(11, 'militaire'),
(12, 'orange');

INSERT INTO vetement(id_vetement, designation, prix, fournisseur, image, marque, quantite, couleur_id, taille_id, type_vetement_id) VALUES
(1, 'T-shirt mixte en coton', 75, 'Buchy', 'tshirt_blanc.jpg', 'Le slip français', 10, 2, 2, 1),
(2, 'T-shirt mixte en coton', 75, 'Buchy', 'tshirt_blanc.jpg', 'Nike', 8, 2, 3, 1),
(3, 'T-shirt en coton à col montant et imprimé lapin', 450, 'Italie', 'tshirt_lapin.jpg', 'Gucci', 5, 8, 4, 1),
(4, 'Pull mixte camionneur', 180, 'Roanne', 'pull_marine.jpg', 'Le slip français', 6, 6, 1, 2),
(5, 'Nike Sportswear Phoenix Fleece', 79.99, 'Chine', 'pantalon_beige.jpg', 'Nike', 3, 9, 5, 4),
(6, 'Jogging mixte élastiqué en molleton', 100, 'France', 'jogging_gris.jpg', 'Le slip français', 10, 7, 1, 5),
(7, 'Hoodie oversize imprimé', 29.99, 'Chine', 'sweatshirt_beige.jpeg', 'H&M', 13, 9, 5, 3),
(8, 'Robe à paillettes avec franges', 59.99, 'Chine', 'robe_rose.jpg', 'H&M', 2, 10, 2, 6),
(9, 'Pantalon en organza de soie avec plumes', 12500, 'Afrique du sud', 'pantalon_vert.jpg', 'Gucci', 2, 3, 1, 4),
(10,'Pantalon cargo', 22, 'Chine', 'jeans_militaire.jpeg', 'Primark', 1, 11, 2, 7),
(11, 'Blouson aviateur en nylon matelassé adidas x Gucci', 2700, 'Italie', 'veste_vert.jpg', 'Gucci', 3, 3, 3, 8),
(12, 'Doudoune à capuche', 39.99, 'Chine', 'veste_rouge.jpg', 'H&M', 7, 1, 1, 8),
(13, 'Pull avec col', 19.99, 'Chine', 'pull_marron.jpg', 'H&M', 1, 4, 4, 2),
(14, 'Top bustier', 14.99, 'Chine', 'top_noir.jpg', 'H&M', 0, 5, 5, 9),
(15, 'Pantalon habillé', 29.99, 'Chine', 'pantalon_orange.jpg', 'H&M', 1, 12, 4, 4);

INSERT INTO ligne_commande(commande_id, vetement_id, prix, quantite) VALUES
(1, 11, 5400, 2),
(2, 15, 179.94, 6),
(3, 9, 12500, 1),
(4, 11, 5400, 2),
(5, 6, 300, 6);

INSERT INTO ligne_panier(utilisateur_id, vetement_id, quantite, prix, date_ajout) VALUES
(1, 13, 2, 39.9, '2023-01-19'),
(1, 2, 2, 150, '2023-01-19'),
(2, 8, 1, 59.99, '2023-01-20'),
(2, 4, 4, 720, '2023-01-19'),
(3, 7, 3, 89.97, '2023-01-19');

# Verif table

DESCRIBE utilisateur;
DESCRIBE etat;
DESCRIBE commande;
DESCRIBE taille;
DESCRIBE type_vetement;
DESCRIBE couleur;
DESCRIBE vetement;
DESCRIBE ligne_commande;
DESCRIBE ligne_panier;

# Verif contenus table

SELECT * FROM utilisateur;
SELECT * FROM etat;
SELECT * FROM commande;
SELECT * FROM taille;
SELECT * FROM type_vetement;
SELECT * FROM couleur;
SELECT * FROM vetement;
SELECT * FROM ligne_commande;
SELECT * FROM ligne_panier;
