#app.py

from flask import Flask, render_template, redirect, url_for, flash, session, request
from config import Config
from forms import RegisterForm, LoginForm, SalesForm, CropForm, FertilizerPesticideForm
from models import db, FarmerProfile, CropInfo, Grows, Sales, FertilizerPesticide, ManageCrop
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

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
        existing_farmer = FarmerProfile.query.filter_by(PhoneNumber=form.phone_number.data).first()
        if existing_farmer:
            flash('Phone number already registered. Please log in instead.', 'warning')
            return redirect(url_for('register'))
        
        hashed_password = generate_password_hash(form.password.data)
        new_farmer = FarmerProfile(
            FirstName=form.first_name.data,
            MiddleName=form.middle_name.data,
            LastName=form.last_name.data,
            PhoneNumber=form.phone_number.data,
            Location=form.location.data,
            LandArea=form.land_area.data,
            PasswordHash=hashed_password
        )
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

        session['farmer_id'] = farmer.FarmerId
        flash('Login successful!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('login.html', form=form)

@app.route('/dashboard')
def dashboard():
    farmer_id = session.get('farmer_id')
    if farmer_id is None:
        flash("Please log in to access the dashboard.", "danger")
        return redirect(url_for('login'))

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

        crop_ids = request.form.getlist('crop_ids')
        for crop_id in crop_ids:
            manage_crop_entry = ManageCrop(CropId=crop_id, ProductId=new_product.ProductId)
            db.session.add(manage_crop_entry)
        db.session.commit()
        flash('Fertilizer/Pesticide added and linked to crops successfully!', 'success')
        return redirect(url_for('dashboard'))

    farmer_id = session.get('farmer_id')
    crops = CropInfo.query.join(Grows).filter(Grows.FarmerId == farmer_id).all()
    
    return render_template('add_fertilizer_pesticide.html', form=form, crops=crops)

@app.route('/update_crop/<int:crop_id>', methods=['GET', 'POST'])
def update_crop(crop_id):
    crop = CropInfo.query.get(crop_id)
    if request.method == 'POST':
        crop.CropName = request.form['CropName']
        crop.EstimatedYield = request.form['EstimatedYield']
        crop.Status = request.form['Status']
        db.session.commit()
        return redirect(url_for('dashboard'))

    return render_template('update_crop.html', crop=crop)

@app.route('/update_sale/<int:sale_id>', methods=['GET', 'POST'])
def update_sale(sale_id):
    sale = Sales.query.get(sale_id)
    if request.method == 'POST':
        sale.PricePerUnit = float(request.form['PricePerUnit'])
        sale.QuantitySold = float(request.form['QuantitySold'])
        sale.Earnings = sale.PricePerUnit * sale.QuantitySold
        db.session.commit()

        crop_info = CropInfo.query.get(sale.CropId)
        total_sold = db.session.query(db.func.sum(Sales.QuantitySold)).filter(Sales.CropId == sale.CropId).scalar() or 0
        if total_sold >= crop_info.EstimatedYield:
            crop_info.Status = 'Unavailable'
            db.session.commit()

        flash('Sale updated successfully!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('update_sale.html', sale=sale)

@app.route('/update_fertilizer/<int:fertilizer_id>', methods=['GET', 'POST'])
def update_fertilizer(fertilizer_id):
    fertilizer = FertilizerPesticide.query.get(fertilizer_id)
    if request.method == 'POST':
        fertilizer.ProductName = request.form['ProductName']
        fertilizer.Type = request.form['Type']
        fertilizer.QuantityUsed = request.form['QuantityUsed']
        fertilizer.Cost = request.form['Cost']
        db.session.commit()
        return redirect(url_for('dashboard'))

    return render_template('update_fertilizer.html', fertilizer=fertilizer)

@app.route('/delete_crop/<int:crop_id>', methods=['GET', 'POST'])
def delete_crop(crop_id):
    # Get the crop and associated Grows entries
    crop = CropInfo.query.get(crop_id)
    if crop:
        # Delete related sales
        Sales.query.filter_by(CropId=crop_id).delete()
        
        # Get all ManageCrop entries related to this crop
        manage_crop_entries = ManageCrop.query.filter_by(CropId=crop_id).all()
        
        # Create a set to hold product IDs that need to be deleted
        product_ids_to_delete = set()
        
        for entry in manage_crop_entries:
            product_ids_to_delete.add(entry.ProductId)  # Collect product IDs for related fertilizers/pesticides
            db.session.delete(entry)  # Delete ManageCrop entry
        
        # Delete Grows entries
        Grows.query.filter_by(CropId=crop_id).delete()

        # Finally, delete the crop itself
        db.session.delete(crop)

        # Delete related FertilizerPesticide entries if necessary
        for product_id in product_ids_to_delete:
            fertilizer = FertilizerPesticide.query.get(product_id)
            if fertilizer:
                db.session.delete(fertilizer)

        db.session.commit()
        flash('Crop and related data deleted successfully.', 'success')
    else:
        flash('Crop not found.', 'danger')
    
    return redirect(url_for('dashboard'))



@app.route('/delete_sale/<int:sale_id>', methods=['GET','POST'])
def delete_sale(sale_id):
    sale = Sales.query.get(sale_id)
    if sale:
        crop_id = sale.CropId  # Get the crop ID from the sale
        db.session.delete(sale)  # Delete the sale
        db.session.commit()  # Commit the deletion first

        # Now, update the crop status
        crop_info = CropInfo.query.get(crop_id)  # Get the associated crop
        total_sold = db.session.query(db.func.sum(Sales.QuantitySold)).filter(Sales.CropId == crop_id).scalar() or 0

        if total_sold < crop_info.EstimatedYield:
            crop_info.Status = 'Available'  # Update status to Available
            db.session.commit()  # Commit the status update

        flash('Sale deleted successfully and crop status updated if necessary.', 'success')
    else:
        flash('Sale not found.', 'danger')
    
    return redirect(url_for('dashboard'))

@app.route('/delete_fertilizer/<int:fertilizer_id>', methods=['GET','POST'])
def delete_fertilizer(fertilizer_id):
    fertilizer = FertilizerPesticide.query.get(fertilizer_id)
    if fertilizer:
        db.session.delete(fertilizer)
        db.session.commit()
        flash('Fertilizer/Pesticide-related data deleted successfully.', 'success')
    else:
        flash('Fertilizer/Pesticide not found.', 'danger')
    return redirect(url_for('dashboard'))
@app.route('/logout')
def logout():
    # Clear the user's session
    session.clear()
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('login'))
@app.route('/admin', methods=['GET'])
def admin():
    farmers = FarmerProfile.query.all()
    crops = CropInfo.query.all()
    sales = Sales.query.all()
    fertilizers = FertilizerPesticide.query.all()
    grows = Grows.query.all()
    manage_crops = ManageCrop.query.all()

    return render_template('admin.html', farmers=farmers, crops=crops, sales=sales, fertilizers=fertilizers, grows=grows, manage_crops=manage_crops)


if __name__ == "__main__":
    app.run(debug=True)
