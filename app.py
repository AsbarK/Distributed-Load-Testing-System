import os
from flask import Flask, render_template, request

app = Flask(__name__)
pwd = os.getcwd()
print(pwd)
def run_driver_node(driver_id):
    command = f"python3 {pwd}/driverNode.py localhost:9092 localhost:9092"
    os.system(f"osascript -e 'tell application \"Terminal\" to do script \"{command}\"'")

@app.route('/')
def index():
    return render_template('tesss.html')

@app.route('/run-orchestration', methods=['POST'])
def run_orchestration_route():
    num_drivers = int(request.form['num_drivers'])
    test_type = request.form['test_type']
    
    # Check if 'delay' is empty or not provided
    delay = request.form['delay']
    delay = int(delay) if delay and delay.isdigit() else 0
    
    num_messages = int(request.form['num_messages'])

    print(num_drivers, num_messages)

    # Run orchestration node
    orchestration_command = f"python3 {pwd}/orchetratorNode.py {num_drivers} {test_type} {delay} {num_messages}"
    os.system(f"osascript -e 'tell application \"Terminal\" to do script \"{orchestration_command}\"'")

    # Run driver nodes
    for i in range(num_drivers):
        run_driver_node(i + 1)

    return "Orchestration and Drivers started successfully!"

if __name__ == '__main__':
    app.run(debug=True)