from flask import Flask, render_template, jsonify
import subprocess
import os

app = Flask(__name__)

# Global variable to hold the process
mouse_process = None

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/start')
def start_mouse():
    global mouse_process
    if mouse_process is None:
        # Start the script as a subprocess
        # Using "python" might default to a different env. Ensure we use the same python running this app or just "python" if path is set.
        try:
            mouse_process = subprocess.Popen(['python', 'ai_mouse.py'])
            return jsonify({"status": "started", "message": "Bhootiya Mouse Started!"})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)})
    else:
         # Check if it's still running
        if mouse_process.poll() is None:
            return jsonify({"status": "running", "message": "Already Running!"})
        else:
            # Restart
            mouse_process = subprocess.Popen(['python', 'ai_mouse.py'])
            return jsonify({"status": "started", "message": "Bhootiya Mouse Restarted!"})

@app.route('/stop')
def stop_mouse():
    global mouse_process
    if mouse_process is not None:
        mouse_process.terminate()
        mouse_process = None
        return jsonify({"status": "stopped", "message": "Bhootiya Mouse Stopped!"})
    else:
        return jsonify({"status": "stopped", "message": "Not Running!"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
