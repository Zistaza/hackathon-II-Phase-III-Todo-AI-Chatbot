'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { useAuth } from '../../../contexts/auth-context';
import { Card, CardContent, CardHeader, CardTitle } from '../../../components/ui/card';
import { Button } from '../../../components/ui/button';
import { todoService } from '../../../services/todo-service';
import AnimatedButton from '../../../components/ui/animated-button';
import { FiHome } from 'react-icons/fi';

export default function DashboardPage() {
  const { state } = useAuth();
  const [stats, setStats] = useState({
    totalTasks: 0,
    completedTasks: 0,
    pendingTasks: 0,
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchTaskStats = async () => {
      try {
        const tasks = await todoService.getTasks();
        setStats({
          totalTasks: tasks.length,
          completedTasks: tasks.filter(t => t.completed).length,
          pendingTasks: tasks.filter(t => !t.completed).length,
        });
      } catch {
        setStats({ totalTasks: 0, completedTasks: 0, pendingTasks: 0 });
      } finally {
        setLoading(false);
      }
    };

    fetchTaskStats();
  }, []);

  return (
    <section className="min-h-[calc(100vh-4rem)] flex justify-center px-4 sm:px-6 lg:px-8">
      <div className="w-full max-w-6xl py-16 sm:py-20 animate-fade-in">
        {/* Header */}
        <div className="flex flex-col sm:flex-row justify-between items-center gap-6 mb-14 text-center sm:text-left">
          <div>
            <h1 className="text-4xl font-bold text-foreground mb-2">
              Dashboard
            </h1>
            <p className="text-lg text-muted-foreground">
              Welcome back, {state.user?.name}!
            </p>
          </div>

          <Link href="/">
            <AnimatedButton
              variant="outline"
              size="lg"
              className="flex items-center gap-3 px-6 py-3"
            >
              <FiHome className="w-5 h-5" />
              Back to Home
            </AnimatedButton>
          </Link>
        </div>

        {/* Action Cards */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-16 place-items-center">
          <Card className="hover-lift p-8 w-full max-w-xl">
            <CardHeader className="pb-6 text-center">
              <CardTitle className="text-2xl">Manage Your Tasks</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6 text-center">
              <p className="text-lg text-muted-foreground">
                Create, view, and manage your todo items efficiently.
              </p>
              <Link href="/tasks">
                <Button size="lg" className="px-8 py-4 text-lg rounded-lg hover-lift">
                  View Tasks
                </Button>
              </Link>
            </CardContent>
          </Card>

          <Card className="hover-lift p-8 w-full max-w-xl">
            <CardHeader className="pb-6 text-center">
              <CardTitle className="text-2xl">Add New Task</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6 text-center">
              <p className="text-lg text-muted-foreground">
                Get started by creating your first task.
              </p>
              <Link href="/tasks/create">
                <Button size="lg" className="px-8 py-4 text-lg rounded-lg hover-lift">
                  Create Task
                </Button>
              </Link>
            </CardContent>
          </Card>
        </div>

        {/* Stats */}
        <div className="bg-card rounded-2xl border p-10 text-center">
          <h2 className="text-2xl font-bold mb-8">Quick Stats</h2>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 place-items-center">
            {[
              { label: 'Total Tasks', value: stats.totalTasks },
              { label: 'Completed', value: stats.completedTasks },
              { label: 'Pending', value: stats.pendingTasks },
            ].map((item, i) => (
              <div
                key={i}
                className="p-6 bg-secondary rounded-2xl w-full max-w-xs hover-lift"
              >
                <p className="text-5xl font-bold text-primary mb-2">
                  {loading ? <span className="animate-pulse">...</span> : item.value}
                </p>
                <p className="text-lg text-muted-foreground">{item.label}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
