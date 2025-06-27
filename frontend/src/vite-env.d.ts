

interface ImportMetaEnv {
  readonly VITE_API_URL: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}

interface Window {
  SpeechRecognition: any;
  webkitSpeechRecognition: any;
}
