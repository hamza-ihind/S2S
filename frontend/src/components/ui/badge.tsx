import * as React from "react"
import { cn } from "@/lib/utils"

export interface BadgeProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: "default" | "secondary" | "destructive" | "outline" | "success"
}

function Badge({ className, variant = "default", ...props }: BadgeProps) {
  const variants = {
    default: "border-transparent bg-[#5C5470]/60 text-[#FAF0E6] border border-[#B9B4C7]/30",
    secondary: "border-transparent bg-[#352F44] text-[#B9B4C7] border border-[#5C5470]/50",
    destructive: "border-transparent bg-red-900/40 text-red-200 border border-red-700/50",
    outline: "text-[#B9B4C7] border border-[#B9B4C7]/40",
    success: "border-transparent bg-emerald-900/40 text-emerald-200 border border-emerald-700/50"
  }

  return (
    <div
      className={cn(
        "inline-flex items-center rounded-full px-3 py-1 text-xs font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-[#B9B4C7]",
        variants[variant],
        className
      )}
      {...props}
    />
  )
}

export { Badge }
