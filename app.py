import os
from flask import Flask, render_template, request, jsonify, redirect, url_for



app = Flask(__name__)
pwd = os.getcwd()
print(pwd)
def run_driver_node(driver_id):
    command = f"python3 {pwd}/driverNode.py localhost:9092 localhost:9092"
    os.system(f"osascript -e 'tell application \"Terminal\" to do script \"{command}\"'")

@app.route('/')
def index():
    return render_template('tesss.html')

metric_result = {}       
prev_metric_result = {}
heartBeat = {}

@app.route('/update_metrics', methods=['POST'])
def update_metrics():
    global metric_result, prev_metric_result
    data = request.json
    current_metrics = data['metric_result']
    prev_metric_result = metric_result.copy()

    for node_id, metrics_per_test in current_metrics.items():
        if node_id not in metric_result:
            metric_result[node_id] = {}
        
        for test_id, metrics in metrics_per_test.items():
            if test_id not in metric_result[node_id] or metric_result[node_id][test_id] != metrics:
                metric_result[node_id][test_id] = metrics
    
    print("Updated metric results:", metric_result)
    return jsonify({"status": "success"})
@app.route('/heartbeat', methods=['POST'])
def heartbeat():
    global heartBeat
    data = request.json
    heartBeat[data['heartbeat']['node_id']] = data['heartbeat']
    return jsonify({"status": "success"})

@app.route('/metrics')
def metrics():
    global metric_result,heartBeat
    return render_template('metrics.html', metric_result=metric_result,heartBeat=heartBeat)
@app.route('/run-orchestration', methods=['POST'])
def run_orchestration_route():
    num_drivers = int(request.form['num_drivers'])
    test_type = request.form['test_type']
    
    delay = request.form['delay']
    delay = int(delay) if delay and delay.isdigit() else 0
    
    num_messages = int(request.form['num_messages'])

    

    orchestration_command = f"python3 {pwd}/orchetratorNode.py {num_drivers} {test_type} {delay} {num_messages}"
    os.system(f"osascript -e 'tell application \"Terminal\" to do script \"{orchestration_command}\"'")

    # Run driver nodes
    for i in range(num_drivers):
        run_driver_node(i + 1)

    # Redirect to the 'metrics' endpoint
    return redirect(url_for('metrics'))

if __name__ == '__main__':
    app.run(debug=True)
