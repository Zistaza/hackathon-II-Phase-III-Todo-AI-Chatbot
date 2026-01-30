'use client';

import { motion } from 'framer-motion';
import { useRouter } from 'next/navigation';
import HeroSection from '@/components/home/hero-section';
import FeaturesSection from '@/components/home/features-section';
import AuthSection from '@/components/home/auth-section';
import ThemeToggle from '@/components/ui/theme-toggle';

export default function Home() {
  const router = useRouter();

  return (
    <div className="min-h-screen bg-background text-foreground overflow-hidden">
      {/* Animated background elements */}
      <div className="fixed inset-0 -z-20 overflow-hidden">
        <div className="absolute -top-1/3 left-1/4 w-[1200px] h-[1200px] rounded-full bg-gradient-to-r from-primary/10 to-secondary/10 blur-3xl animate-pulse"></div>
        <div className="absolute top-1/4 right-1/4 w-[1000px] h-[1000px] rounded-full bg-gradient-to-r from-secondary/10 to-accent/10 blur-3xl animate-pulse delay-1000"></div>
        <div className="absolute bottom-1/4 left-1/2 w-[800px] h-[800px] rounded-full bg-gradient-to-r from-accent/10 to-primary/10 blur-3xl animate-pulse delay-2000"></div>
      </div>

      {/* Header with theme toggle */}
      <header className="absolute top-6 right-6 z-20">
        <ThemeToggle />
      </header>

      {/* Main content */}
      <main className="container mx-auto px-4 sm:px-6 lg:px-8 py-16 sm:py-24">
        <div className="flex flex-col items-center justify-center min-h-screen">
          {/* Hero Section */}
          <motion.section
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, ease: "easeOut" }}
            className="w-full max-w-6xl text-center mb-20 sm:mb-28 lg:mb-32"
          >
            <HeroSection />
          </motion.section>

          {/* Features Section */}
          <motion.section
            initial={{ opacity: 0, y: 40 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={{ duration: 0.7, delay: 0.2, ease: "easeOut" }}
            className="w-full max-w-7xl mb-20 sm:mb-28 lg:mb-32"
          >
            <FeaturesSection />
          </motion.section>

          {/* Auth Section */}
          <motion.section
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={{ duration: 0.6, delay: 0.4, ease: "easeOut" }}
            className="w-full max-w-2xl"
          >
            <AuthSection />
          </motion.section>
        </div>
      </main>

      {/* Floating particles for extra animation */}
      {[...Array(12)].map((_, i) => (
        <motion.div
          key={`particle-${i}`}
          className="fixed rounded-full bg-gradient-to-r from-primary/20 to-secondary/20"
          style={{
            width: 8 + (i % 6) * 4,
            height: 8 + (i % 6) * 4,
            top: `${10 + (i * 8)}%`,
            left: `${5 + (i * 12)}%`,
          }}
          animate={{
            y: [0, -40, 0],
            x: [0, 20, 0],
            opacity: [0.1, 0.3, 0.1],
            scale: [1, 1.2, 1],
          }}
          transition={{
            duration: 4 + (i % 3) * 2,
            repeat: Infinity,
            ease: "easeInOut",
            delay: i * 0.3,
          }}
        />
      ))}

      {/* Subtle floating shapes */}
      {[...Array(6)].map((_, i) => (
        <motion.div
          key={`shape-${i}`}
          className="fixed rounded-full border border-primary/20 bg-primary/5"
          style={{
            width: 100 + i * 40,
            height: 100 + i * 40,
            top: `${20 + i * 15}%`,
            left: `${80 - i * 10}%`,
          }}
          animate={{
            y: [-20, 20, -20],
            x: [-10, 10, -10],
            rotate: [0, 180, 360],
          }}
          transition={{
            duration: 8 + i * 2,
            repeat: Infinity,
            ease: "linear",
            delay: i * 0.5,
          }}
        />
      ))}
    </div>
  );
}