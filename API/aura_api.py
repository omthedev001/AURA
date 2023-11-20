from flask import *
import openrouteservice as ors
import os

ors_key = '5b3ce3597851110001cf62488603f4ba0cbe4b149200076a33b1fd7b'
ors_client = ors.Client(key = ors_key)

def nearest_hospital(dict,finder_key):
    min_duration = float('inf')
    min_duration_key = None
    
    for key, inner_dict in dict.items():
        duration = int(inner_dict[finder_key])
        if duration < min_duration:
            min_duration = duration
            min_duration_key = key
    
    return min_duration_key

ambulance_points = [[[81.650402,21.211172],"Om:+917724811110"],
                [[81.637685,21.227515],"Rajiv:+917724811110"],
                [[81.658727,21.205652],"Raju:+917724811110"],
                [[81.657879,21.271156],"Pramod:+917724811110"],
                [[81.670563,21.210926],"Darsh:+917724811110"]]

app = Flask(__name__)
@app.route('/get_ambulance/<string:coords>',methods = ['GET','POST'])
def get_ambulance(coords):
    route_durations = []
    new_coords = str(coords).split(',')
    lng = float(new_coords[1])
    lat = float(new_coords[0])

    for points in ambulance_points:
                print(points)
                coords_temp = [points[0],[lng,lat]]
                route_temp = ors_client.directions(coordinates=[points[0],[lng,lat]],
                              profile='driving-car',
                              format='geojson')
                duration_temp = route_temp['features'][0]['properties']['summary']['duration']
                route_durations.append(duration_temp)
    shortest_duration_index = route_durations.index(min(route_durations))
    print(shortest_duration_index)
    # Get the coordinates and duration of the shortest route
    shortest_duration_coordinates = ambulance_points[shortest_duration_index][0]
    driver_data = ambulance_points[shortest_duration_index][1] 
    driver_number = str(driver_data).split(":")
    driver_number = driver_number[1]
    print(shortest_duration_coordinates)
    data = {'selected_ambulance':ambulance_points[shortest_duration_index],'other':ambulance_points}

    return jsonify(data), 200
@app.route('/pois/<string:coords>/<id>/<int:buffer>/<int:limit>',methods = ['GET','POST'])
def get_pois(coords,id,buffer,limit):
    
    # data = {"coords":str(coords).split(','),"id":id,"buffer":buffer}
    hospital_list = {}
    new_coords = str(coords).split(',')
    lng = float(new_coords[1])
    lat = float(new_coords[0])
    print([int(id)])
    geojson = {"type": "point", "coordinates": [lng,lat]}
    pois = ors_client.places(request='pois',
                             geojson=geojson,
                             buffer=buffer,
                             filter_category_ids=[int(id)])
    print(pois)
    limit = limit
    index = 0
    for poi in pois['features']:
        coords1 = poi['geometry']['coordinates']
        hospitals = poi['properties']['osm_tags']['name']
        coords2 = [[lng,lat],coords1]
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
        print(f'{hospitals},{duration1}')
        print(list(reversed(coords1)))
        index = index+1
        if index >= limit:
            break
    selected_hospital = nearest_hospital(hospital_list,'duration')
    print(selected_hospital)
    print(hospital_list)
    data = {"selected_hospital":hospital_list[selected_hospital],"hospitals":hospital_list}
    print(jsonify(data))
    return jsonify(data), 200
if __name__ == "__main__":
    app.run(debug=True,port=7777)
