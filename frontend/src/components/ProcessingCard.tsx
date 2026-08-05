"use client"

import React, { useEffect, useState } from "react"
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Loader2, Music2, Eye, AudioWaveform, CheckCircle2, Clock } from "lucide-react"

interface ProcessingCardProps {
  jobId: string
  filename: string
  apiUrl: string
  onComplete: (jobId: string) => void
  onError: (errorMsg: string, stage: string) => void
  onCancel: () => void
}

export function ProcessingCard({
  jobId,
  filename,
  apiUrl,
  onComplete,
  onError,
  onCancel
}: ProcessingCardProps) {
  const [progress, setProgress] = useState<number>(5)
  const [stageText, setStageText] = useState<string>("Initializing OMR Engine...")
  const [status, setStatus] = useState<string>("processing")
  const [elapsed, setElapsed] = useState<number>(0)

  useEffect(() => {
    const timer = setInterval(() => {
      setElapsed((prev) => prev + 1)
    }, 1000)
    return () => clearInterval(timer)
  }, [])

  useEffect(() => {
    let isSubscribed = true

    const pollStatus = async () => {
      try {
        const res = await fetch(`${apiUrl}/api/status/${jobId}`)
        if (!res.ok) throw new Error("Failed to check status")

        const data = await res.json()
        if (!isSubscribed) return

        setProgress(data.progress)
        setStageText(data.stage)
        setStatus(data.status)

        if (data.status === "done") {
          setTimeout(() => {
            onComplete(jobId)
          }, 600)
        } else if (data.status === "error") {
          onError(data.error || "An unknown error occurred during conversion.", data.stage)
        }
      } catch (err) {
        console.error("Polling error:", err)
      }
    }

    pollStatus()
    const interval = setInterval(pollStatus, 1000)

    return () => {
      isSubscribed = false
      clearInterval(interval)
    }
  }, [jobId, apiUrl, onComplete, onError])

  const getStageStep = () => {
    if (progress < 15) return 0
    if (progress < 50) return 1
    if (progress < 90) return 2
    return 3
  }

  const currentStep = getStageStep()

  const stages = [
    { label: "Queued", icon: Clock },
    { label: "OMR Analysis (oemer)", icon: Eye },
    { label: "Audio Synthesis (FluidSynth)", icon: AudioWaveform },
    { label: "Complete", icon: CheckCircle2 },
  ]

  return (
    <Card className="max-w-4xl mx-auto shadow-2xl border-[#B9B4C7]/30 glass-panel-custom animate-music-glow">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="text-2xl font-bold flex items-center gap-3 text-[#FAF0E6]">
              <Loader2 className="h-6 w-6 animate-spin text-[#B9B4C7]" />
              Processing Sheet Music
            </CardTitle>
            <CardDescription className="text-[#B9B4C7]">
              Converting &quot;{filename}&quot; to MIDI and Audio
            </CardDescription>
          </div>
          <Badge variant="default" className="px-3.5 py-1 bg-[#5C5470] text-[#FAF0E6] border-[#B9B4C7]/30">
            Job #{jobId.substring(0, 8)}
          </Badge>
        </div>
      </CardHeader>

      <CardContent className="space-y-6">
        <div className="space-y-3">
          <div className="flex justify-between items-center text-sm font-medium">
            <span className="text-[#FAF0E6] flex items-center gap-2">
              <Music2 className="h-4 w-4 text-[#B9B4C7]" />
              {stageText}
            </span>
            <span className="text-[#FAF0E6] font-bold text-lg">{progress}%</span>
          </div>

          <Progress value={progress} />

          <div className="flex justify-between text-xs text-[#B9B4C7]">
            <span>Elapsed time: {elapsed}s</span>
            <span>Batch OMR mode</span>
          </div>
        </div>

        <div className="grid grid-cols-4 gap-3 pt-3 border-t border-[#B9B4C7]/20">
          {stages.map((stg, idx) => {
            const Icon = stg.icon
            const isActive = idx === currentStep
            const isDone = idx < currentStep

            return (
              <div
                key={stg.label}
                className={`p-4 rounded-xl flex flex-col items-center text-center transition-all ${
                  isActive
                    ? "bg-[#5C5470] border border-[#B9B4C7]/60 text-[#FAF0E6]"
                    : isDone
                    ? "bg-[#5C5470]/30 border border-emerald-500/40 text-emerald-300"
                    : "bg-[#352F44]/40 border border-[#5C5470]/40 text-[#B9B4C7]/50"
                }`}
              >
                <Icon className={`h-6 w-6 mb-2 ${isActive ? "animate-bounce" : ""}`} />
                <span className="text-xs font-medium leading-tight">{stg.label}</span>
              </div>
            )
          })}
        </div>
      </CardContent>

      <CardFooter className="flex justify-between items-center">
        <span className="text-xs text-[#B9B4C7]">
          Please wait while oemer processes stave contours & notes
        </span>
        <Button variant="outline" size="sm" onClick={onCancel}>
          Cancel
        </Button>
      </CardFooter>
    </Card>
  )
}
