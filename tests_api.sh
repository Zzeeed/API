#!/bin/bash
# Tests de l'API REST de la vidéothèque avec curl

API=${1:-http://localhost:5001}

echo "== GET /films : liste complète"
curl -s -w "\nCode HTTP : %{http_code}\n\n" $API/films

echo "== GET /films?genre=Policier : recherche par genre"
curl -s -w "\nCode HTTP : %{http_code}\n\n" "$API/films?genre=Policier"

echo "== GET /films?titre=blade : recherche par titre"
curl -s -w "\nCode HTTP : %{http_code}\n\n" "$API/films?titre=blade"

echo "== GET /films/3 : détail d'un film"
curl -s -w "\nCode HTTP : %{http_code}\n\n" $API/films/3

echo "== GET /films/99 : film inexistant (404 attendu)"
curl -s -w "\nCode HTTP : %{http_code}\n\n" $API/films/99

echo "== POST /films : ajout d'un film (201 attendu)"
curl -s -w "\nCode HTTP : %{http_code}\n\n" -X POST -H "Content-Type: application/json" \
  -d '{"titre": "Dune", "realisateur": "Denis Villeneuve", "annee": 2021, "genre": "Science-fiction", "duree": 155, "support": "Numérique"}' \
  $API/films

echo "== POST /films : titre manquant (400 attendu)"
curl -s -w "\nCode HTTP : %{http_code}\n\n" -X POST -H "Content-Type: application/json" \
  -d '{"realisateur": "Inconnu", "annee": 2021, "genre": "Drame", "support": "DVD"}' \
  $API/films

echo "== PUT /films/6 : modification du film ajouté"
curl -s -w "\nCode HTTP : %{http_code}\n\n" -X PUT -H "Content-Type: application/json" \
  -d '{"titre": "Dune : Première partie", "realisateur": "Denis Villeneuve", "annee": 2021, "genre": "Science-fiction", "duree": 155, "support": "Blu-ray"}' \
  $API/films/6

echo "== DELETE /films/6 : suppression du film ajouté"
curl -s -w "\nCode HTTP : %{http_code}\n\n" -X DELETE $API/films/6

echo "== DELETE /films/6 : déjà supprimé (404 attendu)"
curl -s -w "\nCode HTTP : %{http_code}\n\n" -X DELETE $API/films/6
