import { useLocation } from "react-router-dom";
import { useState } from "react";
import "./results.css";

const PLACEHOLDER_IMAGE = "https://via.placeholder.com/512?text=Website";

function getPredictionLabel(product) {
  if (product.prediction) {
    return product.prediction.replace("copyright_infringement_of_", "");
  }

  return product.counterfeit ? "Counterfeit" : "OK";
}

function normalizeProducts(data, query) {
  if (!data) {
    return null;
  }

  if (Array.isArray(data.products) && data.products.length > 0) {
    return data.products.map((product, index) => ({
      id: product.id ?? `${product.picture ?? product.link ?? "product"}-${index}`,
      name: product.name || `${data.name || "Product"} ${index + 1}`,
      link: product.link || data.link || query,
      picture: product.picture || product.image || product.image_url || PLACEHOLDER_IMAGE,
      counterfeit: Number(product.counterfeit) || 0,
      prediction: product.prediction || "",
    }));
  }

  if (Array.isArray(data.images) && data.images.length > 0) {
    return data.images.map((image, index) => ({
      id: `${image}-${index}`,
      name: `${data.name || "Product"} ${index + 1}`,
      link: data.link || query,
      picture: image,
      counterfeit: 0,
      prediction: "OK",
    }));
  }

  return [
    {
      id: 1,
      name: data.name || "Website",
      link: data.link || query,
      picture: data.picture || data.image || PLACEHOLDER_IMAGE,
      counterfeit: Number(data.counterfeit) || 0,
      prediction: data.prediction || "",
    },
  ];
}

export default function Results() {
  const location = useLocation();
  const params = new URLSearchParams(location.search);
  const query = params.get("query");
  const { data } = location.state || {};

  const [sortType, setSortType] = useState("risk-high");

  // Use the data from the backend API call, or fallback to fake data if not available
  const products = normalizeProducts(data, query) || [
      {
        id: 1,
        name: "EasyWarm+",
        link: "https://www.youtube.com/watch?v=oHg5SJYRHA0",
        picture:
          "https://minervablob.blob.core.windows.net/resized-images-container/BARRIER%20Easywarm+-629910_124877_E-512x512.png?sv=2019-07-07&sr=b&sig=aEwfap14IHBPvQveasXLv8i5djcmaAEPIplIFMIfjOc%3D&se=2029-04-07T21%3A31%3A45Z&sp=r",
        counterfeit: 0.2,
        prediction: "copyright_infringement_of_EasyWarm+",
      },
      {
        id: 2,
        name: "Filtrerande munskydd, PPE",
        link: "https://www.youtube.com/watch?v=oHg5SJYRHA0",
        picture:
          "https://minervablob.blob.core.windows.net/resized-images-container/Filtering%20Half%20Mask-42904,42902_104373_E-512x512.png?sv=2019-07-07&sr=b&sig=klj27vnnUfEIBY48%2FEcPCZYKJygomgTg7uTarw1UKLI%3D&se=2029-04-07T21%3A31%3A45Z&sp=r",
        counterfeit: 0.5,
        prediction: "copyright_infringement_of_Filtrerande munskydd, PPE",
      },
      {
        id: 5,
        name: "Filtrerande munskydd, PPE",
        link: "https://www.youtube.com/watch?v=oHg5SJYRHA0",
        picture:
          "https://minervablob.blob.core.windows.net/resized-images-container/Filtering%20Half%20Mask-42904,42902_104373_E-512x512.png?sv=2019-07-07&sr=b&sig=klj27vnnUfEIBY48%2FEcPCZYKJygomgTg7uTarw1UKLI%3D&se=2029-04-07T21%3A31%3A45Z&sp=r",
        counterfeit: 0.25,
        prediction: "copyright_infringement_of_Filtrerande munskydd, PPE",
      },
      {
        id: 3,
        name: "4 Pack Mouth Cover Feboy Mask, Anime Mouth Cover Cotton Mask Funny Kawaii Cartoon Cotton Mask Reusable Cosplay Manga Mask For Men Women Kids School Outdoor Party",
        link: "https://www.youtube.com/watch?v=oHg5SJYRHA0",
        picture:
          "https://m.media-amazon.com/images/I/61yx+36SSbL._AC_UL480_FMwebp_QL65_.jpg",
        counterfeit: 0.02,
        prediction: "OK",
      },
      {
        id: 4,
        name: "Hjälmar",
        link: "https://www.youtube.com/watch?v=oHg5SJYRHA0",
        picture:
          "https://minervablob.blob.core.windows.net/resized-images-container/Staff%20clothing%20in%20the%20OR%E2%80%93030_187258_E-512x512.png?sv=2019-07-07&sr=b&sig=jQ8u2k4wfq3mMZScb1Kx6q0yB9AbGiOWCQ2ac0magA0%3D&se=2029-04-07T21%3A31%3A45Z&sp=r",
        counterfeit: 0.92,
        prediction: "copyright_infringement_of_Hjälmar",
      },
    ];

  const sortedProducts = [...products].sort((a, b) => {
    switch (sortType) {
      case "risk-high":
        return b.counterfeit - a.counterfeit;
      case "risk-low":
        return a.counterfeit - b.counterfeit;
      case "name-az":
        return a.name.localeCompare(b.name);
      case "name-za":
        return b.name.localeCompare(a.name);
      default:
        return 0;
    }
  });

  return (
    <div className="results-container">
      <h1 className="results-title">Results</h1>
      <div className="results-header">
        <h6>Based on search: {query || "nothing"}</h6>
        <div className="sort-controls">
          <label htmlFor="sort">Sort by: </label>
          <select
            id="sort"
            value={sortType}
            onChange={(e) => setSortType(e.target.value)}
          >
            <option value="risk-high">Counterfeit risk: High to low </option>
            <option value="risk-low">Counterfeit risk: Low to high</option>
            <option value="name-az">Name: A to Z</option>
            <option value="name-za">Name: Z to A</option>
          </select>
        </div>
      </div>

      <div className="products">
        {sortedProducts.map((product) => (
          <a
            className="product-container"
            key={product.id}
            href={product.link}
            target="_blank"
            rel="noopener noreferrer"
          >
            <img src={product.picture} alt={product.name} />
            <div className="bar-and-name">
              <div className="name">
                <h5 className="product-link">{product.name}</h5>
              </div>
              <div className="prediction-text">
                <p>Copycat prediction:</p>
              </div>
              <div className="prediction-value">
                <span>{getPredictionLabel(product)}</span>
              </div>
            </div>
          </a>
        ))}
      </div>
    </div>
  );
}
