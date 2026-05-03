import { useNavigate } from "react-router-dom";
import SearchBar from "../components/SearchBar";
import "./search.css";

export default function Search() {
  const navigate = useNavigate();

  const handleSearch = (query) => {
    let trimmedQuery = query.trim();
    if (!trimmedQuery) {
      return;
    }

    if (!/^https?:\/\//i.test(trimmedQuery)) {
      trimmedQuery = `https://${trimmedQuery}`;
    }

    navigate(`/results?query=${encodeURIComponent(trimmedQuery)}`);
    // navigate(`/statistics?query=${query}`);
  };

  return (
    <div className="search-container">
      <h1>Search.</h1>
      <SearchBar onSearch={handleSearch} />
    </div>
  );
}
