import React, { useState } from "react";

function HomePage() {
	const [selectedOption, setSelectedOption] = useState("entailment");
	const [attributes, setAttributes] = useState("");
	const [functionalDependencies, setFunctionalDependencies] = useState("");
	const [decomposition, setDecomposition] = useState("");
	const [dependency, setDependency] = useState("");
	const [result, setResult] = useState("");
	const [loading, setLoading] = useState(false);
  const [table, setTable] = useState("");
  const [showTable, setShowTable] = useState(false);

	const API_BASE_URL =
		process.env.REACT_APP_API_BASE_URL || "http://localhost:8080/api";

	const endpointMap = {
		entailment: "/entailment",
		lossless: "/lossless-decomposition",
		"minimal-cover": "/minimal-cover",
	};

	const handleCheck = async () => {
		const baseUrl = API_BASE_URL.replace(/\/$/, "");
		const endpoint = `${baseUrl}${endpointMap[selectedOption]}`;

		setLoading(true);
		setResult("");
    setTable("");
    setShowTable(false);

		try {
			const payload = {
				selectedOption,
				functionalDependencies,
			};

			if (selectedOption === "lossless") {
				payload.attributes = attributes;
				payload.decomposition = decomposition;
			}

			if (selectedOption === "minimal-cover") {
				payload.attributes = attributes; // included even if backend does not use it - removed
			}

			if (selectedOption === "entailment") {
				payload.attributes = attributes;
				payload.dependency = dependency;
			}

			const response = await fetch(endpoint, {
				method: "POST",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify(payload),
			});

			const data = await response.json();

			if (!response.ok) {
				throw new Error(data.message || "Something went wrong");
			}

      // setShowTable(
      //   data.result === "Not lossless decomposition." ||
      //   data.result === "False, Dependency is not logically entailed."
      // );			
      setResult(data.result || data.message);
      setTable(data.table || "")
		} catch (error) {
			setResult(error.message || "Error connecting to backend");
		} finally {
			setLoading(false);
		}
	};

	const showAttributes =
		selectedOption === "lossless" || selectedOption === "entailment";

	const showFD =
		selectedOption === "lossless" ||
		selectedOption === "minimal-cover" ||
		selectedOption === "entailment";

	const showDecomposition = selectedOption === "lossless";
	const showDependency = selectedOption === "entailment";
  const showMC = selectedOption == "minimal-cover";

	return (
		<div
			style={{
				minHeight: "100vh",
				background: "linear-gradient(135deg, #f9fbff 0%, #eef2ff 100%)",
				display: "flex",
				justifyContent: "center",
				alignItems: "center",
				padding: "30px",
				fontFamily: "Arial, sans-serif",
			}}
		>
			<div
				style={{
					width: "100%",
					maxWidth: "850px",
					backgroundColor: "white",
					borderRadius: "28px",
					padding: "42px",
					boxShadow: "0 16px 40px rgba(0,0,0,0.12)",
					border: "1px solid #ececec",
				}}
			>
				<h1
					style={{
						textAlign: "center",
						marginBottom: "8px",
						fontSize: "3rem",
						color: "#1f2937",
					}}
				>
					The Chase
				</h1>

				<p
					style={{
						textAlign: "center",
						marginBottom: "32px",
						color: "#6b7280",
						fontSize: "1rem",
					}}
				>
					Pick a challenge, enter your input, and check.
				</p>

				<div style={{ marginBottom: "22px" }}>
					<label
						style={{
							display: "block",
							marginBottom: "10px",
							fontWeight: "bold",
							color: "#374151",
						}}
					>
						Choose a challenge
					</label>

					<select
						value={selectedOption}
						onChange={(e) => {
							const newOption = e.target.value;
							setSelectedOption(newOption);

							setAttributes("");
							setFunctionalDependencies("");
							setDecomposition("");
							setDependency("");
							setResult("");
						}}
						style={{
							width: "100%",
							padding: "14px",
							borderRadius: "12px",
							border: "2px solid #dbeafe",
							backgroundColor: "#f8fbff",
							fontSize: "1rem",
							cursor: "pointer",
							outline: "none",
						}}
					>
						<option value="entailment">Entailment</option>
						<option value="lossless">Lossless decomposition</option>
						<option value="minimal-cover">Minimal cover generation</option>
					</select>
				</div>

				{showAttributes && (
					<div style={{ marginBottom: "22px" }}>
						<label
							style={{
								display: "block",
								marginBottom: "10px",
								fontWeight: "bold",
								color: "#374151",
							}}
						>
							Enter Attributes
						</label>

						<textarea
							value={attributes}
							onChange={(e) => setAttributes(e.target.value)}
							placeholder={"Example:\nABCDE\nor A,B,C,D,E"}
							style={{
								width: "100%",
								height: "90px",
								padding: "16px",
								borderRadius: "14px",
								border: "2px solid #dbeafe",
								backgroundColor: "#fcfdff",
								fontSize: "1rem",
								resize: "vertical",
								outline: "none",
								boxSizing: "border-box",
							}}
						/>
					</div>
				)}

				{showFD && (
					<div style={{ marginBottom: "22px" }}>
						<label
							style={{
								display: "block",
								marginBottom: "10px",
								fontWeight: "bold",
								color: "#374151",
							}}
						>
							Enter Functional Dependencies
						</label>

						<textarea
							value={functionalDependencies}
							onChange={(e) => setFunctionalDependencies(e.target.value)}
							placeholder={"Example:\nA -> B\nB -> C\nAC -> D"}
							style={{
								width: "100%",
								height: "220px",
								padding: "16px",
								borderRadius: "14px",
								border: "2px solid #dbeafe",
								backgroundColor: "#fcfdff",
								fontSize: "1rem",
								resize: "vertical",
								outline: "none",
								boxSizing: "border-box",
							}}
						/>
					</div>
				)}

				{showDependency && (
					<div style={{ marginBottom: "22px" }}>
						<label
							style={{
								display: "block",
								marginBottom: "10px",
								fontWeight: "bold",
								color: "#374151",
							}}
						>
							Enter Dependency to Check
						</label>

						<textarea
							value={dependency}
							onChange={(e) => setDependency(e.target.value)}
							placeholder={"Example:\nA -> B \nB -> C \nAC -> D"}
							style={{
								width: "100%",
								height: "120px",
								padding: "16px",
								borderRadius: "14px",
								border: "2px solid #dbeafe",
								backgroundColor: "#fcfdff",
								fontSize: "1rem",
								resize: "vertical",
								outline: "none",
								boxSizing: "border-box",
							}}
						/>
					</div>
				)}

				{showDecomposition && (
					<div style={{ marginBottom: "22px" }}>
						<label
							style={{
								display: "block",
								marginBottom: "10px",
								fontWeight: "bold",
								color: "#374151",
							}}
						>
							Enter Decomposition
						</label>

						<textarea
							value={decomposition}
							onChange={(e) => setDecomposition(e.target.value)}
							placeholder={"Example:\nABC;BCD;CDE"}
							style={{
								width: "100%",
								height: "120px",
								padding: "16px",
								borderRadius: "14px",
								border: "2px solid #dbeafe",
								backgroundColor: "#fcfdff",
								fontSize: "1rem",
								resize: "vertical",
								outline: "none",
								boxSizing: "border-box",
							}}
						/>
					</div>
				)}

				<button
					onClick={handleCheck}
					disabled={loading}
					style={{
						width: "100%",
						padding: "16px",
						borderRadius: "14px",
						border: "none",
						background: "linear-gradient(135deg, #4f46e5 0%, #22c55e 100%)",
						color: "white",
						fontSize: "1.05rem",
						fontWeight: "bold",
						cursor: loading ? "not-allowed" : "pointer",
						opacity: loading ? 0.7 : 1,
					}}
				>
					{/* {loading ? "Validating..." : "Validate"} */}
					{loading && showMC? "Generating..." : loading ? "Validating" : showMC ? "Generate" : "Validate"}
				</button>
        
        {result && (
          <div style={{
            marginTop: "22px",
            padding: "16px",
            borderRadius: "12px",
            backgroundColor: "#f3f4f6",
            textAlign: "center",
            fontWeight: "bold",
            color: "#1f2937",
            whiteSpace: "pre-wrap",
          }}>
            {result}
            {table && (
              <div style={{ marginTop: "16px" }}>
                <button
                  onClick={() => setShowTable(!showTable)}
                  style={{
                    display: "inline-flex",
                    alignItems: "center",
                    gap: "6px",
                    padding: "7px 16px",
                    borderRadius: "8px",
                    border: "1.5px solid #d1d5db",
                    backgroundColor: showTable ? "#1f2937" : "#ffffff",
                    color: showTable ? "#ffffff" : "#1f2937",
                    fontWeight: "600",
                    fontSize: "13px",
                    cursor: "pointer",
                    transition: "all 0.2s ease",
                  }}
                >
                  <span style={{ fontSize: "15px" }}>{showTable ? "▲" : "▼"}</span>
                  {showTable ? "Hide Chase Table" : "Show Chase Table"}
                </button>

                {showTable && showDecomposition && (
                  <>
                  <div style={{
                    marginTop: "8px",
                    fontSize: "12px",
                    color: "#6b7280",
                    fontStyle: "italic",
                    fontWeight: "normal",
                  }}>
                    💡 The chase is lossless if there exists a row with all unsubscripted values (X).
                  </div>
                  
                  <pre style={{
                    marginTop: "10px",
                    padding: "14px",
                    borderRadius: "10px",
                    border: "1.5px solid #e5e7eb",
                    backgroundColor: "#ffffff",
                    textAlign: "left",
                    fontWeight: "normal",
                    fontSize: "13px",
                    fontFamily: "monospace",
                    whiteSpace: "pre",
                    overflowX: "auto",
                    color: "#374151",
                    boxShadow: "0 1px 4px rgba(0,0,0,0.06)",
                  }}>
                    {table}
                  </pre>
                  </>
                )}

                {showTable && showDependency && (
                  <>
                  <div style={{
                    marginTop: "8px",
                    fontSize: "12px",
                    color: "#6b7280",
                    fontStyle: "italic",
                    fontWeight: "normal",
                  }}>
                    💡 A dependency LHS → RHS is entailed if every pair of rows that agree on LHS also agree on RHS.
                  </div>

                  <pre style={{
                    marginTop: "10px",
                    padding: "14px",
                    borderRadius: "10px",
                    border: "1.5px solid #e5e7eb",
                    backgroundColor: "#ffffff",
                    textAlign: "left",
                    fontWeight: "normal",
                    fontSize: "13px",
                    fontFamily: "monospace",
                    whiteSpace: "pre",
                    overflowX: "auto",
                    color: "#374151",
                    boxShadow: "0 1px 4px rgba(0,0,0,0.06)",
                  }}>
                    {table}
                  </pre>
                  </>
                )}
              </div>)}
          </div>
        )}
			</div>
		</div>
	);
}

export default HomePage;
