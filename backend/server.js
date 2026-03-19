const express = require("express");
const cors = require("cors");

const app = express();
const PORT = 8080;

app.use(cors({
  origin: "http://localhost:3000",
  methods: ["GET", "POST", "OPTIONS"],
  allowedHeaders: ["Content-Type"]
}));

app.options(/.*/, cors());

app.use(express.json());

app.get("/", (req, res) => {
  res.json({ message: "Backend is running" });
});

app.post("/api/entailment", (req, res) => {
  console.log("Hit /api/entailment", req.body);

  const { functionalDependencies, selectedOption } = req.body;

  res.json({
    success: true,
    endpoint: "entailment",
    message: "Entailment endpoint reached",
    received: { functionalDependencies, selectedOption }
  });
});

app.post("/api/lossless-decomposition", (req, res) => {
  console.log("Hit /api/lossless-decomposition", req.body);

  const { functionalDependencies, selectedOption } = req.body;

  res.json({
    success: true,
    endpoint: "lossless-decomposition",
    message: "Lossless decomposition endpoint reached",
    received: { functionalDependencies, selectedOption }
  });
});

app.post("/api/minimal-cover", (req, res) => {
  console.log("Hit /api/minimal-cover", req.body);

  const { functionalDependencies, selectedOption } = req.body;

  res.json({
    success: true,
    endpoint: "minimal-cover",
    message: "Minimal cover endpoint reached",
    received: { functionalDependencies, selectedOption }
  });
});

app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});
