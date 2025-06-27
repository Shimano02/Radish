import React, { useState, useEffect } from 'react'
import { ArrowLeft, Download, Eye, Calendar, User, Clock } from 'lucide-react'
import { getInterviewRecords, downloadRecording } from '../services/api'

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

      <div className="container mx-auto px-4 py-8">
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
          <div className="grid gap-4">
            {records.map((record) => (
              <div
                key={record.id}
                className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow"
              >
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-4 mb-2">
                      <div className="flex items-center text-gray-600">
                        <Calendar size={16} className="mr-1" />
                        <span className="text-sm">{formatDate(record.timestamp)}</span>
                      </div>
                      <div className="flex items-center text-gray-600">
                        <User size={16} className="mr-1" />
                        <span className="text-sm">{record.interviewer_name}</span>
                      </div>
                      <div className="flex items-center text-gray-600">
                        <Clock size={16} className="mr-1" />
                        <span className="text-sm">{record.duration}</span>
                      </div>
                    </div>
                    <div className="text-sm text-gray-500">
                      会話ID: {record.conversation_id}
                    </div>
                    <div className="text-sm text-gray-500">
                      メッセージ数: {record.user_messages} / AI応答数: {record.ai_responses}
                    </div>
                  </div>
                  <div className="flex space-x-2">
                    <button
                      onClick={() => handleViewDetails(record)}
                      className="p-2 bg-blue-500 hover:bg-blue-600 text-white rounded-full transition-colors"
                      title="詳細を表示"
                    >
                      <Eye size={16} />
                    </button>
                    {record.has_recording && (
                      <button
                        onClick={() => handleDownloadRecording(record.id)}
                        className="p-2 bg-green-500 hover:bg-green-600 text-white rounded-full transition-colors"
                        title="録画をダウンロード"
                      >
                        <Download size={16} />
                      </button>
                    )}
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
