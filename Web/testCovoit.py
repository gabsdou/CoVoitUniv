
from models import AddressCache, db
import polyline
import requests





def geocode_address(address):
    url = f'https://api-adresse.data.gouv.fr/search/?q={address}&limit=1'


    cached_entry = AddressCache.query.filter_by(address=address).first()
    if cached_entry:
        print(f"Cache hit for address: {address}")
        return (cached_entry.lat, cached_entry.lon)

    print(f"Cache miss for address: {address}. Calling Nominatim API...")
 
    response = requests.get(url)
     # Vérifier si la réponse est valide et contient des données
    if response.status_code == 200:
        data = response.json()
        if data:
            coords = data["features"][0]["geometry"]["coordinates"]
            lat = coords[1]
            lon = coords[0]
            
            # Vérifier si lat et lon sont valides (pas de None ou 'undefined')
            if lat is not None and lon is not None:
                try:
                    lat = float(lat)
                    lon = float(lon)
                    
                    # Vérifier que ce sont bien des nombres avant de les arrondir
                    if isinstance(lat, (int, float)) and isinstance(lon, (int, float)):
                        lat = round(lat, 6)
                        lon = round(lon, 6)
                        new_entry = AddressCache(address=address, lat=lat, lon=lon)
                        db.session.add(new_entry)
                        db.session.commit()
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
        coords_list = [start_coords, end_coords]
        return {
            "label": label,
            "distance": route["distance"] / 1000,  # En km
            "duration": route["duration"] / 60,   # En minutes
            "geometry": coords_list
        }
    return None


def replace_placeholders(obj, user_address):
    """
    Recursively traverse 'obj' (which can be dict, list, or string)
    and replace certain placeholder words with full addresses.
    In particular, if we encounter 'maison', replace it with 'user_address'.

    Returns the updated object.
    """
    # Define your placeholders -> real addresses
    replacements = {
        "Villetaneuse": "99 Av. Jean Baptiste Clément, 93430 Villetaneuse",
        "Bobigny": "74 Rue Marcel Cachin, 93000 Bobigny",
        "Saint-Denis": "Place du 8 Mai 1945, 93200, Saint-Denis",

        # Now "maison" points to this user's address
        "Maison": user_address
    }

    if isinstance(obj, dict):
        # Recurse into each key/value
        for key, value in obj.items():
            obj[key] = replace_placeholders(value, user_address)
        return obj

    elif isinstance(obj, list):
        # Recurse into each element
        for i in range(len(obj)):
            obj[i] = replace_placeholders(obj[i], user_address)
        return obj

    elif isinstance(obj, str):
        # Perform string replacements for each placeholder
        for placeholder, full_address in replacements.items():
            obj = obj.replace(placeholder, full_address)
        return obj

    else:
        # If it's an int, float, bool, or None, just return as is
        return obj


    
