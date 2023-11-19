from flask import *
import openrouteservice as ors
import os

ors_key = os.environ.get('ORS_KEY')
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

app = Flask(__name__)

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
