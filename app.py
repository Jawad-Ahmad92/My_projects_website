import os
import json
import joblib
from datetime import datetime
import pandas as pd
import numpy as np

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-key-ai-portfolio-123456'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///portfolio.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Upload folders configuration
UPLOAD_FOLDER = os.path.join(app.root_path, 'uploads')
MODEL_FOLDER = os.path.join(app.root_path, 'models')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MODEL_FOLDER'] = MODEL_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(MODEL_FOLDER, exist_ok=True)

# Allowed file extensions
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'svg'}
ALLOWED_MODEL_EXTENSIONS = {'pkl', 'joblib', 'h5', 'pb'}
ALLOWED_DATA_EXTENSIONS = {'csv', 'xlsx', 'json'}
ALLOWED_DOC_EXTENSIONS = {'pdf', 'docx', 'txt', 'md'}

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'admin_login'

# Helper functions
def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

# ----------------- Database Models -----------------

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(50), nullable=False) # Machine Learning, Deep Learning, Data Analysis
    tags = db.Column(db.String(200), nullable=True) # Comma separated
    image_filename = db.Column(db.String(100), nullable=True)
    model_filename = db.Column(db.String(100), nullable=True)
    dataset_filename = db.Column(db.String(100), nullable=True)
    doc_filename = db.Column(db.String(100), nullable=True)
    
    # ML Stats
    accuracy = db.Column(db.Float, nullable=True)
    precision = db.Column(db.Float, nullable=True)
    recall = db.Column(db.Float, nullable=True)
    f1_score = db.Column(db.Float, nullable=True)
    status = db.Column(db.String(20), default='Completed') # Completed, In Progress
    
    # Links & Metadata
    github_link = db.Column(db.String(255), nullable=True)
    demo_link = db.Column(db.String(255), nullable=True)
    algorithm = db.Column(db.String(100), nullable=True)
    
    # Case Study Content
    problem_statement = db.Column(db.Text, nullable=True)
    dataset_info = db.Column(db.Text, nullable=True)
    data_cleaning = db.Column(db.Text, nullable=True)
    feature_engineering = db.Column(db.Text, nullable=True)
    training_process = db.Column(db.Text, nullable=True)
    evaluation_metrics = db.Column(db.Text, nullable=True)
    future_improvements = db.Column(db.Text, nullable=True)
    conclusion = db.Column(db.Text, nullable=True)
    
    # Metric visualization images
    confusion_matrix_img = db.Column(db.String(100), nullable=True)
    roc_curve_img = db.Column(db.String(100), nullable=True)
    feature_importance_img = db.Column(db.String(100), nullable=True)
    
    # Flags & Dynamic Prediction Form Schema (JSON)
    is_featured = db.Column(db.Boolean, default=False)
    is_interactive = db.Column(db.Boolean, default=False)
    inputs_schema = db.Column(db.Text, nullable=True) 

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    slug = db.Column(db.String(150), unique=True, nullable=False)
    summary = db.Column(db.Text, nullable=True)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=True) # Machine Learning, Python, etc.
    image_filename = db.Column(db.String(100), nullable=True)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    tags = db.Column(db.String(200), nullable=True)

class Certificate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    organization = db.Column(db.String(100), nullable=False)
    issue_date = db.Column(db.String(50), nullable=True)
    image_filename = db.Column(db.String(100), nullable=True)
    credential_url = db.Column(db.String(255), nullable=True)

class Resume(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100), nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

class ContactMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    subject = db.Column(db.String(150), nullable=True)
    message = db.Column(db.Text, nullable=False)
    date_sent = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)

class Stat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), unique=True, nullable=False)
    value = db.Column(db.String(20), nullable=False)
    icon = db.Column(db.String(50), nullable=True) # FontAwesome class

# ----------------- Flask-Login Loader -----------------

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ----------------- File Serving Routes -----------------

@app.route('/uploads/<filename>')
def serve_upload(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/uploads/resumes/<filename>')
def serve_resume(filename):
    return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], 'resumes'), filename)

