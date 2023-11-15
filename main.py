from flask import Flask, render_template, request, redirect, url_for
from flask_socketio import SocketIO, join_room, leave_room, send

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

rooms = {}  # Dictionary to keep track of rooms and their occupancy

def create_room(roomID):
    template = {
        "roomID": roomID,
        "roomLimit": 2,
        "occupancy": 0,
        "users": []  # List of users in the room", the list filling with the names
    }
    rooms[roomID] = template

def edit_room(roomID, key, value):
    if key == "roomLimit":
        if value < 2:
            return "Room limit cannot be less than 2", 403
        else:
            rooms[roomID][key] = value
    else:
        rooms[roomID][key] = value

def add_user(roomID, userName):
    rooms[roomID]["users"].append(userName)
    # 更新当前occupancy
    rooms[roomID]["occupancy"] += 1

def delete_user(roomID, userName):
    rooms[roomID]["users"].remove(userName)
    # 更新当前occupancy
    rooms[roomID]["occupancy"] -= 1

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/room/<roomID>/<userName>')
def room(roomID, userName):
    # 创建房间
    create_room(roomID)
    print(rooms)
    return render_template('room.html', roomID=roomID, userName=userName)

@socketio.on('join')
def on_join(data):
    username = data['username']
    room = data['room']
    join_room(room)
    # 加入房间
    add_user(room, username)
    send(f"SYSTEM##{username} has entered the room.", room=room)

@socketio.on('leave')
def on_leave(data):
    username = data['username']
    room = data['room']
    leave_room(room)
    # 离开房间
    delete_user(room, username)
    send(f"SYSTEM##{username} has left the room.", room=room)

@socketio.on('update')
def on_update(data):
    # 如果不是以EDIT##开头，则表示是获取
    room = data['room']
    key = data['key']
    value = data['value']
    edit_room(room, key, value)
    send(f"SYSTEM##{key} has been updated to {value}.", room=room)

@socketio.on('message')
def handle_message(data):
    send(data['msg'], room=data['room'])

if __name__ == '__main__':
    socketio.run(app, debug=True)
