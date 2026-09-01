# 🎥 StreamSight

# Dataset Profiling & Quality Assessment

This repository documents the StreamSight assignment focused on dataset profiling and quality assessment. The project includes data validation scripts, reporting outputs, and workflow notes for monitoring data integrity throughout the pipeline.

## Assignment Focus

- Profile input datasets and identify schema, quality, and consistency issues.
- Validate missing values, duplicates, and anomalies in the engagement dataset.
- Generate actionable reports and document the workflow for team collaboration.

> **Transforming Viewer Engagement into Smarter Content Decisions**

StreamSight is a Python-based viewer engagement analytics platform designed to help streaming service providers understand audience behavior through data. The platform provides a simplified video streaming experience where user interactions such as watch duration, pause frequency, completion rate, and search activity are recorded and analyzed.

Live demo: [StreamSight Live Demo](https://streamsightpro.netlify.app)

Instead of focusing on building a complete streaming platform, StreamSight emphasizes collecting engagement metrics and converting them into meaningful insights that help acquisition teams make informed content investment decisions.

---

# 📖 Problem Statement

Subscription-based streaming platforms capture viewer engagement data such as watch duration, pause frequency, and episode completion. However, acquisition teams often greenlight new content without understanding which viewer engagement patterns correlate with long-term retention.

StreamSight solves this problem by collecting engagement data and presenting interactive analytics that reveal viewer behavior, helping organizations make data-driven content decisions.

---

# 🎯 Objectives

- Capture viewer engagement data.
- Analyze viewing behavior and engagement patterns.
- Measure viewer retention using analytics.
- Provide an interactive analytics dashboard.
- Support data-driven content acquisition decisions.

---

# ✨ Features

## 👤 User Features

- Secure User Authentication
- Video Search
- Browse Content Categories
- Video Playback
- Continue Watching
- Watch History
- Bookmark Videos

---

## 📊 Analytics Features

- Watch Duration Tracking
- Pause Frequency Analysis
- Completion Rate Monitoring
- Search Analytics
- Viewer Retention Insights
- Trending Content Analysis
- Engagement Dashboard

---

## 🔐 Admin Features

- Upload Videos
- Manage Content Library
- View Analytics Dashboard
- Monitor User Engagement
- Generate Content Performance Reports

---

# ⚙️ System Workflow

```
User Login
      │
      ▼
Search Content
      │
      ▼
Watch Video
      │
      ▼
System Records

• Watch Duration
• Pause Frequency
• Completion Rate
• Search Activity
• Watch History

      │
      ▼
Database
      │
      ▼
Analytics Engine
      │
      ▼
Analytics Dashboard
      │
      ▼
Content Acquisition Decisions
```

---

# 🛠️ Technology Stack

## Backend

- Python
- Flask
- SQLAlchemy

## Database

- SQLite
- PostgreSQL (Future Scope)

## Frontend

- HTML5
- CSS3
- JavaScript
- Bootstrap

## Data Analytics

- Pandas
- NumPy

## Data Visualization

- Matplotlib
- Plotly

## Machine Learning (Future Scope)

- Scikit-learn

---

# 📊 Engagement Metrics Collected

| Metric | Description |
|---------|-------------|
| Watch Duration | Total viewing time of a user |
| Pause Frequency | Number of pauses during playback |
| Completion Rate | Percentage of video watched |
| Search Activity | User search keywords |
| Watch History | Previously watched videos |
| Repeat Views | Number of replays |
| Session Duration | Total viewing session time |

---

# 📈 Analytics Dashboard

The dashboard provides valuable insights including:

- 📺 Total Views
- ⏱️ Average Watch Time
- 📊 Completion Rate
- ⏸️ Pause Frequency
- 📈 Viewer Retention Score
- 🔍 Most Searched Categories
- 🔥 Top Performing Content
- 📉 Viewer Drop-off Analysis
- 📅 Engagement Trends

---

# � Business Visualisation Principles

## Choosing the Right Chart Type

Every chart type has a purpose. Bar charts compare categories; line charts show trends over time; histograms describe distributions; scatter plots expose correlation; stacked bars show composition. Choosing the wrong chart creates confusion and delays decisions.

### Recommended chart matches

- Bar Chart: comparison across categories such as revenue by product line or sales by region.
- Line Chart: trends over time such as monthly revenue, weekly active users, or churn rate.
- Histogram: distribution of values such as order values or customer age bands.
- Scatter Plot: relationship between two variables such as marketing spend and revenue.
- Stacked Bar: composition and part-to-whole relationships such as quarterly revenue by product.

## Complete Labelling

Every chart should include a clear title, axis labels with units, a legend when needed, and labels on key bars or points. Human-readable formatting reduces cognitive load and makes charts comprehensible in seconds.

## Colour Palette and Accessibility

Use one consistent palette across all dashboards, and avoid relying on colour alone to communicate meaning. Pair colour with shape, line style, or text to keep the dashboard accessible for colour-blind viewers.

## Annotation and Context

Use annotations for insights such as peaks, dips, launch dates, and targets. Reference lines help viewers judge performance against benchmarks and convert raw data into decisions.

> Branch 2.45 includes the dashboard visualisation update and documentation for PR creation.

---

# �🚀 Future Enhancements

- AI-powered Content Recommendation System
- Viewer Segmentation
- Retention Prediction using Machine Learning
- Personalized Video Recommendations
- Real-Time Analytics Dashboard
- User Feedback & Sentiment Analysis
- Genre-wise Performance Analysis

---

# 🌿 Git Workflow

### Branching Strategy

- `main` contains stable production-ready code.
- Every new feature is developed in a separate feature branch.
- Branch naming conventions:
  - `feature/<feature-name>`
  - `fix/<bug-name>`
  - `docs/<documentation>`
  - `refactor/<module>`
  - `chore/<task>`

> Note: This branch includes a small documentation update to enable PR creation.

---

### Commit Message Convention

Format

```
[type]: description
```

Examples

```
feat: implement viewer engagement tracking

fix: resolve dashboard calculation bug

docs: update project documentation

refactor: optimize analytics module

chore: update project dependencies
```

---

### Pull Request Process

- Every feature is submitted through a Pull Request.
- PRs reference the related GitHub Issue.
- Code is reviewed before merging.
- Merge only after approval.

---

### GitHub Issue Tracking

Every task starts with a GitHub Issue containing:

- Title
- Description
- Label
- Assignee

Issues are automatically closed using:

```
Closes #Issue_Number
```

---

# 🎯 Expected Outcome

StreamSight enables streaming platforms to move beyond raw viewing statistics by identifying engagement patterns that correlate with viewer retention.

Using these insights, acquisition teams can:

- Identify high-performing content.
- Improve underperforming content.
- Understand audience preferences.
- Make informed content investment decisions.
- Increase viewer retention through data-driven strategies.

---

# 👨‍💻 Team Members

| Name | Role |
|------|------|
| **Subhadeep** | Project Lead & Backend Developer |
| **Aman** | Data Analytics & Dashboard Developer |
| **Tanmay** | Frontend Developer |

---

# 📜 License

This project is developed for educational purposes as part of the **Kalvium Software Engineering Program**.