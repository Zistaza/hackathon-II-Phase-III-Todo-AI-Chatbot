'use client';

import React, { useState } from 'react';
import { TaskCreate } from '../../types';
import { Input } from '../ui/input';
import { Button } from '../ui/button';

interface TaskFormProps {
  onSubmit: (taskData: TaskCreate) => void;
  onCancel?: () => void;
  initialData?: Partial<TaskCreate>;
  submitButtonText?: string;
}

export const TaskForm: React.FC<TaskFormProps> = ({
  onSubmit,
  onCancel,
  initialData = {},
  submitButtonText = 'Create Task',
}) => {
  const [title, setTitle] = useState(initialData.title || '');
  const [description, setDescription] = useState(initialData.description || '');
  const [error, setError] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (!title.trim()) {
      setError('Title is required');
      return;
    }

    if (title.length > 255) {
      setError('Title must be less than 255 characters');
      return;
    }

    setError('');
    onSubmit({
      title: title.trim(),
      description: description || null,
      completed: initialData.completed || false,
    });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && <div className="text-destructive text-sm">{error}</div>}

      {/* Title input */}
      <Input
        label="Title"
        id="title"
        type="text"
        placeholder="Enter task title"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        required
      />

      {/* Description textarea */}
      <Input
        label="Description"
        id="description"
        placeholder="Enter task description (optional)"
        value={description}
        onChange={(e) => setDescription(e.target.value)}
        as="textarea"
        rows={3}
      />

      <div className="flex space-x-2">
        <Button type="submit">{submitButtonText}</Button>
        {onCancel && (
          <Button type="button" variant="secondary" onClick={onCancel}>
            Cancel
          </Button>
        )}
      </div>
    </form>
  );
};
