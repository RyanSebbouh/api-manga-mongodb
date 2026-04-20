from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson import ObjectId

app = Flask(__name__)

client = MongoClient("mongodb://localhost:27017/")
db = client["manga_db"]

def seed():
    if db.mangas.count_documents({}) == 0:
        db.mangas.insert_many([
            {"titre": "Naruto",          "auteur": "Masashi Kishimoto", "genre": "action",   "note": 9, "description": "Un ninja qui veut devenir Hokage"},
            {"titre": "One Piece",        "auteur": "Eiichiro Oda",      "genre": "aventure", "note": 10, "description": "Un pirate à la recherche du trésor ultime"},
            {"titre": "Death Note",       "auteur": "Tsugumi Ohba",      "genre": "thriller", "note": 9, "description": "Un carnet qui tue quiconque dont on écrit le nom"},
            {"titre": "Attack on Titan",  "auteur": "Hajime Isayama",    "genre": "action",   "note": 10, "description": "L'humanité survit derrière des murs face aux titans"},
            {"titre": "Demon Slayer",     "auteur": "Koyoharu Gotouge",  "genre": "action",   "note": 8,  "description": "Un jeune garçon combat des démons pour sauver sa sœur"},
            {"titre": "Tokyo Ghoul",      "auteur": "Sui Ishida",        "genre": "thriller", "note": 8,  "description": "Un étudiant devient mi-humain mi-goule"},
            {"titre": "My Hero Academia", "auteur": "Kohei Horikoshi",   "genre": "action",   "note": 8,  "description": "Dans un monde de super-héros, un garçon sans pouvoir rêve de devenir le meilleur"},
            {"titre": "Fullmetal Alchemist", "auteur": "Hiromu Arakawa", "genre": "aventure", "note": 10, "description": "Deux frères alchimistes cherchent la pierre philosophale"},
            {"titre": "Bleach",           "auteur": "Tite Kubo",         "genre": "action",   "note": 7,  "description": "Un lycéen devient un shinigami pour protéger les vivants et les morts"},
            {"titre": "Dragon Ball",      "auteur": "Akira Toriyama",     "genre": "action",   "note": 9,  "description": "Un garçon aux pouvoirs extraordinaires cherche les boules de cristal"},
            {"titre": "One Punch Man",    "auteur": "ONE",               "genre": "action",   "note": 8,  "description": "Un homme ordinaire devient un super-héros avec un seul coup"},
            {"titre": "Fairy Tail",       "auteur": "Hiro Mashima",      "genre": "aventure", "note": 7,  "description": "Une guilde de magiciens vit des aventures fantastiques"},
             
        ])
        print("Mangas insérés")

seed()


def format_doc(doc):
    doc["_id"] = str(doc["_id"])
    return doc


@app.route("/items", methods=["POST"])
def create_manga():
    data = request.json
    if not data or "titre" not in data or "auteur" not in data:
        return jsonify({"erreur": "Les champs 'titre' et 'auteur' sont obligatoires"}), 400
    result = db.mangas.insert_one(data)
    return jsonify({"message": "Manga créé", "id": str(result.inserted_id)}), 201


@app.route("/items", methods=["GET"])
def get_mangas():
    page  = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 12))
    skip  = (page - 1) * limit
    mangas = list(db.mangas.find().skip(skip).limit(limit))
    return jsonify([format_doc(m) for m in mangas])


@app.route("/items/<id>", methods=["GET"])
def get_manga(id):
    try:
        manga = db.mangas.find_one({"_id": ObjectId(id)})
    except Exception:
        return jsonify({"erreur": "ID invalide"}), 400
    if not manga:
        return jsonify({"erreur": "Manga introuvable"}), 404
    return jsonify(format_doc(manga))


@app.route("/search", methods=["GET"])
def search_manga():
    keyword  = request.args.get("keyword", "")
    genre    = request.args.get("genre", "")
    note_min = request.args.get("note_min", None)

    query = {}

    if keyword:
        query["$or"] = [
            {"titre":       {"$regex": keyword, "$options": "i"}},
            {"description": {"$regex": keyword, "$options": "i"}}
        ]

    if genre:
        query["genre"] = {"$regex": genre, "$options": "i"}

    if note_min:
        query["note"] = {"$gte": int(note_min)}

    resultats = list(db.mangas.find(query))
    if not resultats:
        return jsonify({"message": "Aucun résultat"}), 404
    return jsonify([format_doc(m) for m in resultats])


if __name__ == "__main__":
    app.run(debug=True)
