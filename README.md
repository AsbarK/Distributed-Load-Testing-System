# Distributed Load Testing System

## Project Description

This project implements a distributed load-testing system that coordinates multiple driver nodes to perform highly concurrent, high-throughput load tests on a web server. The system uses Kafka as a communication service, facilitating communication between the orchestrator node and driver nodes.

## Application Architecture

The system consists of orchestrator and driver nodes, implemented as separate processes. They communicate via Kafka, adhering to the specified topics and message formats.

### Orchestrator Node

The Orchestrator node exposes a REST API to view and control tests. It can trigger and manage load tests and report statistics for ongoing tests.

### Driver Node

The Driver node sends requests to the target webserver as directed by the Orchestrator node. It records statistics for response times and sends the results back to the Orchestrator node.

### Target Server

The target server provides an endpoint to test and a metrics endpoint to track the number of requests sent and responses received.

## Features

- Supports Tsunami and Avalanche testing modes.
- Allows setting a delay interval between each request for Tsunami testing.
- Performs Avalanche testing by sending requests as soon as they are ready.
- Supports user-defined target throughput per driver node.
- Provides observability with metrics reporting.
- Orchestrator node tracks requests sent by each driver node and displays a dashboard with aggregated response latency statistics.
- Scalable, allowing a minimum of three (one orchestrator, two driver nodes) to a maximum of nine (one orchestrator, eight driver nodes).
- Implements Kafka-based communication using specified message formats.
- Orchestrator node exposes a REST API for test configuration and control.

## Installation and Setup

1. Clone the repository.
2. Install the required dependencies.
3. Configure Kafka IP Address and Orchestrator node IP Address as command-line arguments.
4. Run Orchestrator node and Driver nodes separately.

## You can find the architecture design for the above project.
https://app.eraser.io/workspace/w1WtgR9IKSSTMuHdOEMF?origin=share
