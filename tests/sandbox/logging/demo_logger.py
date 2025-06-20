import logging
from logging.handlers import QueueHandler, QueueListener
import queue
import time

# Create a queue
log_queue = queue.Queue(-1)  # -1 for unlimited size

# Configure a QueueHandler to put logs into the queue
queue_handler = QueueHandler(log_queue)

# Configure a file handler for the actual log writing
file_handler = logging.FileHandler("async_app.log")
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)

# Create a QueueListener to process logs from the queue
listener = QueueListener(log_queue, file_handler)

# Configure the main logger to use the QueueHandler
logger = logging.getLogger(__name__)
logger.addHandler(queue_handler)
logger.setLevel(logging.INFO)

# Start the listener in a separate thread
listener.start()


# Example usage in an asynchronous application
def simulate_work():
    logger.info("Starting a simulated task.")
    # time.sleep(0.1)  # Simulate some work
    logger.info("Finished a simulated task.")


if __name__ == "__main__":
    for i in range(1000):
        simulate_work()

    # Stop the listener when the application is shutting down
    listener.stop()
