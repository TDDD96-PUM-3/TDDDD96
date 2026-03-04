import { useNavigate } from "react-router-dom";
import Login from "../components/LoginBoxes.jsx";
import "./search.css";

export default function Search() {
  const navigate = useNavigate();

  return (
    <div className="login-container">
      <Login />

      <div className="text-center mt-3">
        <button
          className="btn btn-secondary"
          onClick={() => navigate("/results")}
        >
          Go To Results
        </button>
      </div>
    </div>
  );
}
