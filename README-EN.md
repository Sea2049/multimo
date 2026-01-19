<div align="center">

<img src="./static/image/Multimo_logo_compressed.jpeg" alt="Multimo Logo" width="75%"/>

简洁通用的群体智能引擎，预测万物
</br>
<em>A Simple and Universal Swarm Intelligence Engine, Predicting Anything</em>

<a href="https://www.shanda.com/" target="_blank"><img src="./static/image/shanda_logo.png" alt="666ghj%2Multimo | Shanda" height="40"/>

[![GitHub Stars](https://img.shields.io/github/stars/666ghj/Multimo?style=flat-square)](https://github.com/666ghj/Multimo/stargazers)
[![GitHub Watchers](https://img.shields.io/github/watchers/666ghj/Multimo?style=flat-square)](https://github.com/666ghj/Multimo/watchers)
[![GitHub Forks](https://img.shields.io/github/forks/666ghj/Multimo?style=flat-square)](https://github.com/666ghj/Multimo/network)
[![GitHub Issues](https://img.shields.io/github/issues/666ghj/Multimo?style=flat-square)](https://github.com/666ghj/Multimo/issues)
[![GitHub Pull Requests](https://img.shields.io/github/issues-pr/666ghj/Multimo?style=flat-square)](https://github.com/666ghj/Multimo/pulls)

[![GitHub License](https://img.shields.io/github/license/666ghj/Multimo?style=flat-square)](https://github.com/666ghj/Multimo/blob/main/LICENSE)
[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/666ghj/Multimo)
[![Version](https://img.shields.io/badge/version-v0.1.0-green.svg?style=flat-square)](https://github.com/666ghj/Multimo)

[English](./README-EN.md) | [中文文档](./README.md)

</div>

## ⚡ Overview

**Multimo** is a next-generation AI prediction engine powered by multi-agent technology. By extracting seed information from the real world (such as breaking news, policy drafts, or financial signals), it automatically constructs a high-fidelity parallel digital world. Within this space, thousands of intelligent agents with independent personalities, long-term memory, and behavioral logic freely interact and undergo social evolution. You can inject variables dynamically from a "God's-eye view" to precisely deduce future trajectories — **rehearse the future in a digital sandbox, and win decisions after countless simulations**.

> You only need to: Upload seed materials (data analysis reports or interesting novel stories) and describe your prediction requirements in natural language</br>
> Multimo will return: A detailed prediction report and a deeply interactive high-fidelity digital world

### Our Vision

Multimo is dedicated to creating a swarm intelligence mirror that maps reality. By capturing the collective emergence triggered by individual interactions, we break through the limitations of traditional prediction:

- **At the Macro Level**: We are a rehearsal laboratory for decision-makers, allowing policies and public relations to be tested at zero risk
- **At the Micro Level**: We are a creative sandbox for individual users — whether deducing novel endings or exploring imaginative scenarios, everything can be fun, playful, and accessible

From serious predictions to playful simulations, we let every "what if" see its outcome, making it possible to predict anything.

## 📸 Screenshots

<div align="center">
<table>
<tr>
<td><img src="./static/image/Screenshot/运行截图1.png" alt="Screenshot 1" width="100%"/></td>
<td><img src="./static/image/Screenshot/运行截图2.png" alt="Screenshot 2" width="100%"/></td>
</tr>
<tr>
<td><img src="./static/image/Screenshot/运行截图3.png" alt="Screenshot 3" width="100%"/></td>
<td><img src="./static/image/Screenshot/运行截图4.png" alt="Screenshot 4" width="100%"/></td>
</tr>
<tr>
<td><img src="./static/image/Screenshot/运行截图5.png" alt="Screenshot 5" width="100%"/></td>
<td><img src="./static/image/Screenshot/运行截图6.png" alt="Screenshot 6" width="100%"/></td>
</tr>
</table>
</div>

## 🎬 Demo Videos

<div align="center">
<a href="https://www.bilibili.com/video/BV1VYBsBHEMY/" target="_blank"><img src="./static/image/武大模拟演示封面.png" alt="MiroFish Demo Video" width="75%"/></a>

Click the image to watch the complete demo video for prediction using BettaFish-generated "Wuhan University Public Opinion Report"
</div>

> More demo videos coming soon: "Dream of the Red Chamber" ending simulation, financial prediction examples...

## 🔄 Workflow

1. **Graph Building**: Seed extraction & Individual/collective memory injection & GraphRAG construction
2. **Environment Setup**: Entity relationship extraction & Persona generation & Agent configuration injection
3. **Simulation**: Dual-platform parallel simulation & Auto-parse prediction requirements & Dynamic temporal memory updates
4. **Report Generation**: ReportAgent with rich toolset for deep interaction with post-simulation environment
5. **Deep Interaction**: Chat with any agent in the simulated world & Interact with ReportAgent

## 🚀 Quick Start

### Prerequisites

| Tool | Version | Description | Check Installation |
|------|---------|-------------|-------------------|
| **Node.js** | 18+ | Frontend runtime, includes npm | `node -v` |
| **Python** | ≥3.11, ≤3.12 | Backend runtime | `python --version` |
| **uv** | Latest | Python package manager | `uv --version` |

### 1. Configure Environment Variables

```bash
# Copy the example configuration file
cp .env.example .env

# Edit the .env file and fill in the required API keys
```

**Required Environment Variables:**

```env
# LLM API Configuration (supports any LLM with OpenAI SDK format)
# Recommended: Alibaba Qwen-plus model via Bailian Platform: https://bailian.console.aliyun.com/
# High consumption, try simulations with fewer than 40 rounds first
LLM_API_KEY=your_api_key
LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
LLM_MODEL_NAME=qwen-plus

# Zep Cloud Configuration
# Free monthly quota is sufficient for simple usage: https://app.getzep.com/
ZEP_API_KEY=your_zep_api_key
```

### 2. Install Dependencies

```bash
# One-click installation of all dependencies (root + frontend + backend)
npm run setup:all
```

Or install step by step:

```bash
# Install Node dependencies (root + frontend)
npm run setup

# Install Python dependencies (auto-creates virtual environment)
npm run setup:backend
```

### 3. Start Services

```bash
# Start both frontend and backend (run from project root)
npm run dev
```

**Service URLs:**
- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:5001`

**Start Individually:**

```bash
npm run backend   # Start backend only
npm run frontend  # Start frontend only
```

## 📁 Project Structure

```
Multimo/
├── backend/                 # Backend Python application
│   ├── app/                 # Core application code
│   │   ├── api/            # API route layer
│   │   ├── models/         # Data model layer
│   │   ├── services/       # Business logic layer
│   │   └── utils/          # Utility functions layer
│   ├── scripts/            # Scripts directory
│   ├── uploads/            # Upload files directory
│   └── logs/               # Logs directory
├── frontend/                # Frontend Vue.js application
│   ├── src/
│   │   ├── api/            # API clients
│   │   ├── components/     # Vue components
│   │   ├── views/          # Page views
│   │   └── router/         # Router configuration
│   └── public/             # Public static resources
├── static/                  # Static resources (images, etc.)
├── FRAMEWORK.md             # Framework architecture documentation
├── CODE_DIRECTORY.md        # Code directory documentation
├── README.md                # Chinese documentation
└── README-EN.md             # English documentation (this file)
```

For detailed directory structure and file descriptions, please refer to:
- [Framework Architecture Documentation](./FRAMEWORK.md)
- [Code Directory Documentation](./CODE_DIRECTORY.md)

## 🛠️ Tech Stack

### Backend Technologies
- **Python 3.11-3.12** - Programming language
- **Flask 3.0+** - Web framework
- **OpenAI SDK** - LLM interaction
- **Zep Cloud 3.13.0** - Long-term memory service
- **CAMEL-OASIS 0.2.5** - Social simulation engine
- **PyMuPDF** - PDF parsing

### Frontend Technologies
- **Vue.js 3** - Frontend framework
- **Vue Router** - Route management
- **Axios** - HTTP client
- **D3.js** - Graph visualization
- **Vite** - Build tool

## 📖 Documentation

- [Framework Architecture Documentation](./FRAMEWORK.md) - Detailed system architecture and technical design
- [Code Directory Documentation](./CODE_DIRECTORY.md) - Complete code directory structure and file descriptions
- [API Documentation](./FRAMEWORK.md#6-api-端点) - REST API endpoint descriptions
- [Configuration Documentation](./FRAMEWORK.md#5-配置管理) - Environment variables and configuration options

## 🤝 Contributing

Contributions are welcome! Feel free to submit pull requests, report issues, or suggest new features!

1. Fork this repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📬 Join the Conversation

<div align="center">
<img src="./static/image/QQ群.png" alt="QQ Group" width="60%"/>
</div>

&nbsp;

The Multimo team is recruiting full-time/internship positions. If you're interested in multi-agent simulation and LLM applications, feel free to send your resume to: **multimo@shanda.com**

## 📄 Acknowledgments

**Multimo has received strategic support and incubation from Shanda Group!**

Multimo's simulation engine is powered by **[OASIS (Open Agent Social Interaction Simulations)](https://github.com/camel-ai/oasis)**, We sincerely thank the CAMEL-AI team for their open-source contributions!

## 📄 License

This project is licensed under the [AGPL-3.0](LICENSE) License.

## 📈 Project Statistics

<a href="https://www.star-history.com/#666ghj/Multimo&type=date&legend=top-left">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=666ghj/Multimo&type=date&theme=dark&legend=top-left" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=666ghj/Multimo&type=date&theme=light&legend=top-left" />
   <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=666ghj/Multimo&type=date&legend=top-left" />
 </picture>
</a>