# ----------------- Public Routes -----------------

@app.route('/')
def index():
    projects = Project.query.order_by(Project.is_featured.desc(), Project.id.desc()).all()
    blogs = Blog.query.order_by(Blog.date_posted.desc()).limit(3).all()
    certificates = Certificate.query.order_by(Certificate.id.desc()).all()
    stats = Stat.query.all()
    active_resume = Resume.query.filter_by(is_active=True).order_by(Resume.upload_date.desc()).first()
    
    # Structure projects by category
    ml_projects = [p for p in projects if p.category.lower() == 'machine learning']
    dl_projects = [p for p in projects if p.category.lower() == 'deep learning']
    da_projects = [p for p in projects if p.category.lower() == 'data analysis']
    
    return render_template(
        'index.html',
        projects=projects,
        ml_projects=ml_projects,
        dl_projects=dl_projects,
        da_projects=da_projects,
        blogs=blogs,
        certificates=certificates,
        stats=stats,
        resume=active_resume
    )

@app.route('/project/<slug>')
def project_detail(slug):
    project = Project.query.filter_by(slug=slug).first_or_404()
    
    # Try parsing inputs schema
    schema = []
    if project.is_interactive and project.inputs_schema:
        try:
            schema = json.loads(project.inputs_schema)
        except Exception:
            pass
            
    return render_template('project_detail.html', project=project, schema=schema)

@app.route('/blog/<slug>')
def blog_detail(slug):
    blog = Blog.query.filter_by(slug=slug).first_or_404()
    return render_template('blog_detail.html', blog=blog)

@app.route('/contact', methods=['POST'])
def contact_submit():
    name = request.form.get('name')
    email = request.form.get('email')
    subject = request.form.get('subject')
    message = request.form.get('message')
    
    if not name or not email or not message:
        return jsonify({'success': False, 'message': 'Please fill all required fields.'}), 400
        
    msg = ContactMessage(name=name, email=email, subject=subject, message=message)
    db.session.add(msg)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Your message has been sent successfully!'})

# ----------------- Interactive Prediction Endpoint -----------------

@app.route('/project/<slug>/predict', methods=['POST'])
def predict(slug):
    project = Project.query.filter_by(slug=slug).first_or_404()
    
    if not project.is_interactive or not project.model_filename:
        return jsonify({'error': 'Interactive prediction is not configured for this project.'}), 400
        
    model_path = os.path.join(app.config['MODEL_FOLDER'], project.model_filename)
    if not os.path.exists(model_path):
        return jsonify({'error': 'Model weights not found on server.'}), 404
        
    try:
        # Load model using joblib
        model = joblib.load(model_path)
        
        # Process input features based on schema
        schema = json.loads(project.inputs_schema) if project.inputs_schema else []
        features = []
        
        for field in schema:
            name = field['name']
            val = request.form.get(name)
            
            if val is None:
                return jsonify({'error': f'Missing input value for field: {name}'}), 400
                
            # Cast feature type
            field_type = field.get('type', 'number')
            if field_type == 'number' or field_type == 'select':
                try:
                    if '.' in str(val):
                        features.append(float(val))
                    else:
                        features.append(int(val))
                except ValueError:
                    features.append(float(val) if '.' in str(val) else int(val) if val.isdigit() else val)
            else:
                features.append(val)
                
        # Reshape data (1, N) for inference
        features_arr = np.array(features).reshape(1, -1)
        
        # Predict
        prediction = model.predict(features_arr)[0]
        
        # Compute probabilities if classification
        probabilities = None
        if hasattr(model, 'predict_proba'):
            prob = model.predict_proba(features_arr)[0]
            probabilities = [float(p) for p in prob]
            
        # Serialize predictions for response
        if isinstance(prediction, (np.integer, np.int64, np.int32)):
            prediction = int(prediction)
        elif isinstance(prediction, (np.floating, np.float64, np.float32)):
            prediction = float(prediction)
            
        is_classification = hasattr(model, 'predict_proba') or isinstance(prediction, (int, str))
        
        response = {
            'success': True,
            'prediction': prediction,
            'is_classification': bool(is_classification)
        }
        if probabilities:
            response['probabilities'] = probabilities
            
        return jsonify(response)
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Prediction execution failed: {str(e)}'}), 500

