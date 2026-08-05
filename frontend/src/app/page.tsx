"use client"

import React, { useState } from "react"
import { Navbar } from "@/components/Navbar"
import { UploadCard } from "@/components/UploadCard"
import { ProcessingCard } from "@/components/ProcessingCard"
import { ResultView } from "@/components/ResultView"
import { ErrorAlert } from "@/components/ErrorAlert"
import { Music, Cpu, Download, Sparkles, SlidersHorizontal, Disc } from "lucide-react"

type ViewState = "upload" | "processing" | "result" | "error"

export default function Home() {
  const [view, setView] = useState<ViewState>("upload")
  const [jobId, setJobId] = useState<string | null>(null)
  const [filename, setFilename] = useState<string>("")
  const [errorDetails, setErrorDetails] = useState<{ message: string; stage: string } | null>(null)

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

  const handleUploadSuccess = (newJobId: string, uploadedFilename: string) => {
    setJobId(newJobId)
    setFilename(uploadedFilename)
    setView("processing")
  }

  const handleProcessingComplete = (completedJobId: string) => {
    setJobId(completedJobId)
    setView("result")
  }

  const handleProcessingError = (errorMsg: string, stage: string) => {
    setErrorDetails({ message: errorMsg, stage })
    setView("error")
  }

  const handleReset = () => {
    setView("upload")
    setJobId(null)
    setFilename("")
    setErrorDetails(null)
  }

  return (
    <div className="min-h-screen flex flex-col bg-[#352F44] text-[#FAF0E6] selection:bg-[#5C5470] selection:text-[#FAF0E6]">
      <Navbar />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 py-10 flex flex-col justify-center">
        {/* Intro Header */}
        {view === "upload" && (
          <div className="text-center max-w-4xl mx-auto mb-12 space-y-4">
            <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-[#5C5470]/50 border border-[#B9B4C7]/30 text-xs font-semibold text-[#FAF0E6] mb-2 shadow-sm">
              <Sparkles className="h-3.5 w-3.5 text-[#B9B4C7]" />
              Sheet Music to Audio Converter Engine
            </div>

            <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight text-[#FAF0E6] leading-tight">
              Turn PDF Sheet Music into Playable Audio
            </h1>

            <p className="text-[#B9B4C7] text-base sm:text-xl max-w-3xl mx-auto leading-relaxed">
              Upload your piano PDF scores to automatically recognize notes via Optical Music Recognition (OMR) and synthesize MIDI, WAV audio, and MusicXML.
            </p>
          </div>
        )}

        {/* Dynamic Workflow Views */}
        <div className="w-full">
          {view === "upload" && (
            <UploadCard onUploadSuccess={handleUploadSuccess} apiUrl={apiUrl} />
          )}

          {view === "processing" && jobId && (
            <ProcessingCard
              jobId={jobId}
              filename={filename}
              apiUrl={apiUrl}
              onComplete={handleProcessingComplete}
              onError={handleProcessingError}
              onCancel={handleReset}
            />
          )}

          {view === "result" && jobId && (
            <ResultView jobId={jobId} apiUrl={apiUrl} onReset={handleReset} />
          )}

          {view === "error" && errorDetails && (
            <ErrorAlert
              errorMsg={errorDetails.message}
              stage={errorDetails.stage}
              onReset={handleReset}
            />
          )}
        </div>

        {/* Feature Highlights Grid */}
        {view === "upload" && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-16 max-w-6xl mx-auto border-t border-[#5C5470]/30 pt-12">
            <div className="p-6 rounded-2xl bg-[#5C5470]/20 border border-[#B9B4C7]/20 flex items-start gap-4 hover:border-[#B9B4C7]/40 transition-all">
              <div className="p-3.5 rounded-xl bg-[#5C5470] text-[#FAF0E6] shrink-0 border border-[#B9B4C7]/30 shadow-md">
                <Cpu className="h-6 w-6" />
              </div>
              <div>
                <h3 className="font-bold text-[#FAF0E6] text-base">oemer OMR Engine</h3>
                <p className="text-xs text-[#B9B4C7] mt-1.5 leading-relaxed">
                  Deep-learning model for stave detection, notehead extraction, and key signature parsing.
                </p>
              </div>
            </div>

            <div className="p-6 rounded-2xl bg-[#5C5470]/20 border border-[#B9B4C7]/20 flex items-start gap-4 hover:border-[#B9B4C7]/40 transition-all">
              <div className="p-3.5 rounded-xl bg-[#5C5470] text-[#FAF0E6] shrink-0 border border-[#B9B4C7]/30 shadow-md">
                <Disc className="h-6 w-6" />
              </div>
              <div>
                <h3 className="font-bold text-[#FAF0E6] text-base">FluidSynth Grand Piano</h3>
                <p className="text-xs text-[#B9B4C7] mt-1.5 leading-relaxed">
                  Synthesizes polyphonic acoustic piano audio performances using General MIDI SoundFonts.
                </p>
              </div>
            </div>

            <div className="p-6 rounded-2xl bg-[#5C5470]/20 border border-[#B9B4C7]/20 flex items-start gap-4 hover:border-[#B9B4C7]/40 transition-all">
              <div className="p-3.5 rounded-xl bg-[#5C5470] text-[#FAF0E6] shrink-0 border border-[#B9B4C7]/30 shadow-md">
                <Download className="h-6 w-6" />
              </div>
              <div>
                <h3 className="font-bold text-[#FAF0E6] text-base">Multi-Format Export</h3>
                <p className="text-xs text-[#B9B4C7] mt-1.5 leading-relaxed">
                  Download rendered WAV audio files, editable MIDI tracks, or standard MusicXML scores.
                </p>
              </div>
            </div>
          </div>
        )}
      </main>

      <footer className="border-t border-[#5C5470]/40 py-8 text-center text-xs text-[#B9B4C7]">
        <p className="font-medium text-sm">© 2026 Sheet2Sound by E11even. All rights reserved.</p>
      </footer>
    </div>
  )
}
