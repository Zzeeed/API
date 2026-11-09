import json
import threading
from flask import Flask, jsonify, request

app = Flask(__name__)
app.json.ensure_ascii = False  # pour garder les accents dans les réponses

FICHIER = "data/videotheque.json"
SUPPORTS = ["DVD", "Blu-ray", "Numérique"]
verrou = threading.Lock()  # une seule écriture à la fois dans le fichier


def lire():
    with open(FICHIER, encoding="utf-8") as f:
        return json.load(f)


def ecrire(videotheque):
    with open(FICHIER, "w", encoding="utf-8") as f:
        json.dump(videotheque, f, ensure_ascii=False, indent=2)


def chercher(films, id_film):
    for film in films:
        if film["id"] == id_film:
            return film
    return None


def est_valide(film):
    if film is None:
        return False
    for champ in ["titre", "realisateur", "annee", "genre", "support"]:
        if not film.get(champ):
            return False
    return isinstance(film["annee"], int) and film["support"] in SUPPORTS


def erreur(message, code):
    return jsonify({"succes": False, "message": message}), code


@app.route("/films", methods=["GET"])
def lister_films():
    films = lire()["films"]

    titre = request.args.get("titre")
    genre = request.args.get("genre")
    support = request.args.get("support")

    if titre:
        films = [f for f in films if titre.lower() in f["titre"].lower()]
    if genre:
        films = [f for f in films if f["genre"] == genre]
    if support:
        films = [f for f in films if f["support"] == support]

    return jsonify({"nombre": len(films), "films": films})


@app.route("/films/<int:id_film>", methods=["GET"])
def lire_film(id_film):
    film = chercher(lire()["films"], id_film)
    if film is None:
        return erreur("Film introuvable", 404)
    return jsonify(film)


@app.route("/films", methods=["POST"])
def ajouter_film():
    film = request.get_json(silent=True)
    if not est_valide(film):
        return erreur("Données invalides", 400)

    with verrou:
        videotheque = lire()
        # nouvel id = plus grand id existant + 1
        nouvel_id = 1
        for f in videotheque["films"]:
            if f["id"] >= nouvel_id:
                nouvel_id = f["id"] + 1
        film["id"] = nouvel_id
        videotheque["films"].append(film)
        ecrire(videotheque)

    return jsonify(film), 201


@app.route("/films/<int:id_film>", methods=["PUT"])
def modifier_film(id_film):
    nouveau = request.get_json(silent=True)
    if not est_valide(nouveau):
        return erreur("Données invalides", 400)

    with verrou:
        videotheque = lire()
        film = chercher(videotheque["films"], id_film)
        if film is None:
            return erreur("Film introuvable", 404)
        film.update(nouveau)
        film["id"] = id_film  # l'id ne change jamais
        ecrire(videotheque)

    return jsonify(film)


@app.route("/films/<int:id_film>", methods=["DELETE"])
def supprimer_film(id_film):
    with verrou:
        videotheque = lire()
        film = chercher(videotheque["films"], id_film)
        if film is None:
            return erreur("Film introuvable", 404)
        videotheque["films"].remove(film)
        ecrire(videotheque)

    return jsonify({"succes": True, "message": f"Film {id_film} supprimé"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
