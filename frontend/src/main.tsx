import React from "react";
import ReactDOM from "react-dom/client";

import App from "./App";
import "./styles.css";

const rootElement = document.getElementById("root");

if (rootElement === null) {
  throw new Error('Root element "#root" not found.');
}

document.body.classList.add("decision-engine-body");
rootElement.classList.add("decision-engine-root");

ReactDOM.createRoot(rootElement).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
