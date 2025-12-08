# README.md（中文说明）

前端静态资源与构建说明。

---

<!-- 说明：以下保留英文原文，供核对；若需中文摘要请参考主文档。 -->
# MCP Memory Service Interactive Dashboard

This directory contains the static assets for the interactive memory management dashboard.

## Files Overview

- **`index.html`** - Main dashboard interface with complete UI structure
- **`app.js`** - Frontend JavaScript application with API integration and real-time updates
- **`style.css`** - Comprehensive CSS with responsive design and component styling
- **`sse_test.html`** - Server-Sent Events testing interface (existing)

## Features Implemented

### 🎯 Core Dashboard
- **Welcome overview** with memory statistics and quick actions
- **Recent memories** display with click-to-view details
- **Quick stats** showing total memories, recent activity, and tag counts
- **Responsive design** that works on mobile, tablet, and desktop

### 🔍 Search & Browse
- **Semantic search** with real-time suggestions
- **Advanced filters** by tags, date range, and content type
- **Grid/list view** toggles for different viewing preferences
- **Search results** with relevance scoring and highlighting

### 📝 Memory Management
- **Add new memories** with modal interface and auto-tagging
- **View memory details** with full content, metadata, and tags
- **Edit/delete operations** with confirmation and undo capabilities
- **Bulk operations** for efficient memory organization

### ⚡ Real-time Features
- **Server-Sent Events** integration for live updates
- **Connection status** monitoring with reconnection logic
- **Toast notifications** for user feedback
- **Live statistics** updates without page refresh

### 🎨 User Experience
- **Progressive disclosure** - simple by default, powerful when needed
- **Keyboard shortcuts** - Ctrl+K for search, Ctrl+M for add memory
- **Loading states** and error handling throughout
- **Accessibility** features with proper ARIA labels and focus management

## Testing the Dashboard

### 1. Start the Server
```bash
# With HTTPS (recommended)
export MCP_HTTPS_ENABLED=true
export MCP_HTTPS_PORT=8443
python run_server.py
```

### 2. Access the Dashboard
- **HTTPS**: https://localhost:8443/
- **HTTP**: http://localhost:8000/

### 3. Test Core Functionality
1. **Search**: Use semantic queries and apply filters
2. **Add Memory**: Click "Add Memory" and create test content
3. **View Details**: Click memory cards to see full details
4. **Real-time Updates**: Open in multiple tabs to test SSE
5. **Keyboard Shortcuts**: Try Ctrl+K (search) and Ctrl+M (add)

## Technical Implementation

- **Vanilla JavaScript** - No build process required
- **CSS Grid + Flexbox** - Modern responsive layouts
- **Server-Sent Events** - Real-time backend communication
- **Progressive Enhancement** - Works without JavaScript for basics
- **API Integration** - Full REST API connectivity with error handling