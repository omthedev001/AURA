import openrouteservice as ors
ors_client = ors.Client("5b3ce3597851110001cf62488603f4ba0cbe4b149200076a33b1fd7b")
geojson = {"type": "point", "coordinates": [81.656877,21.205666]}
pois = ors_client.places(request='pois',
                         geojson=geojson,
                         buffer=2000,
                         filter_category_ids=206)
print(pois)