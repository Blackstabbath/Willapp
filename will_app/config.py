import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///will_app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # File paths
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'storage/generated_documents')
    EXCEL_FOLDER = os.path.join(BASE_DIR, 'storage/excel_logs')
    TEMPLATE_FOLDER = os.path.join(BASE_DIR, 'storage/templates')
    
    @staticmethod
    def ensure_directories():
        directories = [
            Config.UPLOAD_FOLDER,
            Config.EXCEL_FOLDER, 
            Config.TEMPLATE_FOLDER
        ]
        for directory in directories:
            os.makedirs(directory, exist_ok=True)

Config.ensure_directories()