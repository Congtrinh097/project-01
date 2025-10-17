import React from 'react'
import { Upload, AlertCircle, CheckCircle } from 'lucide-react'

function UploadTab({ uploadMutation, handleFileUpload }) {
  return (
    <div className="max-w-2xl mx-auto">
      <div className="card p-8">
        <div className="text-center">
          <Upload className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Upload Your CV</h2>
          <p className="text-gray-600 mb-6">
            Upload a PDF or DOCX file to get AI-powered analysis of your CV
          </p>
        </div>

        <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-purple-400 transition-colors">
          <input
            type="file"
            accept=".pdf,.docx"
            onChange={handleFileUpload}
            className="hidden"
            id="file-upload"
            disabled={uploadMutation.isLoading}
          />
          <label
            htmlFor="file-upload"
            className="cursor-pointer"
          >
            {uploadMutation.isLoading ? (
              <div className="flex flex-col items-center">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600 mb-4"></div>
                <p className="text-purple-600 font-medium">Analyzing your CV...</p>
                <p className="text-sm text-gray-500 mt-2">This may take a few moments</p>
              </div>
            ) : (
              <div>
                <Upload className="h-8 w-8 text-gray-400 mx-auto mb-4" />
                <p className="text-lg font-medium text-gray-900 mb-2">
                  Click to upload or drag and drop
                </p>
                <p className="text-sm text-gray-500">
                  PDF or DOCX files up to 10MB
                </p>
              </div>
            )}
          </label>
        </div>

        {uploadMutation.error && (
          <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
            <div className="flex">
              <AlertCircle className="h-5 w-5 text-red-400" />
              <div className="ml-3">
                <p className="text-sm text-red-800">
                  {uploadMutation.error.response?.data?.detail || 'Upload failed. Please try again.'}
                </p>
              </div>
            </div>
          </div>
        )}

        {uploadMutation.isSuccess && (
          <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
            <div className="flex">
              <CheckCircle className="h-5 w-5 text-green-400" />
              <div className="ml-3">
                <p className="text-sm text-green-800">
                  CV uploaded and analyzed successfully!
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default UploadTab
