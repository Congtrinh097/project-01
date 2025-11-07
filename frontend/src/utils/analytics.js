/**
 * Google Analytics 4 Integration
 * Tracks page views and custom events
 */

// Initialize Google Analytics
export const initGA = (measurementId) => {
  if (!measurementId || typeof window === "undefined") {
    return;
  }

  // Load gtag script
  const script1 = document.createElement("script");
  script1.async = true;
  script1.src = `https://www.googletagmanager.com/gtag/js?id=${measurementId}`;
  document.head.appendChild(script1);

  // Initialize gtag
  window.dataLayer = window.dataLayer || [];
  function gtag() {
    window.dataLayer.push(arguments);
  }
  window.gtag = gtag;

  gtag("js", new Date());
  gtag("config", measurementId, {
    send_page_view: false, // We'll track page views manually
  });

  // console.log("Google Analytics initialized:", measurementId);
};

// Track page view
export const trackPageView = (path) => {
  if (typeof window !== "undefined" && window.gtag) {
    window.gtag("event", "page_view", {
      page_path: path || window.location.pathname,
      page_title: document.title,
    });
  }
};

// Track custom event
export const trackEvent = (eventName, eventParams = {}) => {
  if (typeof window !== "undefined" && window.gtag) {
    window.gtag("event", eventName, eventParams);
  }
};

// Track CV upload
export const trackCVUpload = (filename, fileSize) => {
  trackEvent("cv_upload", {
    event_category: "CV Management",
    event_label: filename,
    value: fileSize,
  });
};

// Track CV delete
export const trackCVDelete = (cvId) => {
  trackEvent("cv_delete", {
    event_category: "CV Management",
    event_label: `CV-${cvId}`,
  });
};

// Track resume generation
export const trackResumeGenerate = () => {
  trackEvent("resume_generate", {
    event_category: "Resume Management",
  });
};

// Track tab navigation
export const trackTabChange = (tabName) => {
  trackEvent("tab_change", {
    event_category: "Navigation",
    event_label: tabName,
  });
};

// Track job recommendation
export const trackJobRecommend = (queryLength, resultsCount) => {
  trackEvent("job_recommend", {
    event_category: "Job Search",
    value: resultsCount,
    query_length: queryLength,
  });
};

// Track CV recommendation
export const trackCVRecommend = (queryLength, resultsCount) => {
  trackEvent("cv_recommend", {
    event_category: "CV Search",
    value: resultsCount,
    query_length: queryLength,
  });
};

// Track chatbot message
export const trackChatbotMessage = (botType = "chatbot") => {
  trackEvent("chatbot_message", {
    event_category: "Chat",
    event_label: botType,
  });
};

// Track error
export const trackError = (errorType, errorMessage) => {
  trackEvent("exception", {
    event_category: "Error",
    event_label: errorType,
    description: errorMessage,
  });
};

// Track job view
export const trackJobView = (jobId) => {
  trackEvent("job_view", {
    event_category: "Jobs",
    event_label: `Job-${jobId}`,
  });
};

// Track job search
export const trackJobSearch = (queryLength, resultsCount) => {
  trackEvent("job_search", {
    event_category: "Jobs",
    value: resultsCount,
    query_length: queryLength,
  });
};

// Track job delete
export const trackJobDelete = (jobId) => {
  trackEvent("job_delete", {
    event_category: "Jobs",
    event_label: `Job-${jobId}`,
  });
};

// Track job filter
export const trackJobFilter = (filterType, filterValue) => {
  trackEvent("job_filter", {
    event_category: "Jobs",
    event_label: filterType,
    value: filterValue,
  });
};

// Track CV view (in History tab)
export const trackCVView = (cvId) => {
  trackEvent("cv_view", {
    event_category: "CV Management",
    event_label: `CV-${cvId}`,
  });
};

// Track download CV
export const trackDownloadCV = (cvId) => {
  trackEvent("download_cv", {
    event_category: "CV Management",
    event_label: `CV-${cvId}`,
  });
};

// Track download resume
export const trackDownloadResume = (resumeId) => {
  trackEvent("download_resume", {
    event_category: "Resume Management",
    event_label: `Resume-${resumeId}`,
  });
};
