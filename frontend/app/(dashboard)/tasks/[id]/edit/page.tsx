'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { useParams, useRouter } from 'next/navigation';
import { Task, TaskUpdate } from '../../../../../types';
import { todoService } from '../../../../../services/todo-service';
import { TaskForm } from '../../../../../components/todo/task-form';
import { Card, CardContent, CardHeader, CardTitle } from '../../../../../components/ui/card';
import { Button } from '../../../../../components/ui/button';

export default function EditTaskPage() {
  const params = useParams();
  const router = useRouter();
  const taskId = params.id as string;

  const [task, setTask] = useState<Task | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchTask = async () => {
      try {
        setLoading(true);
        const data = await todoService.getTaskById(taskId);
        setTask(data);
      } catch (err: any) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchTask();
  }, [taskId]);

  const handleSubmit = async (taskData: TaskUpdate) => {
    try {
      await todoService.updateTask(taskId, taskData);
      router.push(`/tasks/${taskId}`);
      router.refresh();
    } catch (err: any) {
      setError(err.message);
    }
  };

  if (loading) {
    return (
      <div className="max-w-2xl mx-auto flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-2xl mx-auto">
        <div className="mb-6">
          <Link href={`/tasks/${taskId}`} className="text-primary hover:underline">
            ← Back to Task
          </Link>
        </div>
        <div className="p-4 bg-destructive/10 border border-destructive/20 rounded-md">
          <p className="text-destructive">{error}</p>
          <Button
            variant="secondary"
            size="sm"
            className="mt-2 rounded-lg hover-lift"
            onClick={() => router.back()}
          >
            Go Back
          </Button>
        </div>
      </div>
    );
  }

  if (!task) {
    return (
      <div className="max-w-2xl mx-auto">
        <div className="mb-6">
          <Link href="/tasks" className="text-primary hover:underline">
            ← Back to Tasks
          </Link>
        </div>
        <div className="text-center py-12">
          <p className="text-muted-foreground">Task not found</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto">
      <div className="mb-6">
        <Link href={`/tasks/${taskId}`} className="text-primary hover:underline">
          ← Back to Task
        </Link>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Edit Task</CardTitle>
        </CardHeader>
        <CardContent>
          <TaskForm
            onSubmit={handleSubmit}
            onCancel={() => router.push(`/tasks/${taskId}`)}
            initialData={{
              title: task.title,
              description: task.description || undefined,
              completed: task.completed
            }}
            submitButtonText="Update Task"
          />

          {error && (
            <div className="mt-4 p-4 bg-destructive/10 border border-destructive/20 rounded-md">
              <p className="text-destructive">{error}</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}