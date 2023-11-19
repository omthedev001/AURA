# importing Libs
from twilio.rest import Client
import flask
import openrouteservice as ors
import what3words as w3w
import time 
import random
import os
from datetime import datetime
import pyrebase
import folium 

# Declaring vars
acc_sid = os.environ.get('TWILIO_ACCOUNT_SID')
acc_auth = os.environ.get('TWILIO_AUTH_TOKEN')
twilio_number = os.environ.get('TWILIO_WHATSAPP')
ors_key = os.environ.get('ORS_KEY')
w3w_key = os.environ.get('W3W_KEY')
# csv_path = "record.csv"

# making clients
twilio_client = Client(acc_sid,acc_auth)
ors_client = ors.Client(key=ors_key)
w3w_geocoder = w3w.Geocoder(w3w_key)
# making firebase instance
config = {
  "apiKey": "AIzaSyBhOKvH-P9nf4-_cHeAmjyOGiyI0PXsa-Y",
  "authDomain": "eahs-389407.firebaseapp.com",
  "databaseURL": "https://eahs-389407-default-rtdb.asia-southeast1.firebasedatabase.app",
  "projectId": "eahs-389407",
  "storageBucket": "eahs-389407.appspot.com",
  "messagingSenderId": "562115977942",
  "appId": "1:562115977942:web:82439118215677b44b9f77",
  "measurementId": "G-T0PDF2Z6P1"
}

# create app instance
app = flask.Flask(__name__)
firebase = pyrebase.initialize_app(config)
database = firebase.database()
storage = firebase.storage()
# create map for example
user={}
hospital_list ={}
route_durations = []
#creating a list of ambulance coordinates

pickup_points = [[[81.650402,21.211172],"Om:+917724811110"],
                [[81.637685,21.227515],"Rajiv:+917724811110"],
                [[81.658727,21.205652],"Raju:+917724811110"],
                [[81.657879,21.271156],"Pramod:+917724811110"],
                [[81.670563,21.210926],"Darsh:+917724811110"]]

# def to send messages and store records

# Path to the local HTML file you want to upload
def save_file_to_firebase(file_path,firebase_path):

    local_file_path = file_path
    # Destination path in Firebase Storage (e.g., "webapp/index.html")
    destination_path = firebase_path
    # Upload the HTML file to Firebase Storage
    storage.child(destination_path).put(local_file_path)
    download_url = storage.child(destination_path).get_url(None)

    return download_url


def record_data(name,number,lat,lng,Duration,map_url,driver,hospital,ambulance_type):
    now = datetime.now()
    data = {"Name":str(name),"Number":str(number),"Coordinates":f"{lat},{lng}","Duration":str(Duration),"Date":str(now.date()),"Time":now.strftime('%H:%M:%S'),
            "Map":str(map_url),"Driver":str(driver),"Hospital":str(hospital),"Ambulance":str(ambulance_type)}
    database.child('Whatsapp').child('Users').child().set(data)
    return data
def SendMsg(number,msg):
    response = twilio_client.messages.create(to=number,
                                  from_= twilio_number,
                                  body=msg)
    return response
def SendQr(number):
    qrres = twilio_client.messages.create(to=number,
                                  media_url='https://omthedev001.github.io/cheems.png.png',
                                  from_=twilio_number,)
    print(qrres.sid)
#def to find the nearest hospital
def nearest_hospital(dict,finder_key):
    min_duration = float('inf')
    min_duration_key = None
    
    for key, inner_dict in dict.items():
        duration = int(inner_dict[finder_key])
        if duration < min_duration:
            min_duration = duration
            min_duration_key = key
    
    return min_duration_key
