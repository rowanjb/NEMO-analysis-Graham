import math

def coord_distance(lat1,lon1,lat2,lon2):
    '''Returns the distance (in m) between two coordinates using the haversine formula''' 
    # from: https://www.movable-type.co.uk/scripts/latlong.html
    
    lat1_rad = lat1 * math.pi / 180
    lon1_rad = lon1 * math.pi / 180
    lat2_rad = lat2 * math.pi / 180
    lon2_rad = lon2 * math.pi / 180

    dlat_rad = ( lat2-lat1 ) * math.pi / 180
    dlon_rad = ( lon2-lon1 ) * math.pi / 180

    a = (math.sin(dlat_rad/2))**2 + math.cos(lat1_rad)*math.cos(lat2_rad)*( (math.sin(dlon_rad/2))**2 )
    c = 2 * math.atan2( math.sqrt(a), math.sqrt(1-a) )
    d = c * 6371000 # 6,371,000 is Earth's mean radius in m

    print('The distance between point 1 and point 2 is ' + str(d) + ' m')

if __name__ == '__main__':
    coord_distance(28.272377967834473,-40.252920150756836,28.272436141967773,-48.25291633605957)
