import { useState, useEffect } from 'react'
import ChatInterface from './components/ChatInterface'
import AdminPanel from './components/AdminPanel'
import { Interviewer } from './types'
import { startChat } from './services/api'

function App() {
  const [currentView, setCurrentView] = useState<'interview' | 'admin'>('interview')
  const [interviewer, setInterviewer] = useState<Interviewer | null>(null)
  const [conversationId, setConversationId] = useState<string>('')
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const initializeInterview = async () => {
      try {
        const defaultInterviewer: Interviewer = {
          id: 'construction_engineer',
          name: '不動',
          title: '施設長',
          description: '１次面接を担当します。',
          image_url: '/assets/dayCare.png'
        }
        
        const response = await startChat(defaultInterviewer.id)
        setInterviewer(defaultInterviewer)
        setConversationId(response.conversation_id)
      } catch (error) {
        console.error('Failed to initialize interview:', error)
      } finally {
        setIsLoading(false)
      }
    }

    if (currentView === 'interview') {
      initializeInterview()
    }
  }, [currentView])

  const handleViewChange = (view: 'interview' | 'admin') => {
    setCurrentView(view)
  }

  if (isLoading && currentView === 'interview') {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-xl text-gray-600">読み込み中...</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {currentView === 'interview' && interviewer ? (
        <ChatInterface 
          interviewer={interviewer}
          conversationId={conversationId}
          onBack={() => handleViewChange('admin')}
          onViewChange={handleViewChange}
        />
      ) : (
        <AdminPanel onViewChange={handleViewChange} />
      )}
    </div>
  )
}

export default App
