import type React from "react"
import { cn } from "@/lib/utils"
import { Scan, ShieldCheck, Zap, Search, Fingerprint, Eye, Activity, Lock } from "lucide-react"

export function FeaturesSectionWithHoverEffects() {
  const features = [
    {
      title: "Pixel Forensic Analysis",
      description: "Deep inspection of frequency domains to detect GAN and diffusion artifacts.",
      icon: <Scan size={24} />,
    },
    {
      title: "Identity Protection",
      description: "Ensure biometric data is authentic and hasn't been tampered with by AI.",
      icon: <ShieldCheck size={24} />,
    },
    {
      title: "Real-time Verification",
      description: "Verify thousands of media files per minute with our distributed edge network.",
      icon: <Zap size={24} />,
    },
    {
      title: "Pattern Recognition",
      description: "Advanced heuristics to identify synthetic textures and lighting anomalies.",
      icon: <Search size={24} />,
    },
    {
      title: "Digital Fingerprinting",
      description: "Unique metadata signatures that persist through compression and resizing.",
      icon: <Fingerprint size={24} />,
    },
    {
      title: "Semantic Consistency",
      description: "AI-driven checks for anatomical correctness and logical object placement.",
      icon: <Eye size={24} />,
    },
    {
      title: "Live Monitoring",
      description: "Continuous oversight of media streams for deepfake intrusion detection.",
      icon: <Activity size={24} />,
    },
    {
      title: "Enterprise Security",
      description: "Role-based access control and high-level encryption for sensitive assets.",
      icon: <Lock size={24} />,
    },
  ]
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 relative z-10 py-10 max-w-7xl mx-auto">
      {features.map((feature, index) => (
        <Feature key={feature.title} {...feature} index={index} />
      ))}
    </div>
  )
}

const Feature = ({
  title,
  description,
  icon,
  index,
}: {
  title: string
  description: string
  icon: React.ReactNode
  index: number
}) => {
  return (
    <div
      className={cn(
        "flex flex-col lg:border-r py-10 relative group/feature dark:border-neutral-800",
        (index === 0 || index === 4) && "lg:border-l dark:border-neutral-800",
        index < 4 && "lg:border-b dark:border-neutral-800",
      )}
    >
      {index < 4 && (
        <div className="opacity-0 group-hover/feature:opacity-100 transition duration-200 absolute inset-0 h-full w-full bg-gradient-to-t from-neutral-100 dark:from-neutral-800 to-transparent pointer-events-none" />
      )}
      {index >= 4 && (
        <div className="opacity-0 group-hover/feature:opacity-100 transition duration-200 absolute inset-0 h-full w-full bg-gradient-to-b from-neutral-100 dark:from-neutral-800 to-transparent pointer-events-none" />
      )}
      <div className="mb-4 relative z-10 px-10 text-neutral-600 dark:text-neutral-400">{icon}</div>
      <div className="text-lg font-bold mb-2 relative z-10 px-10">
        <div className="absolute left-0 inset-y-0 h-6 group-hover/feature:h-8 w-1 rounded-tr-full rounded-br-full bg-neutral-300 dark:bg-neutral-700 group-hover/feature:bg-cyan-500 transition-all duration-200 origin-center" />
        <span className="group-hover/feature:translate-x-2 transition duration-200 inline-block text-neutral-800 dark:text-neutral-100">
          {title}
        </span>
      </div>
      <p className="text-sm text-neutral-600 dark:text-neutral-300 max-w-xs relative z-10 px-10">{description}</p>
    </div>
  )
}
