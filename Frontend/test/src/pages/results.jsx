import { useLocation } from "react-router-dom";
import "./results.css";

export default function Results() {
  const location = useLocation();
  const params = new URLSearchParams(location.search);
  const query = params.get("query");

  return (
    <div>
      <h2 className="results-title">Results for: {query || "nothing"}</h2>
    </div>
  );
}
