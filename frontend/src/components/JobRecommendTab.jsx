import {
  AlertCircle,
  Briefcase,
  Clock,
  Code,
  ExternalLink,
  Gift,
  GraduationCap,
  Loader2,
  MapPin,
  Search,
  Sparkles,
  Tag,
  TrendingUp,
  Upload,
  Users,
} from "lucide-react";
import React, { useState } from "react";
import ReactMarkdown from "react-markdown";

const JobRecommendTab = ({
  onRecommend,
  onRecommendFromCV,
  isLoading,
  error,
  results,
}) => {
  const [query, setQuery] = useState("");
  const [limit, setLimit] = useState(5);
  const [inputMode, setInputMode] = useState("text"); // "text" or "file"
  const [selectedFile, setSelectedFile] = useState(null);

  const handleTextSubmit = (e) => {
    e.preventDefault();
    if (query.trim()) {
      onRecommend(query, limit);
    }
  };

  const handleFileSubmit = (e) => {
    e.preventDefault();
    if (selectedFile) {
      onRecommendFromCV(selectedFile, limit);
    }
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setSelectedFile(file);
    }
  };

  const handleModeChange = (mode) => {
    setInputMode(mode);
    // Reset state when switching modes
    setQuery("");
    setSelectedFile(null);
    setLimit(5);
  };

  return (
    <div className="space-y-6">
      {/* Header Section */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-center mb-4">
          <Sparkles className="h-6 w-6 text-blue-600 mr-2" />
          <h2 className="text-2xl font-bold text-gray-900">
            Job Recommendation
          </h2>
        </div>
        <p className="text-gray-600">
          Find the best job opportunities that match your skills and experience.
          Use semantic search with text queries or upload your CV to get
          personalized job recommendations.
        </p>
      </div>

      {/* Input Mode Selector */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex space-x-4 mb-4">
          <button
            onClick={() => handleModeChange("text")}
            className={`flex items-center px-4 py-2 rounded-lg font-medium transition-colors ${
              inputMode === "text"
                ? "bg-blue-100 text-blue-700 border-2 border-blue-400"
                : "bg-gray-100 text-gray-600 hover:bg-gray-200"
            }`}
          >
            <Search className="h-4 w-4 mr-2" />
            Text Query
          </button>
          <button
            onClick={() => handleModeChange("file")}
            className={`flex items-center px-4 py-2 rounded-lg font-medium transition-colors ${
              inputMode === "file"
                ? "bg-blue-100 text-blue-700 border-2 border-blue-400"
                : "bg-gray-100 text-gray-600 hover:bg-gray-200"
            }`}
          >
            <Upload className="h-4 w-4 mr-2" />
            Upload CV
          </button>
        </div>

        {/* Text Query Form */}
        {inputMode === "text" && (
          <form onSubmit={handleTextSubmit} className="space-y-4">
            <div>
              <label
                htmlFor="query"
                className="block text-sm font-medium text-gray-700 mb-2"
              >
                Search Query
              </label>
              <textarea
                id="query"
                rows="4"
                className="block w-full px-4 py-3 rounded-lg border border-gray-300 shadow-sm focus:outline-none focus:border-blue-400 focus:ring-2 focus:ring-blue-200 transition-colors duration-200 text-sm placeholder-gray-400 disabled:bg-gray-50 disabled:text-gray-500"
                placeholder="e.g., I'm a senior software engineer with 5+ years of Python and React experience. Looking for remote positions with good work-life balance and competitive salary..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                disabled={isLoading}
              />
              <p className="mt-2 text-sm text-gray-500">
                Describe your skills, experience, and job preferences using
                natural language.
              </p>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label
                  htmlFor="limit"
                  className="block text-sm font-medium text-gray-700 mb-2"
                >
                  Number of Results
                </label>
                <select
                  id="limit"
                  className="block w-[100px] px-3 py-2 rounded-lg border border-gray-300 shadow-sm focus:outline-none focus:border-blue-400 focus:ring-2 focus:ring-blue-200 transition-colors duration-200 text-sm disabled:bg-gray-50 disabled:text-gray-500"
                  value={limit}
                  onChange={(e) => setLimit(Number(e.target.value))}
                  disabled={isLoading}
                >
                  <option value="3">Top 3</option>
                  <option value="5">Top 5</option>
                  <option value="10">Top 10</option>
                  <option value="20">Top 20</option>
                </select>
              </div>
            </div>

            <button
              type="submit"
              disabled={!query.trim() || isLoading}
              className="w-full flex items-center justify-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:bg-gray-300 disabled:cursor-not-allowed"
            >
              {isLoading ? (
                <>
                  <Loader2 className="animate-spin h-5 w-5 mr-2" />
                  Searching...
                </>
              ) : (
                <>
                  <Search className="h-5 w-5 mr-2" />
                  Find Jobs
                </>
              )}
            </button>
          </form>
        )}

        {/* File Upload Form */}
        {inputMode === "file" && (
          <form onSubmit={handleFileSubmit} className="space-y-4">
            <div>
              <label
                htmlFor="cv-upload"
                className="block text-sm font-medium text-gray-700 mb-2"
              >
                Upload Your CV
              </label>
              <div className="flex items-center space-x-4">
                <label className="flex-1 cursor-pointer">
                  <div className="flex items-center justify-center px-4 py-3 border-2 border-dashed border-gray-300 rounded-lg hover:border-blue-400 transition-colors">
                    <Upload className="h-5 w-5 text-gray-400 mr-2" />
                    <span className="text-sm text-gray-600">
                      {selectedFile
                        ? selectedFile.name
                        : "Choose a PDF or DOCX file"}
                    </span>
                  </div>
                  <input
                    id="cv-upload"
                    type="file"
                    accept=".pdf,.doc,.docx"
                    onChange={handleFileChange}
                    disabled={isLoading}
                    className="hidden"
                  />
                </label>
              </div>
              <p className="mt-2 text-sm text-gray-500">
                Upload your CV (PDF or DOCX) and we'll find jobs that match your
                profile.
              </p>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label
                  htmlFor="limit-file"
                  className="block text-sm font-medium text-gray-700 mb-2"
                >
                  Number of Results
                </label>
                <select
                  id="limit-file"
                  className="block w-[100px] px-3 py-2 rounded-lg border border-gray-300 shadow-sm focus:outline-none focus:border-blue-400 focus:ring-2 focus:ring-blue-200 transition-colors duration-200 text-sm disabled:bg-gray-50 disabled:text-gray-500"
                  value={limit}
                  onChange={(e) => setLimit(Number(e.target.value))}
                  disabled={isLoading}
                >
                  <option value="3">Top 3</option>
                  <option value="5">Top 5</option>
                  <option value="10">Top 10</option>
                  <option value="20">Top 20</option>
                </select>
              </div>
            </div>

            <button
              type="submit"
              disabled={!selectedFile || isLoading}
              className="w-full flex items-center justify-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:bg-gray-300 disabled:cursor-not-allowed"
            >
              {isLoading ? (
                <>
                  <Loader2 className="animate-spin h-5 w-5 mr-2" />
                  Analyzing CV...
                </>
              ) : (
                <>
                  <Briefcase className="h-5 w-5 mr-2" />
                  Find Matching Jobs
                </>
              )}
            </button>
          </form>
        )}
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start">
          <AlertCircle className="h-5 w-5 text-red-600 mt-0.5 mr-3 flex-shrink-0" />
          <div>
            <h3 className="text-sm font-medium text-red-800">Error</h3>
            <p className="text-sm text-red-700 mt-1">{error}</p>
          </div>
        </div>
      )}

      {/* Results Section */}
      {results && (
        <div className="space-y-6">
          {/* AI Recommendation Summary */}
          {results.ai_recommendation && (
            <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg shadow-sm border border-blue-200 p-6">
              <div className="flex items-start mb-3">
                <Sparkles className="h-5 w-5 text-blue-600 mt-1 mr-2 flex-shrink-0" />
                <h3 className="text-lg font-semibold text-gray-900">
                  AI Recommendation
                </h3>
              </div>
              <div className="prose prose-sm max-w-none markdown-content">
                <ReactMarkdown>{results.ai_recommendation}</ReactMarkdown>
              </div>
            </div>
          )}

          {/* Search Results */}
          {results.results && results.results.length > 0 ? (
            <div className="bg-white rounded-lg shadow-sm border border-gray-200">
              <div className="px-6 py-4 border-b border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900">
                  {results.results.length} Matching Job
                  {results.results.length !== 1 ? "s" : ""}
                </h3>
                <p className="text-sm text-gray-500 mt-1">
                  Query: "{results.query}"
                </p>
              </div>

              <div className="divide-y divide-gray-200">
                {results.results.map((result, index) => (
                  <div
                    key={result.id}
                    className="p-6 hover:bg-gray-50 transition-colors"
                  >
                    {/* Job Header */}
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex items-start space-x-3">
                        <div className="flex-shrink-0">
                          <div className="h-10 w-10 rounded-full bg-blue-100 flex items-center justify-center">
                            <span className="text-blue-600 font-semibold">
                              #{index + 1}
                            </span>
                          </div>
                        </div>
                        <div className="flex-1">
                          <div className="flex items-center space-x-2">
                            <Briefcase className="h-5 w-5 text-gray-400" />
                            <h4 className="text-lg font-semibold text-gray-900">
                              {result.position}
                            </h4>
                          </div>
                          <p className="text-base text-gray-700 mt-1">
                            {result.company}
                          </p>
                          <div className="flex flex-wrap items-center gap-3 mt-2 text-sm text-gray-500">
                            {result.location && (
                              <div className="flex items-center">
                                <MapPin className="h-4 w-4 mr-1" />
                                {result.location}
                              </div>
                            )}
                            {result.working_type && (
                              <div className="flex items-center">
                                <Clock className="h-4 w-4 mr-1" />
                                {result.working_type}
                              </div>
                            )}
                          </div>
                        </div>
                      </div>

                      <div className="flex flex-col items-end space-y-2">
                        <div className="flex items-center space-x-2">
                          <TrendingUp className="h-4 w-4 text-green-500" />
                          <span className="text-sm font-semibold text-green-600">
                            {(result.similarity_score * 100).toFixed(1)}% Match
                          </span>
                        </div>
                        <a
                          href={result.job_link}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex items-center px-3 py-1.5 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-md transition-colors"
                        >
                          Apply
                          <ExternalLink className="h-4 w-4 ml-1" />
                        </a>
                      </div>
                    </div>

                    {/* Job Summary */}
                    {result.summary && (
                      <div className="mt-3 bg-gray-50 rounded-lg p-3">
                        <p className="text-sm text-gray-700 line-clamp-3">
                          {result.summary}
                        </p>
                      </div>
                    )}

                    {/* Job Details Grid */}
                    <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
                      {/* Experience & Education */}
                      {(result.experience || result.education) && (
                        <div className="space-y-2">
                          {result.experience && (
                            <div className="flex items-start">
                              <Users className="h-4 w-4 text-gray-400 mt-0.5 mr-2 flex-shrink-0" />
                              <div>
                                <p className="text-xs font-medium text-gray-500">
                                  Experience
                                </p>
                                <p className="text-sm text-gray-700">
                                  {result.experience}
                                </p>
                              </div>
                            </div>
                          )}
                          {result.education && (
                            <div className="flex items-start">
                              <GraduationCap className="h-4 w-4 text-gray-400 mt-0.5 mr-2 flex-shrink-0" />
                              <div>
                                <p className="text-xs font-medium text-gray-500">
                                  Education
                                </p>
                                <p className="text-sm text-gray-700">
                                  {result.education}
                                </p>
                              </div>
                            </div>
                          )}
                        </div>
                      )}

                      {/* Technical Skills */}
                      {result.technical_skills &&
                        result.technical_skills.length > 0 && (
                          <div>
                            <div className="flex items-center mb-2">
                              <Code className="h-4 w-4 text-gray-400 mr-2" />
                              <p className="text-xs font-medium text-gray-500">
                                Technical Skills
                              </p>
                            </div>
                            <div className="flex flex-wrap gap-1.5">
                              {result.technical_skills
                                .slice(0, 6)
                                .map((skill, idx) => (
                                  <span
                                    key={idx}
                                    className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800"
                                  >
                                    {skill}
                                  </span>
                                ))}
                              {result.technical_skills.length > 6 && (
                                <span className="text-xs text-gray-500">
                                  +{result.technical_skills.length - 6} more
                                </span>
                              )}
                            </div>
                          </div>
                        )}

                      {/* Benefits */}
                      {result.benefits && result.benefits.length > 0 && (
                        <div className="md:col-span-2">
                          <div className="flex items-center mb-2">
                            <Gift className="h-4 w-4 text-gray-400 mr-2" />
                            <p className="text-xs font-medium text-gray-500">
                              Benefits
                            </p>
                          </div>
                          <div className="flex flex-wrap gap-2">
                            {result.benefits.slice(0, 5).map((benefit, idx) => (
                              <span
                                key={idx}
                                className="inline-flex items-center px-2 py-1 rounded-md text-xs bg-green-50 text-green-700"
                              >
                                {benefit}
                              </span>
                            ))}
                            {result.benefits.length > 5 && (
                              <span className="text-xs text-gray-500">
                                +{result.benefits.length - 5} more
                              </span>
                            )}
                          </div>
                        </div>
                      )}

                      {/* Tags */}
                      {result.tags && result.tags.length > 0 && (
                        <div className="md:col-span-2">
                          <div className="flex items-center mb-2">
                            <Tag className="h-4 w-4 text-gray-400 mr-2" />
                            <p className="text-xs font-medium text-gray-500">
                              Tags
                            </p>
                          </div>
                          <div className="flex flex-wrap gap-1.5">
                            {result.tags.map((tag, idx) => (
                              <span
                                key={idx}
                                className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-700"
                              >
                                {tag}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ) : results.results && results.results.length === 0 ? (
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 text-center">
              <Briefcase className="h-12 w-12 text-yellow-500 mx-auto mb-3" />
              <h3 className="text-lg font-medium text-yellow-900 mb-2">
                No Matches Found
              </h3>
              <p className="text-yellow-700">
                No jobs matched your search criteria. Try adjusting your query
                or add more jobs to the database.
              </p>
            </div>
          ) : null}
        </div>
      )}
    </div>
  );
};

export default JobRecommendTab;
