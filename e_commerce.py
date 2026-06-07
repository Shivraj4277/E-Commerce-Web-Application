import pytz
from datetime import datetime,timedelta,timezone
from werkzeug.utils import secure_filename
import os
from flask import Flask, render_template, request, url_for, redirect, flash,session
import mysql.connector
import calendar
import decimal
import json
import random
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="ec"
    )

def ctime():
	ist = pytz.timezone('Asia/Kolkata')
	ist_time = datetime.now(ist)
	return ist_time.strftime('%d-%m-%Y %H:%M:%S')
	
app = Flask(__name__)
app.secret_key = 'your_secret_key'  
UPLOAD_FOLDER = "static/product"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

UPLOAD_add = "static/adds"
os.makedirs(UPLOAD_add, exist_ok=True)
app.config["UPLOAD_add"] = UPLOAD_add

@app.route("/")
def index():
    session.clear()
    return redirect('home')

@app.route("/home",methods=["POST","GET"])
def home():
    
    if request.method == 'GET':
    	

        images = os.listdir('static/adds')
        images = [img for img in images if img.endswith(('jpg','png','jpeg'))]
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        query="""SELECT *
FROM product
WHERE pid > 1
ORDER BY pcategory ,date DESC;

"""
        cursor.execute(query,)
        related_products = cursor.fetchall()
        
        cursor.close()
        conn.close()
        # 🔹 Parse 'discription' for related products
        for p1 in related_products:
            try:
                p1['discription'] = json.loads(p1['discription'])
            except:
                p1['discription'] = {"main": {"images": []}}
        
        c = list({i['pcategory'] for i in related_products})
        random.shuffle(c)
        random.shuffle(related_products)
        return render_template(
            "home.html",
            products=related_products,c=c,images=images
        )
    return render_template("home.html")
    
@app.route("/login",methods=["POST","GET"])
def login():
    if request.method == 'POST':
    	
    	mobileno= request.form.get("mno")
    	ano = request.form.get("ano")
    	conn = get_db_connection()
    	cursor = conn.cursor(dictionary=True)
    	cursor.execute("SELECT ano,mobileno FROM admin WHERE ano=%s AND mobileno=%s",(ano,mobileno))
    	s=cursor.fetchone()
    	
    	if s:
    		session['user_type'] = 'admin'
    		session['user_id']=s['ano']
    		session['login']=True
    		session['ip'] = request.remote_addr  # Store IP to identify the session
    		session.permanent = True  # Make session permanent (stay across browser restarts)
    		return render_template("add_pro.html")
    	
    	cursor.execute("SELECT uid,mobileno FROM user WHERE password=%s AND mobileno=%s",(ano,mobileno))
    	s=cursor.fetchone()
    	
    	if s:
    		session['user_type'] = 'user'
    		session['user_id']=s['uid']
    		session['login']=True
    		session['ip'] = request.remote_addr  # Store IP to identify the session
    		session.permanent = True  # Make session permanent (stay across browser restarts)
    		
    		return redirect(url_for('home'))
    	flash("Incorrect data",'danger')
    return render_template("login.html")


@app.route("/forgot",methods=["POST","GET"])
def forgot():
    if request.method == 'POST':
    	email = request.form.get("email")
    	mobileno= request.form.get("mobileno")
    	conn = get_db_connection()
    	cursor = conn.cursor(dictionary=True)
    	cursor.execute("SELECT password,email,mobileno FROM user WHERE email=%s AND mobileno=%s",(email,mobileno))
    	s=cursor.fetchone()
    	if s:
    		flash(f'Your password is {s["password"]}','success')
    		return render_template("login.html")
    	else:
    		flash('User not exist','danger')
    		return render_template("createaccount.html")
    return render_template("forgot.html")
    
@app.route("/new-account",methods=["POST","GET"])
def c_account():
    if request.method == 'POST':
    	name = request.form.get("name")
    	address= request.form.get("address")
    	email= request.form.get("email")
    	mobile= request.form.get("mobile")
    	pin = request.form.get("pin")
    	password= request.form.get("password")
    	conn = get_db_connection()
    	cursor = conn.cursor(dictionary=True)
    	cursor.execute("SELECT email,mobileno FROM user WHERE email=%s AND mobileno=%s",(email,mobile))
    	s=cursor.fetchone()
    	if s:
    		flash(f'User already exist','danger')
    		return render_template("createaccount.html")
    	if s is None:
    		cursor.execute("INSERT INTO user (name,mobileno,email,pin,address,password) VALUES (%s,%s,%s,%s,%s,%s)",(name,mobile,email,pin,address,password,))
    		conn.commit()
    		conn.close()
    		flash('Account create successfully','success')
    		return render_template("login.html")
    return render_template("createaccount.html")
    
@app.route("/logout")
def logout():
    session.clear()
    return redirect('home')


