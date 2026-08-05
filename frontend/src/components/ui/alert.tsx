import * as React from "react"
import { cn } from "@/lib/utils"

const Alert = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement> & { variant?: "default" | "destructive" | "success" | "warning" }
>(({ className, variant = "default", ...props }, ref) => {
  const variantStyles = {
    default: "bg-zinc-900/90 text-zinc-200 border-zinc-700",
    destructive: "bg-red-950/40 text-red-200 border-red-800/60 shadow-lg shadow-red-950/30",
    warning: "bg-amber-950/40 text-amber-200 border-amber-800/60 shadow-lg shadow-amber-950/30",
    success: "bg-emerald-950/40 text-emerald-200 border-emerald-800/60 shadow-lg shadow-emerald-950/30"
  }

  return (
    <div
      ref={ref}
      role="alert"
      className={cn(
        "relative w-full rounded-xl border p-4 backdrop-blur-md transition-all flex gap-3 items-start",
        variantStyles[variant],
        className
      )}
      {...props}
    />
  )
})
Alert.displayName = "Alert"

const AlertTitle = React.forwardRef<
  HTMLParagraphElement,
  React.HTMLAttributes<HTMLHeadingElement>
>(({ className, ...props }, ref) => (
  <h5
    ref={ref}
    className={cn("mb-1 font-semibold leading-none tracking-tight text-base", className)}
    {...props}
  />
))
AlertTitle.displayName = "AlertTitle"

const AlertDescription = React.forwardRef<
  HTMLParagraphElement,
  React.HTMLAttributes<HTMLParagraphElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("text-sm opacity-90 leading-relaxed", className)}
    {...props}
  />
))
AlertDescription.displayName = "AlertDescription"

export { Alert, AlertTitle, AlertDescription }
