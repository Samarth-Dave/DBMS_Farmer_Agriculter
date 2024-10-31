import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key")
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:saur2005@127.0.0.1/FarmerAgriculture'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False