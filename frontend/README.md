# Todo AI Chatbot Frontend

A responsive, stateless ChatKit-based frontend interface that connects to the POST /api/{user_id}/chat endpoint, allowing users to manage todos through natural language commands.

## Overview

This frontend provides a chat interface for users to interact with an AI-powered todo management system using natural language commands. The interface is built with Next.js and OpenAI's ChatKit components, following a stateless design where all conversation persistence is handled by the backend.

## Features

- Natural language todo management through chat interface
- Real-time conversation with AI assistant
- Display of tool call results from backend operations
- Stateless design with backend-driven session management
- Responsive UI for desktop and mobile devices
- Input validation and error handling
- Cross-browser compatibility

## Tech Stack

- Next.js 16+ with App Router
- React 18+
- OpenAI ChatKit
- TypeScript
- Tailwind CSS 4.0+
- Framer Motion 11+

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
NEXT_PUBLIC_JWT_TOKEN=<your-jwt-token-here>
NEXT_PUBLIC_DEFAULT_USER_ID=<default-user-id-for-development>
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

## Environment Variables

- `NEXT_PUBLIC_API_BASE_URL`: Base URL for the backend API (e.g., http://localhost:8000)
- `NEXT_PUBLIC_JWT_TOKEN`: Authentication token for API requests (development only)
- `NEXT_PUBLIC_DEFAULT_USER_ID`: Default user ID for testing (development only)

## API Integration

The frontend communicates with the backend via the POST `/api/{user_id}/chat` endpoint. All requests include proper authentication headers and follow the established API contract.

## Architecture

The application follows a stateless design where:
- All conversation history is maintained by the backend
- Session restoration happens automatically on page load
- No local storage is used for conversation data
- The UI simply renders the conversation state provided by the backend

## Key Components

- **ChatInterface**: Main ChatKit wrapper component
- **MessageRenderer**: Component for displaying messages and tool call results
- **InputValidator**: Component for input validation
- **ErrorHandler**: Component for error handling display
- **apiService**: Service for API communication
- **validationService**: Service for input validation
- **authService**: Service for authentication token handling

## Testing

### Available Scripts

- `dev`: Start development server with hot reloading
- `build`: Create production build
- `start`: Start production server
- `lint`: Run linter
- `test`: Run unit tests
- `test:e2e`: Run end-to-end tests
- `test:watch`: Run tests in watch mode

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

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Commit your changes (`git commit -m 'Add amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
