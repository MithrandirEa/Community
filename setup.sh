#!/usr/bin/env bash
# =============================================================================
# setup.sh — Initialisation de Community sur Raspberry Pi (Raspberry Pi OS / Debian)
# À exécuter une seule fois depuis le répertoire du projet
# Usage : bash setup.sh
# =============================================================================
set -e

CERT_DIR="certs"
VENV_DIR=".venv"

echo "=== Community — Setup ==="

# --- Environnement virtuel ---
if [ ! -d "$VENV_DIR" ]; then
    echo "[1/5] Création de l'environnement virtuel Python..."
    python3 -m venv "$VENV_DIR"
else
    echo "[1/5] Environnement virtuel existant — ignoré."
fi

# --- Dépendances ---
echo "[2/5] Installation des dépendances..."
"$VENV_DIR/bin/pip" install --upgrade pip --quiet
"$VENV_DIR/bin/pip" install -r requirements.txt --quiet

# --- Certificat TLS auto-signé ---
if [ ! -f "$CERT_DIR/cert.pem" ] || [ ! -f "$CERT_DIR/key.pem" ]; then
    echo "[3/5] Génération du certificat TLS auto-signé..."
    mkdir -p "$CERT_DIR"
    openssl req -x509 -newkey rsa:4096 -sha256 -days 3650 \
        -nodes \
        -keyout "$CERT_DIR/key.pem" \
        -out    "$CERT_DIR/cert.pem" \
        -subj   "/CN=community.local/O=Les Petits Debrouillards/C=FR" \
        -addext "subjectAltName=IP:0.0.0.0" \
        2>/dev/null
    echo "    Certificat généré dans : $CERT_DIR/"
else
    echo "[3/5] Certificat existant — ignoré."
fi

# --- Dossiers statiques ---
echo "[4/5] Création des dossiers nécessaires..."
mkdir -p instance app/static/photos app/static/js

# --- Vérification HTMX (embarqué — NE PAS télécharger) ---
echo "[4/5] Vérification de HTMX local..."
if [ ! -f "app/static/js/htmx.min.js" ]; then
    echo ""
    echo "  ERREUR : app/static/js/htmx.min.js est absent."
    echo "  Ce fichier doit être présent dans le dépôt git."
    echo "  Il ne peut pas être téléchargé (pas d'internet requis)."
    echo "  Vérifiez que vous avez bien cloné/copié l'intégralité du projet."
    echo ""
    exit 1
else
    echo "    HTMX présent ($(du -k app/static/js/htmx.min.js | cut -f1) Ko) — OK"
fi

# --- Initialisation de la base de données ---
echo "[5/5] Initialisation de la base de données..."
"$VENV_DIR/bin/python" -c "from app import create_app; create_app()"

echo ""
echo "=== Setup terminé ==="
echo ""
echo "Pour démarrer l'application :"
echo "  source $VENV_DIR/bin/activate"
echo "  python run.py"
echo ""
echo "Accès depuis les tablettes (remplacez <IP> par l'IP du Raspberry Pi) :"
echo "  https://<IP>:5443"
echo ""
echo "Codes par défaut :"
echo "  Cellule de crise : MAIRIE2026"
echo "  Population       : CITOYEN2026"
echo "  Animateur        : ADMIN2026"
echo ""
echo "IMPORTANT : Le certificat TLS est auto-signé."
echo "Les tablettes afficheront un avertissement de sécurité."
echo "Appuyer sur 'Avancé' puis 'Continuer' pour accepter."
