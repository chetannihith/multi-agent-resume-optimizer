# Multi-Agent Resume Optimizer - Streamlit App

A comprehensive Streamlit web application that provides an intuitive interface for the Multi-Agent Resume Optimizer system with Groq API integration.

## 🌟 Features

### Core Functionality
- **📤 Resume Upload**: Upload resume in JSON format
- **🔗 Job Description Input**: Paste job posting URLs from major platforms
- **🚀 AI-Powered Optimization**: Multi-agent workflow with LangGraph orchestration
- **📊 ATS Score Analysis**: Real-time ATS compatibility scoring (target: 90%+)
- **👁️ Resume Preview**: Interactive preview of optimized resume
- **📥 Multiple Downloads**: LaTeX (.tex) and PDF formats
- **⚡ Real-time Progress**: Live workflow execution tracking

### Advanced Features
- **🎯 Groq API Integration**: Powered by Llama 3 for intelligent optimization
- **📈 Detailed Analytics**: Comprehensive job analysis and profile matching
- **🔍 Content Alignment**: Keyword matching and content optimization
- **⚙️ Configurable Settings**: Environment-based configuration management
- **🛡️ Error Handling**: Robust error recovery and user feedback
- **📱 Responsive Design**: Mobile-friendly interface

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <repository-url>
cd multi-agent-resume-optimizer

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

```bash
# Copy the sample environment file
cp sample.env .env

# Edit .env with your API keys
nano .env
```

**Required Configuration:**
```env
# Get your Groq API key from: https://console.groq.com/
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama3-8b-8192
```

### 3. Setup Directories

```bash
# Create required directories
mkdir -p templates output data/profiles logs

# Copy the LaTeX template (if you have one)
cp path/to/your/template.tex templates/resume_template.tex
```

### 4. Run the Application

```bash
# Start the Streamlit app
streamlit run app.py

# The app will open in your browser at http://localhost:8501
```

## 📋 Usage Guide

### Step 1: Upload Resume
1. **Prepare Resume**: Convert your resume to JSON format (see sample format below)
2. **Upload File**: Use the file uploader to select your resume JSON
3. **Verify Upload**: Check the resume preview and statistics

### Step 2: Job Description
1. **Enter URL**: Paste the job posting URL from supported platforms
2. **Validate URL**: Ensure the URL format is correct
3. **Platform Check**: Verify the platform is supported

### Step 3: Optimize Resume
1. **Start Optimization**: Click "Optimize Resume" to begin the process
2. **Monitor Progress**: Watch the real-time progress indicator
3. **View Results**: Review the ATS score and detailed analysis

### Step 4: Download Results
1. **LaTeX Download**: Get the Overleaf-ready .tex file
2. **PDF Generation**: Generate and download PDF version
3. **Preview**: View the optimized resume content

## 📊 Resume JSON Format

Your resume should be in the following JSON structure:

```json
{
  "name": "Your Name",
  "email": "your.email@example.com",
  "phone": "+1 (555) 123-4567",
  "location": "City, State",
  "linkedin": "linkedin.com/in/yourprofile",
  "github": "github.com/yourusername",
  
  "summary": "Professional summary...",
  
  "skills": {
    "programming_languages": ["JavaScript", "Python"],
    "frameworks": ["React", "Node.js"],
    "databases": ["MongoDB", "PostgreSQL"],
    "cloud_devops": ["AWS", "Docker"]
  },
  
  "experience": [
    {
      "title": "Job Title",
      "company": "Company Name",
      "location": "City, State",
      "duration": "2020 - Present",
      "description": "Job description...",
      "achievements": ["Achievement 1", "Achievement 2"],
      "technologies": ["Tech1", "Tech2"]
    }
  ],
  
  "education": [
    {
      "degree": "Bachelor of Science",
      "field": "Computer Science",
      "institution": "University Name",
      "graduation_year": "2020",
      "gpa": "3.7"
    }
  ],
  
  "projects": [
    {
      "name": "Project Name",
      "description": "Project description...",
      "technologies": ["Tech1", "Tech2"],
      "impact": "Impact description...",
      "date": "2023"
    }
  ]
}
```

See `examples/sample_resume.json` for a complete example.

## 🔧 Configuration Options

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `GROQ_API_KEY` | Groq API key for LLM | - | ✅ |
| `GROQ_MODEL` | Groq model to use | `llama3-8b-8192` | ❌ |
| `APP_TITLE` | Application title | `Multi-Agent Resume Optimizer` | ❌ |
| `MAX_FILE_SIZE_MB` | Max upload size | `10` | ❌ |
| `WORKFLOW_TIMEOUT_SECONDS` | Workflow timeout | `300` | ❌ |
| `LOG_LEVEL` | Logging level | `INFO` | ❌ |

### Supported Platforms

The app supports job URLs from:
- LinkedIn Jobs
- Indeed
- Glassdoor
- Monster
- ZipRecruiter
- Other major job boards

### File Formats

- **Input**: JSON, TXT (containing JSON)
- **Output**: LaTeX (.tex), PDF
- **Max Size**: 10MB (configurable)

## 🎨 User Interface

### Main Sections

1. **Header**: App title and configuration status
2. **Sidebar**: Configuration, help, and troubleshooting
3. **Upload Section**: Resume file upload with preview
4. **Job Input**: URL input with validation
5. **Optimization**: Workflow execution with progress tracking
6. **Results**: ATS score, analytics, and detailed breakdown
7. **Downloads**: LaTeX and PDF download options

