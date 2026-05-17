import { useLocation } from "react-router-dom";
import { useState } from "react";
import "./results.css";

const placeholderImage =
  "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='512' height='512' viewBox='0 0 512 512'%3E%3Crect width='512' height='512' fill='%23eef2f1'/%3E%3Cpath d='M136 352h240L304 248l-48 64-32-40-88 80z' fill='%2393a39d'/%3E%3Ccircle cx='176' cy='176' r='36' fill='%23b7c3bf'/%3E%3C/svg%3E";

function unwrapBackendData(data) {
  return data?.data || data?.result || data;
}

function getImageUrl(item) {
  return (
    item?.image_url ||
    item?.imageUrl ||
    item?.url ||
    item?.image ||
    item?.src ||
    item?.picture ||
    placeholderImage
  );
}

function isCounterfeitItem(item) {
  return Boolean(
    item?.is_counterfeit ||
      item?.isCounterfeit ||
      item?.counterfeit === true ||
      item?.prediction?.includes("copyright_infringement_of_"),
  );
}

function formatPredictionName(prediction) {
  if (!prediction || typeof prediction === "number") {
    return "Unknown product";
  }

  if (prediction === "OK") {
    return "No matching product";
  }

  return prediction
    .replace("copyright_infringement_of_", "")
    .replaceAll("_", " ")
    .trim() || prediction;
}

function normalizeBackendProducts(data, query) {
  const unwrappedData = unwrapBackendData(data);

  if (!unwrappedData) {
    return [];
  }

  const backendProducts = Array.isArray(unwrappedData)
    ? unwrappedData
    : [unwrappedData];

  return backendProducts.flatMap((product, productIndex) => {
    const flaggedImages =
      product.flagged_images ||
      product.flaggedImages ||
      product.images ||
      [];

    return flaggedImages.map((item, imageIndex) => {
      const prediction = item.prediction ?? item.counterfeit ?? 0;

      return {
        id: `${productIndex}-${imageIndex}-${getImageUrl(item)}`,
        name: product.name || item.name || "Product image",
        link: product.link || item.link || query || "#",
        picture: getImageUrl(item),
        prediction,
        predictedProduct: formatPredictionName(prediction),
        counterfeit:
          typeof prediction === "number"
            ? prediction
            : isCounterfeitItem(item)
              ? 1
              : 0,
      };
    });
  });
}

export default function Results() {
  const location = useLocation();
  const params = new URLSearchParams(location.search);
  const query = params.get("query");
  const { data } = location.state || {};

  const [sortType, setSortType] = useState("risk-high");

  // Use the data from the backend API call, or fallback to fake data if not available
  const demoProducts = [
    {
      name: "EasyWarm+",
      link: "https://www.youtube.com/watch?v=oHg5SJYRHA0",
      flagged_images: [
        {
          image_url:
            "https://minervablob.blob.core.windows.net/resized-images-container/BARRIER%20Easywarm+-629910_124877_E-512x512.png?sv=2019-07-07&sr=b&sig=aEwfap14IHBPvQveasXLv8i5djcmaAEPIplIFMIfjOc%3D&se=2029-04-07T21%3A31%3A45Z&sp=r",
          prediction: 0.2,
        },
      ],
    },
    {
      name: "Filtrerande munskydd, PPE",
      link: "https://www.youtube.com/watch?v=oHg5SJYRHA0",
      flagged_images: [
        {
          image_url:
            "https://minervablob.blob.core.windows.net/resized-images-container/Filtering%20Half%20Mask-42904,42902_104373_E-512x512.png?sv=2019-07-07&sr=b&sig=klj27vnnUfEIBY48%2FEcPCZYKJygomgTg7uTarw1UKLI%3D&se=2029-04-07T21%3A31%3A45Z&sp=r",
          prediction: 0.5,
        },
        {
          image_url:
            "https://minervablob.blob.core.windows.net/resized-images-container/Filtering%20Half%20Mask-42904,42902_104373_E-512x512.png?sv=2019-07-07&sr=b&sig=klj27vnnUfEIBY48%2FEcPCZYKJygomgTg7uTarw1UKLI%3D&se=2029-04-07T21%3A31%3A45Z&sp=r",
          prediction: 0.25,
        },
      ],
    },
    {
      name: "4 Pack Mouth Cover Feboy Mask, Anime Mouth Cover Cotton Mask Funny Kawaii Cartoon Cotton Mask Reusable Cosplay Manga Mask For Men Women Kids School Outdoor Party",
      link: "https://www.youtube.com/watch?v=oHg5SJYRHA0",
      flagged_images: [
        {
          image_url:
            "https://m.media-amazon.com/images/I/61yx+36SSbL._AC_UL480_FMwebp_QL65_.jpg",
          prediction: 0.02,
        },
      ],
    },
    {
      name: "Hjälmar",
      link: "https://www.youtube.com/watch?v=oHg5SJYRHA0",
      flagged_images: [
        {
          image_url:
            "https://minervablob.blob.core.windows.net/resized-images-container/Staff%20clothing%20in%20the%20OR%E2%80%93030_187258_E-512x512.png?sv=2019-07-07&sr=b&sig=jQ8u2k4wfq3mMZScb1Kx6q0yB9AbGiOWCQ2ac0magA0%3D&se=2029-04-07T21%3A31%3A45Z&sp=r",
          prediction: 0.92,
        },
      ],
    },
  ];

  const products = normalizeBackendProducts(data || demoProducts, query);

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
        {sortedProducts.length > 0 ? (
          sortedProducts.map((product) => (
            <a
              className="product-container"
              key={product.id}
              href={product.link}
              target="_blank"
              rel="noopener noreferrer"
            >
              <div className="product-image">
                <img
                  src={product.picture}
                  alt={product.name}
                  onError={(event) => {
                    event.currentTarget.src = placeholderImage;
                  }}
                />
              </div>
              <div className="bar-and-name">
                <div className="name">
                  <h5 className="product-link">{product.name}</h5>
                </div>
                <div className="bar-text">
                  <p>Copycat match:</p>
                </div>
                <div className="prediction">
                  <p>{product.predictedProduct}</p>
                </div>
              </div>
            </a>
          ))
        ) : (
          <p className="empty-results">
            No product images were found for this search.
          </p>
        )}
      </div>
    </div>
  );
}
