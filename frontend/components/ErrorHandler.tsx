import React from 'react';

interface ErrorHandlerProps {
  errorMessage: string;
  onClose?: () => void;
}

const ErrorHandler: React.FC<ErrorHandlerProps> = ({ errorMessage, onClose }) => {
  return (
    <div className="flex items-start justify-between p-3 bg-destructive/10 border border-destructive/30 rounded-lg">
      <div className="flex-1">
        <p className="text-sm text-destructive font-medium">Error</p>
        <p className="text-sm text-destructive/80 mt-1">{errorMessage}</p>
      </div>
      {onClose && (
        <button
          onClick={onClose}
          className="ml-2 text-destructive/70 hover:text-destructive transition-colors"
          aria-label="Close error"
        >
          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
          </svg>
        </button>
      )}
    </div>
  );
};

export default ErrorHandler;