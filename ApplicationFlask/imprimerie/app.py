from flask import Flask, redirect, url_for, flash, render_template_string
from config import DevelopmentConfig


def create_app():
    app = Flask(__name__)
    app.config.from_object(DevelopmentConfig)

    from routes.main import main_bp
    from db import DatabaseError
    app.register_blueprint(main_bp)

    @app.route('/')
    def index():
        return redirect(url_for('main.tableau_bord'))

    # =========================================
    # GESTIONNAIRE D'ERREURS GLOBAL
    # =========================================

    @app.errorhandler(DatabaseError)
    def handle_database_error(e):
        """Capture toutes les erreurs DatabaseError."""
        flash(str(e), "danger")
        return redirect(url_for('main.tableau_bord'))

    @app.errorhandler(Exception)
    def handle_generic_error(e):
        """Capture toutes les autres erreurs."""
        app.logger.error(f"Erreur inattendue: {e}")
        flash("Une erreur inattendue s'est produite.", "danger")
        return redirect(url_for('main.tableau_bord'))

    return app


if __name__ == '__main__':
    app = create_app()
    print("\n" + "=" * 50)
    print("IMPRIMERIE MOSAÏQUE")
    print("=" * 50)
    print("Ouvrir dans le navigateur:")
    print("http://localhost:5000")
    print("=" * 50)
    print("Pour fermer: Ctrl+C")
    print("=" * 50 + "\n")
    app.run(debug=False, host='0.0.0.0', port=5000) #Mettre debug=True pour afficher l'erreur complète (en mode développement) sinon debug=False
