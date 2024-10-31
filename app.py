from flask import Flask, render_template, redirect, url_for, flash, session
from config import Config
from forms import RegisterForm, LoginForm, SalesForm, CropForm, FertilizerPesticideForm
from models import db, FarmerProfile, CropInfo, Grows, Sales, FertilizerPesticide, ManageCrop
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask import request

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

@app.before_request
def create_tables():
    db.create_all()

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        # Check if the phone number already exists
        existing_farmer = FarmerProfile.query.filter_by(PhoneNumber=form.phone_number.data).first()
        
        if existing_farmer:
            flash('Phone number already registered. Please log in instead.', 'warning')
            return redirect(url_for('register'))  # Redirect back to the registration page
        
        # Hash the password before storing
        hashed_password = generate_password_hash(form.password.data)

        # Create a new FarmerProfile instance with the hashed password
        new_farmer = FarmerProfile(
            FirstName=form.first_name.data,
            MiddleName=form.middle_name.data,
            LastName=form.last_name.data,
            PhoneNumber=form.phone_number.data,
            Location=form.location.data,
            LandArea=form.land_area.data,
            PasswordHash=hashed_password  # Store the hashed password
        )

        # Add the new farmer to the session and commit to the database
        db.session.add(new_farmer)
        db.session.commit()
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        farmer = FarmerProfile.query.filter_by(PhoneNumber=form.phone_number.data).first()
        if farmer is None:
            flash('Phone number not registered. Please register first.', 'danger')
            return redirect(url_for('register'))

        if not check_password_hash(farmer.PasswordHash, form.password.data):
            flash('Incorrect password. Please try again.', 'danger')
            return redirect(url_for('login'))

        # Store farmer ID in session if login is successful
        session['farmer_id'] = farmer.FarmerId  # Ensure this is the correct column name
        flash('Login successful!', 'success')
        return redirect(url_for('dashboard'))  # This should redirect to the dashboard

    return render_template('login.html', form=form)

@app.route('/dashboard')
def dashboard():
    farmer_id = session.get('farmer_id')

    if farmer_id is None:
        flash("Please log in to access the dashboard.", "danger")
        return redirect(url_for('login'))

    # Fetch and render necessary data for the dashboard
    crops = db.session.query(CropInfo).join(Grows, CropInfo.CropId == Grows.CropId).filter(Grows.FarmerId == farmer_id).all()
    sales = Sales.query.filter_by(FarmerId=farmer_id).all()
    fertilizers = (
        db.session.query(FertilizerPesticide, ManageCrop)
        .join(ManageCrop, FertilizerPesticide.ProductId == ManageCrop.ProductId)
        .join(CropInfo, ManageCrop.CropId == CropInfo.CropId)
        .join(Grows, CropInfo.CropId == Grows.CropId)
        .filter(Grows.FarmerId == farmer_id)
        .all()
    )

    return render_template('dashboard.html', crops=crops, sales=sales, fertilizers=fertilizers)

@app.route('/add_crop', methods=['GET', 'POST'])
def add_crop():
    form = CropForm()
    if form.validate_on_submit():
        new_crop = CropInfo(
            CropName=form.crop_name.data,
            PlantingDate=form.planting_date.data,
            HarvestDate=form.harvest_date.data,
            EstimatedYield=form.estimated_yield.data,
            Status=form.status.data
        )
        
        db.session.add(new_crop)
        db.session.commit()

        new_grow = Grows(FarmerId=session.get('farmer_id'), CropId=new_crop.CropId)
        db.session.add(new_grow)
        db.session.commit()

        flash('Crop added successfully!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('add_crop.html', form=form)

@app.route('/sales', methods=['GET', 'POST'])
def sales():
    form = SalesForm()
    if form.validate_on_submit():
        crop_id = form.crop_id.data
        quantity_sold = form.quantity_sold.data
        price_per_unit = form.price_per_unit.data

        crop_info = CropInfo.query.get(crop_id)
        
        if crop_info is None:
            flash('Invalid crop selected. Please select a valid crop.', 'danger')
            return redirect(url_for('sales'))
        
        if crop_info.Status == 'Unavailable':
            flash('You cannot record a sale for this crop because it is currently unavailable.', 'danger')
            return redirect(url_for('sales'))
        
        total_earnings = quantity_sold * price_per_unit * 1000

        new_sale = Sales(
            DateOfSale=form.date_of_sale.data,
            PricePerUnit=price_per_unit,
            QuantitySold=quantity_sold,
            Earnings=total_earnings,
            CropId=crop_id,
            FarmerId=session.get('farmer_id')
        )

        db.session.add(new_sale)
        db.session.commit()

        total_sold = db.session.query(db.func.sum(Sales.QuantitySold)).filter(Sales.CropId == crop_id).scalar() or 0

        if total_sold >= crop_info.EstimatedYield:
            crop_info.Status = 'Unavailable'
            db.session.commit()

        flash('Sale recorded successfully!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('sales.html', form=form)

@app.route('/add_fertilizer_pesticide', methods=['GET', 'POST'])
def add_fertilizer_pesticide():
    form = FertilizerPesticideForm()
    if form.validate_on_submit():
        new_product = FertilizerPesticide(
            ProductName=form.product_name.data,
            Type=form.type.data,
            QuantityUsed=form.quantity_used.data,
            Cost=form.cost.data
        )
        
        db.session.add(new_product)
        db.session.commit()

        # Link product to selected crops
        crop_ids = request.form.getlist('crop_ids')  # Get list of crop IDs from the form
        for crop_id in crop_ids:
            manage_crop_entry = ManageCrop(CropId=crop_id, ProductId=new_product.ProductId)
            db.session.add(manage_crop_entry)
        
        db.session.commit()
        flash('Fertilizer/Pesticide added and linked to crops successfully!', 'success')
        
        return redirect(url_for('dashboard'))

    # Fetch available crops for the dropdown in the form
    farmer_id = session.get('farmer_id')
    crops = CropInfo.query.join(Grows).filter(Grows.FarmerId == farmer_id).all()
    
    return render_template('add_fertilizer_pesticide.html', form=form, crops=crops)

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
