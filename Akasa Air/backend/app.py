# import os
# from flask import Flask, render_template, request, jsonify
# from pymongo import MongoClient
# import random
 

# # Set the current working directory
# current_directory = os.path.dirname(os.path.abspath(__file__))

# app = Flask(__name__, template_folder=os.path.join(current_directory, '..', 'templates'))

# # MongoDB connection
# client = MongoClient('mongodb://localhost:27017/')
# db = client['airline_preferences']
# users_collection = db['users']
# flights_collection = db['flights']


# @app.route('/')
# def index():
#     return render_template('index.html')

# @app.route('/register', methods=['POST'])
# def register_user():
#     user_id = request.form.get('user_id')
#     name = request.form.get('name')
#     flight_id = request.form.get('flight_id')  # Retrieve flight_id
#     seat = request.form.get('seat')
#     meal = request.form.get('meal')
#     baggage = request.form.get('baggage')

#     # Store user details
#     users_collection.insert_one({
#     "user_id": user_id,
#     "name": name,
#     "seat": seat,
#     "meal": meal,
#     "baggage": baggage,
#     "flight_id": flight_id  # Include flight_id in user details
# })


#     # Store some flight data for disruption management (mock data)
#     flights_collection.insert_one({
#     "flight_id": flight_id,  # Use the provided flight_id
#     "status": "on-time",
#     "predicted_delay": random.choice([0, 15, 30, 45, 60])  # Random delay prediction
# })


#     # Create preferences dictionary to pass to the template
#     preferences = {
#         "user_id": user_id,
#         "name": name,
#         "flight_id": flight_id,
#         "seat": seat,
#         "meal": meal,
#         "baggage": baggage
#     }

#     return render_template('result.html', message="User registered successfully!", preferences=preferences)


# @app.route('/check_disruption', methods=['GET'])
# def check_disruption():
#     flight_id = request.args.get('flight_id')
#     flight = flights_collection.find_one({"flight_id": flight_id})

#     if flight:
#         if flight["predicted_delay"] > 0:
#             return jsonify({
#                 "status": "Disruption detected!",
#                 "predicted_delay": flight["predicted_delay"],
#                 "suggestions": ["Alternative flight available", "Rescheduling options"]
#             }), 200
#         else:
#             return jsonify({"status": "Flight is on time!"}), 200
#     else:
#         return jsonify({"error": "Flight not found!"}), 404

# if __name__ == '__main__':
#     app.run(debug=True)

from pymongo import MongoClient
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from flask import Flask, render_template, request, jsonify
import random
import os

# Set the current working directory
current_directory = os.path.dirname(os.path.abspath(__file__))

# Initialize Flask app
app = Flask(__name__, template_folder=os.path.join(current_directory, '..', 'templates'))

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['airline_preferences']

# Retrieve synthetic user data
users_collection = db['synthetic_users']
users_df = pd.DataFrame(list(users_collection.find()))

# Retrieve flight data
flights_collection = db['flights']
flights_df = pd.DataFrame(list(flights_collection.find()))

def auto_fill_form(user_id):
    """Function to retrieve the most used information by user."""
    user_data = users_df[users_df['user_id'] == user_id]
    if not user_data.empty:
        return {
            'user_id': user_data.iloc[0]['user_id'],
            'name': user_data.iloc[0]['name'],
            'flight_id': user_data.iloc[0]['flight_id'],
            'seat': user_data.iloc[0]['seat'],
            'meal': user_data.iloc[0]['meal'],
            'baggage': user_data.iloc[0].get('baggage', '')  # Ensure 'baggage' exists
        }
    else:
        return None

# Prepare flight data for delay prediction
flights_df['delay'] = (flights_df['predicted_delay'] > 0).astype(int)
features = flights_df[['predicted_delay']]
labels = flights_df['delay']

# Split the dataset for training and testing
X_train, X_test, y_train, y_test = train_test_split(features, labels, test_size=0.2, random_state=42)

# Train the Random Forest model
model = RandomForestClassifier(n_estimators=100)
model.fit(X_train, y_train)

# Predict flight disruptions
predictions = model.predict(X_test)

# Evaluate the model
accuracy = accuracy_score(y_test, predictions)
print("Random Forest Model Accuracy for Flight Disruption Prediction:", accuracy)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_user_info/<user_id>', methods=['GET'])
def get_user_info(user_id):
    """Endpoint to get user information by user_id."""
    user = users_collection.find_one({"user_id": user_id})
    if user:
        return jsonify({
            "user_id": user["user_id"],
            "name": user["name"],
            "seat": user["seat"],
            "meal": user["meal"],
            "baggage": user["baggage"],
            "flight_id": user["flight_id"]
        }), 200
    else:
        return jsonify({"error": "User not found"}), 404

@app.route('/validate_flight/<flight_id>', methods=['GET'])
def validate_flight(flight_id):
    """Endpoint to validate if a flight exists."""
    flight = flights_collection.find_one({"flight_id": flight_id})
    if flight:
        return jsonify({"status": "Flight is available"}), 200
    else:
        return jsonify({"error": "Flight not found"}), 404

@app.route('/register', methods=['POST'])
def register_user():
    """Endpoint to register user preferences."""
    user_id = request.form.get('user_id')
    name = request.form.get('name')
    flight_id = request.form.get('flight_id')
    seat = request.form.get('seat')
    meal = request.form.get('meal')
    baggage = request.form.get('baggage')

    # Store user details in MongoDB
    users_collection.insert_one({
        "user_id": user_id,
        "name": name,
        "seat": seat,
        "meal": meal,
        "baggage": baggage,
        "flight_id": flight_id
    })

    # Store some flight data for disruption management (mock data)
    flights_collection.insert_one({
        "flight_id": flight_id,
        "status": "on-time",
        "predicted_delay": random.choice([0, 15, 30, 45, 60])
    })

    # Create preferences dictionary to pass to the template
    preferences = {
        "user_id": user_id,
        "name": name,
        "flight_id": flight_id,
        "seat": seat,
        "meal": meal,
        "baggage": baggage
    }

    return render_template('result.html', message="User registered successfully!", preferences=preferences)

@app.route('/user/<user_id>')
def user_profile(user_id):
    """Endpoint to display user profile with auto-filled form."""
    filled_form = auto_fill_form(user_id)
    if filled_form:
        return render_template('user_profile.html', user=filled_form)
    else:
        return render_template('user_profile.html', message="User not found")

@app.route('/flights')
def flights_status():
    """Endpoint to display flight status."""
    return render_template('flights.html', flights=flights_df.to_dict(orient='records'))

@app.route('/check_disruption', methods=['GET'])
def check_disruption():
    """Endpoint to check for flight disruptions."""
    flight_id = request.args.get('flight_id')
    flight = flights_collection.find_one({"flight_id": flight_id})

    if flight:
        if flight["predicted_delay"] > 0:
            return jsonify({
                "status": "Disruption detected!",
                "predicted_delay": flight["predicted_delay"],
                "suggestions": ["Alternative flight available", "Rescheduling options"]
            }), 200
        else:
            return jsonify({"status": "Flight is on time!"}), 200
    else:
        return jsonify({"error": "Flight not found!"}), 404

if __name__ == '__main__':
    app.run(debug=True)
