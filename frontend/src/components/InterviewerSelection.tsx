import React, { useState, useEffect } from 'react'
import { Interviewer } from '../types'
import { getInterviewers, startChat } from '../services/api'

interface Props {
  onSelect: (interviewer: Interviewer, conversationId: string) => void
}

const InterviewerSelection: React.FC<Props> = ({ onSelect }) => {
  const [interviewers, setInterviewers] = useState<Interviewer[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchInterviewers = async () => {
      try {
        const data = await getInterviewers()
        setInterviewers(data)
      } catch (error) {
        console.error('Failed to fetch interviewers:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchInterviewers()
  }, [])

  const handleSelect = async (interviewer: Interviewer) => {
    try {
      const response = await startChat(interviewer.id)
      onSelect(interviewer, response.conversation_id)
    } catch (error) {
      console.error('Failed to start chat:', error)
    }
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
      <div className="gradient-header text-white py-8">
        <div className="container mx-auto px-4 text-center">
          <h1 className="text-3xl font-bold mb-2">山野ケアサービス面接画面</h1>
          <p className="text-lg opacity-90">面接官を選択してください</p>
        </div>
      </div>

      <div className="container mx-auto px-4 py-12">
        <div className="flex flex-col items-center justify-center">
          {/* 面接官カード */}
          <div className="w-full max-w-md mb-16">
            {interviewers.map((interviewer) => (
              <div
                key={interviewer.id}
                className="interviewer-card bg-white rounded-xl p-6 cursor-pointer border border-gray-200"
                onClick={() => handleSelect(interviewer)}
              >
                <div className="text-center">
                  <div className="w-32 h-32 mx-auto mb-4 bg-gray-200 rounded-full flex items-center justify-center overflow-hidden">
                    <img 
                      src={interviewer.image_url} 
                      alt={`${interviewer.title} ${interviewer.name}`}
                      className="w-full h-full object-cover"
                    />
                  </div>
                  <h3 className="text-xl font-bold text-gray-800 mb-2">
                    {interviewer.title} {interviewer.name}
                  </h3>
                  <p className="text-gray-600 text-sm leading-relaxed">
                    {interviewer.description}
                  </p>
                  <button className="mt-4 bg-orange-500 hover:bg-orange-600 text-white px-6 py-2 rounded-full transition-colors">
                    選択する
                  </button>
                </div>
              </div>
            ))}
          </div>

          {/* 面接の流れ */}
          <div className="w-full max-w-4xl bg-white rounded-xl p-8 border border-gray-200">
            <h2 className="text-2xl font-bold text-gray-800 mb-6 text-center">面接の流れ</h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-6">
              <div className="text-center">
                <div className="w-12 h-12 bg-orange-500 text-white rounded-full flex items-center justify-center mx-auto mb-3 text-xl font-bold">
                  1
                </div>
                <h3 className="font-semibold text-gray-800 mb-2">面接開始</h3>
                <p className="text-sm text-gray-600">挨拶と面接の説明</p>
              </div>
              <div className="text-center">
                <div className="w-12 h-12 bg-orange-500 text-white rounded-full flex items-center justify-center mx-auto mb-3 text-xl font-bold">
                  2
                </div>
                <h3 className="font-semibold text-gray-800 mb-2">自己紹介</h3>
                <p className="text-sm text-gray-600">経歴や背景について</p>
              </div>
              <div className="text-center">
                <div className="w-12 h-12 bg-orange-500 text-white rounded-full flex items-center justify-center mx-auto mb-3 text-xl font-bold">
                  3
                </div>
                <h3 className="font-semibold text-gray-800 mb-2">スキル確認</h3>
                <p className="text-sm text-gray-600">専門知識や経験について</p>
              </div>
              <div className="text-center">
                <div className="w-12 h-12 bg-orange-500 text-white rounded-full flex items-center justify-center mx-auto mb-3 text-xl font-bold">
                  4
                </div>
                <h3 className="font-semibold text-gray-800 mb-2">志望動機</h3>
                <p className="text-sm text-gray-600">キャリア目標について</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default InterviewerSelection
