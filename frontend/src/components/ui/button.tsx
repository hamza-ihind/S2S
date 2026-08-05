import * as React from "react"
import { cn } from "@/lib/utils"

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "default" | "destructive" | "outline" | "secondary" | "ghost" | "link"
  size?: "default" | "sm" | "lg" | "icon"
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = "default", size = "default", children, disabled, ...props }, ref) => {
    const baseStyles = "inline-flex items-center justify-center rounded-xl font-medium transition-all duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#B9B4C7] disabled:pointer-events-none disabled:opacity-50 active:scale-[0.98]"
    
    const variants = {
      default: "bg-[#5C5470] text-[#FAF0E6] hover:bg-[#B9B4C7] hover:text-[#352F44] shadow-lg border border-[#B9B4C7]/30",
      destructive: "bg-red-800 text-[#FAF0E6] hover:bg-red-700 shadow-md border border-red-500/30",
      outline: "border border-[#B9B4C7]/40 bg-[#352F44]/80 text-[#FAF0E6] hover:bg-[#5C5470] hover:border-[#B9B4C7]",
      secondary: "bg-[#5C5470]/60 text-[#FAF0E6] hover:bg-[#5C5470] border border-[#B9B4C7]/20",
      ghost: "hover:bg-[#5C5470]/40 text-[#B9B4C7] hover:text-[#FAF0E6]",
      link: "text-[#B9B4C7] underline-offset-4 hover:underline p-0 h-auto"
    }

    const sizes = {
      default: "h-11 px-6 py-2 text-sm",
      sm: "h-9 rounded-lg px-4 text-xs",
      lg: "h-12 rounded-xl px-8 text-base",
      icon: "h-10 w-10 p-0 rounded-xl"
    }

    return (
      <button
        className={cn(baseStyles, variants[variant], sizes[size], className)}
        ref={ref}
        disabled={disabled}
        {...props}
      >
        {children}
      </button>
    )
  }
)
Button.displayName = "Button"

export { Button }
