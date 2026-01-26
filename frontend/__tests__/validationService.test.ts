import ValidationService from '../services/validationService';

describe('ValidationService', () => {
  let validationService: ValidationService;

  beforeEach(() => {
    validationService = new ValidationService();
  });

  describe('validate', () => {
    it('should validate a valid string with no rules', () => {
      const result = validationService.validate('test');
      expect(result.isValid).toBe(true);
      expect(result.errors).toHaveLength(0);
      expect(result.sanitizedValue).toBe('test');
    });

    it('should validate required field', () => {
      const result = validationService.validate('', { required: true });
      expect(result.isValid).toBe(false);
      expect(result.errors).toContain('This field is required');
    });

    it('should validate minimum length', () => {
      const result = validationService.validate('ab', { minLength: 5 });
      expect(result.isValid).toBe(false);
      expect(result.errors).toContain('Must be at least 5 characters long');
    });

    it('should validate maximum length', () => {
      const result = validationService.validate('very long string', { maxLength: 5 });
      expect(result.isValid).toBe(false);
      expect(result.errors).toContain('Must be no more than 5 characters long');
    });

    it('should validate pattern', () => {
      const result = validationService.validate('abc', { pattern: /^\d+$/ });
      expect(result.isValid).toBe(false);
      expect(result.errors).toContain('Input does not match required format');
    });

    it('should run custom validator', () => {
      const customValidator = (value: string) => value.includes('test');
      const result = validationService.validate('hello', { customValidator });
      expect(result.isValid).toBe(false);
      expect(result.errors).toContain('Input does not meet custom validation requirements');
    });

    it('should pass validation when all rules are satisfied', () => {
      const result = validationService.validate('testing', {
        required: true,
        minLength: 5,
        maxLength: 10,
        pattern: /^test/,
        customValidator: (value) => value.length > 6
      });
      expect(result.isValid).toBe(true);
      expect(result.errors).toHaveLength(0);
    });
  });

  describe('sanitizeInput', () => {
    it('should sanitize script tags', () => {
      const input = '<script>alert("xss")</script>Hello';
      const result = validationService.sanitizeInput(input);
      expect(result).toBe('Hello');
    });

    it('should sanitize javascript protocol', () => {
      const input = 'javascript:alert("xss")';
      const result = validationService.sanitizeInput(input);
      expect(result).toBe('Hello');
    });

    it('should sanitize event handlers', () => {
      const input = '<div onclick="alert()">Click me</div>';
      const result = validationService.sanitizeInput(input);
      expect(result).toBe('<div >Click me</div>');
    });

    it('should sanitize eval statements', () => {
      const input = 'eval(alert("xss"))';
      const result = validationService.sanitizeInput(input);
      expect(result).toBe('eval_disabled(alert("xss"))');
    });

    it('should sanitize alert statements', () => {
      const input = 'alert("xss")';
      const result = validationService.sanitizeInput(input);
      expect(result).toBe('alert_disabled("xss")');
    });

    it('should trim whitespace', () => {
      const input = '  hello world  ';
      const result = validationService.sanitizeInput(input);
      expect(result).toBe('hello world');
    });
  });

  describe('validateMessage', () => {
    it('should validate a valid message', () => {
      const result = validationService.validateMessage('This is a valid message');
      expect(result.isValid).toBe(true);
      expect(result.errors).toHaveLength(0);
    });

    it('should invalidate empty message', () => {
      const result = validationService.validateMessage('');
      expect(result.isValid).toBe(false);
      expect(result.errors).toContain('This field is required');
    });

    it('should invalidate message that is just whitespace', () => {
      const result = validationService.validateMessage('   ');
      expect(result.isValid).toBe(false);
      expect(result.errors).toContain('This field is required');
    });

    it('should invalidate message that exceeds max length', () => {
      const longMessage = 'a'.repeat(2001);
      const result = validationService.validateMessage(longMessage);
      expect(result.isValid).toBe(false);
      expect(result.errors).toContain('Must be no more than 2000 characters long');
    });
  });

  describe('validateUserId', () => {
    it('should validate a valid user ID', () => {
      const result = validationService.validateUserId('user_123-test');
      expect(result.isValid).toBe(true);
    });

    it('should invalidate empty user ID', () => {
      const result = validationService.validateUserId('');
      expect(result.isValid).toBe(false);
      expect(result.errors).toContain('This field is required');
    });

    it('should invalidate user ID with invalid characters', () => {
      const result = validationService.validateUserId('user<script>');
      expect(result.isValid).toBe(false);
      expect(result.errors).toContain('Input does not match required format');
    });
  });

  describe('validateSessionId', () => {
    it('should validate a valid session ID', () => {
      const result = validationService.validateSessionId('session_123-test');
      expect(result.isValid).toBe(true);
    });

    it('should allow empty session ID', () => {
      const result = validationService.validateSessionId('');
      expect(result.isValid).toBe(true);
    });

    it('should invalidate session ID that is too short', () => {
      const result = validationService.validateSessionId('short');
      expect(result.isValid).toBe(false);
      expect(result.errors).toContain('Must be at least 10 characters long');
    });
  });

  describe('validateChatRequest', () => {
    it('should validate a complete chat request', () => {
      const result = validationService.validateChatRequest(
        'Valid message',
        'user_123',
        'session_456'
      );
      expect(result.isValid).toBe(true);
      expect(result.errors).toHaveLength(0);
    });

    it('should invalidate with invalid message', () => {
      const result = validationService.validateChatRequest(
        '', // empty message
        'user_123',
        'session_456'
      );
      expect(result.isValid).toBe(false);
      expect(result.errors).toContain('This field is required');
    });

    it('should invalidate with invalid user ID', () => {
      const result = validationService.validateChatRequest(
        'Valid message',
        '', // empty user ID
        'session_456'
      );
      expect(result.isValid).toBe(false);
      expect(result.errors).toContain('This field is required');
    });
  });

  describe('validateApiResponse', () => {
    it('should validate a proper API response', () => {
      const response = {
        response: 'Hello from assistant',
        toolCallResults: [],
        conversationHistory: [],
        sessionId: 'session_123',
        timestamp: new Date().toISOString()
      };
      const result = validationService.validateApiResponse(response);
      expect(result).toBe(true);
    });

    it('should invalidate a response without required fields', () => {
      const response = {
        response: 'Hello from assistant',
        toolCallResults: []
        // Missing other required fields
      };
      const result = validationService.validateApiResponse(response);
      expect(result).toBe(false);
    });

    it('should invalidate non-object response', () => {
      const result = validationService.validateApiResponse(null);
      expect(result).toBe(false);
    });
  });
});