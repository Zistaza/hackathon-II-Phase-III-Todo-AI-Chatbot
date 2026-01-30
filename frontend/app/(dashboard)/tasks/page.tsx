'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { useRouter } from 'next/navigation';

import { useTodo } from '../../../contexts/todo-context';
import { TaskList } from '../../../components/todo/task-list';
import { Card, CardContent, CardHeader, CardTitle } from '../../../components/ui/card';
import AnimatedButton from '../../../components/ui/animated-button';

import {
  FiPlus,
  FiHome,
  FiRefreshCw,
  FiFilter,
  FiCheckSquare,
} from 'react-icons/fi';

export default function TasksPage() {
  const router = useRouter();
  const { state, fetchTasks, deleteTask, toggleTaskCompletion } = useTodo();
  const [filter, setFilter] = useState<'all' | 'active' | 'completed'>('all');

  const filteredTasks = state.tasks.filter(task => {
    if (filter === 'active') return !task.completed;
    if (filter === 'completed') return task.completed;
    return true;
  });

  return (
    <section className="flex justify-center px-4 sm:px-6 lg:px-8 py-12 sm:py-16 lg:py-20">
      <div className="w-full max-w-5xl">

        {/* ===== Header ===== */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="mb-16"
        >
          {/* Title + Subtitle */}
          <div className="text-center lg:text-left mb-8">
            <h1 className="text-4xl sm:text-5xl font-bold text-primary mb-3">
              My Tasks
            </h1>
            <p className="text-muted-foreground text-lg sm:text-xl">
              Manage your daily activities efficiently
            </p>
          </div>

          {/* ===== Action Buttons ===== */}
          <div className="flex flex-col sm:flex-row justify-between items-center mb-8 gap-4">
            {/* Left: Back to Home */}
            <div className="flex justify-center sm:justify-start w-full sm:w-auto">
              <Link href="/">
                <AnimatedButton
                  variant="outline"
                  size="md"
                  className="flex items-center gap-2 px-6 py-3 rounded-xl"
                >
                  <FiHome className="w-4 h-4" />
                  Back to Home
                </AnimatedButton>
              </Link>
            </div>

            {/* Right: Create Task */}
            <div className="flex justify-center sm:justify-end w-full sm:w-auto">
              <Link href="/tasks/create">
                <AnimatedButton
                  variant="primary"
                  size="md"
                  className="flex items-center gap-2 px-6 py-3 rounded-xl"
                >
                  <FiPlus className="w-4 h-4" />
                  Create Task
                </AnimatedButton>
              </Link>
            </div>
          </div>

          {/* ===== Filters ===== */}
          <div className="flex flex-col sm:flex-row sm:items-center gap-6 justify-center lg:justify-start">
            {/* Filter label */}
            <div className="flex items-center gap-3 text-muted-foreground mb-2 sm:mb-0">
              <FiFilter className="w-5 h-5" />
              <span className="text-sm sm:text-base font-medium">Filter</span>
            </div>

            {/* Filter buttons */}
            <div className="flex flex-wrap justify-center sm:justify-start bg-muted rounded-xl p-3 gap-4">
              {(['all', 'active', 'completed'] as const).map(option => (
                <button
                  key={option}
                  onClick={() => setFilter(option)}
                  className={`px-6 py-3 rounded-lg text-sm sm:text-base font-medium transition ${
                    filter === option
                      ? 'bg-background text-primary shadow-sm'
                      : 'text-muted-foreground hover:text-foreground'
                  }`}
                >
                  {option}
                </button>
              ))}
            </div>
          </div>
        </motion.div>

        {/* ===== Task List Card ===== */}
        <Card className="border shadow-lg rounded-2xl mt-12 sm:mt-16">
          <CardHeader className="pt-6 pb-4 sm:pt-8 sm:pb-6">
            <CardTitle className="flex items-center justify-center gap-2 text-xl sm:text-2xl">
              <FiCheckSquare className="text-primary" />
              Your Tasks
            </CardTitle>
          </CardHeader>

          <CardContent className="pt-6 sm:pt-8 pb-8 sm:pb-10">
            <TaskList
              tasks={filteredTasks}
              loading={state.loading}
              onToggleCompletion={toggleTaskCompletion}
              onDelete={deleteTask}
              onEdit={(id) => router.push(`/tasks/${id}/edit`)}
            />

            {state.error && (
              <div className="mt-8 p-5 sm:p-6 border border-destructive rounded-xl">
                <p className="text-destructive text-sm mb-4">{state.error}</p>
                <AnimatedButton
                  variant="outline"
                  size="sm"
                  className="flex items-center gap-2 px-5 py-2.5 rounded-lg"
                  onClick={fetchTasks}
                >
                  <FiRefreshCw className="w-4 h-4" />
                  Retry
                </AnimatedButton>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </section>
  );
}
