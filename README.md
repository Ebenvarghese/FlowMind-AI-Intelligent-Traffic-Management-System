# 🚦 FlowMind AI – Intelligent Traffic Management System

An AI-powered Intelligent Traffic Management System built using **Python**, **Flask**, **OpenCV**, **YOLOv8**, and **Flask-SocketIO**. The project detects vehicles, manages traffic signals dynamically, provides emergency vehicle priority, and displays live traffic analytics through a web dashboard.

---

## Features

- User Login & Signup
- Real-time Vehicle Detection using YOLOv8
- Multi-Lane Traffic Monitoring
- Adaptive Traffic Signal Simulation
- Emergency Corridor Priority
- Live Traffic Analytics Dashboard
- AI vs Fixed Timer Comparison
- Runs completely on local hardware

---

## Modules

- Login Page
- Signup Page
- Dashboard
- Live Simulation
- Compare Module
- YOLO Analysis
- Emergency Corridor

---

## System Architecture

```text
Traffic Videos
      │
      ▼
YOLOv8 Detection
      │
      ▼
Vehicle Counting
      │
      ▼
Traffic Simulation
      │
      ▼
Adaptive Signal Control
      │
      ▼
Flask Backend
      │
      ▼
Web Dashboard
```

---

## Project Structure

```text
FlowMind-AI-Intelligent-Traffic-Management-System/
│
├── app.py
├── sim_engine.py
├── yolo_engine.py
├── users.json
├── yolov8n.pt
├── templates/
│   ├── index.html
│   ├── login.html
│   └── signup.html
├── static/
├── sample_videos/
└── README.md
```

---

## Installation

### Clone the repository

```bash
git clone https://github.com/Ebenvarghese/FlowMind-AI-Intelligent-Traffic-Management-System.git
cd FlowMind-AI-Intelligent-Traffic-Management-System
```

### Create a virtual environment

**Windows**

```bash
python -m venv .venv
.venv\Scripts\activate
```

**Linux/macOS**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Install dependencies

```bash
pip install Flask Flask-SocketIO Flask-Cors opencv-python numpy ultralytics requests
```

---

## Run the Project

```bash
python app.py
```

Open your browser and visit:

```text
http://127.0.0.1:5000
```

---

## Technology Stack

### Backend

- Python
- Flask
- Flask-SocketIO
- Flask-CORS

### Computer Vision

- OpenCV
- YOLOv8

### Frontend

- HTML
- CSS
- JavaScript

### Communication

- Socket.IO

---

## Testing

### Black-box Testing

- Login Authentication
- Signup Validation
- Dashboard Access
- Live Simulation
- Compare Module
- Emergency Corridor
- YOLO Analysis

### White-box Testing

- Login Logic
- Signup Logic
- Video Selection Logic
- Lane Weight Calculation
- Lane Selection Logic
- Emergency Corridor Logic

---

## Future Improvements

- Live CCTV Integration
- Multi-Camera Support
- Database Authentication
- Historical Traffic Analytics
- Accident Detection
- IoT Sensor Integration

---

## Author

**Eben Varghese**

B.Tech Computer Engineering

Pillai College of Engineering

GitHub: https://github.com/Ebenvarghese