import {
  cn,
  generateId,
  formatDate,
  formatTimestamp,
  debounce,
  deepClone,
  isBrowser,
  getCurrentUserId,
  sleep,
  isEmpty,
  formatBytes,
  capitalize,
  randomString,
  isValidUrl
} from '../lib/utils';

// Mock localStorage for tests
const localStorageMock = (() => {
  let store: { [key: string]: string } = {};
  return {
    getItem: (key: string) => store[key] || null,
    setItem: (key: string, value: string) => {
      store[key] = value.toString();
    },
    removeItem: (key: string) => {
      delete store[key];
    },
    clear: () => {
      store = {};
    }
  };
})();

Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
});

// Mock window object for isBrowser tests
Object.defineProperty(window, 'location', {
  value: {
    href: 'http://localhost:3000'
  },
  writable: true
});

describe('Utils Functions', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  describe('cn', () => {
    it('should merge class names', () => {
      const result = cn('class1', 'class2');
      expect(result).toBe('class1 class2');
    });

    it('should handle conditional classes', () => {
      const result = cn('class1', false && 'class2', true && 'class3');
      expect(result).toBe('class1 class3');
    });
  });

  describe('generateId', () => {
    it('should generate a unique ID', () => {
      const id1 = generateId();
      const id2 = generateId();
      expect(id1).toBeDefined();
      expect(id2).toBeDefined();
      expect(id1).not.toBe(id2);
    });

    it('should generate IDs of reasonable length', () => {
      const id = generateId();
      expect(id.length).toBeGreaterThan(10);
    });
  });

  describe('formatDate', () => {
    it('should format a date as ISO string', () => {
      const date = new Date('2023-01-01T10:00:00Z');
      const result = formatDate(date);
      expect(result).toBe('2023-01-01T10:00:00.000Z');
    });
  });

  describe('formatTimestamp', () => {
    it('should format a timestamp string', () => {
      const timestamp = '2023-01-01T10:00:00.000Z';
      const result = formatTimestamp(timestamp);
      expect(typeof result).toBe('string');
      expect(result.length).toBeGreaterThan(0);
    });
  });

  describe('debounce', () => {
    jest.useFakeTimers();

    it('should debounce a function', () => {
      const fn = jest.fn();
      const debouncedFn = debounce(fn, 100);

      debouncedFn();
      debouncedFn(); // This should cancel the previous call
      expect(fn).toHaveBeenCalledTimes(0);

      jest.advanceTimersByTime(100);
      expect(fn).toHaveBeenCalledTimes(1);
    });

    it('should call the function after the delay', () => {
      const fn = jest.fn();
      const debouncedFn = debounce(fn, 100);

      debouncedFn();
      jest.advanceTimersByTime(100);
      expect(fn).toHaveBeenCalledTimes(1);
    });
  });

  describe('deepClone', () => {
    it('should clone primitive values', () => {
      expect(deepClone(42)).toBe(42);
      expect(deepClone('hello')).toBe('hello');
      expect(deepClone(true)).toBe(true);
      expect(deepClone(null)).toBeNull();
      expect(deepClone(undefined)).toBeUndefined();
    });

    it('should clone arrays', () => {
      const arr = [1, 2, [3, 4]];
      const cloned = deepClone(arr);
      expect(cloned).toEqual(arr);
      expect(cloned).not.toBe(arr);
      expect(cloned[2]).not.toBe(arr[2]); // Nested array should be cloned too
    });

    it('should clone objects', () => {
      const obj = { a: 1, b: { c: 2 } };
      const cloned = deepClone(obj);
      expect(cloned).toEqual(obj);
      expect(cloned).not.toBe(obj);
      expect(cloned.b).not.toBe(obj.b); // Nested object should be cloned too
    });

    it('should clone dates', () => {
      const date = new Date();
      const cloned = deepClone(date);
      expect(cloned).toEqual(date);
      expect(cloned).not.toBe(date);
    });
  });

  describe('isBrowser', () => {
    it('should return true when window is defined', () => {
      expect(isBrowser()).toBe(true);
    });
  });

  describe('getCurrentUserId', () => {
    it('should return user ID from localStorage', () => {
      localStorage.setItem('userId', 'user-123');
      const result = getCurrentUserId();
      expect(result).toBe('user-123');
    });

    it('should return user ID from JWT token', () => {
      // Create a mock JWT token with userId in payload
      const payload = { userId: 'user-456', exp: Math.floor(Date.now() / 1000) + 3600 };
      const token = `header.${btoa(JSON.stringify(payload))}.signature`;
      localStorage.setItem('jwtToken', token);

      const result = getCurrentUserId();
      expect(result).toBe('user-456');
    });

    it('should return null if no user ID found', () => {
      const result = getCurrentUserId();
      expect(result).toBeNull();
    });
  });

  describe('sleep', () => {
    jest.useFakeTimers();

    it('should wait for specified time', async () => {
      const promise = sleep(100);
      jest.advanceTimersByTime(100);
      await expect(promise).resolves.toBeUndefined();
    });
  });

  describe('isEmpty', () => {
    it('should return true for null/undefined', () => {
      expect(isEmpty(null)).toBe(true);
      expect(isEmpty(undefined)).toBe(true);
    });

    it('should return true for empty strings', () => {
      expect(isEmpty('')).toBe(true);
      expect(isEmpty('   ')).toBe(true); // Whitespace-only string
    });

    it('should return true for empty arrays', () => {
      expect(isEmpty([])).toBe(true);
    });

    it('should return true for empty objects', () => {
      expect(isEmpty({})).toBe(true);
    });

    it('should return false for non-empty values', () => {
      expect(isEmpty('hello')).toBe(false);
      expect(isEmpty([1])).toBe(false);
      expect(isEmpty({ a: 1 })).toBe(false);
      expect(isEmpty(0)).toBe(false);
      expect(isEmpty(false)).toBe(false);
    });
  });

  describe('formatBytes', () => {
    it('should format bytes correctly', () => {
      expect(formatBytes(0)).toBe('0 Bytes');
      expect(formatBytes(1024)).toBe('1 KB');
      expect(formatBytes(1024 * 1024)).toBe('1 MB');
      expect(formatBytes(1024 * 1024 * 1024)).toBe('1 GB');
    });

    it('should format with specified decimals', () => {
      expect(formatBytes(1500, 2)).toBe('1.46 KB');
    });
  });

  describe('capitalize', () => {
    it('should capitalize first letter of a string', () => {
      expect(capitalize('hello')).toBe('Hello');
      expect(capitalize('world')).toBe('World');
    });

    it('should handle empty strings', () => {
      expect(capitalize('')).toBe('');
    });

    it('should handle single character', () => {
      expect(capitalize('a')).toBe('A');
    });
  });

  describe('randomString', () => {
    it('should generate random string of specified length', () => {
      const str = randomString(10);
      expect(str.length).toBe(10);
    });

    it('should generate different strings each time', () => {
      const str1 = randomString(10);
      const str2 = randomString(10);
      expect(str1).not.toBe(str2);
    });
  });

  describe('isValidUrl', () => {
    it('should validate valid URLs', () => {
      expect(isValidUrl('https://example.com')).toBe(true);
      expect(isValidUrl('http://localhost:3000')).toBe(true);
      expect(isValidUrl('ftp://files.example.com')).toBe(true);
    });

    it('should invalidate invalid URLs', () => {
      expect(isValidUrl('not-a-url')).toBe(false);
      expect(isValidUrl('')).toBe(false);
    });
  });
});