@app.route("/add-product", methods=["POST","GET"])
def add_product():
    if request.method == 'POST':
        try:
            # Get form data
            name = request.form.get("name")
            category = request.form.get("category")
            company = request.form.get("cname")
            price = request.form.get("price")
            discount = request.form.get("discount")
            discount_price = request.form.get("discountPrice")
            stock = request.form.get("stock")
            descriptions = request.form.getlist("description[]")
            attributes = request.form.getlist("aname[]")
            images = request.files.getlist("description_image[]")
           
            # Build product description JSON
            product_description = {
                "main": {
                    "description": descriptions[0] if descriptions else "",
                    "images": []
                },
                "attributes": []
            }

            #main_image_count = len(images) - len(attributes)
            main_image_count = max(1, len(images) - len(attributes))


            # Main images
            for i in range(main_image_count):
                img = images[i]
                if img.filename:
                    filename = secure_filename(img.filename)
                    img.save(os.path.join(UPLOAD_FOLDER, filename))
                    product_description["main"]["images"].append(filename)

            # Attribute images
            img_index = main_image_count
            for i, attr in enumerate(attributes):
                if img_index < len(images):
                    img = images[img_index]
                    filename = secure_filename(img.filename)
                    img.save(os.path.join(UPLOAD_FOLDER, filename))
                    product_description["attributes"].append({
                        "name": attr,
                        "description": descriptions[i + 1] if i + 1 < len(descriptions) else "",
                        "image": filename
                    })
                    img_index += 1

            description_json = json.dumps(product_description)

            # Insert into DB
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                INSERT INTO product 
                (pname, pcategory, company, price, discount, discount_price, stock, discription, date)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,now())
            """, (
                name, category, company, price, discount,
                discount_price, stock, description_json
            ))
            conn.commit()
            cursor.close()
            conn.close()

            flash("Product added successfully!", "success")
            return redirect("/add-product")

        except Exception as e:
            flash("Product already exists or some error occurred.", "danger")
            return redirect("/add-product")

    # GET request
    return render_template("add_pro.html")
        
@app.route("/add-adds", methods=["POST","GET"])
def add_adds():
    try:
        if request.method == 'POST':
	        images = request.files.getlist("description_image[]")
	        main_image_count = len(images)
	        # Main images
	        for i in range(main_image_count):
	            img = images[i]
	            if img.filename:
	                filename = secure_filename(img.filename)
	                img.save(os.path.join(UPLOAD_add, filename))

	        flash("Successfully added", "success")
	        return render_template("add_ads.html")
    except Exception as e:
          # debugging
        flash("Already Exist", "danger")

    return render_template("add_ads.html")


@app.route('/info/<int:pid>', methods=["GET", "POST"])
def info(pid):

    if request.method == 'GET':

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # 🔹 Main product
        cursor.execute("SELECT * FROM product WHERE pid = %s", (pid,))
        products = cursor.fetchall()

        # Parse 'discription' for main product
        for p in products:
            try:
                p['discription'] = json.loads(p['discription'])
            except:
                p['discription'] = {"main": {"images": []}}

        # 🔹 Related products query
        query = """
        SELECT * 
        FROM product
        WHERE 
            pcategory = (SELECT pcategory FROM product WHERE pid = %s)
            AND price BETWEEN 
                (SELECT MIN(price)FROM product WHERE pcategory = (SELECT pcategory FROM product WHERE pid = %s))
                AND 
                (SELECT MAX(price)FROM product WHERE pcategory = (SELECT pcategory FROM product WHERE pid = %s))
            AND stock > 0
            AND pid != %s
        ORDER BY 
            CASE 
                WHEN company = (SELECT company FROM product WHERE pid = %s) THEN 1
                ELSE 2
            END,
            STR_TO_DATE(date, '%%d-%%m-%%Y') DESC
        LIMIT 15
        """

        cursor.execute(query, (pid, pid, pid, pid, pid))
        related_products = cursor.fetchall()
        random.shuffle(related_products)
        cursor.close()
        conn.close()
        
        
        # 🔹 Parse 'discription' for related products
        for p1 in related_products:
            try:
                p1['discription'] = json.loads(p1['discription'])
            except:
                p1['discription'] = {"main": {"images": []}}

        # 🔹 After processing all the products, render the template
        return render_template(
            "seeinfo.html",
            products=products,
            related_product=related_products
        )


@app.route("/cart/<int:uid>/<pid>",methods=["POST","GET"])
def cart(uid,pid=None):
    if request.method == 'GET':
    	conn = get_db_connection()
    	cursor = conn.cursor(dictionary=True)
    	if pid:
	    	cursor.execute("SELECT * FROM cart WHERE pid=%s AND uid=%s",(pid,uid))
	    	c=cursor.fetchall()
	    	if not c:
	    		cursor.execute("INSERT INTO cart(pid,uid,added_at) values(%s,%s,now())",(pid,uid,))
	    		conn.commit()
    	
    	cursor.execute("SELECT * FROM product p INNER JOIN cart c WHERE c.pid=p.pid and c.uid=%s;",(uid,))
    	c=cursor.fetchall()
    	cursor.close()
    	conn.close()
    	return render_template("demo.html",products=c,table='cart')
    

@app.route("/select/<name>")
def sname(name):
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    if session.get('user_type')=='user':
    	if name=='cart':
    		cursor.execute("SELECT * FROM product p INNER JOIN cart c WHERE c.pid=p.pid and c.uid=%s;",(session.get('user_id'),))
    	elif name=='orders':
    		cursor.execute("""
