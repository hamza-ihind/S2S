"use client"

import React, { useState, useRef } from "react"
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Alert, AlertTitle, AlertDescription } from "@/components/ui/alert"
import { Badge } from "@/components/ui/badge"
import { UploadCloud, FileText, AlertCircle, Music, Settings2, CheckCircle2, Music4 } from "lucide-react"

interface UploadCardProps {
  onUploadSuccess: (jobId: string, filename: string) => void
  apiUrl: string
}

export function UploadCard({ onUploadSuccess, apiUrl }: UploadCardProps) {
  const [file, setFile] = useState<File | null>(null)
  const [dragOver, setDragOver] = useState(false)
  const [errorMsg, setErrorMsg] = useState<string | null>(null)
  const [isUploading, setIsUploading] = useState(false)
  const [simulateError, setSimulateError] = useState<string>("none")
  const fileInputRef = useRef<HTMLInputElement>(null)

  const validateAndSetFile = (selectedFile: File) => {
    setErrorMsg(null)
    if (!selectedFile.name.toLowerCase().endsWith(".pdf")) {
      setErrorMsg("Invalid file format. Please upload a valid PDF sheet music file.")
      setFile(null)
      return
    }

    const maxSizeBytes = 15 * 1024 * 1024 // 15MB
    if (selectedFile.size > maxSizeBytes) {
      setErrorMsg(`File size exceeds 15MB limit (${(selectedFile.size / (1024 * 1024)).toFixed(1)} MB).`)
      setFile(null)
      return
    }

    setFile(selectedFile)
  }

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    setDragOver(true)
  }

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault()
    setDragOver(false)
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setDragOver(false)
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      validateAndSetFile(e.dataTransfer.files[0])
    }
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      validateAndSetFile(e.target.files[0])
    }
  }

  const handleSubmit = async () => {
    if (!file) return
    setIsUploading(true)
    setErrorMsg(null)

    try {
      const formData = new FormData()
      formData.append("file", file)

      const uploadRes = await fetch(`${apiUrl}/api/upload`, {
        method: "POST",
        body: formData,
      })

      if (!uploadRes.ok) {
        const errorData = await uploadRes.json().catch(() => ({}))
        throw new Error(errorData.detail || "Failed to upload file to backend server.")
      }

      const uploadData = await uploadRes.json()
      const jobId = uploadData.job_id

      const convertPayload: { simulate_error?: string } = {}
      if (simulateError !== "none") {
        convertPayload.simulate_error = simulateError
      }

      const convertRes = await fetch(`${apiUrl}/api/convert/${jobId}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(convertPayload),
      })

      if (!convertRes.ok) {
        throw new Error("Failed to initialize conversion process.")
      }

      onUploadSuccess(jobId, file.name)
    } catch (err: any) {
      setErrorMsg(err.message || "An unexpected error occurred during file upload.")
      setIsUploading(false)
    }
  }

  return (
    <Card className="max-w-4xl mx-auto shadow-2xl border-[#B9B4C7]/30 glass-panel-custom">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="text-2xl font-bold flex items-center gap-3 text-[#FAF0E6]">
              <Music4 className="h-7 w-7 text-[#B9B4C7]" />
              Upload Piano Sheet Music
            </CardTitle>
            <CardDescription className="text-[#B9B4C7]">
              Select or drag & drop a PDF sheet music score to generate MIDI & audio
            </CardDescription>
          </div>
          <Badge variant="default" className="px-4 py-1.5 bg-[#5C5470] text-[#FAF0E6] border-[#B9B4C7]/40">
            PDF Score Only
          </Badge>
        </div>
      </CardHeader>

      <CardContent className="space-y-6">
        {errorMsg && (
          <Alert variant="destructive">
            <AlertCircle className="h-5 w-5 text-red-400 shrink-0" />
            <div>
              <AlertTitle>Upload Error</AlertTitle>
              <AlertDescription>{errorMsg}</AlertDescription>
            </div>
          </Alert>
        )}

        {/* Drag & Drop Zone */}
        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          className={`relative border-2 border-dashed rounded-2xl p-10 text-center cursor-pointer transition-all duration-300 ${
            dragOver
              ? "border-[#FAF0E6] bg-[#5C5470]/50 scale-[1.01]"
              : file
              ? "border-emerald-400/80 bg-emerald-950/20"
              : "border-[#B9B4C7]/40 hover:border-[#FAF0E6] bg-[#5C5470]/20 hover:bg-[#5C5470]/40"
          }`}
        >
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileChange}
            accept=".pdf"
            className="hidden"
          />

          {file ? (
            <div className="flex flex-col items-center gap-3">
              <div className="h-16 w-16 rounded-2xl bg-emerald-500/20 border border-emerald-400/40 flex items-center justify-center text-emerald-300 shadow-lg">
                <FileText className="h-8 w-8" />
              </div>
              <div>
                <p className="font-semibold text-[#FAF0E6] text-xl">{file.name}</p>
                <p className="text-xs text-[#B9B4C7] mt-1">
                  {(file.size / (1024 * 1024)).toFixed(2)} MB • Ready for OMR conversion
                </p>
              </div>
              <div className="flex items-center gap-2 text-xs text-emerald-300 font-medium bg-emerald-950/50 px-4 py-1.5 rounded-full border border-emerald-700/50">
                <CheckCircle2 className="h-4 w-4" />
                Valid PDF selected
              </div>
            </div>
          ) : (
            <div className="flex flex-col items-center gap-3">
              <div className="h-16 w-16 rounded-2xl bg-[#5C5470]/60 border border-[#B9B4C7]/40 flex items-center justify-center text-[#FAF0E6] shadow-xl">
                <UploadCloud className="h-8 w-8" />
              </div>
              <div>
                <p className="font-semibold text-[#FAF0E6] text-lg">
                  Drag and drop your PDF score here, or <span className="text-[#B9B4C7] underline">browse file</span>
                </p>
                <p className="text-xs text-[#B9B4C7] mt-1.5">
                  Supports single & multi-staff typeset piano scores (up to 15MB)
                </p>
              </div>
            </div>
          )}
        </div>

        {/* Demo options / Error Simulation toggle for frontend testing */}
        <div className="p-4 rounded-xl bg-[#5C5470]/30 border border-[#B9B4C7]/20 text-xs space-y-2">
          <div className="flex items-center justify-between text-[#FAF0E6] font-medium">
            <span className="flex items-center gap-2">
              <Settings2 className="h-4 w-4 text-[#B9B4C7]" />
              Pipeline Simulation Mode
            </span>
            <span className="text-[#B9B4C7]">Demo Testing Helper</span>
          </div>
          <div className="flex items-center gap-4 pt-1">
            <label className="flex items-center gap-2 cursor-pointer text-[#B9B4C7] hover:text-[#FAF0E6]">
              <input
                type="radio"
                name="simError"
                value="none"
                checked={simulateError === "none"}
                onChange={() => setSimulateError("none")}
                className="accent-[#B9B4C7]"
              />
              Normal Success
            </label>
            <label className="flex items-center gap-2 cursor-pointer text-[#B9B4C7] hover:text-[#FAF0E6]">
              <input
                type="radio"
                name="simError"
                value="omr"
                checked={simulateError === "omr"}
                onChange={() => setSimulateError("omr")}
                className="accent-[#B9B4C7]"
              />
              Simulate OMR Failure
            </label>
            <label className="flex items-center gap-2 cursor-pointer text-[#B9B4C7] hover:text-[#FAF0E6]">
              <input
                type="radio"
                name="simError"
                value="synthesis"
                checked={simulateError === "synthesis"}
                onChange={() => setSimulateError("synthesis")}
                className="accent-[#B9B4C7]"
              />
              Simulate Audio Synthesis Failure
            </label>
          </div>
        </div>
      </CardContent>

      <CardFooter className="flex justify-between items-center">
        {file && (
          <Button
            variant="ghost"
            onClick={() => {
              setFile(null)
              setErrorMsg(null)
            }}
            disabled={isUploading}
          >
            Clear File
          </Button>
        )}
        <Button
          className="ml-auto"
          disabled={!file || isUploading}
          onClick={handleSubmit}
          size="lg"
        >
          {isUploading ? (
            <div className="flex items-center gap-2">
              <div className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
              Uploading...
            </div>
          ) : (
            "Start Conversion Pipeline"
          )}
        </Button>
      </CardFooter>
    </Card>
  )
}
