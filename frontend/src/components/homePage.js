import React, { useState } from "react";

function HomePage() {
  const [selectedOption, setSelectedOption] = useState("entailment");
  const [functionalDependencies, setFunctionalDependencies] = useState("");
  const [dependencyToCheck, setDependencyToCheck] = useState("")
  const [decompositionToCheck, setDecompositionToCheck] = useState("")
  const [result, setResult] = useState("");

  const endpointMap = {
    entailment: "http://localhost:8080/api/entailment",
    lossless: "http://localhost:8080/api/lossless-decomposition",
    "minimal-cover": "http://localhost:8080/api/minimal-cover"
    };

  const labelMap = {
    entailment: "Entailment",
    lossless: "Lossless decomposition",
    "minimal-cover": "Minimal cover generation"
  };

  const handleCheck = async () => {
    const endpoint = endpointMap[selectedOption];

    console.log("Selected option:", selectedOption);
    console.log("Endpoint:", endpoint);

    try {
      const response = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          functionalDependencies,
          selectedOption: labelMap[selectedOption]
        })
      });

      const data = await response.json();
      console.log("Response data:", data);
      setResult(data.message);
    } catch (error) {
      console.error("Fetch error:", error);
      setResult("Error connecting to backend");
    }
  };

  return (
    <div style={{ minHeight: "100vh", background: "linear-gradient(135deg, #f9fbff 0%, #eef2ff 100%)", display: "flex", justifyContent: "center", alignItems: "center", padding: "30px", fontFamily: "Arial, sans-serif" }}>
      <div style={{ width: "100%", maxWidth: "850px", backgroundColor: "white", borderRadius: "28px", padding: "42px", boxShadow: "0 16px 40px rgba(0,0,0,0.12)", border: "1px solid #ececec" }}>
        <h1 style={{ textAlign: "center", marginBottom: "8px", fontSize: "3rem", color: "#1f2937" }}>
          The Chase
        </h1>

        <p style={{ textAlign: "center", marginBottom: "32px", color: "#6b7280", fontSize: "1rem" }}>
          Pick a challenge, enter your functional dependencies, and validate.
        </p>

        <div style={{ marginBottom: "22px" }}>
          <label style={{ display: "block", marginBottom: "10px", fontWeight: "bold", color: "#374151" }}>
            Choose a challenge
          </label>

          <select value={selectedOption} onChange={(e) => setSelectedOption(e.target.value)} style={{ width: "100%", padding: "14px", borderRadius: "12px", border: "2px solid #dbeafe", backgroundColor: "#f8fbff", fontSize: "1rem", cursor: "pointer", outline: "none" }}>
            <option value="entailment">Entailment</option>
            <option value="lossless">Lossless decomposition</option>
            <option value="minimal-cover">Minimal cover generation</option>
          </select>

          {selectedOption === "entailment" && (
            <div style={{ marginBottom: "22px" }}>
              <label style={{ display: "block", padding: "16px", fontWeight: "bold", color: "#374151" }}>
                Enter Dependency to check
              </label>

              <textarea
                value={dependencyToCheck}
                onChange={(e) => setDependencyToCheck(e.target.value)}
                placeholder={"Example: A -> B"}
                style={{ width: "100%", height: "50px", padding: "16px", borderRadius: "14px", border: "2px solid #dbeafe", backgroundColor: "#fcfdff", fontSize: "1rem", resize: "vertical", outline: "none", boxSizing: "border-box" }}
              />
            </div>
          )}

          {selectedOption === "lossless" && (
            <div style={{ marginBottom: "22px" }}>
              <label style={{ display: "block", padding: "16px", fontWeight: "bold", color: "#374151" }}>
                Enter Decomposition to check
              </label>

              <textarea
                value={decompositionToCheck}
                onChange={(e) => setDecompositionToCheck(e.target.value)}
                placeholder={"Example: {A,B,C}, {B,C,D}, {B,D,E}"}
                style={{ width: "100%", height: "50px", padding: "16px", borderRadius: "14px", border: "2px solid #dbeafe", backgroundColor: "#fcfdff", fontSize: "1rem", resize: "vertical", outline: "none", boxSizing: "border-box" }}
              />
            </div>
          )}

          {selectedOption !== "minimal-cover" && (
            <div style={{ marginBottom: "22px" }}>
              <label style={{ display: "block", marginBottom: "10px", fontWeight: "bold", color: "#374151" }}>
                Enter Attributes
              </label>

              <textarea
                value={functionalDependencies}
                onChange={(e) => setFunctionalDependencies(e.target.value)}
                placeholder={"Example: A,B,C,D,E"}
                style={{ width: "100%", height: "50px", padding: "16px", borderRadius: "14px", border: "2px solid #dbeafe", backgroundColor: "#fcfdff", fontSize: "1rem", resize: "vertical", outline: "none", boxSizing: "border-box" }}
              />
            </div>
          )}
        </div>

        <div style={{ marginBottom: "22px" }}>
          <label style={{ display: "block", marginBottom: "10px", fontWeight: "bold", color: "#374151" }}>
            Enter Functional Dependencies
          </label>

          <textarea
            value={functionalDependencies}
            onChange={(e) => setFunctionalDependencies(e.target.value)}
            placeholder={"Example:\nA -> B\nB -> C\nAC -> D"}
            style={{ width: "100%", height: "220px", padding: "16px", borderRadius: "14px", border: "2px solid #dbeafe", backgroundColor: "#fcfdff", fontSize: "1rem", resize: "vertical", outline: "none", boxSizing: "border-box" }}
          />
        </div>

        <button onClick={handleCheck} style={{ width: "100%", padding: "16px", borderRadius: "14px", border: "none", background: "linear-gradient(135deg, #4f46e5 0%, #22c55e 100%)", color: "white", fontSize: "1.05rem", fontWeight: "bold", cursor: "pointer" }}>
          Validate
        </button>

        {result && (
          <div style={{ marginTop: "22px", padding: "16px", borderRadius: "12px", backgroundColor: "#f3f4f6", textAlign: "center", fontWeight: "bold", color: "#1f2937" }}>
            {result}
          </div>
        )}
      </div>
    </div>
  );
}

export default HomePage;