'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { useRouter } from 'next/navigation';
import AnimatedButton from '@/components/ui/animated-button';

const AuthSection: React.FC = () => {
  const router = useRouter();

  return (
    <section className="w-full max-w-lg relative" aria-labelledby="auth-section-heading">
      <h2 id="auth-section-heading" className="sr-only">Authentication Options</h2>

      <motion.div
        initial={{ opacity: 0, y: 30 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, margin: "-100px" }}
        transition={{ duration: 0.7, delay: 0.2 }}
        className="flex flex-col sm:flex-row gap-6 justify-center items-center px-4"
        role="group"
        aria-labelledby="auth-section-heading"
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
            className="w-full sm:w-auto px-10 py-5 text-lg font-semibold rounded-xl min-w-[200px]"
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
            className="w-full sm:w-auto px-10 py-5 text-lg font-semibold rounded-xl min-w-[200px]"
            aria-label="Sign in to your account"
          >
            Sign In
          </AnimatedButton>
        </motion.div>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, margin: "-100px" }}
        transition={{ duration: 0.6, delay: 0.4 }}
        className="mt-10 text-center"
      >
        <p className="text-base sm:text-lg text-muted-foreground" id="auth-description">
          Join thousands of productive users managing their tasks efficiently
        </p>
      </motion.div>

      {/* Decorative elements */}
      <motion.div
        className="absolute -top-20 -left-20 w-40 h-40 rounded-full bg-gradient-to-r from-primary/10 to-secondary/10 blur-2xl"
        animate={{
          scale: [1, 1.2, 1],
          opacity: [0.1, 0.3, 0.1]
        }}
        transition={{
          duration: 6,
          repeat: Infinity,
          ease: "easeInOut"
        }}
      />
    </section>
  );
};

export default AuthSection;