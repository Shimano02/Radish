import React, { useState, useEffect, useRef } from 'react'
import { Mic, MicOff, Send, Video, Square, Pause, Play, Download } from 'lucide-react'
import { Interviewer, ChatMessage } from '../types'
import { sendMessage } from '../services/api'
import { useVideoRecording } from '../hooks/useVideoRecording'

interface Props {
  interviewer: Interviewer
  conversationId: string
  onViewChange: (view: 'interview' | 'admin') => void
}

const ChatInterface: React.FC<Props> = ({ interviewer, conversationId, onViewChange }) => {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [inputText, setInputText] = useState('')
  const [isVoiceRecording, setIsVoiceRecording] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const recognitionRef = useRef<any>(null)
  const cameraVideoRef = useRef<HTMLVideoElement>(null)
  
  const {
    isRecording: isVideoRecording,
    isPaused: isVideoPaused,
    recordedBlobs,
    cameraStream,
    startRecording: startVideoRecording,
    stopRecording: stopVideoRecording,
    pauseRecording: pauseVideoRecording,
    resumeRecording: resumeVideoRecording,
    downloadRecording: downloadVideoRecording,
    uploadRecording: uploadVideoRecording,
    error: videoError
  } = useVideoRecording()

  useEffect(() => {
    const initialMessage: ChatMessage = {
      id: '1',
      content: '映像と音声、問題ありませんか？\n準備ができましたら「開始」と入力して下さい。',
      sender: 'ai',
      timestamp: new Date()
    }
    setMessages([initialMessage])

    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
      recognitionRef.current = new SpeechRecognition()
      recognitionRef.current.lang = 'ja-JP'
      recognitionRef.current.continuous = false
      recognitionRef.current.interimResults = false

      recognitionRef.current.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript
        setInputText(transcript)
        setIsVoiceRecording(false)
      }

      recognitionRef.current.onerror = () => {
        setIsVoiceRecording(false)
      }

      recognitionRef.current.onend = () => {
        setIsVoiceRecording(false)
      }
    }
  }, [])

  useEffect(() => {
    if (cameraVideoRef.current && cameraStream) {
      cameraVideoRef.current.srcObject = cameraStream
    }
  }, [cameraStream])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSendMessage = async () => {
    console.log('handleSendMessage called with inputText:', inputText)
    if (!inputText.trim() || isLoading) {
      console.log('Early return - inputText empty or loading')
      return
    }

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      content: inputText,
      sender: 'user',
      timestamp: new Date()
    }

    console.log('Checking for 開始 message:', inputText.trim() === '開始', 'isVideoRecording:', isVideoRecording)
    if (inputText.trim() === '開始' && !isVideoRecording) {
      console.log('開始 message detected - starting automatic recording')
      try {
        await startVideoRecording()
        console.log('Automatic recording started successfully')
      } catch (error) {
        console.error('自動録画開始に失敗しました:', error)
      }
    }

    setMessages(prev => [...prev, userMessage])
    setInputText('')
    setIsLoading(true)

    try {
      const response = await sendMessage({
        message: inputText,
        interviewer_id: interviewer.id,
        conversation_id: conversationId
      })

      const aiMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        content: response.response,
        sender: 'ai',
        timestamp: new Date()
      }

      setMessages(prev => [...prev, aiMessage])

      if ('speechSynthesis' in window) {
        const utterance = new SpeechSynthesisUtterance(response.response)
        utterance.lang = 'ja-JP'
        speechSynthesis.speak(utterance)
      }
    } catch (error) {
      console.error('Failed to send message:', error)
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        content: '申し訳ございませんが、メッセージの送信に失敗しました。もう一度お試しください。',
        sender: 'ai',
        timestamp: new Date()
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const handleVoiceRecord = () => {
    if (!recognitionRef.current) {
      alert('音声認識がサポートされていません。')
      return
    }

    if (isVoiceRecording) {
      recognitionRef.current.stop()
      setIsVoiceRecording(false)
    } else {
      recognitionRef.current.start()
      setIsVoiceRecording(true)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    console.log('handleKeyPress called with key:', e.key)
    if (e.key === 'Enter' && !e.shiftKey) {
      console.log('Enter key pressed, calling handleSendMessage')
      e.preventDefault()
      handleSendMessage()
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <div className="gradient-header text-white p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <div className="w-12 h-12 bg-white/20 rounded-full flex items-center justify-center mr-3">
              <div className="text-2xl">👩‍💼</div>
            </div>
            <div>
              <h1 className="text-xl font-bold">{interviewer.title} {interviewer.name}</h1>
              <p className="text-sm opacity-90">AI面接官</p>
            </div>
          </div>
          <button
            onClick={() => onViewChange('admin')}
            className="bg-white/20 hover:bg-white/30 px-4 py-2 rounded-full transition-colors text-sm"
          >
            管理画面
          </button>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-4">
        <div className="max-w-6xl mx-auto">
          {/* 録画コントロール - 上部中央に配置 */}
          <div className="flex justify-center mb-4">
            <div className="flex items-center space-x-4 bg-white/90 backdrop-blur-sm rounded-full px-6 py-3 shadow-lg">
              <div className="flex space-x-2">
                {!isVideoRecording ? (
                  <button
                    onClick={startVideoRecording}
                    className={`${
                      messages.some(msg => msg.content.trim() === '開始' && msg.sender === 'user')
                        ? 'bg-green-500 hover:bg-green-600 animate-pulse'
                        : 'bg-red-500 hover:bg-red-600'
                    } text-white p-3 rounded-full shadow-lg transition-colors`}
                    title={
                      messages.some(msg => msg.content.trim() === '開始' && msg.sender === 'user')
                        ? '面接開始 - 録画を開始してください'
                        : '録画開始'
                    }
                  >
                    <Video size={24} />
                  </button>
                ) : (
                  <div className="flex space-x-2">
                    <button
                      onClick={stopVideoRecording}
                      className="bg-gray-800 hover:bg-gray-900 text-white p-3 rounded-full shadow-lg transition-colors"
                      title="録画停止"
                    >
                      <Square size={24} />
                    </button>
                    {!isVideoPaused ? (
                      <button
                        onClick={pauseVideoRecording}
                        className="bg-yellow-500 hover:bg-yellow-600 text-white p-3 rounded-full shadow-lg transition-colors"
                        title="録画一時停止"
                      >
                        <Pause size={24} />
                      </button>
                    ) : (
                      <button
                        onClick={resumeVideoRecording}
                        className="bg-green-500 hover:bg-green-600 text-white p-3 rounded-full shadow-lg transition-colors"
                        title="録画再開"
                      >
                        <Play size={24} />
                      </button>
                    )}
                  </div>
                )}
              </div>
              
              {/* 録画状態表示 */}
              {isVideoRecording && (
                <div className="flex items-center space-x-2 bg-black/70 text-white px-4 py-2 rounded-full">
                  <div className={`w-3 h-3 rounded-full ${isVideoPaused ? 'bg-yellow-400' : 'bg-red-500 animate-pulse'}`}></div>
                  <span className="text-sm font-medium">
                    {isVideoPaused ? '一時停止中' : '録画中'}
                  </span>
                </div>
              )}
              
              {/* ダウンロード・アップロードボタン */}
              {recordedBlobs.length > 0 && !isVideoRecording && (
                <div className="flex space-x-2">
                  <button
                    onClick={downloadVideoRecording}
                    className="bg-blue-500 hover:bg-blue-600 text-white p-3 rounded-full shadow-lg transition-colors"
                    title="録画をダウンロード"
                  >
                    <Download size={24} />
                  </button>
                  <button
                    onClick={() => uploadVideoRecording(conversationId)}
                    className="bg-green-500 hover:bg-green-600 text-white p-3 rounded-full shadow-lg transition-colors"
                    title="録画をサーバーに保存"
                  >
                    <Video size={24} />
                  </button>
                </div>
              )}
            </div>
          </div>

          {/* Zoom/Google Meet風の2画面レイアウト */}
          <div className="grid grid-cols-2 gap-6 mb-6">
            {/* 面接官画面 */}
            <div className="relative aspect-video rounded-2xl overflow-hidden shadow-lg bg-gray-900">
              <img 
                src={interviewer.image_url} 
                alt={`${interviewer.title} ${interviewer.name}`}
                className="w-full h-full object-contain"
              />
              <div className="absolute bottom-4 left-4 bg-black/70 text-white px-3 py-1 rounded-lg">
                <span className="text-sm font-medium">{interviewer.title} {interviewer.name}</span>
              </div>
            </div>

            {/* ユーザーカメラ画面 */}
            <div className="relative aspect-video rounded-2xl overflow-hidden shadow-lg bg-gray-900">
              {cameraStream ? (
                <>
                  <video
                    ref={cameraVideoRef}
                    autoPlay
                    muted
                    playsInline
                    className="w-full h-full object-cover"
                  />
                  <div className="absolute bottom-4 left-4 bg-black/70 text-white px-3 py-1 rounded-lg">
                    <span className="text-sm font-medium">あなた</span>
                  </div>
                  {isVideoRecording && (
                    <div className="absolute top-4 right-4 w-4 h-4 bg-red-500 rounded-full animate-pulse"></div>
                  )}
                </>
              ) : (
                <div className="w-full h-full flex items-center justify-center bg-gray-800">
                  <div className="text-center text-white">
                    <Video size={48} className="mx-auto mb-2 opacity-50" />
                    <p className="text-sm opacity-75">カメラが接続されていません</p>
                    <p className="text-xs opacity-50 mt-1">録画開始でカメラが有効になります</p>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* エラー表示 */}
          {videoError && (
            <div className="mb-4 p-4 bg-red-500 text-white rounded-lg text-center">
              <p className="font-medium">録画エラー</p>
              <p className="text-sm mt-1">{videoError}</p>
            </div>
          )}
          
          {messages.length > 0 && messages[messages.length - 1].sender === 'ai' && (
            <div className="mb-6 flex justify-center">
              <div className="relative max-w-2xl">
                <div className="bg-white rounded-2xl px-6 py-4 shadow-lg border border-gray-200 relative">
                  <p className="text-gray-800 text-lg leading-relaxed whitespace-pre-line">{messages[messages.length - 1].content}</p>
                  <div className="absolute bottom-0 left-1/2 transform -translate-x-1/2 translate-y-full">
                    <div className="w-0 h-0 border-l-4 border-r-4 border-t-8 border-l-transparent border-r-transparent border-t-white"></div>
                  </div>
                </div>
              </div>
            </div>
          )}
          {isLoading && (
            <div className="flex justify-center mb-6">
              <div className="relative max-w-2xl">
                <div className="bg-white rounded-2xl px-6 py-4 shadow-lg border border-gray-200 relative">
                  <div className="flex space-x-1 justify-center">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  </div>
                  <div className="absolute bottom-0 left-1/2 transform -translate-x-1/2 translate-y-full">
                    <div className="w-0 h-0 border-l-4 border-r-4 border-t-8 border-l-transparent border-r-transparent border-t-white"></div>
                  </div>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </div>

      <div className="bg-white border-t border-gray-200 p-4">
        <div className="max-w-4xl mx-auto">
          <div className="flex items-center space-x-2">
            <div className="flex-1 relative">
              <textarea
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="メッセージを入力してください..."
                className="w-full p-3 border border-gray-300 rounded-2xl resize-none focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                rows={1}
                disabled={isLoading}
              />
            </div>
            <button
              onClick={handleVoiceRecord}
              className={`p-3 rounded-full transition-colors ${
                isVoiceRecording 
                  ? 'bg-red-500 text-white voice-recording' 
                  : 'bg-gray-200 text-gray-600 hover:bg-gray-300'
              }`}
              disabled={isLoading}
            >
              {isVoiceRecording ? <MicOff size={20} /> : <Mic size={20} />}
            </button>
            <button
              onClick={handleSendMessage}
              disabled={!inputText.trim() || isLoading}
              className="p-3 bg-orange-500 text-white rounded-full hover:bg-orange-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <Send size={20} />
            </button>
          </div>
          <div className="mt-2 text-center">
            <p className="text-xs text-gray-500">
              テキストで回答 | 音声で回答
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ChatInterface
