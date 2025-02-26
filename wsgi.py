from website import create_app, socketio

app = create_app()

if __name__ == "__main__":
    #app.run(host="0.0.0.0", port="5000", debug=True)
    socketio.run(app, debug=True, log_output=True)
