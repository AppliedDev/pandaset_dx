from __future__ import annotations

import argparse
import os

import requests

# TODO: Adjust the constants to the parameters to use for conversions.
MAP_KEY = "sunnyvale"
DRIVE_CONFIG_PATH = "scenario://workspace/starter_strada_config.drv.yaml"

# Local
BASE_SIM_FLAGS = (
    " --container_name 'strada' --customer_server_run_cmd 'python /interface/log_converter.py'"
)
API_URL = "http://localhost:8088"

# Cloud
# API_URL = "https://api.customername.applied.dev/api"
# IMAGE_NAME = "sample_image:tag"   # Only used in cloud
# BASE_SIM_FLAGS = f" --container_name 'strada' --customer_server_run_cmd 'python /interface/log_converter.py' --image_name {IMAGE_NAME}"


def convert_drive(log_path: str, auth_token: str) -> None:
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {auth_token}",
    }
    request_body_template = {
        "logs": [{"name": "default", "path": log_path}],
        "drive_config_path": DRIVE_CONFIG_PATH,
        "drive_duration_secs": 20000,
        "map_key": MAP_KEY,
        "sim_flags": f"{BASE_SIM_FLAGS}",
    }
    print("Request", request_body_template)
    response = requests.post(
        f"{API_URL}/v1/convert_strada_drive?auth_token={auth_token}",
        json=request_body_template,
        headers=headers,
        # TODO(284066) remove, authorization header is preferred. v2 API should
        # be preferred.
        cookies={"auth_token": auth_token},
        timeout=1000,
    )
    print(response)


if __name__ == "__main__":
    """
    Helper script to convert a drive using the rest api.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--log_paths_file",
        type=str,
        required=False,
        default="logs.txt",
        help="Path to a text file with 1 line per log path to convert",
    )
    parser.add_argument(
        "--rest_api_token",
        type=str,
        required=True,
        help="Rest API token. See documentation for how to obtain this here: https://home.applied.co/manual/adp/latest/#/apis/rest_api/rest_api?id=authentication-for-desktop-adp.",
    )
    args = parser.parse_args()

    script_dir = os.path.dirname(__file__)
    logs = open(os.path.join(script_dir, args.log_paths_file)).read().splitlines()
    for log in logs:
        if log.strip():
            print("Converting ", log)
            convert_drive(log, args.rest_api_token)
    print(f"Navigate to {API_URL}/strada/library to view log.")
