import React, { useState } from 'react'
import { Upload, History, FileText, CheckCircle, AlertCircle, Trash2, FileEdit, Download } from 'lucide-react'
import { useQuery, useMutation, useQueryClient } from 'react-query'
import ReactMarkdown from 'react-markdown'
import { uploadCV, getCVs, getCV, deleteCV, generateResume, getResumes, downloadResume, deleteResume } from './services/api'

function App() {
  const [activeTab, setActiveTab] = useState('upload')
  const [selectedCV, setSelectedCV] = useState(null)
  const [selectedResume, setSelectedResume] = useState(null)
  const queryClient = useQueryClient()

  const { data: cvs = [], isLoading: cvsLoading } = useQuery('cvs', getCVs)
  const { data: resumes = [], isLoading: resumesLoading } = useQuery('resumes', getResumes)

  const uploadMutation = useMutation(uploadCV, {
    onSuccess: () => {
      queryClient.invalidateQueries('cvs')
      setActiveTab('history')
    },
  })

  const deleteMutation = useMutation(deleteCV, {
    onSuccess: () => {
      queryClient.invalidateQueries('cvs')
      // Clear selected CV if it was deleted
      if (selectedCV) {
        setSelectedCV(null)
      }
    },
  })

  const generateResumeMutation = useMutation(generateResume, {
    onSuccess: (data) => {
      queryClient.invalidateQueries('resumes')
      setSelectedResume(data)
    },
  })

  const deleteResumeMutation = useMutation(deleteResume, {
    onSuccess: () => {
      queryClient.invalidateQueries('resumes')
      if (selectedResume) {
        setSelectedResume(null)
      }
    },
  })

  const handleFileUpload = (event) => {
    const file = event.target.files[0]
    if (file) {
      uploadMutation.mutate(file)
    }
  }

  const handleCVSelect = async (cvId) => {
    try {
      const cv = await getCV(cvId)
      setSelectedCV(cv)
    } catch (error) {
      console.error('Error fetching CV details:', error)
    }
  }

  const handleDeleteCV = (cvId, event) => {
    event.stopPropagation() // Prevent triggering the CV selection
    if (window.confirm('Are you sure you want to delete this CV?')) {
      deleteMutation.mutate(cvId)
    }
  }

  const handleGenerateResume = (inputText) => {
    generateResumeMutation.mutate(inputText)
  }

  const handleDeleteResume = (resumeId, event) => {
    event.stopPropagation()
    if (window.confirm('Are you sure you want to delete this resume?')) {
      deleteResumeMutation.mutate(resumeId)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <FileText className="h-8 w-8 text-primary-600" />
              <h1 className="ml-2 text-xl font-bold text-gray-900">CV Analyzer</h1>
            </div>
            <div className="flex space-x-4">
              <button
                onClick={() => setActiveTab('upload')}
                className={`flex items-center px-3 py-2 rounded-md text-sm font-medium ${
                  activeTab === 'upload'
                    ? 'bg-primary-100 text-primary-700'
                    : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                <Upload className="h-4 w-4 mr-2" />
                Upload CV
              </button>
              <button
                onClick={() => setActiveTab('generate')}
                className={`flex items-center px-3 py-2 rounded-md text-sm font-medium ${
                  activeTab === 'generate'
                    ? 'bg-primary-100 text-primary-700'
                    : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                <FileEdit className="h-4 w-4 mr-2" />
                Generate Resume
              </button>
              <button
                onClick={() => setActiveTab('history')}
                className={`flex items-center px-3 py-2 rounded-md text-sm font-medium ${
                  activeTab === 'history'
                    ? 'bg-primary-100 text-primary-700'
                    : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                <History className="h-4 w-4 mr-2" />
                History
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'upload' && (
          <UploadTab uploadMutation={uploadMutation} handleFileUpload={handleFileUpload} />
        )}
        
        {activeTab === 'generate' && (
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
        
        {activeTab === 'history' && (
          <HistoryTab 
            cvs={cvs} 
            cvsLoading={cvsLoading}
            selectedCV={selectedCV}
            onCVSelect={handleCVSelect}
            onDeleteCV={handleDeleteCV}
            isDeleting={deleteMutation.isLoading}
          />
        )}
      </main>
    </div>
  )
}

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

        <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-primary-400 transition-colors">
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
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mb-4"></div>
                <p className="text-primary-600 font-medium">Analyzing your CV...</p>
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

function GenerateResumeTab({ generateMutation, resumes, resumesLoading, selectedResume, onGenerateResume, onDeleteResume, isDeleting }) {
  const [inputText, setInputText] = useState('')

  const handleSubmit = (e) => {
    e.preventDefault()
    if (inputText.trim()) {
      onGenerateResume(inputText)
    }
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
      {/* Input Form */}
      <div className="lg:col-span-1">
        <div className="card p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Generate Resume</h3>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label htmlFor="resume-input" className="block text-sm font-medium text-gray-700 mb-2">
                Enter your information
              </label>
              <textarea
                id="resume-input"
                rows={12}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 resize-none"
                placeholder="Enter your professional information, experience, education, skills, etc.&#10;&#10;Example:&#10;Name: John Doe&#10;Title: Software Engineer&#10;Experience: 5 years in web development&#10;Skills: JavaScript, React, Node.js&#10;Education: B.Sc Computer Science"
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                disabled={generateMutation.isLoading}
              />
            </div>
            <button
              type="submit"
              disabled={!inputText.trim() || generateMutation.isLoading}
              className="w-full btn btn-primary flex items-center justify-center"
            >
              {generateMutation.isLoading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Generating...
                </>
              ) : (
                <>
                  <FileEdit className="h-4 w-4 mr-2" />
                  Generate Resume
                </>
              )}
            </button>
          </form>

          {generateMutation.error && (
            <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg">
              <div className="flex">
                <AlertCircle className="h-5 w-5 text-red-400 flex-shrink-0" />
                <p className="ml-2 text-sm text-red-800">
                  {generateMutation.error.response?.data?.detail || 'Generation failed. Please try again.'}
                </p>
              </div>
            </div>
          )}

          {/* Generated Resumes List */}
          <div className="mt-6">
            <h4 className="text-sm font-medium text-gray-700 mb-3">Generated Resumes</h4>
            {resumesLoading ? (
              <div className="flex justify-center py-4">
                <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary-600"></div>
              </div>
            ) : resumes.length === 0 ? (
              <p className="text-sm text-gray-500 text-center py-4">No resumes generated yet</p>
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
                  className="btn btn-primary flex items-center"
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
                      File: {selectedResume.pdf_filename} ({(selectedResume.file_size / 1024).toFixed(1)} KB)
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div className="card p-8 text-center">
            <FileEdit className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">Generate your professional resume</h3>
            <p className="text-gray-500 mb-4">
              Enter your information in the form and click &quot;Generate Resume&quot; to create a professional PDF resume
            </p>
            <div className="text-left max-w-md mx-auto">
              <p className="text-sm text-gray-600 mb-2">Tips for best results:</p>
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
  )
}

function HistoryTab({ cvs, cvsLoading, selectedCV, onCVSelect, onDeleteCV, isDeleting }) {
  if (cvsLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
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
                      ? 'border-primary-500 bg-primary-50'
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

export default App

