from geopy.distance import geodesic
import math

def calculate_bearing(pointA, pointB):
    lat1 = math.radians(pointA[1])
    lon1 = math.radians(pointA[0])
    lat2 = math.radians(pointB[1])
    lon2 = math.radians(pointB[0])

    diffLong = lon2 - lon1

    x = math.sin(diffLong) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - (math.sin(lat1) * math.cos(lat2) * math.cos(diffLong))

    initial_bearing = math.atan2(x, y)
    initial_bearing = math.degrees(initial_bearing)
    compass_bearing = (initial_bearing + 360) % 360
    
    return compass_bearing

def calculate_new_position(lat, lon, bearing, distance):
    origin = (lat, lon)
    destination = geodesic(nautical=distance).destination(origin, bearing)
    return destination.latitude, destination.longitude

def set_reporting_interval(speed_knots):
    if speed_knots <= 3:
        return 180 if speed_knots == 0 else 10  # 3 minutes if anchored, 10 seconds if moving up to 3 knots
    elif 3 < speed_knots <= 14:
        return 10  # 10 seconds for speeds between 3 and 14 knots
    elif 14 < speed_knots <= 23:
        return 6  # 6 seconds for speeds between 14 and 23 knots
    else:
        return 2  # 2 seconds for speeds above 23 knots

def generate_coordinates(start, end, speed_knots, mmsi):
    distance = geodesic((start[1], start[0]), (end[1], end[0])).nautical
    bearing = round(calculate_bearing(start, end), 1)

    coords = []
    current_lat, current_lon = start[1], start[0]
    traveled_distance = 0.0
    reporting_interval = set_reporting_interval(speed_knots)

    # Calculate distance covered in reporting interval
    distance_per_interval = (speed_knots / 3600) * reporting_interval
    while traveled_distance < distance:
        coords.append({
            'msg_type': 3,
            'course': bearing,
            'lat': current_lat,
            'lon': current_lon,
            'mmsi': mmsi,
            'turn': 127.0,
            'speed': speed_knots,
            'heading': 23,
            'second': 4,
        })
        
        current_lat, current_lon = calculate_new_position(current_lat, current_lon, bearing, distance_per_interval)
        traveled_distance += distance_per_interval

    return coords


if __name__ == "__main__":
    start = [10.739573904759887, 59.9307262443234]
    end = [10.774940031007993, 59.92952207732171]
    speed_knots = 25  # Example speed in knots
    mmsi = "319387000"

    messages = generate_coordinates(start, end, speed_knots, mmsi)
    print(len(messages))
    # for message in messages:
    #     print(message)
