'use client';

import React from 'react';
import { motion } from 'framer-motion';

interface FeatureCardProps {
  title: string;
  description: string;
  icon?: React.ReactNode;
  index?: number;
}

const FeatureCard: React.FC<FeatureCardProps> = ({
  title,
  description,
  icon,
  index = 0
}) => {
  const prefersReducedMotion = typeof window !== 'undefined'
    ? window.matchMedia('(prefers-reduced-motion: reduce)').matches
    : false;

  return (
    <motion.div
      whileHover={!prefersReducedMotion ? { y: -10, scale: 1.03 } : {}}
      initial={{ opacity: 0, y: 30, filter: "blur(4px)" }}
      animate={{ opacity: 1, y: 0, filter: "blur(0px)" }}
      transition={{ duration: 0.6, delay: index * 0.15 }}
      className="bg-card border border-border rounded-2xl p-8 shadow-lg hover:shadow-xl transition-all duration-500 cursor-pointer group overflow-hidden relative"
    >
      {/* Gradient overlay */}
      <div className="absolute inset-0 bg-gradient-to-br from-primary/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>

      <div className="relative z-10 flex flex-col items-center text-center">
        <motion.div
          className="mb-6 p-4 bg-primary/10 rounded-2xl group-hover:bg-primary/20 transition-colors duration-300"
          whileHover={!prefersReducedMotion ? { scale: 1.1 } : {}}
        >
          {icon && <div className="text-primary group-hover:text-primary/90 transition-colors duration-300">{icon}</div>}
        </motion.div>

        <motion.h3
          className="text-xl sm:text-2xl font-bold mb-3 text-foreground group-hover:text-primary transition-colors duration-300"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: (index * 0.15) + 0.2 }}
        >
          {title}
        </motion.h3>

        <motion.p
          className="text-muted-foreground text-sm sm:text-base group-hover:text-foreground transition-colors duration-300"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: (index * 0.15) + 0.3 }}
        >
          {description}
        </motion.p>
      </div>
    </motion.div>
  );
};

export default FeatureCard;