# The Chase

This project uses the Chase Algorithm to identify lossless decomposition, minimal cover and entailment.

Run from the repository root:

```
docker compose up --build
```

App URLs:

- Frontend: http://localhost:3000
- Backend: http://localhost:8080/

To stop containers:

```
docker compose down
```

## Without Docker

# It is important to note to launch the backend first before the frontend.

### Setting up backend

```
cd backend
source myenv/bin/activate
pip install -r requirements.txt
python3 app.py
```

### Seting up frontend

```
cd ../frontend
npm install
npm start
```

### About the frontend
The frontend uses React as its stack and communicates with the backend via REST API.

### About the backend
The backend consists of two main components. First, the app.py file handles communication with the frontend by exposing four endpoints: /, /api/minimal-cover, /api/lossless-decomposition, and /api/entailment. The root endpoint (/) uses a GET request to verify that the backend is running, while the remaining endpoints use POST requests to process user inputs for each functionality. Additionally, app.py contains helper functions to parse and format user inputs before passing them to the core logic module.

The core logic is implemented in algorithm.py, which contains a tableau-based implementation of the chase algorithm. This module performs the necessary computations for entailment checking, lossless decomposition verification, and minimal cover generation.
