"use client"

import React, { useEffect, useState, useRef } from "react"
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/card"
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import {
  Play,
  Pause,
  Volume2,
  VolumeX,
  Download,
  FileMusic,
  Music,
  RotateCcw,
  CheckCircle,
  FileCode,
  Sparkles,
  Info,
  Disc
} from "lucide-react"

interface ResultViewProps {
  jobId: string
  apiUrl: string
  onReset: () => void
}

interface ResultData {
  job_id: string
  filename: string
  audio_url: string
  midi_url: string
  musicxml_url: string
  metadata: {
    title: string
    tempo: number
    time_signature: string
    key_signature: string
    total_measures: number
    staves_detected: number
    duration_seconds: number
  }
}

export function ResultView({ jobId, apiUrl, onReset }: ResultViewProps) {
  const [result, setResult] = useState<ResultData | null>(null)
  const [loading, setLoading] = useState<boolean>(true)
  const [error, setError] = useState<string | null>(null)

  const audioRef = useRef<HTMLAudioElement>(null)
  const [isPlaying, setIsPlaying] = useState<boolean>(false)
  const [currentTime, setCurrentTime] = useState<number>(0)
  const [duration, setDuration] = useState<number>(0)
  const [volume, setVolume] = useState<number>(0.8)
  const [isMuted, setIsMuted] = useState<boolean>(false)

  useEffect(() => {
    const fetchResult = async () => {
      try {
        const res = await fetch(`${apiUrl}/api/result/${jobId}`)
        if (!res.ok) throw new Error("Failed to fetch conversion results.")
        const data = await res.json()
        setResult(data)
      } catch (err: any) {
        setError(err.message || "Could not load conversion result.")
      } finally {
        setLoading(false)
      }
    }
    fetchResult()
  }, [jobId, apiUrl])

  const togglePlay = () => {
    if (!audioRef.current) return
    if (isPlaying) {
      audioRef.current.pause()
    } else {
      audioRef.current.play()
    }
    setIsPlaying(!isPlaying)
  }

  const handleTimeUpdate = () => {
    if (audioRef.current) {
      setCurrentTime(audioRef.current.currentTime)
    }
  }

  const handleLoadedMetadata = () => {
    if (audioRef.current) {
      setDuration(audioRef.current.duration)
    }
  }

  const handleSeek = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newTime = parseFloat(e.target.value)
    if (audioRef.current) {
      audioRef.current.currentTime = newTime
      setCurrentTime(newTime)
    }
  }

  const handleVolumeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newVol = parseFloat(e.target.value)
    setVolume(newVol)
    if (audioRef.current) {
      audioRef.current.volume = newVol
    }
    setIsMuted(newVol === 0)
  }

  const toggleMute = () => {
    if (!audioRef.current) return
    if (isMuted) {
      audioRef.current.volume = volume || 0.8
      setIsMuted(false)
    } else {
      audioRef.current.volume = 0
      setIsMuted(true)
    }
  }

  const formatTime = (secs: number) => {
    if (isNaN(secs)) return "0:00"
    const m = Math.floor(secs / 60)
    const s = Math.floor(secs % 60)
    return `${m}:${s < 10 ? "0" : ""}${s}`
  }

  if (loading) {
    return (
      <Card className="max-w-4xl mx-auto p-12 text-center glass-panel-custom">
        <div className="flex flex-col items-center gap-4">
          <div className="h-12 w-12 animate-spin rounded-full border-4 border-[#B9B4C7] border-t-transparent" />
          <p className="text-[#FAF0E6] font-medium text-lg">Fetching generated audio assets...</p>
        </div>
      </Card>
    )
  }

  if (error || !result) {
    return (
      <Card className="max-w-4xl mx-auto p-8 border-red-800/60 glass-panel-custom">
        <p className="text-red-300 font-medium mb-4">{error || "Failed to load result."}</p>
        <Button onClick={onReset}>Try Again</Button>
      </Card>
    )
  }

  const fullAudioUrl = `${apiUrl}${result.audio_url}`
  const fullMidiUrl = `${apiUrl}${result.midi_url}`
  const fullMusicXmlUrl = `${apiUrl}${result.musicxml_url}`

  return (
    <Card className="max-w-5xl mx-auto shadow-2xl border-[#B9B4C7]/30 glass-panel-custom">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center gap-2.5">
              <Badge variant="success" className="gap-1.5 px-3.5 py-1">
                <CheckCircle className="h-4 w-4" />
                Conversion Successful
              </Badge>
              <span className="text-xs text-[#B9B4C7] font-medium">
                {result.filename}
              </span>
            </div>
            <CardTitle className="text-3xl font-extrabold mt-2 text-[#FAF0E6]">
              {result.metadata.title}
            </CardTitle>
          </div>
          <Button variant="outline" size="sm" onClick={onReset} className="gap-2">
            <RotateCcw className="h-4 w-4" />
            Convert Another
          </Button>
        </div>
      </CardHeader>

      <CardContent>
        <audio
          ref={audioRef}
          src={fullAudioUrl}
          onTimeUpdate={handleTimeUpdate}
          onLoadedMetadata={handleLoadedMetadata}
          onEnded={() => setIsPlaying(false)}
        />

        <Tabs defaultValue="audio" className="w-full">
          <TabsList className="grid grid-cols-3 mb-6">
            <TabsTrigger value="audio" className="gap-2">
              <Music className="h-4 w-4" />
              Audio Player
            </TabsTrigger>
            <TabsTrigger value="sheet" className="gap-2">
              <Info className="h-4 w-4" />
              Score Details
            </TabsTrigger>
            <TabsTrigger value="downloads" className="gap-2">
              <Download className="h-4 w-4" />
              Downloads
            </TabsTrigger>
          </TabsList>

          {/* TAB 1: AUDIO PLAYER */}
          <TabsContent value="audio">
            <div className="p-8 rounded-2xl bg-[#352F44]/90 border border-[#B9B4C7]/30 space-y-6 shadow-inner">
              <div className="flex items-center justify-between">
                <div>
                  <h4 className="text-xl font-bold text-[#FAF0E6] flex items-center gap-2.5">
                    <Disc className={`h-6 w-6 text-[#B9B4C7] ${isPlaying ? "animate-spin" : ""}`} />
                    FluidSynth Multi-Note Piano Render
                  </h4>
                  <p className="text-xs text-[#B9B4C7] mt-1">SoundFont: FluidR3_GM Grand Piano</p>
                </div>
                <div className="flex items-center gap-2 px-4 py-1.5 rounded-full bg-[#5C5470]/60 border border-[#B9B4C7]/30 text-[#FAF0E6] text-xs font-semibold">
                  <span>{result.metadata.tempo} BPM</span> • <span>{result.metadata.time_signature}</span>
                </div>
              </div>

              {/* Animated Waveform Visualization */}
              <div className="flex items-center justify-center gap-1.5 h-12 py-2 bg-[#5C5470]/20 rounded-xl border border-[#B9B4C7]/20 px-4">
                {Array.from({ length: 32 }).map((_, i) => (
                  <span
                    key={i}
                    className={`w-1.5 rounded-full bg-[#B9B4C7] transition-all duration-300 ${
                      isPlaying
                        ? i % 2 === 0
                          ? "animate-wave-1 h-full"
                          : "animate-wave-3 h-3/4"
                        : "h-2 opacity-40"
                    }`}
                  />
                ))}
              </div>

              {/* Player Scrubber */}
              <div className="space-y-2">
                <input
                  type="range"
                  min="0"
                  max={duration || 100}
                  step="0.1"
                  value={currentTime}
                  onChange={handleSeek}
                  className="w-full h-2 bg-[#5C5470]/60 rounded-lg appearance-none cursor-pointer accent-[#FAF0E6]"
                />
                <div className="flex justify-between text-xs font-mono text-[#B9B4C7]">
                  <span>{formatTime(currentTime)}</span>
                  <span>{formatTime(duration)}</span>
                </div>
              </div>

              {/* Controls */}
              <div className="flex items-center justify-between pt-2">
                <div className="flex items-center gap-4">
                  <Button
                    onClick={togglePlay}
                    size="icon"
                    className="h-16 w-16 rounded-full bg-[#5C5470] hover:bg-[#B9B4C7] text-[#FAF0E6] hover:text-[#352F44] shadow-xl border border-[#B9B4C7]/40"
                  >
                    {isPlaying ? <Pause className="h-7 w-7" /> : <Play className="h-7 w-7 ml-1" />}
                  </Button>
                  <div>
                    <p className="text-base font-bold text-[#FAF0E6]">
                      {isPlaying ? "Playing Audio Performance" : "Paused"}
                    </p>
                    <p className="text-xs text-[#B9B4C7]">Polyphonic Piano Arrangement</p>
                  </div>
                </div>

                {/* Volume Slider */}
                <div className="flex items-center gap-3 bg-[#5C5470]/40 px-4 py-2.5 rounded-xl border border-[#B9B4C7]/30">
                  <button onClick={toggleMute} className="text-[#B9B4C7] hover:text-[#FAF0E6]">
                    {isMuted || volume === 0 ? (
                      <VolumeX className="h-5 w-5 text-red-400" />
                    ) : (
                      <Volume2 className="h-5 w-5 text-[#FAF0E6]" />
                    )}
                  </button>
                  <input
                    type="range"
                    min="0"
                    max="1"
                    step="0.05"
                    value={isMuted ? 0 : volume}
                    onChange={handleVolumeChange}
                    className="w-24 h-2 bg-[#352F44] rounded-lg appearance-none cursor-pointer accent-[#FAF0E6]"
                  />
                </div>
              </div>
            </div>
          </TabsContent>

          {/* TAB 2: SCORE DETAILS */}
          <TabsContent value="sheet">
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
              <div className="p-5 rounded-xl bg-[#352F44]/90 border border-[#B9B4C7]/20">
                <span className="text-xs text-[#B9B4C7]">Title</span>
                <p className="font-semibold text-[#FAF0E6] text-base mt-1">{result.metadata.title}</p>
              </div>
              <div className="p-5 rounded-xl bg-[#352F44]/90 border border-[#B9B4C7]/20">
                <span className="text-xs text-[#B9B4C7]">Key Signature</span>
                <p className="font-semibold text-[#FAF0E6] text-base mt-1">{result.metadata.key_signature}</p>
              </div>
              <div className="p-5 rounded-xl bg-[#352F44]/90 border border-[#B9B4C7]/20">
                <span className="text-xs text-[#B9B4C7]">Tempo</span>
                <p className="font-semibold text-[#FAF0E6] text-base mt-1">{result.metadata.tempo} BPM</p>
              </div>
              <div className="p-5 rounded-xl bg-[#352F44]/90 border border-[#B9B4C7]/20">
                <span className="text-xs text-[#B9B4C7]">Time Signature</span>
                <p className="font-semibold text-[#FAF0E6] text-base mt-1">{result.metadata.time_signature}</p>
              </div>
              <div className="p-5 rounded-xl bg-[#352F44]/90 border border-[#B9B4C7]/20">
                <span className="text-xs text-[#B9B4C7]">Detected Measures</span>
                <p className="font-semibold text-[#FAF0E6] text-base mt-1">{result.metadata.total_measures} measures</p>
              </div>
              <div className="p-5 rounded-xl bg-[#352F44]/90 border border-[#B9B4C7]/20">
                <span className="text-xs text-[#B9B4C7]">Staff Layout</span>
                <p className="font-semibold text-[#FAF0E6] text-base mt-1">{result.metadata.staves_detected} staves (Grand Staff)</p>
              </div>
            </div>
          </TabsContent>

          {/* TAB 3: DOWNLOADS */}
          <TabsContent value="downloads">
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-5">
              <a href={fullMidiUrl} download="sheet2sound_output.mid" className="block">
                <div className="p-6 rounded-2xl bg-[#352F44]/90 hover:bg-[#5C5470]/40 border border-[#B9B4C7]/30 hover:border-[#B9B4C7] transition-all text-center group cursor-pointer shadow-lg">
                  <FileMusic className="h-10 w-10 mx-auto text-[#B9B4C7] group-hover:scale-110 transition-transform mb-3" />
                  <p className="font-bold text-[#FAF0E6] text-base">MIDI File (.mid)</p>
                  <p className="text-xs text-[#B9B4C7] mt-1">For DAWs & Synthesizers</p>
                  <Button variant="secondary" size="sm" className="mt-4 w-full gap-2">
                    <Download className="h-4 w-4" /> Download MIDI
                  </Button>
                </div>
              </a>

              <a href={fullAudioUrl} download="sheet2sound_output.wav" className="block">
                <div className="p-6 rounded-2xl bg-[#352F44]/90 hover:bg-[#5C5470]/40 border border-[#B9B4C7]/30 hover:border-[#B9B4C7] transition-all text-center group cursor-pointer shadow-lg">
                  <Music className="h-10 w-10 mx-auto text-[#FAF0E6] group-hover:scale-110 transition-transform mb-3" />
                  <p className="font-bold text-[#FAF0E6] text-base">WAV Audio (.wav)</p>
                  <p className="text-xs text-[#B9B4C7] mt-1">Rendered Piano Sound</p>
                  <Button variant="secondary" size="sm" className="mt-4 w-full gap-2">
                    <Download className="h-4 w-4" /> Download WAV
                  </Button>
                </div>
              </a>

              <a href={fullMusicXmlUrl} download="sheet2sound_output.musicxml" className="block">
                <div className="p-6 rounded-2xl bg-[#352F44]/90 hover:bg-[#5C5470]/40 border border-[#B9B4C7]/30 hover:border-[#B9B4C7] transition-all text-center group cursor-pointer shadow-lg">
                  <FileCode className="h-10 w-10 mx-auto text-[#B9B4C7] group-hover:scale-110 transition-transform mb-3" />
                  <p className="font-bold text-[#FAF0E6] text-base">MusicXML (.xml)</p>
                  <p className="text-xs text-[#B9B4C7] mt-1">For Sibelius / MuseScore</p>
                  <Button variant="secondary" size="sm" className="mt-4 w-full gap-2">
                    <Download className="h-4 w-4" /> Download XML
                  </Button>
                </div>
              </a>
            </div>
          </TabsContent>
        </Tabs>
      </CardContent>

      <CardFooter className="text-xs text-[#B9B4C7] border-t border-[#B9B4C7]/20 pt-4 flex justify-between">
        <span>Job ID: {result.job_id}</span>
        <span>Sheet2Sound Engine by E11even</span>
      </CardFooter>
    </Card>
  )
}
