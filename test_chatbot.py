import pytest
from chatbot import app  # Assuming your Flask app is in 'app.py'


@pytest.fixture
def client():
    with app.test_client() as client:
        yield client


# Add the test functions (from above) here
# 1. Test: User Type Prompt
# Description: Verify that the chatbot asks the user whether they are a full-time or part-time student.
def test_user_type_prompt(client):
    # Simulate a GET request to load the chatbot interface
    response = client.get('/')
    assert b"Welcome to the Student Orientation Chatbot! Are you a full-time or part-time student?" in response.data


# 2. Test: Correct Response for Full-Time Student
# Description: Ensure that after the user selects "full-time", the chatbot acknowledges it.
def test_full_time_student_response(client):
    response = client.post('/chat', json={"query": "full-time", "user_type": None})
    assert response.json['response'] == "Great! You're a full-time student. How can I help you?"


# 3. Test: Correct Response for Part-Time Student
# Description: Ensure that after the user selects "part-time", the chatbot acknowledges it.
def test_part_time_student_response(client):
    response = client.post('/chat', json={"query": "part-time", "user_type": None})
    assert response.json['response'] == "Great! You're a part-time student. How can I help you?"


# 4. Test: Welcome Speech Time for Part-Time Students
# Description: Verify that the chatbot responds with the correct time for the welcome speech when asked by a part-time student.
def test_ws_event_time_part_time(client):
    response = client.post('/chat', json={"query": "What time is the welcome speech?", "user_type": "part-time"})
    assert response.json[
               'response'] == "The Welcome Speech will be on 16 January 2025 from 09:00 AM to 09:05 AM at Block C. The speech will be given by the Deputy Vice-Chancellor, Singapore, and the Acting Campus Dean & Head of Learning, Teaching, and Student Engagement."


# 5. Test: Welcome Speech Time for Full-Time Students
# Description: Verify that the chatbot responds with the correct time for the welcome speech when asked by a full-time student.
def test_ws_event_time_full_time(client):
    response = client.post('/chat', json={"query": "What time is the welcome speech?", "user_type": "full-time"})
    assert response.json['response'] == "The Welcome Speech will be on 16 January 2025 from 09:00 AM to 09:05 AM."


# 6. Test: Welcome Speech Venue for Part-Time Students
# Description: Verify that the chatbot provides the correct venue for the welcome speech when asked by a part-time student.
def test_ws_venue_part_time(client):
    response = client.post('/chat', json={"query": "Where will the welcome speech be held?", "user_type": "part-time"})
    assert response.json[
               'response'] == "The Welcome Speech will take place at Block C, James Cook University Singapore."


# 7. Test: Welcome Speech Venue for Full-Time Students
# Description: Verify that the chatbot provides the correct venue for the welcome speech when asked by a full-time student.
def test_ws_venue_full_time(client):
    response = client.post('/chat', json={"query": "Where will the welcome speech be held?", "user_type": "full-time"})
    assert response.json['response'] == "The Welcome Speech will be on 16 January 2025 at Block C."


# 8. Test: Academic Briefing Time for Part-Time Students
# Description: Ensure that the chatbot provides the correct academic briefing time for part-time students.
def test_ab_briefing_time_part_time(client):
    response = client.post('/chat', json={"query": "What time is the academic briefing scheduled for?",
                                          "user_type": "part-time"})
    assert response.json[
               'response'] == "The Academic Briefing will take place on 16 January 2025, from 07:25 PM to 08:30 PM."


# 9. Test: Academic Briefing Time for Full-Time Students
# Description: Ensure that the chatbot provides the correct academic briefing time for full-time students.
def test_ab_briefing_time_full_time(client):
    response = client.post('/chat', json={"query": "What time is the academic briefing scheduled for?",
                                          "user_type": "full-time"})
    assert response.json[
               'response'] == "Academic Advising will take place on 16 January 2025 from 10:40 AM to 11:40 AM in breakout rooms."


# 10. Test: Eligible Courses List for Part-Time Students
# Description: Ensure that the chatbot lists the eligible courses for part-time students.
def test_eligible_courses_part_time(client):
    response = client.post('/chat', json={"query": "Which courses are available for the Welcome Speech?",
                                          "user_type": "part-time"})
    assert response.json[
               'response'] == "The eligible courses for the Welcome Speech are:\n- Part-Time Diploma of Higher Education (Psychological Science)\n- Part-Time Bachelor of Psychological Science\n- Part-Time Master of Guidance and Counselling\n- Part-Time Business Programs"


# 11. Test: Eligible Courses List for Full-Time Students
# Description: Ensure that the chatbot lists the eligible courses for full-time students.
def test_eligible_courses_full_time(client):
    response = client.post('/chat', json={"query": "Which courses are available for the Welcome Speech?",
                                          "user_type": "full-time"})
    assert response.json[
               'response'] == "The eligible courses for the Welcome Speech are:\n- Full-Time Diploma of Higher Education (Psychological Science)\n- Full-Time Bachelor of Psychological Science\n- Full-Time Master of Guidance and Counselling\n- Full-Time Business Programs"


# 12. Test: DigiLearn Workshop Time for Full-Time Students
# Description: Verify that the chatbot provides the correct DigiLearn workshop time for full-time students.
def test_digi_learn_workshop_full_time(client):
    response = client.post('/chat', json={"query": "When is the DigiLearn workshop?", "user_type": "full-time"})
    assert response.json[
               'response'] == "The DigiLearn workshop is on 16 January 2025 from 09:10 AM to 10:25 AM at Block C. It will help you get started with the virtual learning environment and online collaboration spaces at JCU."


# 13. Test: Network with Lecturers Session Time
# Description: Verify that the chatbot provides the correct time for the network with lecturers session.
def test_network_with_lecturers_time(client):
    response = client.post('/chat',
                           json={"query": "When is the network with lecturers session?", "user_type": "full-time"})
    assert response.json[
               'response'] == "The session will be on 16 January 2025 from 03:00 PM to 05:00 PM at the Multi-Purpose Hall."


# 14. Test: Invalid Query Handling
# Description: Verify that the chatbot responds appropriately when an invalid query is entered.
def test_invalid_query_handling(client):
    response = client.post('/chat', json={"query": "How can I enroll?", "user_type": "full-time"})
    assert response.json['response'] == "Sorry, I don't understand that. Can you please ask something else?"


# 15. Test: Chatbot Initialization
# Description: Ensure the chatbot initializes correctly and sends the first welcome message when the page is loaded.
def test_chatbot_initialization(client):
    response = client.get('/')
    assert b'Chatbot' in response.data
    assert b"Welcome to the Student Orientation Chatbot!" in response.data
