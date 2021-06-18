from flask import Flask, request, redirect, url_for, render_template, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_mail import Mail, Message
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
mail = Mail()

db = SQLAlchemy(app)

mail.init_app(app)

class Annuaire(db.Model):
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    prenom = db.Column(db.String(100))
    nom = db.Column(db.String(100))
    region = db.Column(db.String(100))
    departement = db.Column(db.String(100))
    adresse = db.Column(db.String(100))
    commune = db.Column(db.String(100))
    code_postal = db.Column(db.String(5))
    email = db.Column(db.String(100), unique=True)
    telephone_fixe = db.Column(db.String(10))
    telephone_port = db.Column(db.String(10))
    reseau = db.Column(db.String(100))
    structure = db.Column(db.String(100))
    fonction = db.Column(db.String(100))
    lat = db.Column(db.Float)
    long = db.Column(db.Float)
    sites = db.relationship('Site', backref='annuaire', lazy=True)
    expertises = db.relationship('Expertise', backref='annuaire', lazy=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    active = db.Column(db.Boolean, server_default=u'false')

class Site(db.Model):
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    nom = db.Column(db.String(100))
    type_site = db.Column(db.String(100))
    adresse = db.Column(db.String(255))
    annuaire_id = db.Column(db.Integer, db.ForeignKey('annuaire.id'),
        nullable=False)

class Expertise(db.Model):
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    nom = db.Column(db.String(100))
    annuaire_id = db.Column(db.Integer, db.ForeignKey('annuaire.id'),
        nullable=False)

@app.route("/")
def index():
    contacts = Annuaire.query.filter(Annuaire.active.is_(True)).all()
    return render_template('index.html', contacts=contacts)

@app.route('/annuaire')
def annuaire():
    annuaire = Annuaire.query.filter(Annuaire.active.is_(True)).all()
    return render_template('annuaire.html', annuaire=annuaire)

@app.route('/fiche/<id>')
def fiche(id):
    personne = Annuaire.query.filter_by(id=id).first()
    expertises = personne.expertises
    sites = personne.sites
    return render_template('fiche.html', personne=personne, sites=sites, expertises=expertises)

@app.route('/cartographie')
def cartographie():
    contacts = Annuaire.query.filter(Annuaire.active.is_(True)).all()
    return render_template('cartographie.html', contacts=contacts)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        subject = "Message de %s sur l'annuaire de géologie" % (request.form.get('nom'))
        body = "<p><b>Nom :</b> %s<br><b>Sujet :</b> %s<br><b>Mail :</b> %s</p><p><b>Contenu :</b> %s</p>" % (request.form.get('nom'), request.form.get('sujet'), request.form.get('email'),request.form.get('message'))
        msg = Message(subject = subject,
                sender = request.form.get('email'),
                recipients = ['zacharie.moulin-rnf@espaces-naturels.fr'],
                html = body
        )
        mail.send(msg)
        flash(u'Votre message a bien été envoyé aux administrateurs.', 'success')
        return redirect(url_for('index'))
    else:
        return render_template('contact.html')

@app.route('/ajout', methods=['GET', 'POST'])
def ajout():
    if request.method == 'POST':
        prenom = request.form.get('prenom') or None
        nom = request.form.get('nom') or None
        region = request.form.get('region')
        departement = request.form.get('departement')
        adresse = request.form.get('adresse') or None
        commune = request.form.get('commune') or None
        code_postal = request.form.get('code_postal') or None
        email = request.form.get('email') or None
        telephone_fixe = request.form.get('telephone_fixe') or None
        telephone_port = request.form.get('telephone_port') or None
        reseau = request.form.get('reseau')
        structure = request.form.get('structure') or None
        fonction = request.form.get('fonction') or None
        lat = request.form.get('lat') or None
        long = request.form.get('long') or None

        personne = Annuaire.query.filter_by(email=email).first() # if this returns a user, then the email already exists in database

        if personne: # if a user is found, we want to redirect back to signup page so user can try again
            flash(u'L\'e-mail de ce contact est déjà référencé', 'danger')
            return redirect(url_for('ajout'))

        annuaire = Annuaire(prenom = prenom, nom = nom, region = region, departement = departement, adresse = adresse, commune = commune, code_postal = code_postal, lat = lat, long = long, email = email, telephone_fixe = telephone_fixe, telephone_port = telephone_port, reseau = reseau, structure = structure, fonction = fonction, active=False)
        db.session.add(annuaire)
        personne = Annuaire.query.filter_by(nom=nom, prenom=prenom).first()
        nom_sites = request.form.getlist('nom_site[]')
        type_sites = request.form.getlist('type_site[]')
        adresse_sites = request.form.getlist('adresse_site[]')
        sites = list(zip(nom_sites, type_sites, adresse_sites))
        for (nom, type, adresse) in sites :
            if nom != '' :
                site = Site(nom=nom, type_site=type, adresse=adresse, annuaire_id=personne.id)
                db.session.add(site)
        expertises = request.form.getlist('expertise[]' or None)
        for expertise in expertises :
            if expertise != '' :
                expertise = Expertise(nom=expertise, annuaire_id=personne.id)
                db.session.add(expertise)
        msg = Message("Ajout d'un contact à l'annuaire partagé de géologie", sender = 'si-rnf@espaces-naturels.fr',
                recipients = ['si-rnf@espaces-naturels.fr'],
                body= "Le contact %s a été ajouté à l'annuaire." % prenom
        )
        mail.send(msg)
        db.session.commit()


        flash(u'Nouveau contact correctement ajouté. Il sera visible une fois validé par un modérateur.', 'success')
        return redirect(url_for('index'))
    else:
        return render_template('ajout.html')

if __name__ == '__main__':
      app.run(host='0.0.0.0', port=5020)
