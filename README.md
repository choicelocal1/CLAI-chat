# CLAI-Chat

A full-stack ChatGPT-like conversational AI application designed to provide chat functionality with AI models, featuring user management, conversation history, and administrative controls.

## Overview

CLAI-Chat is a complete solution for implementing AI chat capabilities into applications. It provides a widget that can be embedded into websites, a backend API service to handle conversations, and an administrative interface to manage users and settings.

## Features

- **AI Chat Widget**: Embeddable chat widget for integrating into any website
- **User Management**: Create and manage user accounts and access levels
- **Conversation History**: Store and retrieve previous conversations
- **Admin Dashboard**: Administrative interface for system management
- **API Service**: Backend service for handling AI model interactions
- **Docker Integration**: Containerized deployment for easy setup

## Technology Stack

- **Frontend**: React.js
- **Backend**: Python (Flask)
- **Database**: PostgreSQL
- **Caching**: Redis
- **Containerization**: Docker & Docker Compose

## Project Structure

```
/CLAI-chat
├── admin/                 # Admin dashboard application
├── api/                   # Backend API service
│   ├── src/
│   │   ├── config/        # Configuration settings
│   │   ├── models/        # Data models
│   │   ├── routes/        # API route definitions
│   │   ├── services/      # Business logic services
│   │   └── utils/         # Utility functions
│   ├── Dockerfile         # Docker configuration for API
│   └── run.py             # API entry point
├── widget/                # Chat widget frontend
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── context/       # React context providers
│   │   ├── hooks/         # Custom React hooks
│   │   ├── services/      # Frontend services
│   │   └── utils/         # Utility functions
│   ├── Dockerfile         # Docker configuration for widget
│   └── package.json       # NPM dependencies
├── docs/                  # Documentation
├── scripts/               # Utility scripts
├── .github/workflows/     # GitHub Actions workflows
├── docker-compose.yml     # Docker Compose configuration
├── .env.example           # Example environment configuration
└── README.md              # Project documentation
```

## Setup & Installation

### Prerequisites

- Docker and Docker Compose
- Git

### Local Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/choicelocal1/CLAI-chat.git
   cd CLAI-chat
   ```

2. Create an environment file:
   ```bash
   cp .env.example .env
   ```

3. Modify the `.env` file with appropriate API keys and configuration settings.

4. Start the application using Docker Compose:
   ```bash
   docker compose up
   ```

5. Access the different components:
   - Widget Development Server: http://localhost:9000
   - API Service: http://localhost:5000
   - Admin Dashboard: http://localhost:3000

## Deployment

The project is configured for automated deployment using GitHub Actions. When changes are pushed to the main branch, the workflow:

1. Connects to the deployment server
2. Pulls the latest changes
3. Rebuilds and restarts the Docker containers

To configure deployment:

1. Add the following secrets to your GitHub repository:
   - `HOST`: Your server IP address
   - `USERNAME`: SSH username (usually "root")
   - `PASSWORD`: SSH password

2. Ensure the deployment server has Docker and Docker Compose installed.

## API Documentation

The API service provides endpoints for:

- User authentication and management
- Conversation handling
- System configuration

Detailed API documentation is available at `/api/docs` when the service is running.

## Environment Variables

Key environment variables include:

- `DB_HOST`: PostgreSQL host
- `DB_USERNAME`: Database username
- `DB_PASSWORD`: Database password
- `REDIS_HOST`: Redis host
- `API_KEY`: API key for AI service
- `JWT_SECRET`: Secret for JWT authentication

See `.env.example` for a complete list of required environment variables.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Troubleshooting

### Common Issues

- **Database Connection Issues**: Ensure PostgreSQL is running and the connection details in `.env` are correct
- **API Key Problems**: Verify your AI service API key is valid and properly set in the environment
- **Docker Network Issues**: Try recreating the Docker network with `docker compose down && docker compose up -d`

### Logs

- Access container logs using `docker compose logs [service-name]`
- API logs are stored in the `api/logs` directory

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contact

For support or inquiries, please create an issue in the GitHub repository.
