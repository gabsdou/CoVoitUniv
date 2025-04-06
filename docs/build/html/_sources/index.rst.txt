.. CovoitUniv documentation master file, created by
   sphinx-quickstart on Sun Apr  6 20:16:14 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

CovoitUniv documentation
========================

Introduction
------------
Bienvenue dans la documentation technique de **CoVoitUniv**, une application de covoiturage développée avec Flask et SQLAlchemy. Ce document présente l’architecture, les modules, ainsi que les étapes d’installation et d’utilisation de l’application.


Présentation du Projet
----------------------
**CovoitUniv** permet aux utilisateurs de :
- S'inscrire et se connecter.
- Gérer leur calendrier de trajets.
- Créer et mettre à jour des demandes de covoiturage.
- Rechercher et offrir des trajets.

L'application repose sur plusieurs composants :
- **Flask** pour le backend.
- **SQLAlchemy** pour la gestion de la base de données.
- Des API externes pour le géocodage et le calcul d’itinéraires.
- Un système de cache pour accélérer le géocodage d'adresses.

Usage
-----
Pour démarrer l’application, exécutez :

.. code-block:: bash

   python manageReact.py

L’interface web sera accessible à l’adresse :  
   http://localhost:5000

Architecture
------------
L'architecture du projet se compose principalement de :

- **manageReact.py** : Le point d'entrée de l'API Flask.
- **models.py** : Définit les modèles de données (User, RideRequest, DriverOffer, CalendarEntry, etc.) avec SQLAlchemy.
- **utils.py** : Contient des fonctions utilitaires (géocodage, calcul d'itinéraires, etc.).
- **pingMail.py** : Gère l’envoi d’e-mails pour notifier les utilisateurs.

Modules
-------
La documentation détaillée des modules est générée automatiquement à partir des docstrings en utilisant l'extension autodoc de Sphinx.

.. automodule:: manageReact
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: models
   :members:
   :undoc-members:
   :show-inheritance:


.. toctree::
   :maxdepth: 2
   :caption: Sommaire:

.. MonProjet documentation master file

Indices and tables
==================
* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
