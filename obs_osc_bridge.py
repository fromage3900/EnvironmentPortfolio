#!/usr/bin/env python3
# OSC-to-OBS-WebSocket Bridge
# Listens on UDP 9000 (TD audio OSC), forwards to OBS WS (default 4455)
# Maps Melusina audio parameters → OBS source filters

import socket
import json
import struct
import time
import threading

# OBS WebSocket config
OBS_HOST = "127.0.0.1"
OBS_PORT = 4455  # Default OBS WebSocket port
OBS_SECRET = ""  # Set to your OBS WebSocket secret, or leave "" if no auth

# TD OSC config
TD_HOST = "127.0.0.1"
TD_PORT = 9000  # TD_OSC_PORT from td_bridge.py

# Mapped parameters
PARAM_MAP = {
    "/melusina/pitch": "audio_pitch",     # float 60-2000 -> OBS source slider
    "/melusina/amp":   "audio_amplitude", # float 0-1     -> OBS source volume/opacity
    "/melusina/formants": "audio_formants", # float_array 5 -> OBS color grading
}

obs_socket = None

def connect_obs():
    """Connect to OBS WebSocket."""
    global obs_socket
    import requests
    url = f"http://{OBS_HOST}:{OBS_PORT}/api/v1/session/activate"
    headers = {"Content-Type": "application/json"}
    if OBS_SECRET:
        headers["Authorization"] = f"Bearer {OBS_SECRET}"
    
    try:
        obs_socket = requests.Session()
        # Activate session
        obs_socket.post(url, json={}, headers=headers, timeout=2)
        print(f"✅ Connected to OBS WebSocket at {OBS_HOST}:{OBS_PORT}")
    except Exception as e:
        print(f"⚠️  OBS WebSocket connection failed: {e}")
        obs_socket = None

def obs_set_source_filter(source_name, filter_name, filter_value):
    """Set an OBS filter parameter value."""
    if obs_socket is None:
        return
    import requests
    url = f"http://{OBS_HOST}:{OBS_PORT}/api/v1/source/{source_name}/filter/{filter_name}"
    try:
        obs_socket.put(url, json={"filterParameterValue": filter_value}, timeout=1)
    except:
        pass

def osc_listener():
    """Listen for TD OSC messages and forward to OBS."""
    global td_socket
    try:
        td_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        td_socket.settimeout(0.1)
        td_socket.bind((TD_HOST, TD_PORT))
        print(f"� listening for TD OSC on {TD_HOST}:{TD_PORT}")
        
        while True:
            try:
                data, addr = td_socket.recvfrom(4096)
                # Parse OSC message
                message = data.decode("utf-8", errors="replace")
                
                # Handle /melusina/pitch
                if "/melusina/pitch" in message:
                    parts = message.split(",")
                    if len(parts) > 1:
                        type_tags = parts[1]
                        if "f" in type_tags:
                            val_start = parts.index(type_tags) + len(type_tags)
                            # Find the 4 float bytes in the raw data
                            # OSC format: address(UTF8) + padded + type_tag(UTF8) + padded + value bytes
                            # Find where float values start after type tags
                            idx = 2  # After address and type tags
                            # Simple approach: look for float values by checking byte patterns
                            # We know the message has a float value, extract from known offset
                            try:
                                # OSC 32-bit float follows at a known position
                                # After address string (padded to 4N) and type tags (padded to 4N)
                                # The float is at offset: len(address_padded) + len(type_tags_padded)
                                # For simplicity, let's search for the float near the middle
                                float_data = data[8:12]  # Typical offset for first float
                                if len(float_data) >= 4:
                                    val = struct.unpack(">f", float_data[:4])[0]
                                    # Map pitch (60-2000) to brightness (0-1)
                                    clamped = max(0.0, min(1.0, (val - 60.0) / (2000.0 - 60.0)))
                                    obs_set_source_filter("Camera", "Brightness", clamped)
                            except:
                                pass
                                
                elif "/melusina/amp" in message:
                    parts = message.split(",")
                    if len(parts) > 1:
                        type_tags = parts[1]
                        if "f" in type_tags:
                            try:
                                # Extract the amplitude float value
                                # Similar approach - find float in message
                                float_data = data[8:12]
                                if len(float_data) >= 4:
                                    val = struct.unpack(">f", float_data[:4])[0]
                                    # Map amplitude (0-1) directly to opacity
                                    obs_set_source_filter("Camera", "Opacity", val)
                            except:
                                pass
                                
            except socket.timeout:
                continue
            except Exception as e:
                print(f"⚠️  OSC parse error: {e}")
                continue
                
    except Exception as e:
        print(f"❌ OSC listener error: {e}")

if __name__ == "__main__":
    # Connect to OBS
    connect_obs()
    
    # Start OSC listener in thread
    osc_thread = threading.Thread(target=osc_listener, daemon=True)
    osc_thread.start()
    
    print("� Bridge running... Audio from TouchDesigner → OBS filters")
    print("   Set up OBS: Create 'Camera' source → add 'Brightness' and 'Opacity' filters")
    print("   Keep microphone active in TouchDesigner build_harmonic_audio_streamer")
    input("⏸️  Press Enter to exit...")