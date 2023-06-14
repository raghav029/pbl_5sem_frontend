from flask import Flask, jsonify, request, session
# from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_session import Session
from models import db, User, Events, event_schema, events_schema, user_schema, users_schema, UserEvent, UserEvent_schema, UserEvents_schema, EventSchema
from config import ApplicationConfig
from flask_cors import CORS

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.config.from_object(ApplicationConfig)
db.init_app(app)

server_session = Session(app)
bcrypt = Bcrypt(app)
# migrate = Migrate(app, db)


# ****Events Routes****
@app.route('/get/', methods=['GET'])
def getEvents():
    all_events = Events.query.all()
    results = events_schema.dump(all_events)
    # results.headers.add('Access-Control-Allow-Origin', '*')
    return jsonify(results)

@app.route("/get/<id>/", methods=['GET'])
def getEventById(id):
    event = Events.query.get(id)
    return event_schema.jsonify(event)


@app.route('/add', methods=['POST'])
def add_event():
    image = request.json['image']
    title = request.json['title']
    description = request.json['description']
    dept = request.json['dept']

    event = Events(image, title, description, dept)
    db.session.add(event)
    db.session.commit()
    return event_schema.jsonify(event)

# ****End Events Routes****


# ****User Routes****
@app.route('/@me')
def get_current_user():
    user_id = session.get('user_id')

    if not user_id:
        return jsonify("Unauthorised asscess"), 401
    user = User.query.filter_by(id=user_id).first()

    return user_schema.jsonify(user)

@app.route('/register', methods=['POST'])
def register_new_user():
    username = request.json['username']
    usn = request.json['usn']
    email = request.json['email']
    ph_number = request.json['ph_number']
    password = request.json['password']

    user_exist = User.query.filter_by(email=email).first() is not None
    if user_exist:
        return jsonify("Unauthorised asscess"), 401

    hashed_password = bcrypt.generate_password_hash(password)
    new_user = User(usn=usn, email=email, password=hashed_password, ph_number=ph_number, username=username)
    db.session.add(new_user)
    db.session.commit()

    session['user_id'] = new_user.id

    return user_schema.jsonify(new_user)
    

@app.route('/login', methods=['POST'])
def login_user():
    # email = request.json['email']
    username = request.json['username']
    password = request.json['password']

    user =  User.query.filter_by(username=username).first()
    
    if user is None:
        return jsonify("Unauthorised access"), 401
    
    if not bcrypt.check_password_hash(user.password, password):
        return jsonify("Unauthorised access"), 401
    
    session["user_id"] = user.id
    return user_schema.jsonify(user)

@app.route('/logout', methods=['POST'])
def logout_user():
    if 'user_id' in session:
        session.pop('user_id')
    return '200'

# ****End User Routes****


# ****UserEvent Routes****
@app.route('/userEvents', methods=['POST'])
def user_events():
    user_id = session.get('user_id')
    # check if user exist
    if not user_id:
        return jsonify("Unauthorised asscess"), 401
    
    # get the event id
    event_id = request.json['event_id']

    user_event = UserEvent.query.filter_by(user_id=user_id, event_id=event_id).first()
    if user_event:
        user_event.applied = True
    else:
        user_event = UserEvent(user_id=user_id, event_id=event_id, applied=True)
        db.session.add(user_event)
    
    db.session.commit()

    return UserEvent_schema.jsonify(user_event)

@app.route('/getUserEvents')
def get_current_user_events():
    user_id = session.get('user_id')
    # check if user exist
    if not user_id:
        return jsonify("Unauthorised asscess"), 401
    # retrieve all the events user applied for
    user_events = UserEvent.query.filter(UserEvent.user_id == user_id).all()

    if not user_events:
        return jsonify("No events selected")
    
    # retrieve events details for each user_event
    event_ids = [user_event.event_id for user_event in user_events]
    events = Events.query.filter(Events.id.in_(event_ids)).all()

    event_data = events_schema.dump(events)

    return jsonify(event_data)

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(host='192.168.0.104', port=3000, debug=True)
