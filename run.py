import os

from app import create_app

app = create_app()

if __name__ == '__main__':
    cert = os.path.join('certs', 'cert.pem')
    key = os.path.join('certs', 'key.pem')

    if os.path.exists(cert) and os.path.exists(key):
        # Production Raspberry Pi : HTTPS avec certificat auto-signé
        # Flask/Werkzeug HTTPS avec threads — adapté pour 30 clients en LAN
        print('Démarrage HTTPS sur https://0.0.0.0:5443')
        print('Accès tablettes : https://<ip-du-pi>:5443')
        app.run(
            host='0.0.0.0',
            port=5443,
            ssl_context=(cert, key),
            debug=False,
            threaded=True,
        )
    else:
        # Développement : HTTP via Waitress
        print('⚠  Certs TLS absents — démarrage en HTTP (développement uniquement)')
        print('   Accès : http://127.0.0.1:5000')
        from waitress import serve
        serve(app, host='0.0.0.0', port=5000)

