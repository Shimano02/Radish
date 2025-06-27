import axios from 'axios'
import { Interviewer, ChatResponse } from '../types'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const getInterviewers = async (): Promise<Interviewer[]> => {
  const response = await api.get('/api/interviewers')
  return response.data
}

export const startChat = async (interviewerId: string) => {
  const response = await api.post('/api/chat/start', null, {
    params: { interviewer_id: interviewerId }
  })
  return response.data
}

export const sendMessage = async (data: {
  message: string
  interviewer_id: string
  conversation_id: string
}): Promise<ChatResponse> => {
  const response = await api.post('/api/chat/message', data)
  return response.data
}
