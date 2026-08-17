---

source_id: loopin
source_type: project
title: Loopin — Real-Time Communication Application
url: https://github.com/Premx24/Loopin
----

# Overview

Loopin is a minimal real-time communication application that supports instant messaging and peer-to-peer video calls. It uses WebSockets for real-time messaging and signaling and WebRTC for direct peer-to-peer audio and video communication.

# Problem

Traditional communication applications can be complex to build because they require real-time messaging, room management, signaling, and peer-to-peer media communication.

Loopin was built to explore how these real-time communication concepts work together in a lightweight application.

# Solution

* WebSockets are used for real-time messaging and signaling.
* WebRTC is used for peer-to-peer audio and video streaming.
* Users can create or join temporary rooms using unique room codes.
* A lightweight Node.js WebSocket server manages rooms, message broadcasting, and WebRTC signaling.
* The frontend provides a responsive interface for messaging and video communication.

# Tech Stack

## Frontend

* React
* TypeScript
* Tailwind CSS

## Backend

* Node.js
* TypeScript
* ws

## Real-Time Communication

* WebSockets
* WebRTC

# Project Structure

```text
Loopin/
├── client/
├── server/
└── README.md
```

# Key Features

## Real-Time Messaging

Users can exchange messages instantly through a WebSocket connection.

## Peer-to-Peer Video Calling

Users can start audio and video calls using WebRTC, with media streamed directly between connected peers.

## Temporary Rooms

Users can create or join temporary communication rooms using unique room codes.

## Room Creation and Joining

A user can create a room or join an existing room by providing its unique code.

## Lightweight Interface

The application uses a minimal, responsive React interface designed around the real-time communication experience.

# How It Works

1. A user creates or joins a room.
2. The client connects to the WebSocket signaling server.
3. Users exchange messages through WebSockets.
4. WebSockets are also used for WebRTC signaling.
5. WebRTC establishes a peer-to-peer connection between users.
6. Audio and video are streamed directly between the connected peers.

# Development

## Client

The client is built with React and TypeScript.

Development server:

```text
http://localhost:5173
```

## Server

The server is built with Node.js, TypeScript, and the `ws` WebSocket library.

Development WebSocket server:

```text
ws://localhost:8080
```

# Project Goal

Loopin was built to explore real-time communication by implementing WebSockets for signaling and messaging and WebRTC for peer-to-peer media streaming.

The project focuses on understanding how real-time messaging, room management, WebSocket signaling, and peer-to-peer video communication work together in a lightweight application.

# Resume Facts

* Project: Loopin
* Dates: June 2026 – Present
* Built a real-time communication application supporting instant messaging and peer-to-peer video calls.
* Implemented temporary room-based communication using unique room codes.
* Developed WebSocket signaling for communication between peers.
* Implemented direct peer-to-peer audio and video streaming using WebRTC.
* Developed a responsive React interface.
* Built a lightweight TypeScript WebSocket server for real-time message broadcasting, room management, and WebRTC signaling.

# Grounding Rules

* Do not claim that Loopin has features not documented in this source.
* Do not invent user counts, deployment status, performance metrics, or production usage.
* When answering questions about Loopin, use the information in this document as the source of truth.
* If a requested detail is not present here, state that the available project documentation does not provide that information.
