import { useEffect } from "react";
import { initGA, trackPageView } from "../utils/analytics";

const GA_MEASUREMENT_ID = import.meta.env.VITE_GA_MEASUREMENT_ID || "";

function GoogleAnalytics() {
  useEffect(() => {
    // Initialize GA on mount
    if (GA_MEASUREMENT_ID) {
      console.log("🔵 Initializing Google Analytics");
      initGA(GA_MEASUREMENT_ID);
      // Track initial page view
      trackPageView(window.location.pathname);

      // Verify initialization after a short delay
      setTimeout(() => {
        if (typeof window !== "undefined" && window.gtag) {
          console.log("✅ Google Analytics is initialized and ready");
        } else {
          console.warn("⚠️ Google Analytics script may not have loaded yet");
        }
      }, 1000);
    } else {
      console.log(
        "ℹ️ Google Analytics is disabled - VITE_GA_MEASUREMENT_ID not set"
      );
    }
  }, []);

  return null; // This component doesn't render anything
}

export default GoogleAnalytics;
