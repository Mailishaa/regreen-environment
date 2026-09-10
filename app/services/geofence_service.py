import json


def point_in_polygon(latitude: float, longitude: float, polygon_json: str) -> bool:
    try:
        polygon = json.loads(polygon_json)
    except (json.JSONDecodeError, TypeError):
        return False

    if len(polygon) < 3:
        return False

    point_x = longitude
    point_y = latitude
    inside = False

    for i in range(len(polygon)):
        j = (i - 1) % len(polygon)

        lat1, lon1 = polygon[i]
        lat2, lon2 = polygon[j]

        x1, y1 = lon1, lat1
        x2, y2 = lon2, lat2

        # Point is exactly on a horizontal boundary
        if (
            min(y1, y2) <= point_y <= max(y1, y2)
            and min(x1, x2) <= point_x <= max(x1, x2)
            and (y2 - y1) * (point_x - x1)
            == (x2 - x1) * (point_y - y1)
        ):
            return True

        if (y1 > point_y) != (y2 > point_y):
            intersection_x = (
                (x2 - x1) * (point_y - y1)
                / (y2 - y1)
                + x1
            )

            if point_x < intersection_x:
                inside = not inside

    return inside