# ----------------- Admin Auth Routes -----------------

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if current_user.is_authenticated:
        return redirect(url_for('admin_dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash('Successfully logged in!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid username or password.', 'error')
            
    return render_template('admin/login.html')

@app.route('/admin/logout')
@login_required
def admin_logout():
    logout_user()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('admin_login'))

# ----------------- Admin Dashboard Panel -----------------

@app.route('/admin')
@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    project_count = Project.query.count()
    blog_count = Blog.query.count()
    cert_count = Certificate.query.count()
    unread_messages = ContactMessage.query.filter_by(is_read=False).order_by(ContactMessage.date_sent.desc()).all()
    
    projects = Project.query.order_by(Project.id.desc()).limit(5).all()
    
    return render_template(
        'admin/dashboard.html',
        project_count=project_count,
        blog_count=blog_count,
        cert_count=cert_count,
        unread_messages=unread_messages,
        projects=projects
    )

# Manage Projects
@app.route('/admin/projects')
@login_required
def admin_projects():
    projects = Project.query.order_by(Project.id.desc()).all()
    return render_template('admin/projects.html', projects=projects)

@app.route('/admin/projects/add', methods=['GET', 'POST'])
@login_required
def admin_project_add():
    if request.method == 'POST':
        name = request.form.get('name')
        slug = secure_filename(name.lower().replace(' ', '-'))
        description = request.form.get('description')
        category = request.form.get('category')
        tags = request.form.get('tags')
        
        accuracy = request.form.get('accuracy')
        precision = request.form.get('precision')
        recall = request.form.get('recall')
        f1_score = request.form.get('f1_score')
        status = request.form.get('status', 'Completed')
        algorithm = request.form.get('algorithm')
        github_link = request.form.get('github_link')
        demo_link = request.form.get('demo_link')
        
        problem_statement = request.form.get('problem_statement')
        dataset_info = request.form.get('dataset_info')
        data_cleaning = request.form.get('data_cleaning')
        feature_engineering = request.form.get('feature_engineering')
        training_process = request.form.get('training_process')
        evaluation_metrics = request.form.get('evaluation_metrics')
        future_improvements = request.form.get('future_improvements')
        conclusion = request.form.get('conclusion')
        
        is_featured = 'is_featured' in request.form
        is_interactive = 'is_interactive' in request.form
        inputs_schema = request.form.get('inputs_schema')
        
        project = Project(
            name=name, slug=slug, description=description, category=category, tags=tags,
            accuracy=float(accuracy) if accuracy else None,
            precision=float(precision) if precision else None,
            recall=float(recall) if recall else None,
            f1_score=float(f1_score) if f1_score else None,
            status=status, algorithm=algorithm, github_link=github_link, demo_link=demo_link,
            problem_statement=problem_statement, dataset_info=dataset_info, data_cleaning=data_cleaning,
            feature_engineering=feature_engineering, training_process=training_process,
            evaluation_metrics=evaluation_metrics, future_improvements=future_improvements,
            conclusion=conclusion, is_featured=is_featured, is_interactive=is_interactive,
            inputs_schema=inputs_schema
        )
        
        # File uploads
        image_file = request.files.get('image_file')
        if image_file and allowed_file(image_file.filename, ALLOWED_IMAGE_EXTENSIONS):
            filename = f"p_{slug}_{secure_filename(image_file.filename)}"
            image_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            project.image_filename = filename
            
        model_file = request.files.get('model_file')
        if model_file and allowed_file(model_file.filename, ALLOWED_MODEL_EXTENSIONS):
            filename = f"model_{slug}_{secure_filename(model_file.filename)}"
            model_file.save(os.path.join(app.config['MODEL_FOLDER'], filename))
            project.model_filename = filename
            
        dataset_file = request.files.get('dataset_file')
        if dataset_file and allowed_file(dataset_file.filename, ALLOWED_DATA_EXTENSIONS):
            filename = f"data_{slug}_{secure_filename(dataset_file.filename)}"
            dataset_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            project.dataset_filename = filename
            
        doc_file = request.files.get('doc_file')
        if doc_file and allowed_file(doc_file.filename, ALLOWED_DOC_EXTENSIONS):
            filename = f"doc_{slug}_{secure_filename(doc_file.filename)}"
            doc_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            project.doc_filename = filename
            
        # Metric images
        cm_file = request.files.get('confusion_matrix_img')
        if cm_file and allowed_file(cm_file.filename, ALLOWED_IMAGE_EXTENSIONS):
            filename = f"cm_{slug}_{secure_filename(cm_file.filename)}"
            cm_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            project.confusion_matrix_img = filename
            
        roc_file = request.files.get('roc_curve_img')
        if roc_file and allowed_file(roc_file.filename, ALLOWED_IMAGE_EXTENSIONS):
            filename = f"roc_{slug}_{secure_filename(roc_file.filename)}"
            roc_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            project.roc_curve_img = filename
            
        fi_file = request.files.get('feature_importance_img')
        if fi_file and allowed_file(fi_file.filename, ALLOWED_IMAGE_EXTENSIONS):
            filename = f"fi_{slug}_{secure_filename(fi_file.filename)}"
            fi_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            project.feature_importance_img = filename
            
        db.session.add(project)
        db.session.commit()
        
        flash('Project added successfully!', 'success')
        return redirect(url_for('admin_projects'))
        
    return render_template('admin/project_form.html', action='Add', project=None)

@app.route('/admin/projects/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def admin_project_edit(id):
    project = Project.query.get_or_404(id)
    if request.method == 'POST':
        project.name = request.form.get('name')
        project.description = request.form.get('description')
        project.category = request.form.get('category')
        project.tags = request.form.get('tags')
        
        accuracy = request.form.get('accuracy')
        project.accuracy = float(accuracy) if accuracy else None
        
        precision = request.form.get('precision')
        project.precision = float(precision) if precision else None
        
        recall = request.form.get('recall')
        project.recall = float(recall) if recall else None
        
        f1_score = request.form.get('f1_score')
        project.f1_score = float(f1_score) if f1_score else None
        
        project.status = request.form.get('status', 'Completed')
        project.algorithm = request.form.get('algorithm')
        project.github_link = request.form.get('github_link')
        project.demo_link = request.form.get('demo_link')
        
        project.problem_statement = request.form.get('problem_statement')
        project.dataset_info = request.form.get('dataset_info')
        project.data_cleaning = request.form.get('data_cleaning')
        project.feature_engineering = request.form.get('feature_engineering')
        project.training_process = request.form.get('training_process')
        project.evaluation_metrics = request.form.get('evaluation_metrics')
        project.future_improvements = request.form.get('future_improvements')
        project.conclusion = request.form.get('conclusion')
        
        project.is_featured = 'is_featured' in request.form
        project.is_interactive = 'is_interactive' in request.form
        project.inputs_schema = request.form.get('inputs_schema')
        
        # Files updates
        image_file = request.files.get('image_file')
        if image_file and allowed_file(image_file.filename, ALLOWED_IMAGE_EXTENSIONS):
            filename = f"p_{project.slug}_{secure_filename(image_file.filename)}"
            image_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            project.image_filename = filename
            
        model_file = request.files.get('model_file')
        if model_file and allowed_file(model_file.filename, ALLOWED_MODEL_EXTENSIONS):
            filename = f"model_{project.slug}_{secure_filename(model_file.filename)}"
            model_file.save(os.path.join(app.config['MODEL_FOLDER'], filename))
            project.model_filename = filename
            
        dataset_file = request.files.get('dataset_file')
        if dataset_file and allowed_file(dataset_file.filename, ALLOWED_DATA_EXTENSIONS):
            filename = f"data_{project.slug}_{secure_filename(dataset_file.filename)}"
            dataset_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            project.dataset_filename = filename
            
        doc_file = request.files.get('doc_file')
        if doc_file and allowed_file(doc_file.filename, ALLOWED_DOC_EXTENSIONS):
            filename = f"doc_{project.slug}_{secure_filename(doc_file.filename)}"
            doc_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            project.doc_filename = filename
            
        # Metric images updates
        cm_file = request.files.get('confusion_matrix_img')
        if cm_file and allowed_file(cm_file.filename, ALLOWED_IMAGE_EXTENSIONS):
            filename = f"cm_{project.slug}_{secure_filename(cm_file.filename)}"
            cm_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            project.confusion_matrix_img = filename
            
        roc_file = request.files.get('roc_curve_img')
        if roc_file and allowed_file(roc_file.filename, ALLOWED_IMAGE_EXTENSIONS):
            filename = f"roc_{project.slug}_{secure_filename(roc_file.filename)}"
            roc_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            project.roc_curve_img = filename
            
        fi_file = request.files.get('feature_importance_img')
        if fi_file and allowed_file(fi_file.filename, ALLOWED_IMAGE_EXTENSIONS):
            filename = f"fi_{project.slug}_{secure_filename(fi_file.filename)}"
            fi_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            project.feature_importance_img = filename
            
        db.session.commit()
        flash('Project updated successfully!', 'success')
        return redirect(url_for('admin_projects'))
        
    return render_template('admin/project_form.html', action='Edit', project=project)

@app.route('/admin/projects/delete/<int:id>', methods=['POST'])
@login_required
def admin_project_delete(id):
    project = Project.query.get_or_404(id)
    db.session.delete(project)
    db.session.commit()
    flash('Project deleted successfully.', 'info')
    return redirect(url_for('admin_projects'))

# Manage Blog
@app.route('/admin/blogs')
@login_required
def admin_blogs():
    blogs = Blog.query.order_by(Blog.date_posted.desc()).all()
    return render_template('admin/blogs.html', blogs=blogs)

@app.route('/admin/blogs/add', methods=['GET', 'POST'])
@login_required
def admin_blog_add():
    if request.method == 'POST':
        title = request.form.get('title')
        slug = secure_filename(title.lower().replace(' ', '-'))
        summary = request.form.get('summary')
        content = request.form.get('content')
        category = request.form.get('category')
        tags = request.form.get('tags')
        
        blog = Blog(title=title, slug=slug, summary=summary, content=content, category=category, tags=tags)
        
        image_file = request.files.get('image_file')
        if image_file and allowed_file(image_file.filename, ALLOWED_IMAGE_EXTENSIONS):
            filename = f"blog_{slug}_{secure_filename(image_file.filename)}"
            image_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            blog.image_filename = filename
            
        db.session.add(blog)
        db.session.commit()
        flash('Blog post added successfully!', 'success')
        return redirect(url_for('admin_blogs'))
        
    return render_template('admin/blog_form.html', action='Add', blog=None)

@app.route('/admin/blogs/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def admin_blog_edit(id):
    blog = Blog.query.get_or_404(id)
    if request.method == 'POST':
        blog.title = request.form.get('title')
        blog.summary = request.form.get('summary')
        blog.content = request.form.get('content')
        blog.category = request.form.get('category')
        blog.tags = request.form.get('tags')
        
        image_file = request.files.get('image_file')
        if image_file and allowed_file(image_file.filename, ALLOWED_IMAGE_EXTENSIONS):
            filename = f"blog_{blog.slug}_{secure_filename(image_file.filename)}"
            image_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            blog.image_filename = filename
            
        db.session.commit()
        flash('Blog post updated successfully!', 'success')
        return redirect(url_for('admin_blogs'))
        
    return render_template('admin/blog_form.html', action='Edit', blog=blog)

@app.route('/admin/blogs/delete/<int:id>', methods=['POST'])
@login_required
def admin_blog_delete(id):
    blog = Blog.query.get_or_404(id)
    db.session.delete(blog)
    db.session.commit()
    flash('Blog post deleted successfully.', 'info')
    return redirect(url_for('admin_blogs'))

# Manage Certificates
@app.route('/admin/certificates')
@login_required
def admin_certificates():
    certificates = Certificate.query.all()
    return render_template('admin/certificates.html', certificates=certificates)

@app.route('/admin/certificates/add', methods=['GET', 'POST'])
@login_required
def admin_certificate_add():
    if request.method == 'POST':
        name = request.form.get('name')
        organization = request.form.get('organization')
        issue_date = request.form.get('issue_date')
        credential_url = request.form.get('credential_url')
        
        cert = Certificate(name=name, organization=organization, issue_date=issue_date, credential_url=credential_url)
        
        image_file = request.files.get('image_file')
        if image_file and allowed_file(image_file.filename, ALLOWED_IMAGE_EXTENSIONS):
            filename = f"cert_{secure_filename(name.lower().replace(' ', '_'))}_{secure_filename(image_file.filename)}"
            image_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            cert.image_filename = filename
            
        db.session.add(cert)
        db.session.commit()
        flash('Certificate added successfully!', 'success')
        return redirect(url_for('admin_certificates'))
        
    return render_template('admin/certificate_form.html', action='Add', certificate=None)

@app.route('/admin/certificates/delete/<int:id>', methods=['POST'])
@login_required
def admin_certificate_delete(id):
    cert = Certificate.query.get_or_404(id)
    db.session.delete(cert)
    db.session.commit()
    flash('Certificate deleted successfully.', 'info')
    return redirect(url_for('admin_certificates'))

# Manage Resume
@app.route('/admin/resume', methods=['GET', 'POST'])
@login_required
def admin_resume():
    if request.method == 'POST':
        resume_file = request.files.get('resume_file')
        if resume_file and allowed_file(resume_file.filename, {'pdf'}):
            # Deactivate current resumes
            Resume.query.update({Resume.is_active: False})
            
            resumes_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'resumes')
            os.makedirs(resumes_dir, exist_ok=True)
            
            filename = f"resume_{secure_filename(resume_file.filename)}"
            resume_file.save(os.path.join(resumes_dir, filename))
            
            new_resume = Resume(filename=filename, is_active=True)
            db.session.add(new_resume)
            db.session.commit()
            flash('Resume uploaded and set active!', 'success')
        else:
            flash('Only PDF files are allowed.', 'error')
            
    resumes = Resume.query.order_by(Resume.upload_date.desc()).all()
    return render_template('admin/resume.html', resumes=resumes)

# Manage Messages
@app.route('/admin/messages')
@login_required
def admin_messages():
    messages = ContactMessage.query.order_by(ContactMessage.date_sent.desc()).all()
    return render_template('admin/messages.html', messages=messages)

@app.route('/admin/messages/read/<int:id>', methods=['POST'])
@login_required
def admin_message_read(id):
    msg = ContactMessage.query.get_or_404(id)
    msg.is_read = True
    db.session.commit()
    return jsonify({'success': True})

@app.route('/admin/messages/delete/<int:id>', methods=['POST'])
@login_required
def admin_message_delete(id):
    msg = ContactMessage.query.get_or_404(id)
    db.session.delete(msg)
    db.session.commit()
    flash('Message deleted.', 'info')
    return redirect(url_for('admin_messages'))

# Manage Stats
@app.route('/admin/stats', methods=['GET', 'POST'])
@login_required
def admin_stats():
    if request.method == 'POST':
        for key, val in request.form.items():
            if key.startswith('stat_'):
                stat_key = key.replace('stat_', '')
                stat_item = Stat.query.filter_by(key=stat_key).first()
                if stat_item:
                    stat_item.value = val
        db.session.commit()
        flash('Statistics updated successfully!', 'success')
        
    stats = Stat.query.all()
    return render_template('admin/stats.html', stats=stats)

# ----------------- 404 Page Route -----------------

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# ----------------- App Start -----------------

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
