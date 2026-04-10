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
      name: "EasyWarm+",
      link: "https://www.youtube.com/watch?v=oHg5SJYRHA0",
      picture:
        "https://minervablob.blob.core.windows.net/resized-images-container/BARRIER%20Easywarm+-629910_124877_E-512x512.png?sv=2019-07-07&sr=b&sig=aEwfap14IHBPvQveasXLv8i5djcmaAEPIplIFMIfjOc%3D&se=2029-04-07T21%3A31%3A45Z&sp=r",
      counterfeit: 0.2,
    },
    {
      id: 2,
      name: "Filtrerande munskydd, PPE",
      link: "https://www.youtube.com/watch?v=oHg5SJYRHA0",
      picture:
        "https://minervablob.blob.core.windows.net/resized-images-container/Filtering%20Half%20Mask-42904,42902_104373_E-512x512.png?sv=2019-07-07&sr=b&sig=klj27vnnUfEIBY48%2FEcPCZYKJygomgTg7uTarw1UKLI%3D&se=2029-04-07T21%3A31%3A45Z&sp=r",
      counterfeit: 0.5,
    },
    {
      id: 5,
      name: "Filtrerande munskydd, PPE",
      link: "https://www.youtube.com/watch?v=oHg5SJYRHA0",
      picture:
        "https://minervablob.blob.core.windows.net/resized-images-container/Filtering%20Half%20Mask-42904,42902_104373_E-512x512.png?sv=2019-07-07&sr=b&sig=klj27vnnUfEIBY48%2FEcPCZYKJygomgTg7uTarw1UKLI%3D&se=2029-04-07T21%3A31%3A45Z&sp=r",
      counterfeit: 0.25,
    },
    {
      id: 3,
      name: "4 Pack Mouth Cover Feboy Mask, Anime Mouth Cover Cotton Mask Funny Kawaii Cartoon Cotton Mask Reusable Cosplay Manga Mask For Men Women Kids School Outdoor Party",
      link: "https://www.youtube.com/watch?v=oHg5SJYRHA0",
      picture:
        "https://m.media-amazon.com/images/I/61yx+36SSbL._AC_UL480_FMwebp_QL65_.jpg",
      counterfeit: 0.02,
    },
    {
      id: 4,
      name: "Hjälmar",
      link: "https://www.youtube.com/watch?v=oHg5SJYRHA0",
      picture:
        "https://minervablob.blob.core.windows.net/resized-images-container/Staff%20clothing%20in%20the%20OR%E2%80%93030_187258_E-512x512.png?sv=2019-07-07&sr=b&sig=jQ8u2k4wfq3mMZScb1Kx6q0yB9AbGiOWCQ2ac0magA0%3D&se=2029-04-07T21%3A31%3A45Z&sp=r",
      counterfeit: 0.92,
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
        <a className="product-container" key={product.id} href={product.link} target="_blank" rel="noopener noreferrer">
          <img src={product.picture} alt={product.name} />
          <div className="bar-and-name">
            <div className="name"><h5 className="product-link">{product.name}</h5></div>
            <div className="bar-text"><p>Counterfeit probability:</p></div>
            <div className="bar"><LinearWithValueLabel percentage={product.counterfeit * 100} /></div>
            
          </div>
        </a>
        ))}
      </div>
    </div>
  );
}
