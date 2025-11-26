
import asyncio
import os
from pathlib import Path
import sys
import argparse

# 1. Define the path to the submodule
# distinct from the current script location
FILE = Path(__file__).resolve()
ROOT = FILE.parents[0]  # root directory of your project
COMM_DIR = ROOT / 'communication_submodule'

# 2. Add the submodule to sys.path so Python can "see" it
if str(COMM_DIR) not in sys.path:
    sys.path.append(str(COMM_DIR))




from async_communication import AsyncReceiver



HOST="127.0.0.1"
PORT=8888
DEST_DIR_NAME="received"
DEST_DIR=ROOT/DEST_DIR_NAME


async def init(host=HOST, port=PORT):
    receiver = AsyncReceiver(host=host, port=port, save_dir=str(DEST_DIR))
    # Run server in background task
    server_task = asyncio.create_task(receiver.start())
    await asyncio.sleep(0.5) # Give it a moment to bind
    return receiver, server_task




if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="YOLO Transfer Client Terminal")
    parser.add_argument("host", type=str, help="Server IP address", default="127.0.0.1")
    parser.add_argument("port", type=int, help="Server Port", default=8888)
     
    args = parser.parse_args()
    
    async def main():
        
        receiver = None
        server_task = None
        try:
            receiver = AsyncReceiver(host=args.host, port=args.port, save_dir=str(DEST_DIR))
        
        
            # Run server in background task
            server_task = asyncio.create_task(receiver.start())
            await server_task
        
        except asyncio.CancelledError:
            # This catches internal cancellations
            print("Task cancelled.")
        except (ConnectionRefusedError, OSError) as e:
            print(f"❌ CRITICAL: Lost conneciton.")
            print(f"Details: {e}")
            sys.exit(1)
        except KeyboardInterrupt:
            print("\nUser interrupted.")
        finally:
            # Cleanup if sender exists and is connected
            if server_task is not None:
                server_task.cancel()
            try:
                await server_task
            except asyncio.CancelledError:
                pass
            
    try:
        # asyncio.run() manages the loop and often catches the KeyboardInterrupt 
        # sent to the main process
        asyncio.run(main())
    except KeyboardInterrupt:
        # This catches CTRL+C at the top level ensures graceful exit 
        # without printing a nasty traceback
        pass