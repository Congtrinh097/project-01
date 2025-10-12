import React, { useState, useRef, useEffect } from 'react'
import { MessageCircle, Send } from 'lucide-react'
import { useMutation } from 'react-query'
import { sendChatMessage } from '../services/api'

function ChatbotTab() {
  const [messages, setMessages] = useState([])
  const [inputMessage, setInputMessage] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const messagesEndRef = useRef(null)
  const inputRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const chatMutation = useMutation(
    ({ message, history }) => sendChatMessage(message, history),
    {
      onSuccess: (data) => {
        setMessages((prev) => [
          ...prev,
          { role: 'assistant', content: data.response, timestamp: data.timestamp }
        ])
        setIsTyping(false)
      },
      onError: (error) => {
        console.error('Chat error:', error)
        setMessages((prev) => [
          ...prev,
          {
            role: 'assistant',
            content: 'Xin lỗi, có lỗi xảy ra. Vui lòng thử lại.',
            timestamp: new Date().toISOString(),
            isError: true
          }
        ])
        setIsTyping(false)
      }
    }
  )

  const handleSendMessage = async (e) => {
    e.preventDefault()
    
    if (!inputMessage.trim() || chatMutation.isLoading) return

    const userMessage = inputMessage.trim()
    setInputMessage('')

    // Add user message to chat
    const newUserMessage = {
      role: 'user',
      content: userMessage,
      timestamp: new Date().toISOString()
    }
    setMessages((prev) => [...prev, newUserMessage])
    setIsTyping(true)

    // Prepare conversation history (only role and content)
    const conversationHistory = messages.map(msg => ({
      role: msg.role,
      content: msg.content
    }))

    // Send to API
    chatMutation.mutate({
      message: userMessage,
      history: conversationHistory
    })
  }

  const handleClearChat = () => {
    if (window.confirm('Bạn có muốn xóa toàn bộ cuộc trò chuyện không?')) {
      setMessages([])
    }
  }

  return (
    <div className="max-w-7xl mx-auto">
      <div className="card overflow-hidden flex flex-col" style={{ height: 'calc(100vh - 200px)' }}>
        {/* Chat Header */}
        <div className="bg-gradient-to-r from-primary-600 to-primary-700 text-white p-6 flex-shrink-0">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <MessageCircle className="h-8 w-8 mr-3" />
              <div>
                <h2 className="text-2xl font-bold">Interview Practice Bot</h2>
                <p className="text-primary-100 text-sm mt-1">
                  Luyện tập phỏng vấn với AI - Nhập vị trí công việc để bắt đầu
                </p>
              </div>
            </div>
            {messages.length > 0 && (
              <button
                onClick={handleClearChat}
                className="px-4 py-2 bg-white bg-opacity-20 hover:bg-opacity-30 rounded-lg text-sm font-medium transition-colors"
              >
                Xóa cuộc trò chuyện
              </button>
            )}
          </div>
        </div>

        {/* Chat Messages */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4 bg-gray-50">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-center">
              <MessageCircle className="h-16 w-16 text-gray-300 mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                Bắt đầu buổi phỏng vấn của bạn
              </h3>
              <p className="text-gray-500 mb-6 max-w-md">
                Chào mừng bạn đến với Interview Practice Bot! Hãy cho tôi biết vị trí công việc bạn muốn luyện tập phỏng vấn.
              </p>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-w-2xl">
                <button
                  onClick={() => setInputMessage('Tôi muốn luyện phỏng vấn vị trí Software Engineer')}
                  className="px-4 py-3 bg-white border border-gray-200 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition-colors text-left"
                >
                  <p className="font-medium text-gray-900">Software Engineer</p>
                  <p className="text-sm text-gray-500">Luyện tập phỏng vấn kỹ sư phần mềm</p>
                </button>
                <button
                  onClick={() => setInputMessage('Tôi muốn luyện phỏng vấn vị trí Data Analyst')}
                  className="px-4 py-3 bg-white border border-gray-200 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition-colors text-left"
                >
                  <p className="font-medium text-gray-900">Data Analyst</p>
                  <p className="text-sm text-gray-500">Luyện tập phỏng vấn phân tích dữ liệu</p>
                </button>
                <button
                  onClick={() => setInputMessage('Tôi muốn luyện phỏng vấn vị trí Marketing Manager')}
                  className="px-4 py-3 bg-white border border-gray-200 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition-colors text-left"
                >
                  <p className="font-medium text-gray-900">Marketing Manager</p>
                  <p className="text-sm text-gray-500">Luyện tập phỏng vấn quản lý marketing</p>
                </button>
                <button
                  onClick={() => setInputMessage('Tôi muốn luyện phỏng vấn vị trí Product Manager')}
                  className="px-4 py-3 bg-white border border-gray-200 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition-colors text-left"
                >
                  <p className="font-medium text-gray-900">Product Manager</p>
                  <p className="text-sm text-gray-500">Luyện tập phỏng vấn quản lý sản phẩm</p>
                </button>
              </div>
            </div>
          ) : (
            <>
              {messages.map((message, index) => (
                <div
                  key={index}
                  className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-3xl rounded-lg px-4 py-3 ${
                      message.role === 'user'
                        ? 'bg-primary-600 text-white'
                        : message.isError
                        ? 'bg-red-100 text-red-800 border border-red-200'
                        : 'bg-white text-gray-800 border border-gray-200'
                    }`}
                  >
                    <div className="flex items-start">
                      {message.role === 'assistant' && (
                        <MessageCircle className={`h-5 w-5 mr-2 flex-shrink-0 mt-0.5 ${message.isError ? 'text-red-500' : 'text-primary-600'}`} />
                      )}
                      <div className="flex-1">
                        <div className="whitespace-pre-wrap break-words">
                          {message.content}
                        </div>
                        <p className={`text-xs mt-2 ${message.role === 'user' ? 'text-primary-100' : 'text-gray-400'}`}>
                          {new Date(message.timestamp).toLocaleTimeString('vi-VN', { 
                            hour: '2-digit', 
                            minute: '2-digit' 
                          })}
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
              {isTyping && (
                <div className="flex justify-start">
                  <div className="bg-white border border-gray-200 rounded-lg px-4 py-3">
                    <div className="flex items-center space-x-2">
                      <MessageCircle className="h-5 w-5 text-primary-600" />
                      <div className="flex space-x-1">
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </>
          )}
        </div>

        {/* Chat Input */}
        <div className="border-t border-gray-200 bg-white p-4 flex-shrink-0">
          <form onSubmit={handleSendMessage} className="flex items-end space-x-3">
            <div className="flex-1">
              <textarea
                ref={inputRef}
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault()
                    handleSendMessage(e)
                  }
                }}
                placeholder="Nhập câu trả lời hoặc vị trí công việc của bạn..."
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 resize-none"
                rows={3}
                disabled={chatMutation.isLoading}
              />
              <p className="text-xs text-gray-500 mt-1">
                Nhấn Enter để gửi, Shift + Enter để xuống dòng
              </p>
            </div>
            <button
              type="submit"
              disabled={!inputMessage.trim() || chatMutation.isLoading}
              className="btn btn-primary px-6 py-3 w-24 flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed flex-shrink-0"
            >
              {chatMutation.isLoading ? (
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
              ) : (
                <>
                  <Send className="h-5 w-5 mr-2" />
                  Gửi
                </>
              )}
            </button>
          </form>
        </div>
      </div>
    </div>
  )
}

export default ChatbotTab
