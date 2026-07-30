import json
from app import db, User, Project, Blog, Certificate, Stat, app
from werkzeug.security import generate_password_hash

def seed_database():
    with app.app_context():
        print("Initializing database tables...")
        db.create_all()
        
        # 1. Create Default Admin User
        if not User.query.filter_by(username='admin').first():
            print("Registering default admin credentials...")
            hashed_pwd = generate_password_hash('admin123')
            admin = User(username='admin', password_hash=hashed_pwd)
            db.session.add(admin)
        else:
            print("Admin user already exists.")
            
        # 2. Seed Default Statistics
        stats_to_seed = [
            {"key": "Projects Completed", "value": "15", "icon": "fa-project-diagram"},
            {"key": "GitHub Repositories", "value": "22", "icon": "fab fa-github"},
            {"key": "Certifications", "value": "12", "icon": "fa-certificate"},
            {"key": "Coding Hours", "value": "800+", "icon": "fa-hourglass-half"},
            {"key": "Technologies Learned", "value": "18", "icon": "fa-laptop-code"},
            {"key": "ML Models Built", "value": "25+", "icon": "fa-brain"}
        ]
        
        for s in stats_to_seed:
            if not Stat.query.filter_by(key=s["key"]).first():
                print(f"Seeding statistic counter: {s['key']}...")
                db.session.add(Stat(key=s["key"], value=s["value"], icon=s["icon"]))
                
        # 3. Seed Default Certifications
        certs_to_seed = [
            {
                "name": "Machine Learning Specialization",
                "organization": "Stanford University & DeepLearning.AI",
                "issue_date": "March 2024",
                "credential_url": "https://coursera.org/verify/specialization/ML"
            },
            {
                "name": "TensorFlow Developer Professional Certificate",
                "organization": "DeepLearning.AI",
                "issue_date": "June 2024",
                "credential_url": "https://coursera.org/verify/specialization/TF"
            },
            {
                "name": "Google Data Analytics Professional Certificate",
                "organization": "Google",
                "issue_date": "September 2023",
                "credential_url": "https://coursera.org/verify/specialization/DA"
            }
        ]
        
        for c in certs_to_seed:
            if not Certificate.query.filter_by(name=c["name"]).first():
                print(f"Seeding certificate: {c['name']}...")
                db.session.add(Certificate(
                    name=c["name"],
                    organization=c["organization"],
                    issue_date=c["issue_date"],
                    credential_url=c["credential_url"]
                ))
                
        # 4. Seed Default Blog Posts
        blogs_to_seed = [
            {
                "title": "Introduction to Supervised Machine Learning",
                "slug": "intro-supervised-ml",
                "summary": "An introductory overview of regression, classification trees, and parameter validation folds.",
                "category": "Machine Learning",
                "tags": "AI, ML, Supervised Learning",
                "content": """<h3>Understanding Supervised Learning</h3>
<p>Supervised learning represents a class of machine learning models trained on labeled datasets. It means that for every input row vector, there is a corresponding target value. The algorithm learns a mathematical mapping function from inputs to outputs.</p>
<h3>Regression vs Classification</h3>
<p>There are two primary subfields of supervised machine learning:</p>
<ul>
    <li><strong>Regression:</strong> Predicting continuous numerical values (e.g. predicting house prices or temperature).</li>
    <li><strong>Classification:</strong> Predicting discrete category labels (e.g. classifying emails as spam/ham or patients as healthy/sick).</li>
</ul>
<h3>Key Steps in Model Evaluation</h3>
<p>To ensure a model generalizes well to unseen data, we split datasets into training, validation, and testing folds. Using cross-validation splits helps identify overfitting early and ensures model accuracy is stable across different partitions.</p>"""
            },
            {
                "title": "Deep Learning Foundations: Artificial Neural Networks",
                "slug": "deep-learning-foundations",
                "summary": "Explores how perceptrons work, activation functions, backpropagation gradients, and compiling layered ANNs.",
                "category": "Deep Learning",
                "tags": "AI, Deep Learning, TensorFlow",
                "content": """<h3>What is a Neural Network?</h3>
<p>Deep Learning is a specialized branch of machine learning powered by Artificial Neural Networks (ANNs). These architectures are inspired by the biological connections in human brains, allowing computer systems to extract highly non-linear feature maps directly from raw inputs.</p>
<h3>Perceptrons and Activations</h3>
<p>The core computational unit is the artificial neuron (perceptron). It calculates a weighted sum of inputs, adds a bias term, and runs it through an activation function:</p>
<ul>
    <li><strong>Sigmoid:</strong> Maps outputs between 0 and 1, ideal for binary classification probabilities.</li>
    <li><strong>ReLU (Rectified Linear Unit):</strong> Converts negative values to 0 and passes positive values directly, preventing vanishing gradients in deep layers.</li>
</ul>
<h3>Training with Backpropagation</h3>
<p>During training, inputs pass forward through the network layers to calculate predictions. The error (loss) is calculated, and backpropagation gradients flow backwards through the network to update the weights, minimizing loss using optimization algorithms like Adam.</p>"""
            }
        ]
        
        for b in blogs_to_seed:
            if not Blog.query.filter_by(slug=b["slug"]).first():
                print(f"Seeding blog post: {b['title']}...")
                db.session.add(Blog(
                    title=b["title"],
                    slug=b["slug"],
                    summary=b["summary"],
                    category=b["category"],
                    tags=b["tags"],
                    content=b["content"]
                ))
                
        # 5. Seed Dynamic Interactive Projects
        projects_to_seed = [
            {
                "name": "Heart Disease Prediction",
                "slug": "heart-disease-prediction",
                "category": "Machine Learning",
                "algorithm": "Logistic Regression",
                "accuracy": 0.85,
                "precision": 0.84,
                "recall": 0.86,
                "f1_score": 0.85,
                "status": "Completed",
                "tags": "Python, Scikit-learn, Classification, Health",
                "description": "Predicts the presence of heart disease based on clinical patient metrics like age, cholesterol, chest pain, and blood pressure.",
                "github_link": "https://github.com/jawad/heart-disease-predictor",
                "is_featured": True,
                "is_interactive": True,
                "model_filename": "heart_disease_model.joblib",
                "problem_statement": "Heart disease remains a leading cause of mortality globally. Early diagnostic prediction using common medical indices (age, resting blood pressure, cholesterol levels) can enable preventative interventions. The goal of this project was to train an optimized classifier that identifies patients at risk with high recall.",
                "dataset_info": "The database contains medical patient entries with 8 key input parameters: age, sex, chest pain type (cp: 0-3), resting blood pressure (trestbps), serum cholesterol (chol), fasting blood sugar (fbs), maximum heart rate achieved (thalach), and exercise-induced angina (exang).",
                "data_cleaning": "Missing values were imputed using column medians, and categorical variables (like chest pain type) were converted into integers. No critical outliers were found.",
                "feature_engineering": "Numerical features (cholesterol, blood pressure, heart rate) were scaled using StandardScaler to ensure optimal convergence speed for gradient solvers.",
                "training_process": "Logistic Regression was trained using 5-fold cross-validation. L2 regularization (C=1.0) was used to avoid over-fitting on high age metrics.",
                "evaluation_metrics": "The final model achieves an accuracy of 85.0% on the test split. F1-score is balanced at 85.0%, and recall is at 86.0%, which is crucial to minimize false negatives in medical diagnostics.",
                "future_improvements": "Integrate Random Forests or Gradient Boosted Trees (XGBoost) to evaluate potential classification margin improvements.",
                "conclusion": "Linear boundary classification with logistic weights provides a highly interpretable and robust clinical screening utility.",
                "inputs_schema": json.dumps([
                    {"name": "age", "label": "Age (years)", "type": "number", "min": 1, "max": 120, "default": 45},
                    {"name": "sex", "label": "Sex (Gender)", "type": "select", "options": [{"label": "Male", "value": 1}, {"label": "Female", "value": 0}], "default": 1},
                    {"name": "cp", "label": "Chest Pain Type", "type": "select", "options": [{"label": "Typical Angina", "value": 0}, {"label": "Atypical Angina", "value": 1}, {"label": "Non-anginal Pain", "value": 2}, {"label": "Asymptomatic", "value": 3}], "default": 1},
                    {"name": "trestbps", "label": "Resting Blood Pressure (mm Hg)", "type": "number", "min": 50, "max": 250, "default": 120},
                    {"name": "chol", "label": "Serum Cholesterol (mg/dl)", "type": "number", "min": 100, "max": 600, "default": 200},
                    {"name": "fbs", "label": "Fasting Blood Sugar > 120 mg/dl", "type": "select", "options": [{"label": "True", "value": 1}, {"label": "False", "value": 0}], "default": 0},
                    {"name": "thalach", "label": "Maximum Heart Rate Achieved", "type": "number", "min": 50, "max": 220, "default": 150},
                    {"name": "exang", "label": "Exercise Induced Angina", "type": "select", "options": [{"label": "Yes", "value": 1}, {"label": "No", "value": 0}], "default": 0}
                ])
            },
            {
                "name": "House Price Prediction",
                "slug": "house-price-prediction",
                "category": "Machine Learning",
                "algorithm": "Linear Regression",
                "accuracy": 0.88,
                "precision": None,
                "recall": None,
                "f1_score": None,
                "status": "Completed",
                "tags": "Python, Scikit-learn, Regression, Real Estate",
                "description": "Predicts real estate sales valuations based on structural house building features (bedrooms, bathrooms, sqft, year built).",
                "github_link": "https://github.com/jawad/house-price-predictor",
                "is_featured": True,
                "is_interactive": True,
                "model_filename": "house_price_model.joblib",
                "problem_statement": "Estimating property values accurately is vital for home buyers, sellers, and mortgage lenders. The goal is to build an interpretable multivariate regression model that uses size, rooms count, and age variables to predict the valuation.",
                "dataset_info": "The data features cover dimensions like bedrooms count, bathrooms count, living area square footage (sqft), total land lot size (lotsize), and the construction year (year_built).",
                "data_cleaning": "Removed rows containing zero bedrooms. Sqft and price fields were transformed to handle skewness.",
                "feature_engineering": "A house age feature was engineered by subtracting YearBuilt from the current year.",
                "training_process": "Multi-variable Linear Regression model was fitted on an 80/20 train/test split. Cross-validation validated coefficient stability.",
                "evaluation_metrics": "The model achieves an R-squared value of 0.88 (accuracy proxy), explaining 88% of price variance. Mean Absolute Error is around $15,000.",
                "future_improvements": "Implement Lasso and Ridge regression to penalize coefficients and test if model generalizes better on larger lot sizes.",
                "conclusion": "A simple multivariate linear model provides a fast, transparent property valuation baseline.",
                "inputs_schema": json.dumps([
                    {"name": "bedrooms", "label": "Bedrooms Count", "type": "number", "min": 1, "max": 10, "default": 3},
                    {"name": "bathrooms", "label": "Bathrooms Count", "type": "number", "min": 1, "max": 10, "default": 2},
                    {"name": "sqft", "label": "Living Area Size (SqFt)", "type": "number", "min": 100, "max": 10000, "default": 2000},
                    {"name": "lotsize", "label": "Lot Size (SqFt)", "type": "number", "min": 100, "max": 100000, "default": 5000},
                    {"name": "year_built", "label": "Year Built", "type": "number", "min": 1800, "max": 2026, "default": 2000}
                ])
            },
            {
                "name": "Diabetes Prediction",
                "slug": "diabetes-prediction",
                "category": "Machine Learning",
                "algorithm": "Decision Tree",
                "accuracy": 0.82,
                "precision": 0.81,
                "recall": 0.80,
                "f1_score": 0.80,
                "status": "Completed",
                "tags": "Python, Scikit-learn, Classification, Medical",
                "description": "Predicts whether a patient has diabetes based on diagnostic patient records like glucose, insulin, and BMI.",
                "github_link": "https://github.com/jawad/diabetes-predictor",
                "is_featured": True,
                "is_interactive": True,
                "model_filename": "diabetes_model.joblib",
                "problem_statement": "Diabetes is a chronic illness that requires proactive management. Implementing machine learning predictors using demographic and physiological diagnostic indicators can identify risk early.",
                "dataset_info": "Features include Pregnancies, Glucose, BloodPressure, SkinThickness, Insulin, BMI, DiabetesPedigreeFunction, and Age.",
                "data_cleaning": "Zero values in fields like BloodPressure and Glucose were replaced with the median values, as zero is physiologically impossible for these measures.",
                "feature_engineering": "BMI and Glucose parameters were grouped into categorical risk levels to analyze split decisions.",
                "training_process": "A Decision Tree Classifier was trained. Cost complexity pruning (max_depth=5) was applied to prevent deep branch overfitting.",
                "evaluation_metrics": "The model yields an accuracy of 82.0% on the test split, with a precision of 81.0% and an F1-Score of 80.0%.",
                "future_improvements": "Train an Ensemble Random Forest or Gradient Boosting machine to improve classifier boundaries.",
                "conclusion": "Decision tree splits provide clean, traceable decision pathways for medical screening.",
                "inputs_schema": json.dumps([
                    {"name": "pregnancies", "label": "Pregnancies Count", "type": "number", "min": 0, "max": 20, "default": 1},
                    {"name": "glucose", "label": "Plasma Glucose Concentration", "type": "number", "min": 0, "max": 300, "default": 120},
                    {"name": "bp", "label": "Diastolic Blood Pressure (mm Hg)", "type": "number", "min": 0, "max": 150, "default": 80},
                    {"name": "skin", "label": "Triceps Skin Fold Thickness (mm)", "type": "number", "min": 0, "max": 100, "default": 20},
                    {"name": "insulin", "label": "2-Hour Serum Insulin (mu U/ml)", "type": "number", "min": 0, "max": 900, "default": 80},
                    {"name": "bmi", "label": "Body Mass Index (BMI)", "type": "number", "min": 0, "max": 70, "default": 32.0},
                    {"name": "pedigree", "label": "Diabetes Pedigree Function", "type": "number", "min": 0.01, "max": 3.0, "default": 0.5},
                    {"name": "age", "label": "Age (years)", "type": "number", "min": 21, "max": 100, "default": 33}
                ])
            }
        ]
        
        for p in projects_to_seed:
            if not Project.query.filter_by(slug=p["slug"]).first():
                print(f"Seeding project: {p['name']}...")
                db.session.add(Project(
                    name=p["name"],
                    slug=p["slug"],
                    category=p["category"],
                    algorithm=p["algorithm"],
                    accuracy=p["accuracy"],
                    precision=p["precision"],
                    recall=p["recall"],
                    f1_score=p["f1_score"],
                    status=p["status"],
                    tags=p["tags"],
                    description=p["description"],
                    github_link=p["github_link"],
                    is_featured=p["is_featured"],
                    is_interactive=p["is_interactive"],
                    model_filename=p["model_filename"],
                    problem_statement=p["problem_statement"],
                    dataset_info=p["dataset_info"],
                    data_cleaning=p["data_cleaning"],
                    feature_engineering=p["feature_engineering"],
                    training_process=p["training_process"],
                    evaluation_metrics=p["evaluation_metrics"],
                    future_improvements=p["future_improvements"],
                    conclusion=p["conclusion"],
                    inputs_schema=p["inputs_schema"]
                ))
                
        db.session.commit()
        print("Database seeding completed successfully!")

if __name__ == '__main__':
    seed_database()
