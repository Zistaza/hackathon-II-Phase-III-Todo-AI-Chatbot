'use client';

import React from 'react';
import { motion } from 'framer-motion';
import FeatureCard from '@/components/ui/feature-card';
import { FiCheckCircle, FiLock, FiCloud, FiZap } from 'react-icons/fi';

const FeaturesSection: React.FC = () => {
  const features = [
    {
      title: 'Task Management',
      description: 'Intuitive interface to create, organize, and track your tasks with due dates and priorities.',
      icon: <FiCheckCircle className="h-8 w-8" aria-hidden="true" />,
    },
    {
      title: 'Secure Login',
      description: 'Enterprise-grade authentication with secure storage of your personal data and privacy protection.',
      icon: <FiLock className="h-8 w-8" aria-hidden="true" />,
    },
    {
      title: 'Cloud Sync',
      description: 'Access your tasks from anywhere, with real-time synchronization across all your devices.',
      icon: <FiCloud className="h-8 w-8" aria-hidden="true" />,
    },
    {
      title: 'Fast & Responsive',
      description: 'Lightning-fast performance with smooth animations and a responsive design that works on all devices.',
      icon: <FiZap className="h-8 w-8" aria-hidden="true" />,
    },
  ];

  return (
    <section className="w-full max-w-6xl relative" aria-labelledby="features-heading">
      {/* Decorative background elements */}
      <div className="absolute inset-0 -z-20">
        <motion.div
          className="absolute -top-40 -left-40 w-80 h-80 rounded-full bg-gradient-to-r from-primary/10 to-secondary/10 blur-3xl"
          animate={{
            scale: [1, 1.3, 1],
            opacity: [0.1, 0.3, 0.1]
          }}
          transition={{
            duration: 8,
            repeat: Infinity,
            ease: "easeInOut"
          }}
        />
        <motion.div
          className="absolute -bottom-40 -right-40 w-80 h-80 rounded-full bg-gradient-to-r from-secondary/10 to-accent/10 blur-3xl"
          animate={{
            scale: [1, 1.4, 1],
            opacity: [0.2, 0.4, 0.2]
          }}
          transition={{
            duration: 9,
            repeat: Infinity,
            ease: "easeInOut",
            delay: 1
          }}
        />
      </div>

      <motion.div
        initial={{ opacity: 0, y: 40 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, margin: "-100px" }}
        transition={{ duration: 0.7 }}
        className="text-center mb-16 relative"
      >
        {/* Title separator */}
        <motion.div
          initial={{ scaleX: 0, opacity: 0 }}
          whileInView={{ scaleX: 1, opacity: 1 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="inline-block mb-6"
        >
          <div className="w-20 h-2 bg-gradient-to-r from-primary to-secondary mx-auto rounded-full"></div>
        </motion.div>

        <motion.h2
          initial={{ opacity: 0, y: 25, filter: "blur(4px)" }}
          whileInView={{ opacity: 1, y: 0, filter: "blur(0px)" }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 0.6, delay: 0.3 }}
          id="features-heading"
          className="text-3xl sm:text-4xl md:text-5xl lg:text-6xl font-bold text-foreground mb-6"
        >
          Powerful Features
        </motion.h2>

        <div className="flex justify-center px-4 pt-24 pb-12 sm:pt-28 sm:pb-16">
  <motion.p
    initial={{ opacity: 0, y: 20 }}
    whileInView={{ opacity: 1, y: 0 }}
    viewport={{ once: true, margin: '-100px' }}
    transition={{ duration: 0.6, delay: 0.4 }}
    className="text-lg sm:text-xl md:text-2xl text-muted-foreground max-w-3xl text-center leading-relaxed"
  >
    Everything you need to stay organized and boost your productivity
  </motion.p>
</div>

      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 50 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, margin: "-100px" }}
        transition={{ duration: 0.7, delay: 0.5 }}
        className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8"
        role="list"
        aria-label="Application features"
      >
        {features.map((feature, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, y: 40 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={{ duration: 0.6, delay: 0.3 * index }}
            whileHover={{ y: -15, scale: 1.02 }}
            className="transform-gpu"
          >
            <FeatureCard
              title={feature.title}
              description={feature.description}
              icon={feature.icon}
              index={index}
            />
          </motion.div>
        ))}
      </motion.div>
    </section>
  );
};

export default FeaturesSection;