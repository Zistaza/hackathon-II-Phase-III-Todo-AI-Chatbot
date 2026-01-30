'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { useRouter } from 'next/navigation';
import AnimatedButton from '@/components/ui/animated-button';

const HeroSection: React.FC = () => {
  const router = useRouter();

  return (
    <section className="w-full max-w-5xl text-center" aria-labelledby="hero-title">
      <motion.header
        initial={{ opacity: 0, y: 40 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, delay: 0.2 }}
        className="relative mb-12"
      >
        {/* Animated decorative elements */}
        <motion.div
          className="absolute -left-20 -top-20 w-40 h-40 rounded-full bg-primary/10 blur-2xl"
          animate={{
            scale: [1, 1.5, 1],
            opacity: [0.2, 0.4, 0.2]
          }}
          transition={{
            duration: 6,
            repeat: Infinity,
            ease: "easeInOut"
          }}
        />

        <motion.div
          className="absolute -right-20 -bottom-20 w-32 h-32 rounded-full bg-secondary/10 blur-2xl"
          animate={{
            scale: [1, 1.4, 1],
            opacity: [0.3, 0.5, 0.3]
          }}
          transition={{
            duration: 7,
            repeat: Infinity,
            ease: "easeInOut",
            delay: 1
          }}
        />

        {/* Title separator */}
        <motion.div
          initial={{ scaleX: 0, opacity: 0 }}
          animate={{ scaleX: 1, opacity: 1 }}
          transition={{ duration: 0.8, delay: 0.3 }}
          className="inline-block mb-8"
        >
          <div className="w-32 h-1.5 bg-gradient-to-r from-primary to-secondary mx-auto rounded-full"></div>
        </motion.div>

        {/* Main headline */}
        <div className="mb-8">
          <h1
            id="hero-title"
            className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl xl:text-8xl font-bold mb-6 leading-tight"
          >
            <motion.span
              initial={{ opacity: 0, y: 30, filter: "blur(4px)" }}
              animate={{ opacity: 1, y: 0, filter: "blur(0px)" }}
              transition={{ duration: 0.8, delay: 0.4 }}
              className="bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent inline-block font-extrabold"
            >
              STREAMLINE
            </motion.span>
            <br />
            <motion.span
              initial={{ opacity: 0, y: 30, filter: "blur(4px)" }}
              animate={{ opacity: 1, y: 0, filter: "blur(0px)" }}
              transition={{ duration: 0.8, delay: 0.6 }}
              className="text-3xl sm:text-4xl md:text-5xl lg:text-6xl xl:text-7xl bg-gradient-to-r from-secondary to-accent bg-clip-text text-blue inline-block mt-2 font-extrabold"
            >
              YOUR TASKS
            </motion.span>
          </h1>
        </div>

        {/* Subtitle */}
        <div className="flex justify-center px-4 pt-24 pb-12 sm:pt-28 sm:pb-16">
  <motion.p
    className="text-lg sm:text-xl md:text-2xl text-muted-foreground max-w-3xl text-center"
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ duration: 0.6, delay: 0.8 }}
  >
    A powerful, intuitive todo application designed to boost your productivity and help you achieve your goals.
  </motion.p>
</div>

        {/* Call to action buttons */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 1.0 }}
          className="flex flex-col sm:flex-row gap-6 justify-center items-center px-4"
          role="group"
          aria-label="Authentication options"
        >
          <motion.div
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="w-full sm:w-auto"
          >
            <AnimatedButton
              variant="primary"
              size="lg"
              onClick={() => router.push('/register')}
              className="px-10 py-5 text-lg font-semibold rounded-xl min-w-[200px]"
              aria-label="Get started with registration"
            >
              Get Started
            </AnimatedButton>
          </motion.div>

          <motion.div
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="w-full sm:w-auto"
          >
            <AnimatedButton
              variant="secondary"
              size="lg"
              onClick={() => router.push('/login')}
              className="px-10 py-5 text-lg font-semibold rounded-xl min-w-[200px]"
              aria-label="Sign in to your account"
            >
              Sign In
            </AnimatedButton>
          </motion.div>
        </motion.div>
      </motion.header>

      {/* Animated floating elements */}
      <div className="relative mt-16">
        {[...Array(6)].map((_, i) => (
          <motion.div
            key={`floating-${i}`}
            className="absolute hidden lg:block"
            style={{
              left: `${(i * 20) + 10}%`,
              top: `${(i * 15) + 10}%`,
            }}
            animate={{
              y: [0, -40, 0],
              x: [0, 25, 0],
              rotate: [0, 15, 0, -15, 0],
              scale: [1, 1.2, 1],
            }}
            transition={{
              duration: 4 + i,
              repeat: Infinity,
              ease: "easeInOut",
              delay: i * 0.3,
            }}
          >
            <div className="w-3 h-3 rounded-full bg-gradient-to-r from-primary/40 to-secondary/40"></div>
          </motion.div>
        ))}
      </div>
    </section>
  );
};

export default HeroSection;