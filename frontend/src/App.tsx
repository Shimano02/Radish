import { useState } from 'react'
import InterviewerSelection from './components/InterviewerSelection'
import ChatInterface from './components/ChatInterface'
import { Interviewer } from './types'

function App() {
  const [selectedInterviewer, setSelectedInterviewer] = useState<Interviewer | null>(null)
  const [conversationId, setConversationId] = useState<string>('')

  const handleInterviewerSelect = (interviewer: Interviewer, convId: string) => {
    setSelectedInterviewer(interviewer)
    setConversationId(convId)
  }

  const handleBackToSelection = () => {
    setSelectedInterviewer(null)
    setConversationId('')
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {!selectedInterviewer ? (
        <InterviewerSelection onSelect={handleInterviewerSelect} />
      ) : (
        <ChatInterface 
          interviewer={selectedInterviewer}
          conversationId={conversationId}
          onBack={handleBackToSelection}
        />
      )}
    </div>
  )
}

export default App
