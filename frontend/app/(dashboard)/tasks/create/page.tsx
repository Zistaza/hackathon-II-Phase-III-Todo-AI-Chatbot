'use client';

import React from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useTodo } from '../../../../contexts/todo-context';
import { TaskForm } from '../../../../components/todo/task-form';
import { Card, CardContent, CardHeader, CardTitle } from '../../../../components/ui/card';
import { Button } from '../../../../components/ui/button';

// TaskCreate type (description is optional)
type TaskCreate = {
  title: string;
  description?: string | null;
};

export default function CreateTaskPage() {
  const router = useRouter();
  const { createTask } = useTodo();

  // handleSubmit now matches TaskForm exactly
  const handleSubmit = async (taskData: TaskCreate) => {
    try {
      // Normalize undefined description to null
      const normalizedData: TaskCreate = {
        ...taskData,
        description: taskData.description ?? null,
      };

      await createTask(normalizedData);
      router.push('/tasks');
      router.refresh();
    } catch (error) {
      console.error('Failed to create task:', error);
    }
  };

  return (
    <div className="max-w-2xl mx-auto">
      <div className="mb-6">
        <Link href="/tasks">
          <Button className="rounded-lg hover-lift">← Back to Tasks</Button>
        </Link>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Create New Task</CardTitle>
        </CardHeader>
        <CardContent>
          <TaskForm
            onSubmit={handleSubmit}
            onCancel={() => router.push('/tasks')}
            submitButtonText="Create Task"
          />
        </CardContent>
      </Card>
    </div>
  );
}
