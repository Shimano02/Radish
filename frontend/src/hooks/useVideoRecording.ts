import { useState, useRef, useCallback } from 'react'

interface UseVideoRecordingReturn {
  isRecording: boolean
  isPaused: boolean
  recordedBlobs: Blob[]
  cameraStream: MediaStream | null
  startRecording: () => Promise<void>
  stopRecording: () => void
  pauseRecording: () => void
  resumeRecording: () => void
  downloadRecording: () => void
  error: string | null
}

export const useVideoRecording = (): UseVideoRecordingReturn => {
  const [isRecording, setIsRecording] = useState(false)
  const [isPaused, setIsPaused] = useState(false)
  const [recordedBlobs, setRecordedBlobs] = useState<Blob[]>([])
  const [error, setError] = useState<string | null>(null)
  const [cameraStream, setCameraStream] = useState<MediaStream | null>(null)
  
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const streamRef = useRef<MediaStream | null>(null)

  const startRecording = useCallback(async () => {
    console.log('startRecording function called')
    try {
      setError(null)
      console.log('Requesting display media...')
      
      const displayStream = await navigator.mediaDevices.getDisplayMedia({
        video: {
          width: { ideal: 1920 },
          height: { ideal: 1080 }
        },
        audio: true
      })

      let audioStream: MediaStream | null = null
      let userCameraStream: MediaStream | null = null
      
      try {
        audioStream = await navigator.mediaDevices.getUserMedia({ audio: true })
      } catch (audioError) {
        console.warn('マイク音声の取得に失敗しました:', audioError)
      }

      try {
        userCameraStream = await navigator.mediaDevices.getUserMedia({ 
          video: { 
            width: { ideal: 640 }, 
            height: { ideal: 480 },
            facingMode: 'user'
          } 
        })
        setCameraStream(userCameraStream)
      } catch (cameraError) {
        console.warn('カメラの取得に失敗しました:', cameraError)
        setError('カメラへのアクセスが拒否されました。ブラウザの設定を確認してください。')
      }

      const tracks = [...displayStream.getVideoTracks()]
      if (userCameraStream) {
        tracks.push(...userCameraStream.getVideoTracks())
      }
      if (displayStream.getAudioTracks().length > 0) {
        tracks.push(...displayStream.getAudioTracks())
      } else if (audioStream) {
        tracks.push(...audioStream.getAudioTracks())
      }

      const combinedStream = new MediaStream(tracks)
      streamRef.current = combinedStream

      const options = {
        mimeType: 'video/webm;codecs=vp9,opus'
      }

      if (!MediaRecorder.isTypeSupported(options.mimeType)) {
        options.mimeType = 'video/webm;codecs=vp8,opus'
        if (!MediaRecorder.isTypeSupported(options.mimeType)) {
          options.mimeType = 'video/webm'
        }
      }

      mediaRecorderRef.current = new MediaRecorder(combinedStream, options)
      
      const chunks: Blob[] = []
      
      mediaRecorderRef.current.ondataavailable = (event) => {
        if (event.data && event.data.size > 0) {
          chunks.push(event.data)
        }
      }

      mediaRecorderRef.current.onstop = () => {
        setRecordedBlobs(chunks)
        setIsRecording(false)
        setIsPaused(false)
        
        if (streamRef.current) {
          streamRef.current.getTracks().forEach(track => track.stop())
          streamRef.current = null
        }
        if (cameraStream) {
          cameraStream.getTracks().forEach(track => track.stop())
          setCameraStream(null)
        }
      }

      mediaRecorderRef.current.onerror = (event) => {
        console.error('MediaRecorder error:', event)
        setError('録画中にエラーが発生しました')
        setIsRecording(false)
        setIsPaused(false)
      }

      displayStream.getVideoTracks()[0].onended = () => {
        stopRecording()
      }

      mediaRecorderRef.current.start(1000) // 1秒ごとにデータを記録
      setIsRecording(true)
      setRecordedBlobs([])

    } catch (err) {
      console.error('録画開始エラー:', err)
      setError('録画を開始できませんでした。画面共有を許可してください。')
      setIsRecording(false)
    }
  }, [cameraStream])

  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop()
    }
  }, [isRecording])

  const pauseRecording = useCallback(() => {
    if (mediaRecorderRef.current && isRecording && !isPaused) {
      mediaRecorderRef.current.pause()
      setIsPaused(true)
    }
  }, [isRecording, isPaused])

  const resumeRecording = useCallback(() => {
    if (mediaRecorderRef.current && isRecording && isPaused) {
      mediaRecorderRef.current.resume()
      setIsPaused(false)
    }
  }, [isRecording, isPaused])

  const downloadRecording = useCallback(() => {
    if (recordedBlobs.length === 0) {
      setError('ダウンロードする録画データがありません')
      return
    }

    try {
      const blob = new Blob(recordedBlobs, { type: 'video/webm' })
      const url = URL.createObjectURL(blob)
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-')
      const filename = `interview-recording-${timestamp}.webm`
      
      const a = document.createElement('a')
      a.href = url
      a.download = filename
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      
      setTimeout(() => URL.revokeObjectURL(url), 1000)
      
    } catch (err) {
      console.error('ダウンロードエラー:', err)
      setError('録画データのダウンロードに失敗しました')
    }
  }, [recordedBlobs])

  return {
    isRecording,
    isPaused,
    recordedBlobs,
    cameraStream,
    startRecording,
    stopRecording,
    pauseRecording,
    resumeRecording,
    downloadRecording,
    error
  }
}
