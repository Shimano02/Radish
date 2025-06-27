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

export const getInterviewRecords = async () => {
  const response = await api.get('/api/admin/records')
  return response.data
}

export const downloadRecording = async (recordId: string) => {
  const response = await api.get(`/api/admin/recording/${recordId}`, {
    responseType: 'blob'
  })
  
  const url = window.URL.createObjectURL(new Blob([response.data]))
  const link = document.createElement('a')
  link.href = url
  link.setAttribute('download', `interview_${recordId}.webm`)
  document.body.appendChild(link)
  link.click()
  link.remove()
  window.URL.revokeObjectURL(url)
}

export const uploadRecording = async (conversationId: string, blob: Blob) => {
  const formData = new FormData()
  formData.append('file', blob, `${conversationId}.webm`)
  formData.append('conversation_id', conversationId)
  
  const response = await api.post('/api/admin/upload-recording', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
  return response.data
}
