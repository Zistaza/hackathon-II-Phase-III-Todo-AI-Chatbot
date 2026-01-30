'use client';

import React from 'react';
import { Task } from '../../types';
import { Button } from '../ui/button';
import AnimatedButton from '../ui/animated-button';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { FiEdit2, FiTrash2, FiCheck, FiCalendar } from 'react-icons/fi';

interface TaskItemProps {
  task: Task;
  onToggleCompletion: (id: string) => void;
  onDelete: (id: string) => void;
  onEdit: (id: string) => void;
}

export const TaskItem: React.FC<TaskItemProps> = ({
  task,
  onToggleCompletion,
  onDelete,
  onEdit
}) => {
  const prefersReducedMotion = typeof window !== 'undefined'
    ? window.matchMedia('(prefers-reduced-motion: reduce)').matches
    : false;

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      whileHover={{ scale: 0.98 }}
      whileTap={{ scale: 0.96 }}
      transition={{ duration: 0.3 }}
      className={`group relative rounded-2xl border btn-enhanced ${
        task.completed
          ? 'bg-muted/50 border-primary/30 shadow-sm hover:shadow-md hover:border-primary/40'
          : 'bg-card border-primary/20 shadow-sm hover:shadow-lg hover:border-primary/30'
      }`}
    >
      <div className="p-6">
        <div className="flex items-start justify-between gap-6">
          <div className="flex items-start space-x-6 flex-1 min-w-0">
            <motion.button
              whileTap={!prefersReducedMotion ? { scale: 0.9 } : {}}
              onClick={() => onToggleCompletion(task.id)}
              className={`flex-shrink-0 w-8 h-8 rounded-full border-2 flex items-center justify-center mt-1 transition-all duration-200 ${
                task.completed
                  ? 'bg-primary border-primary text-white'
                  : 'border-input hover:border-primary'
              }`}
              aria-label={task.completed ? 'Mark as incomplete' : 'Mark as complete'}
            >
              {task.completed && (
                <motion.svg
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  exit={{ scale: 0 }}
                  width="16"
                  height="16"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="3"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <polyline points="20 6 9 17 4 12" />
                </motion.svg>
              )}
            </motion.button>

            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-3 mb-2">
                <h3 className={`font-semibold text-lg ${
                  task.completed
                    ? 'line-through text-muted-foreground'
                    : 'text-foreground'
                }`}>
                  {task.title}
                </h3>
                {task.completed && (
                  <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-primary/10 text-primary dark:bg-primary/20 dark:text-primary">
                    <FiCheck className="w-4 h-4 mr-2" />
                    Completed
                  </span>
                )}
              </div>

              {task.description && (
                <p className={`text-base mt-2 break-words ${
                  task.completed
                    ? 'line-through text-muted-foreground'
                    : 'text-muted-foreground'
                }`}>
                  {task.description}
                </p>
              )}

              <div className="flex flex-wrap items-center gap-6 mt-4 text-sm text-muted-foreground">
                <div className="flex items-center gap-2">
                  <FiCalendar className="w-4 h-4" />
                  <span>Created: {new Date(task.created_at).toLocaleDateString()}</span>
                </div>
                {task.completed && (
                  <div className="flex items-center gap-2">
                    <FiCheck className="w-4 h-4" />
                    <span>Completed: {new Date(task.updated_at || task.created_at).toLocaleDateString()}</span>
                  </div>
                )}
              </div>
            </div>
          </div>

          <div className="flex items-center gap-3 ml-6">
            <Link href={`/tasks/${task.id}/edit`}>
              <AnimatedButton
                variant="outline"
                size="md"
                className="h-12 w-12 p-0 hover:bg-primary/10 hover:text-primary dark:hover:bg-primary/10 dark:hover:text-primary rounded-xl"
                aria-label="Edit task"
              >
                <FiEdit2 className="w-6 h-6" />
              </AnimatedButton>
            </Link>
            <AnimatedButton
              variant="outline"
              size="md"
              className="h-12 w-12 p-0 hover:bg-destructive/10 hover:text-destructive border-destructive/20 dark:hover:bg-destructive/10 dark:hover:text-destructive dark:border-destructive/30 rounded-xl"
              onClick={() => onDelete(task.id)}
              aria-label="Delete task"
            >
              <FiTrash2 className="w-6 h-6" />
            </AnimatedButton>
          </div>
        </div>
      </div>

      {/* Progress indicator bar */}
      {!task.completed && (
        <div className="h-1.5 bg-gradient-to-r from-primary/20 to-transparent" />
      )}
    </motion.div>
  );
};