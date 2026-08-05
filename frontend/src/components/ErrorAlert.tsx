"use client"

import React from "react"
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from "@/components/ui/card"
import { Alert, AlertTitle, AlertDescription } from "@/components/ui/alert"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { AlertTriangle, RotateCcw, HelpCircle } from "lucide-react"

interface ErrorAlertProps {
  errorMsg: string
  stage: string
  onReset: () => void
}

export function ErrorAlert({ errorMsg, stage, onReset }: ErrorAlertProps) {
  const isOmrError = stage.toLowerCase().includes("omr") || errorMsg.toLowerCase().includes("omr")

  return (
    <Card className="max-w-4xl mx-auto shadow-2xl border-red-800/60 glass-panel-custom">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <AlertTriangle className="h-7 w-7 text-red-400" />
            <CardTitle className="text-2xl font-bold text-red-200">
              Pipeline Execution Failed
            </CardTitle>
          </div>
          <Badge variant="destructive" className="px-4 py-1.5">
            {isOmrError ? "Stage 1: OMR Error" : "Stage 2: Synthesis Error"}
          </Badge>
        </div>
      </CardHeader>

      <CardContent className="space-y-5">
        <Alert variant="destructive">
          <div>
            <AlertTitle className="font-semibold text-base mb-1">
              Failed Stage: {stage}
            </AlertTitle>
            <AlertDescription className="text-sm font-mono bg-red-950/80 p-4 rounded-lg border border-red-800/60 mt-2 text-red-200">
              {errorMsg}
            </AlertDescription>
          </div>
        </Alert>

        <div className="p-5 rounded-xl bg-[#352F44] border border-[#B9B4C7]/20 space-y-2 text-xs text-[#B9B4C7]">
          <p className="font-semibold text-[#FAF0E6] flex items-center gap-2 text-sm">
            <HelpCircle className="h-4 w-4 text-[#B9B4C7]" />
            Troubleshooting Suggestions:
          </p>
          <ul className="list-disc list-inside space-y-1 pl-1 text-[#B9B4C7]">
            {isOmrError ? (
              <>
                <li>Ensure score pages are clear, high-resolution digital typesets (not handwritten).</li>
                <li>Check that stave lines are horizontal and uncropped.</li>
                <li>Avoid scanned sheets with heavy shadows or bleed-through.</li>
              </>
            ) : (
              <>
                <li>Check that standard General MIDI piano instrument channels are valid.</li>
                <li>Verify measure durations and time signatures in the input score.</li>
                <li>Ensure FluidSynth engine soundfont binaries are loaded properly.</li>
              </>
            )}
          </ul>
        </div>
      </CardContent>

      <CardFooter className="flex justify-between items-center border-t border-[#B9B4C7]/20 pt-4">
        <span className="text-xs text-[#B9B4C7]">
          Error logged in Sheet2Sound backend telemetry
        </span>
        <Button onClick={onReset} className="gap-2">
          <RotateCcw className="h-4 w-4" />
          Try Another Score
        </Button>
      </CardFooter>
    </Card>
  )
}
