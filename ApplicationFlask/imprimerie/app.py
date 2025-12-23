from flask import Flask, redirect, url_for
from config import DevelopmentConfig

def create_app():
    app = Flask(__name__)
    app.config.from_object(DevelopmentConfig)
    
    from routes.main import main_bp
    app.register_blueprint(main_bp)
    
    @app.route('/')
    def index():
        return redirect(url_for('main.tableau_bord'))
    
    return app

if __name__ == '__main__':
    app = create_app()
    print("\n" + "="*50)
    print("IMPRIMERIE MOSAÏQUE")
    print("="*50)
    print("http://localhost:5000")
    print("="*50 + "\n")
    app.run(debug=True, host='0.0.0.0', port=5000)
