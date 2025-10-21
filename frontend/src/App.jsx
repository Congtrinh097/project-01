import {
  Briefcase,
  Bug,
  FileEdit,
  FileText,
  History,
  Menu,
  MessageCircle,
  Sparkles,
  Upload,
  X,
} from "lucide-react";
import React, { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "react-query";
import {
  deleteCV,
  deleteResume,
  generateResume,
  getCV,
  getCVs,
  getResumes,
  recommendCVs,
  uploadCV,
} from "./services/api";

// Import tab components
import ChatbotTab from "./components/ChatbotTab";
import GenerateResumeTab from "./components/GenerateResumeTab";
import HistoryTab from "./components/HistoryTab";
import JobsTab from "./components/JobsTab";
import RecommendTab from "./components/RecommendTab";
import UploadTab from "./components/UploadTab";

function App() {
  const [activeTab, setActiveTab] = useState("upload");
  const [selectedCV, setSelectedCV] = useState(null);
  const [selectedResume, setSelectedResume] = useState(null);
  const [recommendResults, setRecommendResults] = useState(null);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const queryClient = useQueryClient();

  const { data: cvs = [], isLoading: cvsLoading } = useQuery("cvs", getCVs);
  const { data: resumes = [], isLoading: resumesLoading } = useQuery(
    "resumes",
    getResumes
  );

  const uploadMutation = useMutation(uploadCV, {
    onSuccess: () => {
      queryClient.invalidateQueries("cvs");
      setActiveTab("history");
    },
  });

  const deleteMutation = useMutation(deleteCV, {
    onSuccess: () => {
      queryClient.invalidateQueries("cvs");
      // Clear selected CV if it was deleted
      if (selectedCV) {
        setSelectedCV(null);
      }
    },
  });

  const generateResumeMutation = useMutation(generateResume, {
    onSuccess: (data) => {
      queryClient.invalidateQueries("resumes");
      setSelectedResume(data);
    },
  });

  const deleteResumeMutation = useMutation(deleteResume, {
    onSuccess: () => {
      queryClient.invalidateQueries("resumes");
      if (selectedResume) {
        setSelectedResume(null);
      }
    },
  });

  const recommendMutation = useMutation(
    ({ query, limit }) => recommendCVs(query, limit),
    {
      onSuccess: (data) => {
        setRecommendResults(data);
      },
    }
  );

  const handleFileUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
      uploadMutation.mutate(file);
    }
  };

  const handleCVSelect = async (cvId) => {
    try {
      const cv = await getCV(cvId);
      setSelectedCV(cv);
    } catch (error) {
      console.error("Error fetching CV details:", error);
    }
  };

  const handleDeleteCV = (cvId, event) => {
    event.stopPropagation(); // Prevent triggering the CV selection
    if (window.confirm("Are you sure you want to delete this CV?")) {
      deleteMutation.mutate(cvId);
    }
  };

  const handleGenerateResume = (inputText) => {
    generateResumeMutation.mutate(inputText);
  };

  const handleDeleteResume = (resumeId, event) => {
    event.stopPropagation();
    if (window.confirm("Are you sure you want to delete this resume?")) {
      deleteResumeMutation.mutate(resumeId);
    }
  };

  const handleRecommend = (query, limit) => {
    setRecommendResults(null); // Clear previous results
    recommendMutation.mutate({ query, limit });
  };

  const handleTabChange = (tab) => {
    if (tab === "report-bug") {
      window.open(
        "https://github.com/Congtrinh097/project-01/issues/new",
        "_blank",
        "noopener,noreferrer"
      );
      setIsMobileMenuOpen(false);
      return;
    }
    setActiveTab(tab);
    setIsMobileMenuOpen(false); // Close mobile menu on tab change
  };

  const menuItems = [
    { id: "recommend", icon: Sparkles, label: "Recommend CVs" },
    { id: "chatbot", icon: MessageCircle, label: "Interview Bot" },
    { id: "generate", icon: FileEdit, label: "Generate CV" },
    { id: "jobs", icon: Briefcase, label: "Jobs" },
    { id: "upload", icon: Upload, label: "Upload CV" },
    { id: "history", icon: History, label: "History" },
    { id: "report-bug", icon: Bug, label: "Give Ideas/Bugs" },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo */}
            <div className="flex items-center">
              <FileText className="h-8 w-8 text-purple-600" />
              <h1 className="ml-2 text-xl font-bold text-gray-900">
                CV Analyzer
              </h1>
            </div>

            {/* Desktop Navigation */}
            <nav className="hidden lg:flex space-x-2">
              {menuItems.map((item) => {
                const Icon = item.icon;
                const isReportBug = item.id === "report-bug";
                return (
                  <button
                    key={item.id}
                    onClick={() => handleTabChange(item.id)}
                    className={`flex items-center px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                      activeTab === item.id
                        ? "bg-purple-100 text-purple-700"
                        : isReportBug
                        ? "text-red-600 hover:text-red-700 hover:bg-red-50"
                        : "text-gray-600 hover:text-gray-900 hover:bg-gray-100"
                    }`}
                  >
                    <Icon className="h-4 w-4 mr-2" />
                    <span className="hidden xl:inline">{item.label}</span>
                  </button>
                );
              })}
            </nav>

            {/* Mobile menu button */}
            <button
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              className="lg:hidden inline-flex items-center justify-center p-2 rounded-md text-gray-600 hover:text-gray-900 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-purple-500"
              aria-expanded={isMobileMenuOpen}
            >
              <span className="sr-only">Open main menu</span>
              {isMobileMenuOpen ? (
                <X className="block h-6 w-6" />
              ) : (
                <Menu className="block h-6 w-6" />
              )}
            </button>
          </div>
        </div>

        {/* Mobile Navigation Menu */}
        {isMobileMenuOpen && (
          <div className="lg:hidden border-t border-gray-200">
            <div className="px-2 pt-2 pb-3 space-y-1">
              {menuItems.map((item) => {
                const Icon = item.icon;
                const isReportBug = item.id === "report-bug";
                return (
                  <button
                    key={item.id}
                    onClick={() => handleTabChange(item.id)}
                    className={`w-full flex items-center px-3 py-2 rounded-md text-base font-medium transition-colors ${
                      activeTab === item.id
                        ? "bg-purple-100 text-purple-700"
                        : isReportBug
                        ? "text-red-600 hover:text-red-700 hover:bg-red-50"
                        : "text-gray-600 hover:text-gray-900 hover:bg-gray-100"
                    }`}
                  >
                    <Icon className="h-5 w-5 mr-3" />
                    {item.label}
                  </button>
                );
              })}
            </div>
          </div>
        )}
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 sm:py-6 lg:py-8">
        {activeTab === "upload" && (
          <UploadTab
            uploadMutation={uploadMutation}
            handleFileUpload={handleFileUpload}
          />
        )}

        {activeTab === "generate" && (
          <GenerateResumeTab
            generateMutation={generateResumeMutation}
            resumes={resumes}
            resumesLoading={resumesLoading}
            selectedResume={selectedResume}
            onGenerateResume={handleGenerateResume}
            onDeleteResume={handleDeleteResume}
            isDeleting={deleteResumeMutation.isLoading}
          />
        )}

        {activeTab === "history" && (
          <HistoryTab
            cvs={cvs}
            cvsLoading={cvsLoading}
            selectedCV={selectedCV}
            onCVSelect={handleCVSelect}
            onDeleteCV={handleDeleteCV}
            isDeleting={deleteMutation.isLoading}
          />
        )}

        {activeTab === "chatbot" && <ChatbotTab />}

        {activeTab === "recommend" && (
          <RecommendTab
            onRecommend={handleRecommend}
            isLoading={recommendMutation.isLoading}
            error={
              recommendMutation.error?.response?.data?.detail ||
              recommendMutation.error?.message
            }
            results={recommendResults}
          />
        )}

        {activeTab === "jobs" && <JobsTab />}
      </main>
    </div>
  );
}

export default App;