### Visual Elements

- **Progress Bars**: Real-time workflow progress
- **Metrics Cards**: ATS score and performance indicators
- **Interactive Charts**: Keyword analysis and alignment scores
- **Tabbed Analysis**: Detailed breakdowns by category
- **Responsive Layout**: Mobile-friendly design

## 📈 Analytics & Insights

### ATS Score Breakdown
- **Overall Score**: 0-100 scale with 90%+ target
- **Keyword Density**: Percentage of job keywords matched
- **Section Completeness**: Required sections presence
- **Formatting Score**: ATS-friendly formatting compliance

### Detailed Analysis Tabs
1. **Job Analysis**: Keywords, requirements, company info
2. **Profile Match**: Relevance score and matching elements
3. **Content Alignment**: Keyword matching and gaps
4. **ATS Optimization**: Scores, suggestions, auto-fixes

### Visual Charts
- **ATS Score Gauge**: Interactive score visualization
- **Keyword Analysis**: Bar charts of keyword frequency
- **Performance Metrics**: Execution time and file size
- **Quality Indicators**: Pass/fail status for key criteria

## 🛠️ Development

### Project Structure
```
├── app.py                 # Main Streamlit application
├── config.py             # Configuration management
├── sample.env            # Environment template
├── requirements.txt      # Python dependencies
├── examples/
│   ├── sample_resume.json # Sample resume format
│   └── workflow_demo.py   # Workflow demonstration
├── src/
│   └── workflow/         # LangGraph workflow
├── templates/            # LaTeX templates
├── output/              # Generated files
└── logs/                # Application logs
```

### Key Components

1. **ResumeOptimizerApp**: Main application class
2. **Configuration Management**: Environment-based settings
3. **Workflow Integration**: LangGraph orchestration
4. **UI Components**: Modular Streamlit interface
5. **Error Handling**: Comprehensive error management

### Adding Features

To add new features:

1. **Extend Configuration**: Add new environment variables
2. **Update UI**: Add new Streamlit components
3. **Integrate Workflow**: Connect to existing agents
4. **Add Analytics**: Create new visualization components
5. **Test Integration**: Ensure end-to-end functionality

## 🔍 Troubleshooting

### Common Issues

1. **API Key Errors**
   ```
   Error: GROQ_API_KEY is required
   Solution: Add your Groq API key to .env file
   ```

2. **File Upload Errors**
   ```
   Error: Invalid JSON format
   Solution: Ensure resume is valid JSON format
   ```

3. **Workflow Timeout**
   ```
   Error: Workflow execution timeout
   Solution: Increase WORKFLOW_TIMEOUT_SECONDS in .env
   ```

4. **Template Not Found**
   ```
   Error: Template file not found
   Solution: Ensure templates/resume_template.tex exists
   ```

### Debug Mode

Enable debug logging:
```env
LOG_LEVEL=DEBUG
ENABLE_DETAILED_LOGGING=true
```

Check logs in the `logs/` directory for detailed execution traces.

### Performance Issues

If the app is slow:
1. Reduce `MAX_CONCURRENT_WORKFLOWS`
2. Increase `WORKFLOW_TIMEOUT_SECONDS`
3. Check network connectivity
4. Verify API rate limits

## 🚀 Deployment

### Local Development
```bash
streamlit run app.py
```

### Production Deployment

1. **Streamlit Cloud**:
   - Push to GitHub
   - Connect to Streamlit Cloud
   - Add secrets for environment variables

2. **Docker**:
   ```dockerfile
   FROM python:3.11-slim
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   COPY . .
   EXPOSE 8501
   CMD ["streamlit", "run", "app.py"]
   ```

3. **Heroku**:
   - Add `Procfile`: `web: streamlit run app.py --server.port=$PORT`
   - Configure environment variables
   - Deploy via Git

## 📚 API Integration

### Groq API Setup

1. **Get API Key**: Visit [Groq Console](https://console.groq.com/)
2. **Create Account**: Sign up for free account
3. **Generate Key**: Create new API key
4. **Configure App**: Add key to .env file

### Supported Models
- `llama3-8b-8192` (default)
- `llama3-70b-8192`
- `mixtral-8x7b-32768`
- `gemma-7b-it`

### Rate Limits
- Free tier: 30 requests/minute
- Paid tier: Higher limits available
- Configure `MAX_REQUESTS_PER_HOUR` accordingly

## 🤝 Contributing

1. **Fork Repository**: Create your own fork
2. **Create Branch**: `git checkout -b feature/new-feature`
3. **Make Changes**: Implement your feature
4. **Test Thoroughly**: Ensure all functionality works
5. **Submit PR**: Create pull request with description

### Development Guidelines
- Follow PEP 8 style guidelines
- Add comprehensive docstrings
- Include unit tests for new features
- Update documentation as needed
- Test with various resume formats

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **LangGraph**: Workflow orchestration framework
- **Streamlit**: Web application framework
- **Groq**: Fast LLM inference API
- **ModernCV**: LaTeX resume template
- **Contributors**: All project contributors

## 📞 Support

For support and questions:
1. Check this README and troubleshooting section
2. Review the logs in `logs/` directory
3. Test with the sample resume in `examples/`
4. Open an issue on GitHub with detailed information

---

**Built for Hacktoberfest 2025** 🎃
