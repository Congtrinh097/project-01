import {
  AlertCircle,
  CheckCircle,
  Download,
  FileEdit,
  Trash2,
} from "lucide-react";
import React, { useState } from "react";
import { downloadResume } from "../services/api";
import { trackDownloadResume } from "../utils/analytics";

function GenerateResumeTab({
  generateMutation,
  resumes,
  resumesLoading,
  selectedResume,
  onGenerateResume,
  onDeleteResume,
  isDeleting,
}) {
  const [inputText, setInputText] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    if (inputText.trim()) {
      onGenerateResume(inputText);
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
      {/* Input Form */}
      <div className="lg:col-span-1">
        <div className="card p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Generate CV
          </h3>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label
                htmlFor="resume-input"
                className="block text-sm font-medium text-gray-700 mb-2"
              >
                Enter your information
              </label>
              <textarea
                id="resume-input"
                rows={12}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 resize-none"
                placeholder="Enter your professional information, experience, education, skills, etc.&#10;&#10;Example:&#10;Name: John Doe&#10;Title: Software Engineer&#10;Experience: 5 years in web development&#10;Skills: JavaScript, React, Node.js&#10;Education: B.Sc Computer Science"
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                disabled={generateMutation.isLoading}
              />
            </div>
            <button
              type="submit"
              disabled={!inputText.trim() || generateMutation.isLoading}
              className="w-full flex items-center justify-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-purple-600 hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors duration-200"
            >
              {generateMutation.isLoading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Generating...
                </>
              ) : (
                <>
                  <FileEdit className="h-4 w-4 mr-2" />
                  Generate CV
                </>
              )}
            </button>
          </form>

          {generateMutation.error && (
            <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg">
              <div className="flex">
                <AlertCircle className="h-5 w-5 text-red-400 flex-shrink-0" />
                <p className="ml-2 text-sm text-red-800">
                  {generateMutation.error.response?.data?.detail ||
                    "Generation failed. Please try again."}
                </p>
              </div>
            </div>
          )}

          {/* Generated Resumes List */}
          <div className="mt-6">
            <h4 className="text-sm font-medium text-gray-700 mb-3">
              Generated Resumes
            </h4>
            {resumesLoading ? (
              <div className="flex justify-center py-4">
                <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-purple-600"></div>
              </div>
            ) : resumes.length === 0 ? (
              <p className="text-sm text-gray-500 text-center py-4">
                No resumes generated yet
              </p>
            ) : (
              <div className="space-y-2">
                {resumes.map((resume) => (
                  <div
                    key={resume.id}
                    onClick={() => onGenerateResume.mutate.reset()}
                    className="p-2 rounded-lg border border-gray-200 hover:border-gray-300 cursor-pointer"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-gray-900 truncate">
                          {resume.pdf_filename}
                        </p>
                        <p className="text-xs text-gray-500">
                          {new Date(resume.created_at).toLocaleDateString()}
                        </p>
                      </div>
                      <button
                        onClick={(e) => onDeleteResume(resume.id, e)}
                        disabled={isDeleting}
                        className="p-1 hover:bg-red-100 rounded transition-colors group"
                        title="Delete"
                      >
                        <Trash2 className="h-4 w-4 text-gray-400 group-hover:text-red-600" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Generated Resume Display */}
      <div className="lg:col-span-2">
        {selectedResume ? (
          <div className="space-y-6">
            <div className="card p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900">
                  Generated Resume
                </h3>
                <a
                  href={downloadResume(selectedResume.id)}
                  download
                  onClick={() => trackDownloadResume(selectedResume.id)}
                  className="flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-purple-600 hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500 transition-colors duration-200"
                >
                  <Download className="h-4 w-4 mr-2" />
                  Download PDF
                </a>
              </div>

              <div className="bg-gray-50 border border-gray-200 rounded-lg p-6">
                <pre className="whitespace-pre-wrap text-sm font-mono text-gray-800">
                  {selectedResume.generated_text}
                </pre>
              </div>

              <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
                <div className="flex items-start">
                  <CheckCircle className="h-5 w-5 text-green-500 flex-shrink-0 mt-0.5" />
                  <div className="ml-3">
                    <p className="text-sm font-medium text-green-800">
                      Resume generated successfully!
                    </p>
                    <p className="text-sm text-green-700 mt-1">
                      File: {selectedResume.pdf_filename} (
                      {(selectedResume.file_size / 1024).toFixed(1)} KB)
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div className="card p-8 text-center">
            <FileEdit className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              Generate your professional resume
            </h3>
            <p className="text-gray-500 mb-4">
              Enter your information in the form and click &quot;Generate
              Resume&quot; to create a professional PDF resume
            </p>
            <div className="text-left max-w-md mx-auto">
              <p className="text-sm text-gray-600 mb-2">
                Tips for best results:
              </p>
              <ul className="text-sm text-gray-600 space-y-1 list-disc list-inside">
                <li>Include your name, title, and contact information</li>
                <li>List your work experience with dates and achievements</li>
                <li>Add your education background</li>
                <li>Mention relevant skills and certifications</li>
              </ul>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default GenerateResumeTab;
