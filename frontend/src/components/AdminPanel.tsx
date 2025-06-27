import React, { useState, useEffect } from 'react'
import { ArrowLeft, Download, Eye, Calendar, User, Clock } from 'lucide-react'
import { getInterviewRecords, downloadRecording, downloadCSV } from '../services/api'

interface InterviewRecord {
  id: string
  timestamp: string
  conversation_id: string
  interviewer_name: string
  user_messages: number
  ai_responses: number
  duration: string
  has_recording: boolean
  csv_file: string
}

interface Props {
  onViewChange: (view: 'interview' | 'admin') => void
}

const AdminPanel: React.FC<Props> = ({ onViewChange }) => {
  const [records, setRecords] = useState<InterviewRecord[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedRecord, setSelectedRecord] = useState<InterviewRecord | null>(null)
  const [showDetails, setShowDetails] = useState(false)

  useEffect(() => {
    fetchRecords()
  }, [])

  const fetchRecords = async () => {
    try {
      const data = await getInterviewRecords()
      setRecords(data)
    } catch (error) {
      console.error('Failed to fetch interview records:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleDownloadRecording = async (recordId: string) => {
    try {
      await downloadRecording(recordId)
    } catch (error) {
      console.error('Failed to download recording:', error)
    }
  }

  const handleDownloadCSV = async (csvFilename: string) => {
    try {
      await downloadCSV(csvFilename)
    } catch (error) {
      console.error('Failed to download CSV:', error)
    }
  }

  const handleViewDetails = (record: InterviewRecord) => {
    setSelectedRecord(record)
    setShowDetails(true)
  }

  const formatDate = (timestamp: string) => {
    return new Date(timestamp).toLocaleString('ja-JP')
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-xl text-gray-600">読み込み中...</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="gradient-header text-white p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <button
              onClick={() => onViewChange('interview')}
              className="mr-4 p-2 hover:bg-white/20 rounded-full transition-colors"
            >
              <ArrowLeft size={24} />
            </button>
            <h1 className="text-2xl font-bold">面接記録管理</h1>
          </div>
          <div className="text-sm opacity-90">
            総記録数: {records.length}件
          </div>
        </div>
      </div>

      <div className="container mx-auto px-6 py-8">
        {records.length === 0 ? (
          <div className="text-center py-12">
            <div className="text-gray-500 text-lg">面接記録がありません</div>
            <button
              onClick={() => onViewChange('interview')}
              className="mt-4 bg-orange-500 hover:bg-orange-600 text-white px-6 py-2 rounded-full transition-colors"
            >
              面接を開始する
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {records.map((record) => (
              <div
                key={record.id}
                className="bg-white rounded-xl shadow-md hover:shadow-xl transition-all duration-300 overflow-hidden group cursor-pointer"
                onClick={() => handleViewDetails(record)}
              >
                {/* Video Thumbnail */}
                <div className="relative aspect-video bg-gray-900 rounded-t-xl overflow-hidden">
                  {record.has_recording ? (
                    <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-gray-800 to-gray-900">
                      <div className="text-center">
                        <div className="w-16 h-16 mx-auto mb-3 bg-white/20 rounded-full flex items-center justify-center">
                          <svg className="w-8 h-8 text-white" fill="currentColor" viewBox="0 0 24 24">
                            <path d="M8 5v14l11-7z"/>
                          </svg>
                        </div>
                        <div className="text-white text-sm font-medium">面接録画</div>
                      </div>
                    </div>
                  ) : (
                    <div className="w-full h-full flex items-center justify-center bg-gray-200">
                      <div className="text-center">
                        <div className="w-16 h-16 mx-auto mb-3 bg-gray-400 rounded-full flex items-center justify-center">
                          <svg className="w-8 h-8 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                          </svg>
                        </div>
                        <div className="text-gray-600 text-sm">録画なし</div>
                      </div>
                    </div>
                  )}
                  
                  {/* Duration Badge */}
                  <div className="absolute bottom-2 right-2 bg-black/80 text-white text-xs px-2 py-1 rounded">
                    {record.duration}
                  </div>
                  
                  {/* Hover Overlay */}
                  <div className="absolute inset-0 bg-black/0 group-hover:bg-black/20 transition-all duration-300 flex items-center justify-center opacity-0 group-hover:opacity-100">
                    <div className="flex space-x-2">
                      {record.has_recording && (
                        <button
                          onClick={(e) => {
                            e.stopPropagation()
                            handleDownloadRecording(record.id)
                          }}
                          className="bg-green-500 hover:bg-green-600 text-white p-2 rounded-full transition-colors"
                          title="録画をダウンロード"
                        >
                          <Download size={16} />
                        </button>
                      )}
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          handleDownloadCSV(record.csv_file)
                        }}
                        className="bg-blue-500 hover:bg-blue-600 text-white p-2 rounded-full transition-colors"
                        title="CSVをダウンロード"
                      >
                        <Download size={16} />
                      </button>
                    </div>
                  </div>
                </div>

                {/* Video Info */}
                <div className="p-4">
                  <h3 className="font-semibold text-gray-900 mb-2 line-clamp-2">
                    面接記録 - {record.interviewer_name}
                  </h3>
                  
                  <div className="flex items-center text-sm text-gray-600 mb-2">
                    <Calendar size={14} className="mr-1" />
                    <span>{formatDate(record.timestamp)}</span>
                  </div>
                  
                  <div className="flex items-center justify-between text-sm text-gray-500">
                    <div className="flex items-center">
                      <User size={14} className="mr-1" />
                      <span>{record.interviewer_name}</span>
                    </div>
                    <div className="flex items-center">
                      <span>{record.user_messages + record.ai_responses} メッセージ</span>
                    </div>
                  </div>
                  
                  <div className="mt-2 text-xs text-gray-400 truncate">
                    ID: {record.conversation_id}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {showDetails && selectedRecord && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-[80vh] overflow-y-auto">
            <div className="p-6 border-b">
              <div className="flex items-center justify-between">
                <h2 className="text-xl font-bold">面接記録詳細</h2>
                <button
                  onClick={() => setShowDetails(false)}
                  className="text-gray-500 hover:text-gray-700"
                >
                  ✕
                </button>
              </div>
            </div>
            <div className="p-6">
              <div className="grid grid-cols-2 gap-4 mb-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    面接日時
                  </label>
                  <div className="text-sm text-gray-900">
                    {formatDate(selectedRecord.timestamp)}
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    面接官
                  </label>
                  <div className="text-sm text-gray-900">
                    {selectedRecord.interviewer_name}
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    会話ID
                  </label>
                  <div className="text-sm text-gray-900 font-mono">
                    {selectedRecord.conversation_id}
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    面接時間
                  </label>
                  <div className="text-sm text-gray-900">
                    {selectedRecord.duration}
                  </div>
                </div>
              </div>
              
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  CSVログファイル
                </label>
                <div className="bg-gray-50 p-3 rounded border">
                  <div className="text-sm text-gray-900 font-mono">
                    {selectedRecord.csv_file}
                  </div>
                </div>
              </div>

              <div className="flex justify-end space-x-2">
                {selectedRecord.has_recording && (
                  <button
                    onClick={() => handleDownloadRecording(selectedRecord.id)}
                    className="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded transition-colors"
                  >
                    録画をダウンロード
                  </button>
                )}
                <button
                  onClick={() => handleDownloadCSV(selectedRecord.csv_file)}
                  className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded transition-colors"
                >
                  CSVをダウンロード
                </button>
                <button
                  onClick={() => setShowDetails(false)}
                  className="bg-gray-500 hover:bg-gray-600 text-white px-4 py-2 rounded transition-colors"
                >
                  閉じる
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default AdminPanel