SELECT *
FROM product p
INNER JOIN orders c ON p.pid = c.pid
WHERE c.uid = %s
ORDER BY c.date DESC
""", (session.get('user_id'),))  		
    		
    else:
    	if name=='orders':
    		cursor.execute("SELECT * FROM product p INNER JOIN orders c WHERE c.pid=p.pid ORDER BY c.date DESC")
    	else:
    		cursor.execute(f"SELECT * FROM {name}")
    	
    		
    products = cursor.fetchall()
    if name in ('product','orders','cart'):
	    for p in products:
	        if p['discription']:
	            try:
	                p['discription'] = json.loads(p['discription'])
	            except json.JSONDecodeError:
	                p['discription'] = {}
	        else:
	            p['discription'] = {}
	
    return render_template("demo.html", products=products,table=name)


@app.route("/del/<string:name>/<int:pid>/<int:uid>", methods=["POST","GET"])
def delproduct(name, pid, uid):
    if request.method == 'GET':
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        if session.get('user_type') == 'user':
            if name=='orders':
            	query =f"DELETE FROM {name} WHERE pid=%s AND uid=%s AND oid=%s;"
            	cursor.execute(query, (pid, session.get('user_id'),uid,))
            	
            elif name=='cart':
            	query = f"DELETE FROM {name} WHERE pid=%s AND uid=%s;"
            	cursor.execute(query, (pid, uid,))
        else:
            query = f'DELETE FROM {name} WHERE pid=%s;'
            cursor.execute(query, (pid,))

        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('sname', name=name))

@app.route("/update/<name>/<uid>/<status>/<oid>",methods=["POST","GET"])
def update(name,uid,status,oid):
    if request.method == 'GET':
    	conn = get_db_connection()
    	cursor = conn.cursor(dictionary=True)
    	if status=='status':
    		cursor.execute(f"UPDATE {name} SET status='yes' WHERE uid={uid} AND oid={oid};")
    	elif status=='delivered':
    		cursor.execute(f"UPDATE {name} SET status='delivered' WHERE uid={uid} AND oid= {oid};")
    	conn.commit()
    	cursor.close()
    	conn.close()
    	return redirect(url_for('sname', name=name))

@app.route("/update_info", methods=["GET", "POST"])
def up_info():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        uid = request.form['uid']            # readonly user id from form
        mobileno = request.form['mobileno']  # readonly mobile number
        name = request.form['name']
        address = request.form['address']
        email = request.form['email']
        pin = request.form['pin']

        cursor.execute("""
            UPDATE user
            SET name=%s, address=%s, email=%s, pin=%s
            WHERE uid=%s AND mobileno=%s
        """, (name, address, email, pin, uid, mobileno))

        conn.commit()
        cursor.close()
        conn.close()
        flash("Account updated successfully!", "success")
        return redirect("/update_info")  # POST-redirect-GET pattern

    # -------- GET REQUEST ----------
    uid = session.get('user_id')
    cursor.execute("SELECT * FROM user WHERE uid=%s", (uid,))
    data = cursor.fetchone()   # single row
    cursor.close()
    conn.close()

    return render_template("update_info.html", data=data)


@app.route("/buy/<pid>", methods=["GET", "POST"])
def buy(pid):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        stock = int(request.form['stock'])
        amount = float(request.form['amount'])

        cursor.execute("SELECT stock FROM product WHERE pid=%s", (pid,))
        s = cursor.fetchone()

        if not s:
            flash("Product not found", "danger")
            return redirect("/")

        available_stock = s['stock']

        if stock > available_stock:
            flash("Invalid available stock", "danger")
            return redirect(f"/buy/{pid}")

        cursor.execute("""
            INSERT INTO orders(pid, uid, date, status, stock, amount)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (pid, session.get('user_id'), ctime(), "no", stock, amount))

        cursor.execute(
            "UPDATE product SET stock=%s WHERE pid=%s",
            (available_stock - stock, pid)
        )

        conn.commit()
        cursor.close()
        conn.close()

        return redirect(f"/info/{pid}")

    # -------- GET REQUEST ----------
    cursor.execute("SELECT * FROM product WHERE pid=%s", (pid,))
    data = cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template("buy.html", data=data)


@app.route("/stock/<pid>",methods=["POST","GET"])
def add_stock(pid):
    if request.method == 'POST':
    	stock=int(request.form['stock'])
    	conn = get_db_connection()
    	cursor = conn.cursor(dictionary=True)
    	cursor.execute("SELECT stock FROM product WHERE pid=%s",(pid,))
    	s=cursor.fetchone()
    	s=s['stock']
    	cursor.execute("UPDATE product SET stock=%s WHERE pid=%s",(s+stock,pid,))
    	conn.commit()
    	cursor.close()
    	conn.close()
    	return redirect(url_for('sname', name='product'))
    return render_template("update_stock.html",pid=pid)


if __name__ == "__main__":
    app.run(debug=True)
