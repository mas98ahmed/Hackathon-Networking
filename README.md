md
# Hackathon-Networking: Keyboard Spamming Battle Royale

## Project Overview
Keyboard Spamming Battle Royale is a networking project implemented in Python that allows players to compete in a keyboard spamming battle. The project uses both TCP and UDP protocols for different aspects of the game. The server manages the game state and player interactions, while the client allows users to participate in the battle.

## Key Features & Benefits

*   **Real-time Gameplay:** Players can interact and compete in real-time.
*   **TCP & UDP Implementation:** Demonstrates the use of both TCP and UDP protocols in a networking application.
*   **Multi-threaded Server:** The server utilizes multi-threading to handle multiple clients concurrently.
*   **Simple Client Interface:** Easy-to-use client application for participating in the game.
*   **Scalable Design:** The server architecture can be extended to support a larger number of players.

## Prerequisites & Dependencies

Before you begin, ensure you have the following installed:

*   **Python 3.6+:**  The project is built using Python and requires Python 3.6 or higher.
*   **Scapy:** A Python library for packet manipulation. Install using `pip install scapy`.
*   **getch:** A Python library for getting a single character from the console.  (Likely required for Windows, may need alternative for other OS). Install using `pip install py-getch` (or similar library depending on OS).

## Installation & Setup Instructions

Follow these steps to install and set up the project:

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/mas98ahmed/Hackathon-Networking.git
    cd Hackathon-Networking
    ```

2.  **Install Dependencies:**
    ```bash
    pip install scapy py-getch # replace py-getch with alternative if on non-Windows OS
    ```

3.  **Configure Network Interface (Optional):**
    - In both `Server/main.py` and `Client/main.py`, there are variables `DEV_ip` and `TEST_ip`. By default, the IP will be derived using `scapy.get_if_addr()`. You may need to modify the interface name in these variables (`DEV_ip = "eth1"`) based on your operating system and network setup.  The code contains conditional logic (`TEST = False`) that you can change for testing on alternative network interfaces.

## Usage Examples

1.  **Run the Server:**
    ```bash
    cd Server
    python main.py
    ```

2.  **Run the Client:**
    ```bash
    cd ../Client
    python main.py
    ```

3.  **Gameplay:**  Once the client connects to the server, follow the instructions printed on the client console to participate in the keyboard spamming battle.  The basic idea is to press keys as fast as possible when prompted.

## Configuration Options

The following options can be configured:

*   **`Server/main.py`:**
    *   `GAME_TIME`:  The duration of the game in seconds (default: 5).
    *   `CLIENT_SEARCH_TIME`:  The time the server waits for clients to connect (default: 10).
    *   `DEV_ip`, `TEST_ip`: Network interface configuration (see installation instructions).
    *   `TEST`: A boolean flag to switch between `DEV_ip` and `TEST_ip` for determining the IP address.
*   **`Client/main.py`:**
    *   `DEV_ip`, `TEST_ip`: Network interface configuration (see installation instructions).
    *   `TEST`: A boolean flag to switch between `DEV_ip` and `TEST_ip` for determining the IP address.

## Contributing Guidelines

We welcome contributions to the project!  To contribute, please follow these guidelines:

1.  Fork the repository.
2.  Create a new branch for your feature or bug fix.
3.  Make your changes and commit them with clear, descriptive messages.
4.  Submit a pull request.

Please ensure your code adheres to PEP 8 style guidelines.  Include tests where appropriate.

## License Information

License is not specified. All rights reserved by the owner, mas98ahmed.

## Acknowledgments

This project was inspired by networking principles and the desire to create a fun and engaging game.
