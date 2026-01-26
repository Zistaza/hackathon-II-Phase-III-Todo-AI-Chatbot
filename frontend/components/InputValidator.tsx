import React, { useState } from 'react';
import ValidationService from '../services/validationService';

interface InputValidatorProps {
  value: string;
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  onSubmit: (e: React.FormEvent) => void;
  disabled: boolean;
  placeholder?: string;
}

const InputValidator: React.FC<InputValidatorProps> = ({
  value,
  onChange,
  onSubmit,
  disabled,
  placeholder = 'Type your message...'
}) => {
  const [error, setError] = useState<string | null>(null);
  const validationService = new ValidationService();

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value;

    // Validate the input
    const validationResult = validationService.validateMessage(newValue);

    if (!validationResult.isValid) {
      setError(validationResult.errors[0] || 'Invalid input');
    } else {
      setError(null);
    }

    onChange(e);
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (!disabled && !error && value.trim()) {
        onSubmit(e as any); // Type assertion since React.FormEvent and KeyboardEvent are compatible here
      }
    }
  };

  return (
    <div className="flex-1 relative">
      <input
        type="text"
        value={value}
        onChange={handleInputChange}
        onKeyDown={handleKeyPress}
        placeholder={placeholder}
        disabled={disabled}
        className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary ${
          error
            ? 'border-destructive focus:ring-destructive/30'
            : 'border-input focus:ring-primary/30'
        } ${disabled ? 'opacity-50 cursor-not-allowed' : ''}`}
      />
      {error && (
        <p className="text-xs text-destructive mt-1 absolute left-0">{error}</p>
      )}
    </div>
  );
};

export default InputValidator;