import os

# Set environment variables to suppress logs
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'  # Disable oneDNN optimizations
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # Suppress all TensorFlow logs

import pandas as pd
import numpy as np
from keras.models import Sequential
from keras.layers import Dense
from pymongo import MongoClient

def generate_synthetic_user_data(num_samples):
    # Connect to MongoDB
    client = MongoClient('mongodb://localhost:27017/')
    db = client['airline_preferences']
    users_collection = db['synthetic_users']  # Collection to store synthetic users

    # Define a simple GAN-like model (for example purposes)
    model = Sequential()
    model.add(Dense(256, input_dim=100, activation='relu'))
    model.add(Dense(128, activation='relu'))
    model.add(Dense(5, activation='sigmoid'))  # Output layer for 5 user attributes

    # Compile the model
    model.compile(loss='binary_crossentropy', optimizer='adam')

    # Generate random noise as input
    noise = np.random.normal(0, 1, size=[num_samples, 100])
    
    # Generate synthetic data
    synthetic_data = model.predict(noise)

    # Create a DataFrame from synthetic data
    synthetic_users_df = pd.DataFrame(synthetic_data, columns=['user_id', 'name', 'flight_id', 'seat', 'meal'])

    # Scale the data or format it appropriately if needed
    synthetic_users_df['user_id'] = synthetic_users_df['user_id'].apply(lambda x: f'user_{int(x*10000)}')  # Example formatting
    synthetic_users_df['name'] = synthetic_users_df['name'].apply(lambda x: f'Name_{int(x*100)}')
    synthetic_users_df['flight_id'] = synthetic_users_df['flight_id'].apply(lambda x: f'FL{int(x*1000)}')  # Example flight ID
    synthetic_users_df['seat'] = np.random.choice(['Aisle', 'Window', 'Middle'], num_samples)
    synthetic_users_df['meal'] = np.random.choice(['Vegetarian', 'Non-Vegetarian', 'Vegan'], num_samples)

    # Save to CSV
    synthetic_users_df.to_csv('synthetic_user_data_gan.csv', index=False)

    # Insert data into MongoDB
    users_collection.insert_many(synthetic_users_df.to_dict('records'))

    return synthetic_users_df

# Generate the synthetic data
num_samples = 1000
generate_synthetic_user_data(num_samples)