# app
@app.route('/whatsapp', methods = ['GET','POST'])
def whatsapp():
    print(flask.request.get_data())
    message = flask.request.form['Body']
    number = flask.request.form['From']
    name = flask.request.form['ProfileName']
    print(f'Message----> {message}')
    print(f'Number-----> {number}')
    print(f'Name-------> {str(name)}')
    if (message.count(".") == 2):
        try:
            message = message.split(',')
            print(message)
            print(message[0])
            SendMsg(number,"Getting Your Location....... ")
            res = w3w_geocoder.convert_to_coordinates(message[0])
            # print (res)
            lat = res['square']['southwest']['lat']
            lng = res['square']['southwest']['lng']
            print([lng,lat])
            map= folium.Map(location=[lat,lng], tiles='cartodbpositron', zoom_start=15)
            folium.Marker([lat,lng],popup="Patients location",icon=folium.Icon(color='green'),tooltip="click").add_to(map)
           
            random_time = random.randint(2,8)

            for points in pickup_points:
                print(points)
                coords_temp = [points[0],[lng,lat]]
                route_temp = ors_client.directions(coordinates=[points[0],[lng,lat]],
                              profile='driving-car',
                              format='geojson')
                duration_temp = route_temp['features'][0]['properties']['summary']['duration']
                route_durations.append(duration_temp)
                folium.Marker(list(reversed(points[0])),popup="Ambulances",icon=folium.Icon(color='red'),tooltip="click").add_to(map)
            shortest_duration_index = route_durations.index(min(route_durations))
            print(shortest_duration_index)
            # Get the coordinates and duration of the shortest route
            shortest_duration_coordinates = pickup_points[shortest_duration_index][0]
            driver_data = pickup_points[shortest_duration_index][1] 
            driver_number = str(driver_data).split(":")
            driver_number = driver_number[1]
            print(shortest_duration_coordinates)
            folium.Marker(list(reversed(shortest_duration_coordinates)),popup="Starting point.Ambulance confirms to pick up the patient",icon=folium.Icon(color='darkblue'),tooltip="click").add_to(map)
            print(shortest_duration_coordinates)
            coords =[shortest_duration_coordinates,[lng,lat]]
            route1 = ors_client.directions(coordinates=coords,
                              profile='driving-car',
                              format='geojson')
            print(route1)
            duration = (route1['features'][0]['properties']['summary']['duration'])
            duration = (duration / 60)
            duration = int(duration)
            # folium.GeoJson(route1,name='route1').add_to(map)
            # folium.LayerControl().add_to(map)
            geojson = {"type": "point", "coordinates": [lng,lat]}
            pois = ors_client.places(request='pois',
                                     geojson=geojson,
                                     buffer=2000,
                                     filter_category_ids=[206])
            print(pois)
            folium.Circle(radius=2000, location=[lat,lng], color='green',fill = True,fill_color = 'lightgreen').add_to(map)
            index = 0
            limit = 10
            for poi in pois['features']:
                hospitals = poi['properties']['osm_tags']['name']
                coords1 = poi['geometry']['coordinates']
                coords2 = [shortest_duration_coordinates,coords1]
                route = ors_client.directions(coordinates=coords2,
                                            profile='driving-car',
                                            format='geojson')
                # print(route)
                duration1 = (route['features'][0]['properties']['summary']['duration'])
                hospital_list[index]={}
                hospital_list[index]['name']=hospitals
                hospital_list[index]['duration']=duration1
                hospital_list[index]['coords']=coords1
                hospital_list[index]['coords_rev']= list(reversed(coords1))
                print(f'{hospitals},{duration}')
                folium.Marker(location=list(reversed(poi['geometry']['coordinates'])),
                              icon=folium.Icon(color='orange'),
                              popup=folium.Popup(poi['properties']['osm_tags']['name'])).add_to(map)
                print(list(reversed(coords1)))
                index = index+1
                if index >= limit:
                    break
            selected_hospital = nearest_hospital(hospital_list,'duration')
            print(selected_hospital)
            print(hospital_list[selected_hospital])
            folium.Marker(hospital_list[selected_hospital]['coords_rev'],popup="Selected hospital",icon=folium.Icon(color='lightblue'),tooltip="click").add_to(map)
            route2 = ors_client.directions(coordinates = [hospital_list[selected_hospital]['coords'],[lng,lat]],
                                           profile='driving-car',
                                           format='geojson')
            print(route2)
            # folium.GeoJson(route2,name='route2').add_to(map)
            print(f'Duration----> {duration}')
            time.sleep(1)
            SendMsg(number,"Got it!")
            time.sleep(0.5)
            SendMsg(number,f"Dont Worry {name}, Your Ambulance Would Be Arriving in\n{duration}---{duration + random_time} minutes and will take you to the hospital")
            time.sleep(0.5)
            driver = pickup_points[shortest_duration_index][1]
            SendMsg(number,f'Your driver is {driver}')
            hospital_details = hospital_list[selected_hospital]['name']
            hospital_duration = int(hospital_list[selected_hospital]['duration']/60)
            print(hospital_duration)
            SendMsg(number,f'The ambulance will take you to this hospital {hospital_details} which is {hospital_duration} minutes away')
        
            time.sleep(2)
            extracted_name= name.encode('utf-8')
            # printing result
            print("Extracted String : " + str(extracted_name))
            total_duration = duration+hospital_duration
            new_number = number.split(":")
            folium.GeoJson(route1, name='Route 1', style_function=lambda x: {'color': 'blue'}).add_to(map)
            folium.GeoJson(route2, name='Route 2', style_function=lambda x: {'color': 'red'}).add_to(map)
            # Add layer control for routes
            folium.LayerControl().add_to(map)
            map.save('map.html')
            print("-------------------making records------------------")
            time.sleep(1)
            store_path = f"Maps/Whatsapp/{name}/map.html"
            map_link = save_file_to_firebase("map.html",store_path)
            print(map_link)
            SendMsg(number,f'Here is your planned route\n{map_link}')
            driver_number = f"whatsapp:{driver_number}"
            print(driver_number)
            SendMsg(driver_number,f'New patient at {message[0]}\nName: {name}\nNumber: {number}\nHospital:{hospital_details}\nPlanned route: {map_link}')
            if len(message) > 1:
                amb_type = message[1]
            else:
                amb_type = "Not specified"
            recorded_data = record_data(name,new_number[1],lat,lng,total_duration,map_link,driver_data,hospital_details,amb_type)
            print(recorded_data)
            print("------------------data recorded,process complete---------------------")
            SendMsg(number,"Thanks for contacting AURA!")

        except Exception:
            SendMsg(number,"Something went wrong please try again by saying hi,please check if you have filled the details correctly")
            print(Exception)
    else:
        SendMsg(number,f'Hey there {name}!,\nThanks for contacting our panic messaging service.\nTo begin you may click on the link below and send the three words on the top along with the type of ambulance seperated with a comma from the following\n1.Basic Ambulances\n2.Advanced Life Support Ambulances\nExample=alien.wages.pepper,Basic Ambulances')
        time.sleep(1)
        SendMsg(number,'https://www.what3words.com\n Make sure to send the correct information and have a good internet connection')
    return'200'
if __name__ == "__main__":   
    app.run(port=5000,debug=True)
