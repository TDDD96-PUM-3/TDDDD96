import { useLocation } from "react-router-dom";

export default function Results() {
  const location = useLocation();
  const params = new URLSearchParams(location.search);
  const query = params.get("query");

  return (
    <div>
      <h2>Results for: {query}</h2>
    </div>
  );
}
