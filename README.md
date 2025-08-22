# URL Analysis Project

This project analyzes URL access patterns and categorizes them based on security threat levels.

## Docker Setup

### Prerequisites
- Docker
- Docker Compose

### Running the Application

1. Build and run the application:
```bash
docker-compose up --build
```

2. Run in detached mode:
```bash
docker-compose up -d --build
```

3. View logs:
```bash
docker-compose logs -f
```

4. Stop the application:
```bash
docker-compose down
```

### Configuration

The application uses the following configuration files:
- `config/settings.py` - Main configuration settings
- `requirements.txt` - Python dependencies

### Output

Analysis results are saved to:
- `./data/analysis_results/` - Analysis results (CSV files)
- `./logs/` - Application logs

### Volumes

The following directories are mounted as volumes:
- `./data/analysis_results` - Persistent storage for analysis results
- `./logs` - Persistent storage for logs