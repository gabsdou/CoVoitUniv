from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import requests

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'  # Base de données SQLite
app.config['SECRET_KEY'] = 'your_secret_key'
db = SQLAlchemy(app)


# Modèle pour les utilisateurs
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    is_driver = db.Column(db.Boolean, default=False)


@app.route('/', methods=['GET', 'POST'])
def signup():
    """Page d'inscription avec formulaire."""
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        address = request.form['address']
        is_driver = True if request.form.get('is_driver') == 'on' else False

        # Ajouter l'utilisateur à la base de données
        new_user = User(first_name=first_name, last_name=last_name, address=address, is_driver=is_driver)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('user_profile', user_id=new_user.id))

    return render_template('testcovoit.html')

@app.route('/user/<int:user_id>', methods=['GET', 'POST'])
def user_profile(user_id):
    """Page de profil d'un utilisateur."""
    user = User.query.get_or_404(user_id)
    routes = []

    # Adresse fixe (hardcodée)
    hardcoded_address = "99 Av. Jean Baptiste Clément, 93430 Villetaneuse"
    hardcoded_coords = geocode_address(hardcoded_address)

    # Chercher tous les autres utilisateurs (en excluant l'utilisateur actuel)
    other_users = User.query.filter(User.id != user_id).all()

    for other_user in other_users:
        # Géocodage des adresses des utilisateurs
        user_coords = geocode_address(user.address)
        other_coords = geocode_address(other_user.address) if other_user else None
        
        # Calculer les trajets possibles
        if user_coords and other_coords and hardcoded_coords:
            routes.append({
                'name': other_user.first_name,
                'route': (other_coords),
            })

    return render_template('Conducteur.html', user=user, routes=routes)


def geocode_address(address):
    url = f'https://nominatim.openstreetmap.org/search?q={address}&format=json'
    headers = {
        'User-Agent': 'CovoitUnivTest/1.0 (timothee.mbassidje@edu.univ-paris13.fr)'
    }
    response = requests.get(url, headers=headers)
     # Vérifier si la réponse est valide et contient des données
    if response.status_code == 200:
        data = response.json()
        if data:
            lat = data[0].get('lat')
            lon = data[0].get('lon')
            
            # Vérifier si lat et lon sont valides (pas de None ou 'undefined')
            if lat is not None and lon is not None:
                try:
                    lat = float(lat)
                    lon = float(lon)
                    
                    # Vérifier que ce sont bien des nombres avant de les arrondir
                    if isinstance(lat, (int, float)) and isinstance(lon, (int, float)):
                        lat = round(lat, 6)
                        lon = round(lon, 6)
                        return lat, lon
                    else:
                        raise ValueError("Les coordonnées ne sont pas valides")
                except ValueError as e:
                    print(f"Erreur de conversion des coordonnées : {e}")
                    return None, None
            else:
                print("Les coordonnées de géolocalisation sont manquantes.")
                return None, None
        else:
            print("Aucune donnée retournée pour l'adresse.")
            return None, None
    else:
        print(f"Erreur lors de la récupération des données : {response.status_code}")
        return None, None

def get_route(start_coords, end_coords, label):
    """Obtenir un itinéraire entre deux points avec OSRM."""
    response = requests.get(
        f"http://router.project-osrm.org/route/v1/driving/{start_coords[1]},{start_coords[0]};{end_coords[1]},{end_coords[0]}",
        params={"overview": "full"}
    )
    data = response.json()
    if "routes" in data and data["routes"]:
        route = data["routes"][0]
        return {
            "label": label,
            "distance": route["distance"] / 1000,  # En km
            "duration": route["duration"] / 60,   # En minutes
            "geometry": route["geometry"]
        }
    return None


if __name__ == '__main__':
    with app.app_context():  # Crée un contexte de l'application
        db.create_all()  # Crée la base de données si elle n'existe pas encore
    app.run(debug=True)
