import { useNavigate } from "react-router-dom";
import SearchBar from "../components/SearchBar";
import "./search.css";

export default function Search() {
  const navigate = useNavigate();

  const handleSearch = (query) => {
    navigate(`/results?query=${query}`);
  };

  return (
    <div className="search-container">
      <h1>Search Page</h1>

      <SearchBar onSearch={handleSearch} />

      <button onClick={() => navigate("/results")}>
        Go To Results
      </button>
    </div>
  );
}