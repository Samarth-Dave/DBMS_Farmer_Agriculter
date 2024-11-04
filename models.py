# models.py
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class FarmerProfile(db.Model):
    __tablename__ = 'FarmerProfile'
    FarmerId = db.Column(db.Integer, primary_key=True)
    FirstName = db.Column(db.String(50))
    MiddleName = db.Column(db.String(50))
    LastName = db.Column(db.String(50))
    PhoneNumber = db.Column(db.String(15), unique=True, nullable=False)
    Location = db.Column(db.String(100))
    LandArea = db.Column(db.Float)
    PasswordHash = db.Column(db.String(128), nullable=False)

    # Relationships
    crops = db.relationship('Grows', back_populates='farmer', cascade='all, delete')
    sales = db.relationship('Sales', back_populates='farmer', cascade='all, delete')


class CropInfo(db.Model):
    __tablename__ = 'CropInfo'
    CropId = db.Column(db.Integer, primary_key=True)
    CropName = db.Column(db.String(50))
    PlantingDate = db.Column(db.Date)
    HarvestDate = db.Column(db.Date)
    EstimatedYield = db.Column(db.Float)
    Status = db.Column(db.String(20), nullable=False)

    # Relationships
    grows = db.relationship('Grows', back_populates='crop', cascade='all, delete')
    sales = db.relationship('Sales', back_populates='crop', cascade='all, delete')
    managed_products = db.relationship('ManageCrop', back_populates='crop', cascade='all, delete')


class Grows(db.Model):
    __tablename__ = 'Grows'
    FarmerId = db.Column(db.Integer, db.ForeignKey('FarmerProfile.FarmerId'), primary_key=True)
    CropId = db.Column(db.Integer, db.ForeignKey('CropInfo.CropId'), primary_key=True)

    # Relationships
    farmer = db.relationship('FarmerProfile', back_populates='crops')
    crop = db.relationship('CropInfo', back_populates='grows')


class FertilizerPesticide(db.Model):
    __tablename__ = 'FertilizerPesticide'
    ProductId = db.Column(db.Integer, primary_key=True)
    ProductName = db.Column(db.String(50))
    Type = db.Column(db.Enum('Fertilizer', 'Pesticide'))
    QuantityUsed = db.Column(db.Float)
    Cost = db.Column(db.Float)

    # Relationships
    managed_crops = db.relationship('ManageCrop', back_populates='product', cascade='all, delete')


class ManageCrop(db.Model):
    __tablename__ = 'ManageCrop'
    CropId = db.Column(db.Integer, db.ForeignKey('CropInfo.CropId'), primary_key=True)
    ProductId = db.Column(db.Integer, db.ForeignKey('FertilizerPesticide.ProductId'), primary_key=True)

    # Relationships
    crop = db.relationship('CropInfo', back_populates='managed_products')
    product = db.relationship('FertilizerPesticide', back_populates='managed_crops')


class Sales(db.Model):
    __tablename__ = 'Sales'
    SaleId = db.Column(db.Integer, primary_key=True)
    DateOfSale = db.Column(db.Date)
    PricePerUnit = db.Column(db.Float)
    QuantitySold = db.Column(db.Float)
    Earnings = db.Column(db.Float)
    CropId = db.Column(db.Integer, db.ForeignKey('CropInfo.CropId'))
    FarmerId = db.Column(db.Integer, db.ForeignKey('FarmerProfile.FarmerId'))

    # Relationships
    crop = db.relationship('CropInfo', back_populates='sales')
    farmer = db.relationship('FarmerProfile', back_populates='sales')
