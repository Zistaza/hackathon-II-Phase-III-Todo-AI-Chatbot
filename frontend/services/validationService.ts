// Define types for validation
interface ValidationResult {
  isValid: boolean;
  errors: string[];
  warnings: string[];
  sanitizedValue: string;
}

interface ValidationRules {
  maxLength?: number;
  minLength?: number;
  required?: boolean;
  pattern?: RegExp;
  customValidator?: (value: string) => boolean;
}

class ValidationService {
  // Validate a string value against provided rules
  validate(value: string, rules: ValidationRules = {}): ValidationResult {
    const result: ValidationResult = {
      isValid: true,
      errors: [],
      warnings: [],
      sanitizedValue: this.sanitizeInput(value),
    };

    // Check required
    if (rules.required && !value) {
      result.errors.push('This field is required');
      result.isValid = false;
    }

    // Check min length
    if (rules.minLength && value.length < rules.minLength) {
      result.errors.push(`Must be at least ${rules.minLength} characters long`);
      result.isValid = false;
    }

    // Check max length
    if (rules.maxLength && value.length > rules.maxLength) {
      result.errors.push(`Must be no more than ${rules.maxLength} characters long`);
      result.isValid = false;
    }

    // Check pattern
    if (rules.pattern && !rules.pattern.test(value)) {
      result.errors.push('Input does not match required format');
      result.isValid = false;
    }

    // Run custom validator
    if (rules.customValidator && !rules.customValidator(result.sanitizedValue)) {
      result.errors.push('Input does not meet custom validation requirements');
      result.isValid = false;
    }

    return result;
  }

  // Sanitize user input to prevent XSS and other injection attacks
  sanitizeInput(input: string): string {
    if (typeof input !== 'string') {
      return '';
    }

    // Remove potentially dangerous characters/entities
    let sanitized = input
      // Remove script tags (case insensitive)
      .replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '')
      // Remove javascript:, vbscript:, etc. protocols
      .replace(/javascript:/gi, '')
      .replace(/vbscript:/gi, '')
      .replace(/data:/gi, '')
      // Remove event handlers (onload, onclick, etc.)
      .replace(/\s*on\w+\s*=\s*["'][^"']*["']/gi, '')
      // Remove eval statements
      .replace(/\beval\s*\(/gi, 'eval_disabled(')
      // Remove alert statements
      .replace(/\balert\s*\(/gi, 'alert_disabled(');

    // Additional sanitization can be added based on specific needs
    return sanitized.trim();
  }

  // Validate a message before sending to backend
  validateMessage(message: string): ValidationResult {
    const rules: ValidationRules = {
      required: true,
      minLength: 1,
      maxLength: 2000, // Max length based on our data model
      customValidator: (value) => {
        // Additional custom validation for messages
        // For example, ensure it's not just whitespace
        return value.trim().length > 0;
      },
    };

    return this.validate(message, rules);
  }

  // Validate user ID
  validateUserId(userId: string): ValidationResult {
    const rules: ValidationRules = {
      required: true,
      minLength: 1,
      maxLength: 100,
      pattern: /^[a-zA-Z0-9_-]+$/, // Allow alphanumeric, underscore, hyphen
    };

    return this.validate(userId, rules);
  }

  // Validate session ID
  validateSessionId(sessionId: string): ValidationResult {
    const rules: ValidationRules = {
      required: false,
      minLength: 10,
      maxLength: 100,
      pattern: /^[a-zA-Z0-9_-]+$/,
    };

    return this.validate(sessionId, rules);
  }

  // Validate a complete chat request
  validateChatRequest(message: string, userId: string, sessionId?: string): { isValid: boolean; errors: string[] } {
    const messageValidation = this.validateMessage(message);
    const userIdValidation = this.validateUserId(userId);
    const sessionIdValidation = sessionId ? this.validateSessionId(sessionId) : { isValid: true, errors: [] };

    const allErrors = [
      ...messageValidation.errors,
      ...userIdValidation.errors,
      ...sessionIdValidation.errors,
    ];

    return {
      isValid: messageValidation.isValid && userIdValidation.isValid && sessionIdValidation.isValid,
      errors: allErrors,
    };
  }

  // Validate response from backend
  validateApiResponse(response: any): boolean {
    if (!response || typeof response !== 'object') {
      return false;
    }

    // Check required fields in response
    return (
      'response' in response &&
      typeof response.response === 'string' &&
      'toolCallResults' in response &&
      Array.isArray(response.toolCallResults) &&
      'conversationHistory' in response &&
      Array.isArray(response.conversationHistory) &&
      'sessionId' in response &&
      typeof response.sessionId === 'string' &&
      'timestamp' in response &&
      typeof response.timestamp === 'string'
    );
  }
}

export default ValidationService;