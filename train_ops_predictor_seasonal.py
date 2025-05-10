import pandas as pd
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from sklearn.metrics import mean_squared_error
import numpy as np

def load_data(file_path):
    data = pd.read_csv(file_path)
    
    for col in data.select_dtypes(exclude=['object']).columns:
        data[col] = data[col].astype('float32')

    return data

def build_model(input_dim):
    model = Sequential([
        Dense(64, activation='relu', input_dim=input_dim),
        Dense(32, activation='relu'),
        Dense(1)  # Assuming regression task
    ])
    model.compile(optimizer='adam', loss='mse', metrics=['mae'])
    return model

def train_and_evaluate(X_train, X_test, y_train, y_test):
    input_dim = X_train.shape[1]
    model = build_model(input_dim)

    print(X_train.dtypes)

    print(f"Are there NaNs in X_train? {np.isnan(X_train).any()}")
    print(f"Are there NaNs in X_test? {np.isnan(X_test).any()}")
    print(f"Are there Infs in X_train? {np.isinf(X_train).any()}")
    print(f"Are there Infs in X_test? {np.isinf(X_test).any()}")
    print(f"X_train stats: min={X_train.min()}, max={X_train.max()}, mean={X_train.mean()}")
    print(f"X_test stats: min={X_test.min()}, max={X_test.max()}, mean={X_test.mean()}")
    
    history = model.fit(X_train, y_train, epochs=10000, batch_size=32, validation_split=0.2, verbose=1)
    
    predictions = model.predict(X_test)

    mse = mean_squared_error(y_test, predictions)
    print(f"Mean Squared Error on Test Data: {mse}")

    # Save the model
    model.save('player_ops_model_seasonal.h5')

    return model

if __name__ == "__main__":
    # Replace with actual file paths
    X_train = load_data('X_train_seasonal.csv')
    X_test = load_data('X_test_seasonal.csv')
    y_train = load_data('y_train_seasonal.csv')
    y_test = load_data('y_test_seasonal.csv')
    
    trained_model = train_and_evaluate(X_train, X_test, y_train, y_test)