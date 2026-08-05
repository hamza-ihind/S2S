import React from "react"
import { Music2, Sparkles, FileMusic, Disc } from "lucide-react"

export function Navbar() {
  return (
    <header className="sticky top-0 z-50 border-b border-[#5C5470]/60 bg-[#352F44]/90 backdrop-blur-xl">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 h-20 flex items-center justify-between">
        {/* Brand & Musical Logo */}
        <div className="flex items-center gap-3.5">
          <div className="h-12 w-12 rounded-2xl bg-gradient-to-tr from-[#5C5470] via-[#352F44] to-[#B9B4C7] flex items-center justify-center shadow-lg shadow-black/40 border border-[#B9B4C7]/30 relative group">
            <Music2 className="h-6 w-6 text-[#FAF0E6] group-hover:rotate-12 transition-transform" />
            <span className="absolute -top-1 -right-1 h-3 w-3 rounded-full bg-[#B9B4C7] animate-ping" />
          </div>
          <div>
            <div className="flex items-center gap-2.5">
              <span className="font-extrabold text-xl tracking-tight text-[#FAF0E6]">
                Sheet2Sound
              </span>
              <span className="text-[10px] uppercase font-bold tracking-widest px-2.5 py-0.5 rounded-full bg-[#5C5470] text-[#FAF0E6] border border-[#B9B4C7]/40 shadow-sm">
                by E11even
              </span>
            </div>
            <p className="text-xs text-[#B9B4C7] font-medium flex items-center gap-1.5 mt-0.5">
              <Disc className="h-3 w-3 animate-spin text-[#B9B4C7]" />
              PDF Sheet Music → Audio Converter
            </p>
          </div>
        </div>

        {/* Musical Visualizer Header Accent */}
        <div className="hidden md:flex items-center gap-6 text-xs text-[#B9B4C7]">
          {/* Animated Waveform Accent */}
          <div className="flex items-end gap-1 h-5 px-3 py-1 rounded-full bg-[#5C5470]/30 border border-[#5C5470]/50">
            <span className="w-1 bg-[#FAF0E6] rounded-full h-full animate-wave-1" />
            <span className="w-1 bg-[#B9B4C7] rounded-full h-full animate-wave-2" />
            <span className="w-1 bg-[#FAF0E6] rounded-full h-full animate-wave-3" />
            <span className="w-1 bg-[#B9B4C7] rounded-full h-full animate-wave-4" />
            <span className="w-1 bg-[#FAF0E6] rounded-full h-full animate-wave-5" />
            <span className="text-[11px] font-medium text-[#FAF0E6] ml-2">oemer OMR + FluidSynth</span>
          </div>

          <div className="flex items-center gap-2 px-4 py-2 rounded-xl bg-[#5C5470]/40 border border-[#B9B4C7]/30 text-[#FAF0E6]">
            <Sparkles className="h-4 w-4 text-[#B9B4C7]" />
            <span className="font-semibold text-xs">Capriola Theme</span>
          </div>
        </div>
      </div>
    </header>
  )
}
