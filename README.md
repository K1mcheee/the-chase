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
