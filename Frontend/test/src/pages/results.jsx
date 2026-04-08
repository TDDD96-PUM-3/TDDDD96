import { useLocation } from "react-router-dom";
import "./results.css";
import LinearWithValueLabel from "../components/PercentageBar.jsx";

export default function Results() {
  const location = useLocation();
  const params = new URLSearchParams(location.search);
  const query = params.get("query");

  const fake_products = [
    {
      id: 1,
      name: "bitch",
      link: "https://www.google.com/?client=safari",
      picture: "https://www.youtube.com/watch?v=oHg5SJYRHA0",
      counterfeit: 0.2,
    },
    {
      id: 2,
      name: "bitch",
      link: "https://www.google.com/?client=safari",
      picture: "https://www.youtube.com/watch?v=oHg5SJYRHA0",
      counterfeit: 0.5,
    },
    {
      id: 2,
      name: "bitch",
      link: "https://www.google.com/?client=safari",
      picture: "https://www.youtube.com/watch?v=oHg5SJYRHA0",
      counterfeit: 0.25,
    },
  ];

  return (
    <div className="results-container">
      <h1 className="results-title">Results</h1>
      <h6>Based on search: {query || "nothing"}</h6>
      <div className="products">
        {fake_products
          .sort((a, b) => b.counterfeit - a.counterfeit)
          .map((product) => (
            <div className="product-container" key={product.id}>
              <a href={product.link} className="bajs">
                {product.name}
              </a>
              <img src={product.picture} alt={product.name} />
              <LinearWithValueLabel percentage={product.counterfeit * 100} />
            </div>
          ))}
      </div>
    </div>
  );
}
