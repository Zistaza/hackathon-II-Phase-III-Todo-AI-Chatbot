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

  const completedCount = state.tasks.filter(task => task.completed).length;
  const totalCount = state.tasks.length;

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="mb-8"
      >
        <div className="flex flex-col md:flex-row md:justify-between md:items-center gap-6 mb-8">
          <div>
            <h1 className="text-4xl font-bold text-primary">
              My Tasks
            </h1>
            <p className="text-muted-foreground mt-2">
              Manage your daily activities efficiently
            </p>
          </div>

          <div className="flex flex-wrap gap-3">
            <Link href="/">
              <AnimatedButton variant="outline" size="md" className="flex items-center gap-2">
                <FiHome className="w-4 h-4" />
                Back to Home
              </AnimatedButton>
            </Link>

            <Link href="/tasks/create">
              <AnimatedButton
                variant="default"
                size="md"
                className="flex items-center gap-2"
              >
                <FiPlus className="w-4 h-4" />
                Create Task
              </AnimatedButton>
            </Link>
          </div>
        </div>

        {/* Filters */}
        <div className="flex items-center gap-2">
          <FiFilter className="text-muted-foreground" />
          <div className="flex bg-muted rounded-lg p-1">
            {(['all', 'active', 'completed'] as const).map(option => (
              <button
                key={option}
                onClick={() => setFilter(option)}
                className={`px-3 py-1 rounded-md text-sm font-medium ${
                  filter === option
                    ? 'bg-background text-primary shadow-sm'
                    : 'text-muted-foreground'
                }`}
              >
                {option}
              </button>
            ))}
          </div>
        </div>
      </motion.div>

      {/* Task List */}
      <Card className="overflow-hidden border-0 shadow-lg">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FiCheckSquare className="text-primary" />
            Your Tasks
          </CardTitle>
        </CardHeader>

        <CardContent>
          <TaskList
            tasks={filteredTasks}
            loading={state.loading}
            onToggleCompletion={toggleTaskCompletion}
            onDelete={deleteTask}
            onEdit={(id) => router.push(`/tasks/${id}/edit`)} // ✅ FIXED
          />

          {state.error && (
            <div className="mt-6 p-4 border border-destructive rounded-lg">
              <p className="text-destructive text-sm">{state.error}</p>
              <AnimatedButton
                variant="outline"
                size="sm"
                className="mt-3"
                onClick={fetchTasks}
              >
                <FiRefreshCw className="w-4 h-4 mr-2" />
                Retry
              </AnimatedButton>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
