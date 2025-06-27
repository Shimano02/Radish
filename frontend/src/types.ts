export interface Interviewer {
  id: string
  name: string
  title: string
  description: string
  image_url: string
}

export interface ChatMessage {
  id: string
  content: string
  sender: 'user' | 'ai'
  timestamp: Date
}

export interface ChatResponse {
  response: string
  conversation_id: string
  stage: number
}
