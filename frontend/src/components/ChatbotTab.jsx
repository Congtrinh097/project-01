import { ArrowUp, MessageCircle, Mic, Volume2, VolumeX } from "lucide-react";
import React, { useEffect, useRef, useState } from "react";
import { useMutation, useQuery } from "react-query";
import {
  getTTSStatus,
  sendChatMessage,
  sendChatMessageWithAudio,
} from "../services/api";

function ChatbotTab() {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [ttsEnabled, setTtsEnabled] = useState(true);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);
  const recognitionRef = useRef(null);
  const audioRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Check TTS status on component mount
  const { data: ttsStatus } = useQuery("tts-status", getTTSStatus, {
    onSuccess: (data) => {
      if (!data.available) {
        setTtsEnabled(false);
        console.log("TTS not available, audio responses disabled");
      }
    },
    onError: () => {
      setTtsEnabled(false);
      console.log("Failed to check TTS status, audio responses disabled");
    },
  });

  // Initialize speech recognition
  useEffect(() => {
    if (typeof window !== "undefined") {
      const SpeechRecognition =
        window.SpeechRecognition || window.webkitSpeechRecognition;
      if (SpeechRecognition) {
        const recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = "vi-VN"; // Vietnamese language

        recognition.onstart = () => {
          setIsListening(true);
        };

        recognition.onresult = (event) => {
          const transcript = event.results[0][0].transcript;
          setInputMessage(transcript);
          setIsListening(false);
        };

        recognition.onerror = (event) => {
          console.error("Speech recognition error:", event.error);
          setIsListening(false);
          if (event.error === "not-allowed") {
            alert(
              "Quyền truy cập microphone bị từ chối. Vui lòng cho phép truy cập microphone trong cài đặt trình duyệt."
            );
          }
        };

        recognition.onend = () => {
          setIsListening(false);
        };

        recognitionRef.current = recognition;
      }
    }

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.abort();
      }
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current = null;
      }
    };
  }, []);

  // Audio handling functions
  const playAudio = (audioData) => {
    if (!audioData) return;

    try {
      // Convert hex string back to bytes
      const bytes = new Uint8Array(
        audioData.match(/.{1,2}/g).map((byte) => parseInt(byte, 16))
      );
      // OpenAI TTS returns MP3 format
      const blob = new Blob([bytes], { type: "audio/mpeg" });
      const audioUrl = URL.createObjectURL(blob);

      const audio = new Audio(audioUrl);
      audioRef.current = audio;

      audio.onplay = () => setIsPlaying(true);
      audio.onended = () => {
        setIsPlaying(false);
        URL.revokeObjectURL(audioUrl);
      };
      audio.onerror = () => {
        setIsPlaying(false);
        URL.revokeObjectURL(audioUrl);
        console.error("Error playing audio");
      };

      audio.play();
    } catch (error) {
      console.error("Error creating audio:", error);
      setIsPlaying(false);
    }
  };

  const stopAudio = () => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
      setIsPlaying(false);
    }
  };

  const chatMutation = useMutation(
    ({ message, history, withAudio }) =>
      withAudio
        ? sendChatMessageWithAudio(message, history)
        : sendChatMessage(message, history),
    {
      onSuccess: (data) => {
        const newMessage = {
          role: "assistant",
          content: data.response,
          timestamp: data.timestamp,
          hasAudio: data.has_audio,
          audioData: data.audio_data,
        };

        setMessages((prev) => [...prev, newMessage]);
        setIsTyping(false);

        // Auto-play audio if available and TTS is enabled
        if (data.has_audio && data.audio_data && ttsEnabled) {
          setTimeout(() => playAudio(data.audio_data), 500); // Small delay for better UX
        }
      },
      onError: (error) => {
        console.error("Chat error:", error);
        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            content: "Xin lỗi, có lỗi xảy ra. Vui lòng thử lại.",
            timestamp: new Date().toISOString(),
            isError: true,
          },
        ]);
        setIsTyping(false);
      },
    }
  );

  const handleSendMessage = async (e) => {
    e.preventDefault();

    if (!inputMessage.trim() || chatMutation.isLoading) return;

    const userMessage = inputMessage.trim();
    setInputMessage("");

    // Add user message to chat
    const newUserMessage = {
      role: "user",
      content: userMessage,
      timestamp: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, newUserMessage]);
    setIsTyping(true);

    // Prepare conversation history (only role and content)
    const conversationHistory = messages.map((msg) => ({
      role: msg.role,
      content: msg.content,
    }));

    // Send to API with audio if enabled
    chatMutation.mutate({
      message: userMessage,
      history: conversationHistory,
      withAudio: ttsEnabled,
    });
  };

  const handleClearChat = () => {
    if (window.confirm("Bạn có muốn xóa toàn bộ cuộc trò chuyện không?")) {
      setMessages([]);
    }
  };

  const handleVoiceInput = () => {
    if (!recognitionRef.current) {
      alert(
        "Trình duyệt của bạn không hỗ trợ nhận dạng giọng nói. Vui lòng sử dụng Chrome hoặc Edge."
      );
      return;
    }

    if (isListening) {
      recognitionRef.current.stop();
    } else {
      try {
        recognitionRef.current.start();
      } catch (error) {
        console.error("Error starting speech recognition:", error);
      }
    }
  };

  return (
    <div className="max-w-7xl mx-auto h-full">
      <div className="card overflow-hidden flex flex-col h-[calc(100vh-7rem)] sm:h-[calc(100vh-8rem)] lg:h-[calc(100vh-9rem)]">
        {/* Chat Header */}
        <div className="bg-gradient-to-r from-purple-600 to-purple-700 text-white p-4 sm:p-6 flex-shrink-0">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
            <div className="flex items-center">
              <MessageCircle className="h-6 w-6 sm:h-8 sm:w-8 mr-2 sm:mr-3 flex-shrink-0" />
              <div>
                <h2 className="text-lg sm:text-2xl font-bold">
                  Interview Practice Bot
                </h2>
                <p className="text-purple-100 text-xs sm:text-sm mt-1">
                  Luyện tập phỏng vấn với AI - Nhập vị trí công việc để bắt đầu
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              {/* TTS Toggle */}
              <button
                onClick={() => setTtsEnabled(!ttsEnabled)}
                className={`px-3 py-1.5 sm:px-4 sm:py-2 rounded-lg text-xs sm:text-sm font-medium transition-colors ${
                  ttsEnabled
                    ? "bg-white bg-opacity-20 hover:bg-opacity-30"
                    : "bg-white bg-opacity-10 hover:bg-opacity-20"
                }`}
                title={ttsEnabled ? "Tắt phát âm" : "Bật phát âm"}
              >
                {ttsEnabled ? (
                  <Volume2 className="h-4 w-4 sm:h-5 sm:w-5" />
                ) : (
                  <VolumeX className="h-4 w-4 sm:h-5 sm:w-5" />
                )}
              </button>

              {/* Clear Chat */}
              {messages.length > 0 && (
                <button
                  onClick={handleClearChat}
                  className="px-3 py-1.5 sm:px-4 sm:py-2 bg-white bg-opacity-20 hover:bg-opacity-30 rounded-lg text-xs sm:text-sm font-medium transition-colors"
                >
                  Xóa cuộc trò chuyện
                </button>
              )}
            </div>
          </div>
        </div>

        {/* Chat Messages */}
        <div className="flex-1 overflow-y-auto p-3 sm:p-6 space-y-3 sm:space-y-4 bg-gray-50">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-center px-4">
              <MessageCircle className="h-12 w-12 sm:h-16 sm:w-16 text-gray-300 mb-3 sm:mb-4" />
              <h3 className="text-base sm:text-lg font-medium text-gray-900 mb-2">
                Bắt đầu buổi phỏng vấn của bạn
              </h3>
              <p className="text-sm sm:text-base text-gray-500 mb-4 sm:mb-6 max-w-md">
                Chào mừng bạn đến với Interview Practice Bot! Hãy cho tôi biết
                vị trí công việc bạn muốn luyện tập phỏng vấn.
              </p>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 sm:gap-3 max-w-2xl w-full">
                <button
                  onClick={() =>
                    setInputMessage(
                      "Tôi muốn luyện phỏng vấn vị trí Software Engineer"
                    )
                  }
                  className="px-3 py-2 sm:px-4 sm:py-3 bg-white border border-gray-200 rounded-lg hover:border-purple-500 hover:bg-purple-50 transition-colors text-left"
                >
                  <p className="text-sm sm:text-base font-medium text-gray-900">
                    Software Engineer
                  </p>
                  <p className="text-xs sm:text-sm text-gray-500">
                    Luyện tập phỏng vấn kỹ sư phần mềm
                  </p>
                </button>
                <button
                  onClick={() =>
                    setInputMessage(
                      "Tôi muốn luyện phỏng vấn vị trí Data Analyst"
                    )
                  }
                  className="px-3 py-2 sm:px-4 sm:py-3 bg-white border border-gray-200 rounded-lg hover:border-purple-500 hover:bg-purple-50 transition-colors text-left"
                >
                  <p className="text-sm sm:text-base font-medium text-gray-900">
                    Data Analyst
                  </p>
                  <p className="text-xs sm:text-sm text-gray-500">
                    Luyện tập phỏng vấn phân tích dữ liệu
                  </p>
                </button>
                <button
                  onClick={() =>
                    setInputMessage(
                      "Tôi muốn luyện phỏng vấn vị trí Marketing Manager"
                    )
                  }
                  className="px-3 py-2 sm:px-4 sm:py-3 bg-white border border-gray-200 rounded-lg hover:border-purple-500 hover:bg-purple-50 transition-colors text-left"
                >
                  <p className="text-sm sm:text-base font-medium text-gray-900">
                    Marketing Manager
                  </p>
                  <p className="text-xs sm:text-sm text-gray-500">
                    Luyện tập phỏng vấn quản lý marketing
                  </p>
                </button>
                <button
                  onClick={() =>
                    setInputMessage(
                      "Tôi muốn luyện phỏng vấn vị trí Product Manager"
                    )
                  }
                  className="px-3 py-2 sm:px-4 sm:py-3 bg-white border border-gray-200 rounded-lg hover:border-purple-500 hover:bg-purple-50 transition-colors text-left"
                >
                  <p className="text-sm sm:text-base font-medium text-gray-900">
                    Product Manager
                  </p>
                  <p className="text-xs sm:text-sm text-gray-500">
                    Luyện tập phỏng vấn quản lý sản phẩm
                  </p>
                </button>
              </div>
            </div>
          ) : (
            <>
              {messages.map((message, index) => (
                <div
                  key={index}
                  className={`flex ${
                    message.role === "user" ? "justify-end" : "justify-start"
                  }`}
                >
                  <div
                    className={`max-w-[85%] sm:max-w-2xl lg:max-w-3xl rounded-lg px-3 py-2 sm:px-4 sm:py-3 ${
                      message.role === "user"
                        ? "bg-purple-600 text-white"
                        : message.isError
                        ? "bg-red-100 text-red-800 border border-red-200"
                        : "bg-white text-gray-800 border border-gray-200"
                    }`}
                  >
                    <div className="flex items-start">
                      {message.role === "assistant" && (
                        <MessageCircle
                          className={`h-4 w-4 sm:h-5 sm:w-5 mr-2 flex-shrink-0 mt-0.5 ${
                            message.isError ? "text-red-500" : "text-purple-600"
                          }`}
                        />
                      )}
                      <div className="flex-1">
                        <div className="whitespace-pre-wrap break-words text-sm sm:text-base">
                          {message.content}
                        </div>
                        <div className="flex items-center justify-between mt-1 sm:mt-2">
                          <p
                            className={`text-xs ${
                              message.role === "user"
                                ? "text-purple-100"
                                : "text-gray-400"
                            }`}
                          >
                            {new Date(message.timestamp).toLocaleTimeString(
                              "vi-VN",
                              {
                                hour: "2-digit",
                                minute: "2-digit",
                              }
                            )}
                          </p>
                          {/* Audio Play Button for Assistant Messages */}
                          {message.role === "assistant" &&
                            message.hasAudio &&
                            message.audioData && (
                              <button
                                onClick={() => {
                                  if (isPlaying) {
                                    stopAudio();
                                  } else {
                                    playAudio(message.audioData);
                                  }
                                }}
                                className={`ml-2 p-1 rounded-full transition-colors ${
                                  isPlaying
                                    ? "bg-red-100 text-red-600"
                                    : "bg-purple-100 text-purple-600 hover:bg-purple-200"
                                }`}
                                title={isPlaying ? "Dừng phát âm" : "Phát âm"}
                              >
                                {isPlaying ? (
                                  <VolumeX className="h-3 w-3" />
                                ) : (
                                  <Volume2 className="h-3 w-3" />
                                )}
                              </button>
                            )}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
              {isTyping && (
                <div className="flex justify-start">
                  <div className="bg-white border border-gray-200 rounded-lg px-4 py-3">
                    <div className="flex items-center space-x-2">
                      <MessageCircle className="h-5 w-5 text-purple-600" />
                      <div className="flex space-x-1">
                        <div
                          className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                          style={{ animationDelay: "0ms" }}
                        ></div>
                        <div
                          className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                          style={{ animationDelay: "150ms" }}
                        ></div>
                        <div
                          className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                          style={{ animationDelay: "300ms" }}
                        ></div>
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
        <div className="border-t border-gray-200 bg-white p-3 sm:p-6 flex-shrink-0">
          <form onSubmit={handleSendMessage} className="max-w-4xl mx-auto">
            <div className="relative">
              <div className="flex items-center bg-white border border-gray-200 rounded-full shadow-sm hover:shadow-md transition-shadow duration-200">
                {/* Text Input */}
                <div className="flex-1 px-3 sm:px-6">
                  <input
                    ref={inputRef}
                    type="text"
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === "Enter") {
                        e.preventDefault();
                        handleSendMessage(e);
                      }
                    }}
                    placeholder={
                      isListening
                        ? "Đang lắng nghe..."
                        : "Nhập câu hỏi hoặc sử dụng giọng nói..."
                    }
                    className="w-full py-2 sm:py-4 text-sm sm:text-base text-gray-900 placeholder-gray-500 bg-transparent border-none outline-none"
                    disabled={chatMutation.isLoading || isListening}
                  />
                </div>

                {/* Microphone Icon */}
                <button
                  type="button"
                  onClick={handleVoiceInput}
                  disabled={chatMutation.isLoading}
                  className={`p-2 sm:p-3 transition-colors duration-200 rounded-full ${
                    isListening
                      ? "bg-red-100 text-red-600 animate-pulse"
                      : "text-gray-500 hover:text-gray-700 hover:bg-gray-50"
                  } ${
                    chatMutation.isLoading
                      ? "opacity-50 cursor-not-allowed"
                      : ""
                  }`}
                  title={
                    isListening ? "Đang lắng nghe..." : "Nhập bằng giọng nói"
                  }
                >
                  <Mic className="h-4 w-4 sm:h-5 sm:w-5" />
                </button>

                {/* Send Button - Circular */}
                <button
                  type="submit"
                  disabled={!inputMessage.trim() || chatMutation.isLoading}
                  className={`ml-1 sm:ml-2 mr-1 sm:mr-2 p-2 sm:p-3 rounded-full transition-all duration-200 flex items-center justify-center ${
                    inputMessage.trim() && !chatMutation.isLoading
                      ? "bg-purple-600 hover:bg-purple-700 text-white shadow-md hover:shadow-lg"
                      : "bg-gray-100 text-gray-400 cursor-not-allowed"
                  }`}
                  title="Send message"
                >
                  {chatMutation.isLoading ? (
                    <div className="animate-spin rounded-full h-4 w-4 sm:h-5 sm:w-5 border-b-2 border-white"></div>
                  ) : (
                    <ArrowUp className="h-4 w-4 sm:h-5 sm:w-5" />
                  )}
                </button>
              </div>
            </div>
            <p className="text-xs text-gray-500 mt-1 sm:mt-2 text-center">
              Nhấn Enter để gửi • Click vào biểu tượng mic để nhập bằng giọng
              nói
            </p>
          </form>
        </div>
      </div>
    </div>
  );
}

export default ChatbotTab;
