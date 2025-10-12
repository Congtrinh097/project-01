import React, { useState } from 'react'
import { Upload, History, FileText, MessageCircle, FileEdit } from 'lucide-react'
import { useQuery, useMutation, useQueryClient } from 'react-query'
import { uploadCV, getCVs, getCV, deleteCV, generateResume, getResumes, deleteResume } from './services/api'

// Import tab components
import UploadTab from './components/UploadTab'
import GenerateResumeTab from './components/GenerateResumeTab'
import HistoryTab from './components/HistoryTab'
import ChatbotTab from './components/ChatbotTab'

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
                onClick={() => setActiveTab('chatbot')}
                className={`flex items-center px-3 py-2 rounded-md text-sm font-medium ${
                  activeTab === 'chatbot'
                    ? 'bg-primary-100 text-primary-700'
                    : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                <MessageCircle className="h-4 w-4 mr-2" />
                Interview Practice
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

        {activeTab === 'chatbot' && (
          <ChatbotTab />
        )}
      </main>
    </div>
  )
}


export default App

