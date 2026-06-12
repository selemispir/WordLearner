def init_sockets(socketio):

    @socketio.on("send_message")
    def handle_message(data):
        username = data.get("username", "Anonymous")
        message = data.get("message", "")

        socketio.emit("receive_message", {
            "username": username,
            "message": message
        })