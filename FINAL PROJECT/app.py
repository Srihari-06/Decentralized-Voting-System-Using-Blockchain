
from flask import Flask, render_template, request, redirect, session,url_for
from blockchain import Blockchain
import db  
import os# Custom module for MySQL database operations

app = Flask(__name__, static_url_path='/static')  
app.secret_key = 'your_secret_key'
app.config['UPLOAD_FOLDER'] = 'static/uploads'



blockchain = Blockchain()

# Database connection
db_connection = db.connect_to_database()


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db.register_user(db_connection, username, password)  # Add user to MySQL database
        return redirect('/')
    return render_template('register.html')
    
@app.route('/delete_election', methods=['POST'])
def delete_election():
    if 'admin_id' not in session:
        return redirect('/')
    election_id = request.form['election_id']
    db.delete_election(db_connection, election_id)
    return redirect('/admin')



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = db.authenticate_user(db_connection, username, password)
        if user:
            session['user_id'] = user['id']
            return redirect(url_for('user_dashboard'))
        else:
            # Pass error message via query parameter
            return redirect(url_for('login', error='Invalid credentials'))
    
    # GET request handling
    error = request.args.get('error')
    return render_template('login.html', error=error)

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['admin_username']
        password = request.form['admin_password']
        
        # Verify admin credentials
        admin = db.authenticate_admin(db_connection,username, password)
        if admin:
            session['admin_id'] = admin['id']
            return redirect(('/admin_dashboard'))
        else:
            return redirect(url_for('admin_login', error='Invalid credentials'))
    
    error = request.args.get('error')
    return render_template('admin_login.html', error=error)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/user_dashboard')
def user_dashboard():
    if 'user_id' not in session:
        return redirect('/')
    db_connection = db.connect_to_database()
    elections = db.get_all_elections(db_connection)
    return render_template('user_dashboard.html', elections=elections, db=db, db_connection=db_connection)

@app.route('/admin_dashboard')
def admin_dashboard():
    if 'admin_id' not in session:
        return redirect('/')
    users = db.get_all_users(db_connection)
    votes = db.get_all_votes(db_connection)
    elections = db.get_all_elections(db_connection)
    return render_template('admin_dashboard.html', users=users, votes=votes, elections=elections)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(('/index'))


@app.route('/create_election', methods=['POST'])
def create_election():
    if 'admin_id' not in session:
        return redirect('/')

    name = request.form['name']
    start_date = request.form['start_date']
    end_date = request.form['end_date']
    candidate1_name = request.form['candidate1_name']
    candidate2_name = request.form['candidate2_name']

    # Save candidate images
    candidate1_image = request.files['candidate1_image']
    candidate2_image = request.files['candidate2_image']

    candidate1_image_path = os.path.join(app.config['UPLOAD_FOLDER'], candidate1_image.filename)
    candidate2_image_path = os.path.join(app.config['UPLOAD_FOLDER'], candidate2_image.filename)

    candidate1_image.save(candidate1_image_path)
    candidate2_image.save(candidate2_image_path)

    print("Creating election:", name, start_date, end_date,candidate1_name,candidate2_name,candidate1_image_path,candidate2_image_path )

    # Establish database connection
    db_connection = db.connect_to_database()

    # Ensure this function accepts the correct parameters
    db.create_election(db_connection, name, start_date, end_date,candidate1_name,candidate2_name,candidate1_image_path,candidate2_image_path)

    return redirect('/admin_dashboard')




@app.route('/vote', methods=['POST'])
def vote():
    if 'user_id' not in session:
        return redirect('/')
    election_id = request.form['election_id']
    candidate = request.form['candidate']
    user_id = session['user_id']
    # Check if the user has already voted in this election
    if not db.has_user_voted(db_connection, user_id, election_id):
        # Add vote to the blockchain
        blockchain.add_block({
            'election_id': election_id,
            'candidate': candidate,
            'user_id': user_id
        })
        # Record vote in the database
        db.record_vote(db_connection, user_id, election_id, candidate)
    
    return redirect('/user_dashboard')


@app.route('/results')
def results():
    if 'user_id' not in session:
        return redirect('/')
    
    # Fetch votes from the blockchain
    blockchain_votes = []
    for block in blockchain.chain:
        if block.data != "Genesis Block":
            blockchain_votes.append(block.data)
    
    # Fetch votes from the database
    db_votes = db.get_all_votes(db_connection)
    blockchain_votes = db.get_all_votes(db_connection)
    
    return render_template('results.html', blockchain_votes=blockchain_votes, db_votes=db_votes)


if __name__ == '__main__':
    app.run(debug=True)
    
