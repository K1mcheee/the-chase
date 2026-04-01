import React, { useState } from "react";

function HomePage() {
	const [selectedOption, setSelectedOption] = useState("entailment");
	const [attributes, setAttributes] = useState("");
	const [functionalDependencies, setFunctionalDependencies] = useState("");
	const [decomposition, setDecomposition] = useState("");
	const [dependency, setDependency] = useState("");
	const [result, setResult] = useState("");
	const [loading, setLoading] = useState(false);

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

			setResult(data.result || data.message);
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
					Pick a challenge, enter your input, and validate.
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
					{loading ? "Validating..." : "Validate"}
				</button>

				{result && (
					<div
						style={{
							marginTop: "22px",
							padding: "16px",
							borderRadius: "12px",
							backgroundColor: "#f3f4f6",
							textAlign: "center",
							fontWeight: "bold",
							color: "#1f2937",
							whiteSpace: "pre-wrap",
						}}
					>
						{result}
					</div>
				)}
			</div>
		</div>
	);
}

export default HomePage;
