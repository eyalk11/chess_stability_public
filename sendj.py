
import asyncio
import sys
from commonpy.log_handler import os
import websockets
import json
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

LAM=1 
try:
    if sys.argv[1]=='local':
        LAM=0 
except:
    pass

async def send_message(message):
    logger.debug('Starting websocket client')
    # Replace with your WebSocket server URL
    if LAM:
        uri = "wss://hpmew9eepf.execute-api.eu-west-1.amazonaws.com/prod"  # Example URL - change this to your endpoint
    else:
        uri = "ws://localhost:2772" #"wss://sptpubgl4e.execute-api.eu-west-1.amazonaws.com/Prod"

    try:
        async with websockets.connect(uri) as websocket:
            # Convert dict to JSON string and send
            logger.debug(f"Sent message: {message}")
            import base64 
            # if not LAM:
                # await websocket.send(base64.b64encode(open(r'c:\gitproj\chess_analyzer\message.txt','rb').read()).decode('utf-8'))
            # else:
            await websocket.send(json.dumps(message))

            for i in range(10):
                # Wait for response with timeout
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=30)
                    logger.debug(f"Received response: {response}")
                except asyncio.TimeoutError:
                    logger.debug(".")
                    continue

                # If you expect JSON response, you can parse it
                try:
                    parsed_response = json.loads(response)
                    logger.debug(f"Parsed response: {parsed_response}")
                except json.JSONDecodeError:
                    logger.warning("Response was not in JSON format")
                return parsed_response

    except websockets.exceptions.ConnectionClosedError:
        logger.error("Failed to connect to the WebSocket server")
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")

