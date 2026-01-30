'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { useAuth } from '../../../contexts/auth-context';
import { Card, CardContent, CardHeader, CardTitle } from '../../../components/ui/card';
import { Button } from '../../../components/ui/button';
import { todoService } from '../../../services/todo-service';
import { Task } from '../../../types';
import AnimatedButton from '../../../components/ui/animated-button';

import {FiHome} from 'react-icons/fi';


export default function DashboardPage() {
  const { state } = useAuth();
  const [stats, setStats] = useState({
    totalTasks: 0,
    completedTasks: 0,
    pendingTasks: 0
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchTaskStats = async () => {
      try {
        const tasks = await todoService.getTasks();

        const totalTasks = tasks.length;
        const completedTasks = tasks.filter(task => task.completed).length;
        const pendingTasks = tasks.filter(task => !task.completed).length;

        setStats({
          totalTasks,
          completedTasks,
          pendingTasks
        });
      } catch (error) {
        console.error('Failed to fetch task stats:', error);
        // Set to 0 in case of error
        setStats({
          totalTasks: 0,
          completedTasks: 0,
          pendingTasks: 0
        });
      } finally {
        setLoading(false);
      }
    };

    fetchTaskStats();
  }, []);

  return (
    <div className="max-w-6xl mx-auto animate-fade-in py-8">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-6 mb-12">
        <div>
          <h1 className="text-4xl font-bold text-foreground mb-2">Dashboard</h1>
          <p className="text-lg text-muted-foreground">Welcome back, {state.user?.name}!</p>
        </div>
        <Link href="/">
          <AnimatedButton variant="outline" size="lg" className="flex items-center gap-3 hover-lift px-6 py-3">
            <FiHome className="w-5 h-5" />
            Back to Home
          </AnimatedButton>
        </Link>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-12 animate-slide-in-up">
        <Card className="hover-lift p-8">
          <CardHeader className="pb-6">
            <CardTitle className="text-2xl">Manage Your Tasks</CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <p className="text-lg text-muted-foreground">Create, view, and manage your todo items efficiently.</p>
            <Link href="/tasks">
              <Button size="lg" className="hover-lift px-8 py-4 text-lg">View Tasks</Button>
            </Link>
          </CardContent>
        </Card>

        <Card className="hover-lift p-8">
          <CardHeader className="pb-6">
            <CardTitle className="text-2xl">Add New Task</CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <p className="text-lg text-muted-foreground">Get started by creating your first task.</p>
            <Link href="/tasks/create">
              <Button size="lg" className="hover-lift px-8 py-4 text-lg">Create Task</Button>
            </Link>
          </CardContent>
        </Card>
      </div>

      <div className="bg-card rounded-2xl border p-8 btn-enhanced">
        <h2 className="text-2xl font-bold mb-6 text-foreground">Quick Stats</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="text-center p-6 bg-secondary rounded-2xl hover-lift transition-all">
            <p className="text-5xl font-bold text-primary mb-2">
              {loading ? <span className="animate-pulse">...</span> : stats.totalTasks}
            </p>
            <p className="text-lg text-muted-foreground">Total Tasks</p>
          </div>
          <div className="text-center p-6 bg-secondary rounded-2xl hover-lift transition-all">
            <p className="text-5xl font-bold text-primary mb-2">
              {loading ? <span className="animate-pulse">...</span> : stats.completedTasks}
            </p>
            <p className="text-lg text-muted-foreground">Completed</p>
          </div>
          <div className="text-center p-6 bg-secondary rounded-2xl hover-lift transition-all">
            <p className="text-5xl font-bold text-foreground mb-2">
              {loading ? <span className="animate-pulse">...</span> : stats.pendingTasks}
            </p>
            <p className="text-lg text-muted-foreground">Pending</p>
          </div>
        </div>
      </div>
    </div>
  );
}