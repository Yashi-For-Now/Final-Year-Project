from flask import Flask, request, jsonify, render_template, url_for
import numpy as np
import random, math
app = Flask(__name__)

#User input storage dictionary
userInputData={}

# dummy data
wifi_database = {
        "00:11:22:33:44:55": {"lat": 37.774943, "lng": -122.419345},
        "AA:BB:CC:DD:EE:FF": {"lat": 37.774875, "lng": -122.419410},
        "11:22:33:44:55:66": {"lat": 37.774797, "lng": -122.419275}, 
        "22:33:44:55:66:77": {"lat": 40.712830, "lng": -74.005985},
        "33:44:55:66:77:88": {"lat": 40.712756, "lng": -74.006049},
        "44:55:66:77:88:99": {"lat": 40.712672, "lng": -74.006113},
        "55:66:77:88:99:AA": {"lat": 34.052235, "lng": -118.243629},
        "66:77:88:99:AA:BB": {"lat": 34.052167, "lng": -118.243694},
        "77:88:99:AA:BB:CC": {"lat": 34.052099, "lng": -118.243559},
        "88:99:AA:BB:CC:DD": {"lat": 51.507410, "lng": -0.127765},
        "99:AA:BB:CC:DD:EE": {"lat": 51.507342, "lng": -0.127829},
        "AA:BB:CC:DD:EE:ff": {"lat": 51.507274, "lng": -0.127694},
        "BB:CC:DD:EE:FF:00": {"lat": -33.868815, "lng": 151.209260},
        "CC:DD:EE:FF:00:11": {"lat": -33.868747, "lng": 151.209324},
        "DD:EE:FF:00:11:22": {"lat": -33.868679, "lng": 151.209189},
        "EE:FF:00:11:22:33": {"lat": -37.813629, "lng": 144.963068},
        "FF:00:11:22:33:44": {"lat": -37.813561, "lng": 144.963132},
        "00:11:22:33:44:aa": {"lat": -37.813493, "lng": 144.963253},
        "11:22:33:44:55:bb": {"lat": 52.520018, "lng": 13.404955},
        "22:33:44:55:66:cc": {"lat": 52.519950, "lng": 13.404890},
        "33:44:55:66:77:dd": {"lat": 52.519882, "lng": 13.405025},
    }

# constants
K = 92.45
frequencies={"2.4GHz": 2400e6, "5GHz": 5000e6}

@app.route('/')
def form():
    return render_template("form.html")

@app.route("/submit", methods=["POST"])
def submit():
    macAddress=request.form.get("macAddress")
    signalStrength_str=(request.form.get("signalStrength")) 
    if signalStrength_str is None:
        return jsonify({"error": "Signal strength is missing"}), 400

    try:
        signalStrength = float(signalStrength_str)
    except ValueError:
        return jsonify({"error": "Invalid signal strength value"}), 400
    userInputData[macAddress]=signalStrength

    print(userInputData)


    if len(userInputData) ==3:
        coordinates=[]
        distances=[] 

    # iterating thru inputs
        for macAddress, signalStrength in dict(userInputData).items():
            if macAddress in wifi_database:
              coordinates.append((wifi_database[macAddress]["lng"], wifi_database[macAddress]["lat"]))
              frequency= frequencies["2.4GHz"]
              transmitPower = 14 + random.random() * (28-14)
              distances.append(calculate_distance(signalStrength, transmitPower, frequency))
            else :
              return jsonify({"message": f"MAC address {macAddress} not found"}), 404
            print(distances)
            estimatedLocation= trilateration(coordinates, distances)
            print(estimatedLocation)
            userInputData.clear()

        if estimatedLocation:
            return jsonify({"message": "Location estimated successfully", "latitude": estimatedLocation["lat"], "longitude": estimatedLocation["lng"]
            }), 200
        else:
            return jsonify({"error": "Trilateration failed"}), 500
    else:
        return jsonify({"message": f"Please enter {3 - len(userInputData)} more MAC addresses"}), 200
             

def calculate_distance(signaleStrength, transmitPower, frequency):

    distance= 10** ((transmitPower-signaleStrength+ 20 * math.log10(frequency)-K)/20)
    return distance

def trilateration(coordinates, distances):
    if len(coordinates) !=3 or len(distances) !=3:
        return None
  
    x1, y1= coordinates[0]
    x2, y2= coordinates[1]
    x3, y3= coordinates[2]
    
  
    # Define coefficients
    A = np.array([
        [2 * (x2 - x1), 2 * (y2 - y1)],
        [2 * (x3 - x1), 2 * (y3 - y1)]
    ])
    b = np.array([
        distances[0]**2 - distances[1]**2 + x2**2 - x1**2 + y2**2 - y1**2,
        distances[0]**2 - distances[2]**2 + x3**2 - x1**2 + y3**2 - y1**2
    ])
    
    # Solve the system of linear equations
    try:
        x, y = np.linalg.solve(A, b)
        return {"lat": y, "lng": x}
    except np.linalg.LinAlgError:
        # Handle singular matrix (no unique solution)
        return None


if __name__ == '__main__':
    app.run(debug=True)
