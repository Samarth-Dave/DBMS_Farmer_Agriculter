from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, DecimalField, DateField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, Optional

class RegisterForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=50)])
    middle_name = StringField('Middle Name', validators=[Optional(), Length(max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=50)])
    phone_number = StringField('Phone Number', validators=[DataRequired(), Length(max=15)])
    location = StringField('Location', validators=[Optional(), Length(max=100)])
    land_area = DecimalField('Land Area', validators=[Optional()])
    password = PasswordField('Password', validators=[DataRequired(), Length(max=255)])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    phone_number = StringField('Phone Number', validators=[DataRequired(), Length(max=15)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class CropForm(FlaskForm):
    crop_name = StringField('Crop Name', validators=[DataRequired(), Length(max=50)])
    planting_date = DateField('Planting Date', format='%Y-%m-%d', validators=[Optional()])
    harvest_date = DateField('Harvest Date', format='%Y-%m-%d', validators=[Optional()])
    estimated_yield = DecimalField('Estimated Yield', validators=[Optional()])
    status = StringField('Status', default='available', validators=[Optional()])
    submit = SubmitField('Add Crop')

class SalesForm(FlaskForm):
    date_of_sale = DateField('Date of Sale', format='%Y-%m-%d', validators=[Optional()])
    price_per_unit = DecimalField('Price Per Unit', validators=[Optional()])
    quantity_sold = DecimalField('Quantity Sold', validators=[Optional()])
    earnings = DecimalField('Earnings', validators=[Optional()])
    crop_id = StringField('Crop ID', validators=[Optional()])  # Consider using a dropdown in a real application
    submit = SubmitField('Record Sale')

class FertilizerPesticideForm(FlaskForm):
    product_name = StringField('Product Name', validators=[DataRequired(), Length(max=50)])
    type = SelectField('Type', choices=[('Fertilizer', 'Fertilizer'), ('Pesticide', 'Pesticide')], validators=[DataRequired()])
    quantity_used = DecimalField('Quantity Used', validators=[Optional()])
    cost = DecimalField('Cost', validators=[Optional()])
    submit = SubmitField('Add Product')
