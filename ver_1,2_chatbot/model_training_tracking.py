import logging

from model_training import model, X_test, y_train, X_train, y_test

# Set up logging
logging.basicConfig(filename='model_training.log', level=logging.INFO, format='%(asctime)s - %(message)s')

# Log training process
logging.info("Starting model training...")
model.fit(X_train, y_train)
logging.info("Model training completed.")

# Log model accuracy
accuracy = model.score(X_test, y_test)
logging.info(f"Model accuracy: {accuracy * 100:.2f}%")