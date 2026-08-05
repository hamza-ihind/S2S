import * as React from "react"
import { cn } from "@/lib/utils"

interface TabsContextValue {
  activeTab: string
  setActiveTab: (value: string) => void
}

const TabsContext = React.createContext<TabsContextValue | undefined>(undefined)

export function Tabs({
  defaultValue,
  value,
  onValueChange,
  children,
  className
}: {
  defaultValue?: string
  value?: string
  onValueChange?: (val: string) => void
  children: React.ReactNode
  className?: string
}) {
  const [currentTab, setCurrentTab] = React.useState(defaultValue || "")
  const activeTab = value !== undefined ? value : currentTab

  const setActiveTab = (val: string) => {
    if (value === undefined) {
      setCurrentTab(val)
    }
    onValueChange?.(val)
  }

  return (
    <TabsContext.Provider value={{ activeTab, setActiveTab }}>
      <div className={cn("w-full", className)}>{children}</div>
    </TabsContext.Provider>
  )
}

export function TabsList({ className, children }: { className?: string; children: React.ReactNode }) {
  return (
    <div
      className={cn(
        "inline-flex h-13 items-center justify-center rounded-xl bg-[#5C5470]/30 p-1.5 text-[#B9B4C7] border border-[#B9B4C7]/20 backdrop-blur-md w-full sm:w-auto",
        className
      )}
    >
      {children}
    </div>
  )
}

export function TabsTrigger({
  value,
  children,
  className
}: {
  value: string
  children: React.ReactNode
  className?: string
}) {
  const context = React.useContext(TabsContext)
  if (!context) throw new Error("TabsTrigger must be used within Tabs")

  const isActive = context.activeTab === value

  return (
    <button
      onClick={() => context.setActiveTab(value)}
      className={cn(
        "inline-flex flex-1 sm:flex-initial items-center justify-center whitespace-nowrap rounded-lg px-5 py-2.5 text-sm font-medium transition-all duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#B9B4C7]",
        isActive
          ? "bg-[#5C5470] text-[#FAF0E6] shadow-md border border-[#B9B4C7]/40 font-semibold"
          : "text-[#B9B4C7] hover:text-[#FAF0E6] hover:bg-[#5C5470]/20",
        className
      )}
    >
      {children}
    </button>
  )
}

export function TabsContent({
  value,
  children,
  className
}: {
  value: string
  children: React.ReactNode
  className?: string
}) {
  const context = React.useContext(TabsContext)
  if (!context) throw new Error("TabsContent must be used within Tabs")

  if (context.activeTab !== value) return null

  return (
    <div className={cn("mt-4 animate-in fade-in-50 duration-200", className)}>
      {children}
    </div>
  )
}
