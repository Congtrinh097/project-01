import {
  AlertCircle,
  Download,
  FileText,
  Loader2,
  Search,
  Sparkles,
  TrendingUp,
} from "lucide-react";
import React, { useState } from "react";
import ReactMarkdown from "react-markdown";
import { downloadCV } from "../services/api";

const RecommendTab = ({ onRecommend, isLoading, error, results }) => {
  const [query, setQuery] = useState("");
  const [limit, setLimit] = useState(5);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (query.trim()) {
      onRecommend(query, limit);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header Section */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-center mb-4">
          <Sparkles className="h-6 w-6 text-purple-600 mr-2" />
          <h2 className="text-2xl font-bold text-gray-900">
            CV Recommendation
          </h2>
        </div>
        <p className="text-gray-600">
          Use semantic search to find the most relevant candidates based on
          natural language queries. Our AI will analyze CVs and provide
          intelligent recommendations.
        </p>
      </div>

      {/* Search Form */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label
              htmlFor="query"
              className="block text-sm font-medium text-gray-700 mb-2"
            >
              Search Query
            </label>
            <textarea
              id="query"
              rows="3"
              className="block w-full px-4 py-3 rounded-lg border border-gray-300 shadow-sm focus:outline-none focus:border-purple-400 focus:ring-2 focus:ring-purple-200 transition-colors duration-200 text-sm placeholder-gray-400 disabled:bg-gray-50 disabled:text-gray-500"
              placeholder="e.g., Looking for a senior software engineer with 5+ years of Python and React experience, strong communication skills..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              disabled={isLoading}
            />
            <p className="mt-2 text-sm text-gray-500">
              Describe the ideal candidate using natural language. Be specific
              about skills, experience, and qualifications.
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
                className="block w-[100px] px-3 py-2 rounded-lg border border-gray-300 shadow-sm focus:outline-none focus:border-purple-400 focus:ring-2 focus:ring-purple-200 transition-colors duration-200 text-sm disabled:bg-gray-50 disabled:text-gray-500"
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
            className="w-full flex items-center justify-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-purple-600 hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500 disabled:bg-gray-300 disabled:cursor-not-allowed"
          >
            {isLoading ? (
              <>
                <Loader2 className="animate-spin h-5 w-5 mr-2" />
                Searching...
              </>
            ) : (
              <>
                <Search className="h-5 w-5 mr-2" />
                Find Candidates
              </>
            )}
          </button>
        </form>
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
            <div className="bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg shadow-sm border border-purple-200 p-6">
              <div className="flex items-start mb-3">
                <Sparkles className="h-5 w-5 text-purple-600 mt-1 mr-2 flex-shrink-0" />
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
                  {results.results.length} Matching Candidate
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
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex items-start space-x-3">
                        <div className="flex-shrink-0">
                          <div className="h-10 w-10 rounded-full bg-purple-100 flex items-center justify-center">
                            <span className="text-purple-600 font-semibold">
                              #{index + 1}
                            </span>
                          </div>
                        </div>
                        <div>
                          <div className="flex items-center space-x-2">
                            <FileText className="h-4 w-4 text-gray-400" />
                            <h4 className="text-base font-medium text-gray-900">
                              {result.filename}
                            </h4>
                          </div>
                          {result.upload_time && (
                            <div className="flex items-center space-x-2 mt-1">
                              <p className="text-xs text-gray-500">
                                Uploaded:{" "}
                                {new Date(
                                  result.upload_time
                                ).toLocaleDateString()}
                              </p>
                              <a
                                href={downloadCV(result.id)}
                                download
                                className="inline-flex items-center text-xs text-purple-600 hover:text-purple-800 hover:underline"
                                title="Download CV"
                              >
                                <Download className="h-3 w-3 mr-1" />
                                Download
                              </a>
                            </div>
                          )}
                        </div>
                      </div>

                      <div className="flex items-center space-x-2">
                        <TrendingUp className="h-4 w-4 text-green-500" />
                        <span className="text-sm font-semibold text-green-600">
                          {(result.similarity_score * 100).toFixed(1)}% Match
                        </span>
                      </div>
                    </div>

                    {/* CV Preview */}
                    {result.text_preview && (
                      <div className="mt-3 bg-gray-50 rounded p-3">
                        <p className="text-sm text-gray-600 italic line-clamp-3">
                          {result.text_preview}
                        </p>
                      </div>
                    )}

                    {/* Strengths */}
                    {result.summary_pros && (
                      <div className="mt-3">
                        <h5 className="text-sm font-medium text-gray-700 mb-2">
                          Key Strengths:
                        </h5>
                        <div className="text-sm text-gray-600 prose prose-sm max-w-none markdown-content">
                          <ReactMarkdown>
                            {result.summary_pros
                              .split("\n")
                              .slice(0, 5)
                              .join("\n")}
                          </ReactMarkdown>
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          ) : results.results && results.results.length === 0 ? (
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 text-center">
              <FileText className="h-12 w-12 text-yellow-500 mx-auto mb-3" />
              <h3 className="text-lg font-medium text-yellow-900 mb-2">
                No Matches Found
              </h3>
              <p className="text-yellow-700">
                No CVs matched your search criteria. Try adjusting your query or
                upload more CVs to the database.
              </p>
            </div>
          ) : null}
        </div>
      )}
    </div>
  );
};

export default RecommendTab;
