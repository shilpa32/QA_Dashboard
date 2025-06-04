# QA Metrics Dashboard

A comprehensive dashboard for tracking and analyzing QA metrics across different modules.

## Features

- Overview of open and closed issues
- Priority-based analysis (P0, P1, Other)
- Module-wise performance metrics
- Test type distribution
- Bug details with test case associations
- Interactive visualizations
- Data export capabilities

## Deployment Instructions

### Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the dashboard:
```bash
streamlit run qa_dashboard.py
```

### Deploying to Streamlit Cloud

1. Create a GitHub repository and push your code:
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin <your-github-repo-url>
git push -u origin main
```

2. Go to [Streamlit Cloud](https://streamlit.io/cloud)
3. Sign in with your GitHub account
4. Click "New app"
5. Select your repository, branch, and main file (qa_dashboard.py)
6. Click "Deploy"

## Project Structure

- `qa_dashboard.py`: Main dashboard application
- `qa_data_template.csv`: Template data file
- `requirements.txt`: Project dependencies
- `README.md`: Project documentation

## Data Format

The dashboard expects a CSV file with the following columns:
- Module
- Test Type
- P0 issues Open/Closed
- P1 Issues Open/Closed
- Rest Issues Open/Closed
- Bug Titles
- Test Cases

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request
