from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/admin/login', methods=['POST'])
def admin_login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    # Implement your authentication logic here
    response = {
        "responseCode": 200,
        "message": "Login successful",
        "status": "success"
    }
    return jsonify(response)

@app.route('/admin/list', methods=['GET'])
def admin_list():
    # Implement your logic to fetch the list of events here
    events = [
        {"name": "Event 1", "date": "2023-10-01", "time": "10:00 AM", "poster_link": "link1"},
        {"name": "Event 2", "date": "2023-10-02", "time": "11:00 AM", "poster_link": "link2"}
    ]
    response = {
        "responseCode": 200,
        "message": "List fetched successfully",
        "status": "success",
        "events": events
    }
    return jsonify(response)

@app.route('/admin/add/event', methods=['POST'])
def add_event():
    data = request.get_json()
    name = data.get('name')
    date = data.get('date')
    time = data.get('time')
    image = data.get('image')
    heads = data.get('heads')
    tags = data.get('tags')
    description = data.get('description')
    # Implement your logic to add the event here
    response = {
        "responseCode": 201,
        "message": "Event added successfully",
        "status": "success"
    }
    return jsonify(response)

@app.route('/admin/event/detail', methods=['POST'])
def event_detail():
    data = request.get_json()
    filters = data.get('filters')
    # Implement your logic to fetch event details here
    students_registered = [
        {"name": "Student 1", "id": "1"},
        {"name": "Student 2", "id": "2"}
    ]
    response = {
        "responseCode": 200,
        "message": "Event details fetched successfully",
        "status": "success",
        "students": students_registered
    }
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)