# Frontend Documentation

## Overview

The frontend is a React 18 application built with Vite for fast development and optimized production builds.

## Table of Contents

- [Architecture](./architecture.md)
- [Component Specification](./components.md)
- [Integration Guide](./integration.md)

## Tech Stack

- **Framework**: React 18
- **Build Tool**: Vite 5
- **Styling**: Tailwind CSS 3
- **Package Manager**: npm

## Getting Started

```bash
cd frontend
npm install
npm run dev
```

Visit http://localhost:5173

## Auth & Company Management
- Company Signup: `http://localhost:5173/signup`
- Company Login (API key): `http://localhost:5173/login`
- Company Dashboard (KB upload + stats): `http://localhost:5173/dashboard/:slug`

Dashboard operations that modify or query the knowledge base require your company API key.
