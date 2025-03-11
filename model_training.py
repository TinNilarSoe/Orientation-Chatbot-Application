from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
import pickle

from data_preparation import vectorizer, tags, X

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, tags, test_size=0.2, random_state=42)

# Train model
model = MultinomialNB()
model.fit(X_train, y_train)

# Save model and vectorizer
with open('chatbot_model.pkl', 'wb') as model_file:
    pickle.dump(model, model_file)

with open('vectorizer.pkl', 'wb') as vectorizer_file:
    pickle.dump(vectorizer, vectorizer_file)