import React from 'react'
import { FileText, CheckCircle, AlertCircle, Trash2 } from 'lucide-react'
import ReactMarkdown from 'react-markdown'

function HistoryTab({ cvs, cvsLoading, selectedCV, onCVSelect, onDeleteCV, isDeleting }) {
  if (cvsLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
      </div>
    )
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
      {/* CV List */}
      <div className="lg:col-span-1">
        <div className="card p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Uploaded CVs</h3>
          {cvs.length === 0 ? (
            <p className="text-gray-500 text-center py-8">No CVs uploaded yet</p>
          ) : (
            <div className="space-y-3">
              {cvs.map((cv) => (
                <div
                  key={cv.id}
                  onClick={() => onCVSelect(cv.id)}
                  className={`p-3 rounded-lg border cursor-pointer transition-colors ${
                    selectedCV?.id === cv.id
                      ? 'border-purple-500 bg-purple-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900 truncate">
                        {cv.filename}
                      </p>
                      <p className="text-xs text-gray-500">
                        {(cv.file_size / 1024).toFixed(1)} KB
                      </p>
                    </div>
                    <div className="flex items-center gap-2">
                      <FileText className="h-4 w-4 text-gray-400" />
                      <button
                        onClick={(e) => onDeleteCV(cv.id, e)}
                        disabled={isDeleting}
                        className="p-1 hover:bg-red-100 rounded transition-colors group"
                        title="Delete"
                      >
                        <Trash2 className="h-4 w-4 text-gray-400 group-hover:text-red-600" />
                      </button>
                    </div>
                  </div>
                  <p className="text-xs text-gray-500 mt-1">
                    {new Date(cv.upload_time).toLocaleDateString()}
                  </p>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* CV Analysis */}
      <div className="lg:col-span-2">
        {selectedCV ? (
          <div className="space-y-6">
            <div className="card p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Analysis for: {selectedCV.filename}
              </h3>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Strengths */}
                <div>
                  <div className="flex items-center mb-3">
                    <CheckCircle className="h-5 w-5 text-green-500 mr-2" />
                    <h4 className="font-medium text-gray-900">Strengths</h4>
                  </div>
                  <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                    <div className="markdown-content">
                      <ReactMarkdown>
                        {selectedCV.summary_pros || 'No strengths identified.'}
                      </ReactMarkdown>
                    </div>
                  </div>
                </div>

                {/* Areas for Improvement */}
                <div>
                  <div className="flex items-center mb-3">
                    <AlertCircle className="h-5 w-5 text-orange-500 mr-2" />
                    <h4 className="font-medium text-gray-900">Areas for Improvement</h4>
                  </div>
                  <div className="bg-orange-50 border border-orange-200 rounded-lg p-4">
                    <div className="markdown-content">
                      <ReactMarkdown>
                        {selectedCV.summary_cons || 'No areas for improvement identified.'}
                      </ReactMarkdown>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div className="card p-8 text-center">
            <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">Select a CV to view analysis</h3>
            <p className="text-gray-500">
              Choose a CV from the list to see its detailed analysis
            </p>
          </div>
        )}
      </div>
    </div>
  )
}

export default HistoryTab
