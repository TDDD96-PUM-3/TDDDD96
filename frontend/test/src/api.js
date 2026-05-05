const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export const scrapeUrl = async (url) => {
  try {
    const fullUrl = `${API_BASE_URL}/scrape_url?url=${encodeURIComponent(url)}`;
    console.log("Calling API:", fullUrl);

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 300000); // 5 minute timeout

    const response = await fetch(fullUrl, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(
        errorData.error || `HTTP error! status: ${response.status}`,
      );
    }

    const data = await response.json();
    return data;
  } catch (error) {
    if (error.name === "AbortError") {
      console.error("Request timeout after 5 minutes");
      throw new Error("Request timeout. The URL scraping took too long.");
    }
    console.error("Error scraping URL:", error);
    throw error;
  }
};
