🛡️ Aegis Protocol: AI-Powered Disaster Response System  
Aegis Protocol is an AI-driven disaster response system designed to detect, validate, and manage disaster events in real time. By leveraging a decentralized oracle network (DON), advanced analytics, and smart contracts, the system automates resource allocation and insurance payouts, ensuring rapid and efficient emergency response.

---

📋 **Table of Contents**
- ✨ Key Features
- 🛠️ Requirements
- 🚀 How to Run
- 📁 Project Structure
- 🤝 Contributing

---

✨ **Key Features**  
- **AI-Powered Disaster Detection**: Uses AI models to analyze data from multiple sources (e.g., BMKG, NASA FIRMS, PetaBencana, social media) to detect disasters.  
- **Decentralized Oracle Network (DON)**: An AI-managed validator network that reaches consensus on disaster validity.  
- **Real-Time Dashboard**: An HTML/JavaScript dashboard providing live system status monitoring, logs, and simulation controls.  
- **FastAPI Backend Integration**: A lightweight and fast Python API connecting the dashboard to the core system logic.  
- **Disaster Simulation**: Supports running preset disaster simulations (e.g., Jakarta Flood, Cianjur Earthquake) to test and monitor system performance.  
- **Parametric Insurance**: Modeled smart contracts that automatically trigger payouts once disaster criteria are verified.

---

🛠️ **Requirements**  
Ensure you have **Docker Desktop** installed on your machine. This is the only prerequisite needed, as it will manage all dependencies and required environments. The project is pre-configured with an updated `enhanced_requirements.txt` file, so no manual dependency updates are necessary.

---

🚀 **How to Run**  
Follow the steps below to set up the Aegis Protocol project on your local machine.

1. **Copy All Files Into One Directory**  
   Make sure all project files (including `Dockerfile`, `docker-compose.yml`, `api_server.py`, and `aegis_protocol.html`) are in the same folder.

2. **Run with Docker Compose**  
   Open a terminal or command prompt, navigate to your project folder, and run the following command:

   ```bash
   docker-compose up -d --build
   ```

   This command will build the Docker image from the Dockerfile and run the container in the background. The first build may take a few minutes.

3. **Access the Dashboard**  
   Once the container is running, open your web browser and go to the following URL to view the dashboard:

   ```
   http://localhost:8080
   ```

   You can also access the API documentation at:

   ```
   http://localhost:8080/docs
   ```

   To stop the system, run the following command in the terminal:

   ```bash
   docker-compose down
   ```

---

📁 **Project Structure**  
- `Dockerfile`: Instructions for building the Docker image, including dependency installation.  
- `docker-compose.yml`: Defines the `aegis-api` service for Docker, including port management and volume mounting.  
- `enhanced_requirements.txt`: List of Python dependencies to be installed inside the container.  
- `api_server.py`: Sets up the FastAPI backend server, defines all API endpoints, and manages WebSocket connections for real-time communication.  
- `aegis_protocol.html`: Front-end dashboard connected to the API server for system visualization and control.  
- `enhanced_main.py`: Core logic for initializing and running all components of the Aegis Protocol system.  
- `asi_integration.py`: Class for interacting with ASI:one for advanced analysis and optimization.  
- `base_agent.py`: Base class for all AI agents in the system, defining common structure and functionality.  
- `disaster_parsers.py`: Contains agents responsible for processing raw data from various sources into structured disaster events.  
- `communications.py`: Manages public notifications and communications.

---

🤝 **Contributing**  
We welcome contributions! If you find any bugs or have suggestions for improvements, please open an issue or submit a pull request in the project repository.

