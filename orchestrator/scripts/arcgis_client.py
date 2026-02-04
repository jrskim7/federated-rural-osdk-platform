"""Minimal ArcGIS Online helper: get token and add features to a Feature Service layer."""
import requests
import json

ARCGIS_TOKEN_URL = "https://www.arcgis.com/sharing/rest/generateToken"


def get_token(username: str, password: str, referer: str = "http://localhost", expiration: int = 60) -> str:
    payload = {
        "f": "json",
        "username": username,
        "password": password,
        "referer": referer,
        "expiration": expiration,
    }
    r = requests.post(ARCGIS_TOKEN_URL, data=payload, timeout=15)
    r.raise_for_status()
    data = r.json()
    if "token" not in data:
        raise RuntimeError(f"ArcGIS auth failed: {data}")
    return data["token"]


def add_features(feature_service_url: str, arcgis_features: list, token: str) -> dict:
    """POST features to layer's addFeatures endpoint.

    feature_service_url must be the layer endpoint, e.g.
    https://services.arcgis.com/.../FeatureServer/0
    """
    url = feature_service_url.rstrip("/") + "/addFeatures"
    features_param = json.dumps(arcgis_features)
    payload = {"f": "json", "features": features_param, "token": token}
    r = requests.post(url, data=payload, timeout=30)
    r.raise_for_status()
    return r.json()