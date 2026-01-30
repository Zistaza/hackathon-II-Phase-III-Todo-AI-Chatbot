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
      <div className="fixed inset-0 -z-10 overflow-hidden">
        <div className="absolute -top-1/2 left-1/4 w-[1000px] h-[1000px] rounded-full bg-primary/5 blur-3xl animate-pulse"></div>
        <div className="absolute top-1/3 right-1/4 w-[800px] h-[800px] rounded-full bg-secondary/5 blur-3xl animate-pulse delay-1000"></div>
      </div>

      {/* Header with theme toggle */}
      <header className="absolute top-6 right-6 z-10">
        <ThemeToggle />
      </header>

      {/* Main content */}
      <main className="container mx-auto px-6 py-12">
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.8 }}
          className="min-h-screen flex flex-col items-center justify-center pt-20 pb-12"
        >
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="w-full max-w-5xl"
          >
            <HeroSection />
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={{ duration: 0.6, delay: 0.4 }}
            className="w-full max-w-6xl my-20"
          >
            <FeaturesSection />
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={{ duration: 0.5, delay: 0.6 }}
            className="w-full max-w-lg mt-8"
          >
            <AuthSection />
          </motion.div>
        </motion.div>
      </main>

      {/* Floating particles for extra animation */}
      {[...Array(8)].map((_, i) => (
        <motion.div
          key={i}
          className="fixed rounded-full bg-primary/10"
          style={{
            width: 10 + (i * 4),
            height: 10 + (i * 4),
            top: `${15 + (i * 12)}%`,
            left: `${10 + (i * 15)}%`,
          }}
          animate={{
            y: [0, -30, 0],
            x: [0, 15, 0],
            opacity: [0.2, 0.4, 0.2],
          }}
          transition={{
            duration: 3 + (i * 0.5),
            repeat: Infinity,
            ease: "easeInOut",
            delay: i * 0.4,
          }}
        />
      ))}
    </div>
  );
}