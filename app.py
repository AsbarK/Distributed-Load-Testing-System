from flask import Flask, render_template, request
import subprocess
import time

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('tesss.html')

@app.route('/run-orchestration', methods=['POST'])
def run_orchestration():
    num_drivers = int(request.form['num_drivers'])
    test_type = request.form['test_type']
    
    # Check if 'delay' is empty or not provided
    delay = request.form['delay']
    delay = int(delay) if delay and delay.isdigit() else 0
    
    num_messages = int(request.form['num_messages'])

    print(num_drivers, num_messages)

    # Run orchestration node
    # orchestration_command = "orchetratorNode.py {} {} {} {}".format(num_drivers, test_type, delay, num_messages)
    orchestration_result = subprocess.run(["python3",'orchetratorNode.py',str(num_drivers),str(test_type),str(delay),str(num_messages)],  capture_output=True, text=True)
    print("Orchestration Output:", orchestration_result.stdout)
    print("Orchestration Error:", orchestration_result.stderr)

    # Run driver nodes
    for i in range(num_drivers):
        # driver_command = "driverNode.py localhost:9092 localhost:9092 {} {} {}".format(test_type, delay, num_messages)
        driver_result = subprocess.run(["python3",'driverNode.py','localhost:9092','localhost:9092'],  capture_output=True, text=True)
        print(f"Driver Node {i + 1} Output:", driver_result.stdout)
        print(f"Driver Node {i + 1} Error:", driver_result.stderr)
        time.sleep(2)

    return "Orchestration and Drivers started successfully!"

if __name__ == '__main__':
    app.run(debug=True)
