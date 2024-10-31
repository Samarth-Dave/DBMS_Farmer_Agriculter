# models.py
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class FarmerProfile(db.Model):
    __tablename__ = 'FarmerProfile'
    FarmerId = db.Column(db.Integer, primary_key=True)
    FirstName = db.Column(db.String(50))
    MiddleName = db.Column(db.String(50))
    LastName = db.Column(db.String(50))
    PhoneNumber = db.Column(db.String(15))
    Location = db.Column(db.String(100))
    LandArea = db.Column(db.Float)
    PasswordHash = db.Column(db.String(128), nullable=False) 

class CropInfo(db.Model):
    __tablename__ = 'CropInfo'
    CropId = db.Column(db.Integer, primary_key=True)
    CropName = db.Column(db.String(50))
    PlantingDate = db.Column(db.Date)
    HarvestDate = db.Column(db.Date)
    EstimatedYield = db.Column(db.Float)
    Status = db.Column(db.String(20), nullable=False)

class Grows(db.Model):
    __tablename__ = 'Grows'
    FarmerId = db.Column(db.Integer, db.ForeignKey('FarmerProfile.FarmerId'), primary_key=True)
    CropId = db.Column(db.Integer, db.ForeignKey('CropInfo.CropId'), primary_key=True)

class FertilizerPesticide(db.Model):
    __tablename__ = 'FertilizerPesticide'
    ProductId = db.Column(db.Integer, primary_key=True)
    ProductName = db.Column(db.String(50))
    Type = db.Column(db.Enum('Fertilizer', 'Pesticide'))
    QuantityUsed = db.Column(db.Float)
    Cost = db.Column(db.Float)

class ManageCrop(db.Model):
    __tablename__ = 'ManageCrop'
    CropId = db.Column(db.Integer, db.ForeignKey('CropInfo.CropId'), primary_key=True)
    ProductId = db.Column(db.Integer, db.ForeignKey('FertilizerPesticide.ProductId'), primary_key=True)

class Sales(db.Model):
    __tablename__ = 'Sales'
    SaleId = db.Column(db.Integer, primary_key=True)
    DateOfSale = db.Column(db.Date)
    PricePerUnit = db.Column(db.Float)
    QuantitySold = db.Column(db.Float)
    Earnings = db.Column(db.Float)
    CropId = db.Column(db.Integer, db.ForeignKey('CropInfo.CropId'))
    FarmerId = db.Column(db.Integer, db.ForeignKey('FarmerProfile.FarmerId'))
