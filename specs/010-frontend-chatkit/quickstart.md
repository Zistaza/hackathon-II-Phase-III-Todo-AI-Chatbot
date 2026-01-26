# Quickstart Guide: Todo AI Chatbot Frontend - ChatKit Interface

## Prerequisites

- Node.js 18.x or higher
- npm or yarn package manager
- Access to the backend API with `/api/{user_id}/chat` endpoint
- Valid JWT token for authentication

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd hackathon-II-phase-III-todo-ai-chatbot
```

2. Navigate to the frontend directory:
```bash
cd frontend
```

3. Install dependencies:
```bash
npm install
# or
yarn install
```

## Configuration

1. Copy the environment example file:
```bash
cp .env.example .env.local
```

2. Update the environment variables in `.env.local`:
```env
NEXT_PUBLIC_API_BASE_URL=<backend-api-base-url>
NEXT_PUBLIC_CHATKIT_API_KEY=<chatkit-api-key-if-needed>
NEXT_PUBLIC_USER_ID=<default-user-id-for-development>
```

## Running the Application

### Development Mode
```bash
npm run dev
# or
yarn dev
```

The application will be available at `http://localhost:3000`

### Production Build
```bash
npm run build
npm run start
# or
yarn build
yarn start
```

## Key Components

### Chat Interface
Located in `src/components/ChatInterface.tsx`, this component wraps the OpenAI ChatKit component and handles:
- Message sending to the backend API
- Displaying conversation history
- Error handling and validation
- Session management

### API Service
Located in `src/services/apiService.ts`, this service manages:
- Communication with the `/api/{user_id}/chat` endpoint
- Request/response formatting
- Error handling
- Authentication header management

## Testing

### Unit Tests
```bash
npm run test
# or
yarn test
```

### E2E Tests
```bash
npm run test:e2e
# or
yarn test:e2e
```

## Available Scripts

- `dev`: Start development server with hot reloading
- `build`: Create production build
- `start`: Start production server
- `lint`: Run linter
- `test`: Run unit tests
- `test:e2e`: Run end-to-end tests
- `test:watch`: Run tests in watch mode

## Environment Variables

- `NEXT_PUBLIC_API_BASE_URL`: Base URL for the backend API
- `NEXT_PUBLIC_JWT_TOKEN`: Authentication token for API requests (development only)
- `NEXT_PUBLIC_DEFAULT_USER_ID`: Default user ID for testing (development only)

## Troubleshooting

### Common Issues

1. **API Connection Errors**: Verify that the backend API is running and accessible at the configured URL
2. **Authentication Failures**: Ensure the JWT token is valid and properly formatted
3. **ChatKit Not Loading**: Check that the ChatKit API key is correctly configured (if required)

### Development Tips

- Use the development server for real-time updates
- Check browser console for JavaScript errors
- Verify network requests in browser developer tools
- Ensure all required environment variables are set