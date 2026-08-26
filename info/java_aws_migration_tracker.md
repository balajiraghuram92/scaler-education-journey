# Java (Spring Boot 3) & AWS Migration Tracker

## Migration Strategy & Overview
- **Source Architecture**: ASP.NET Core Minimal API (.NET 8/9) deployed on Azure Container Apps / Static Web Apps.
- **Target Architecture**: Java 21 / Spring Boot 3 REST API deployed on AWS (AWS ECR + App Runner / ECS Fargate + AWS S3 / CloudFront).
- **Execution Strategy**: Mentorship & Upskilling Mode — Raghuram Balaji manually writes code with local Qwen 2.5/3.5 35B autocomplete; Agent reviews code and orchestrates architecture.

---

## Phase 8 Breakdown: Java & AWS Migration Roadmap

### 📦 Milestone 1: Java (Spring Boot 3) Backend Core
- [ ] **Sub-task 8.1: Project Scaffolding & Build Configuration**
  - Scaffold `api-java/` folder.
  - Create Maven `pom.xml` with Java 21, Spring Boot 3.2+, Spring Web, Data JPA, SQLite/PostgreSQL drivers, Lombok.
  - Implement `StudyTrackerApplication.java` entry point.
  - Configure `application.yml` for database connection, port `8080`, and CORS.

- [ ] **Sub-task 8.2: JPA Data Models & Spring Data Repositories**
  - Map `StudyVertical` entity (`@Entity`, `@Table`, `@Id`, `@GeneratedValue`, `@OneToMany`).
  - Map `StudyTask` entity (`@Entity`, `@ManyToOne`, `@JoinColumn`).
  - Implement `StudyVerticalRepository` & `StudyTaskRepository` extending `JpaRepository`.

- [ ] **Sub-task 8.3: DTOs, Service Layer & Database Seeding**
  - Create DTOs (`VerticalResponseDto`, `TaskResponseDto`, `IngestPayloadDto`).
  - Build `StudyService` handling business logic and task status toggling.
  - Build `DataSeeder` (`CommandLineRunner`) to populate default verticals/tasks on startup.

- [ ] **Sub-task 8.4: REST Controllers & Security Filter**
  - Implement `StudyVerticalController` (`@RestController`, `@RequestMapping("/api/verticals")`).
  - Implement `StudyTaskController` (`@RequestMapping("/api/tasks")`).
  - Implement `ApiKeyFilter` (`OncePerRequestFilter`) validating `x-api-key` header.

- [ ] **Sub-task 8.5: Dynamic Markdown Ingestion Parser in Java**
  - Build `MarkdownParserService` to convert raw curriculum Markdown into `StudyVertical` & `StudyTask` objects.
  - Expose `POST /api/verticals/ingest` endpoint.

- [ ] **Sub-task 8.6: Java API Containerization (Docker)**
  - Write multi-stage `Dockerfile` for Java 21 (Maven Build stage -> Eclipse Temurin 21 JRE runtime stage).
  - Update `docker-compose.yml` to include `api-java` service alongside `app`.

---

### ☁️ Milestone 2: AWS Infrastructure & CI/CD Pipeline
- [ ] **Sub-task 8.7: AWS Infrastructure Provisioning**
  - AWS ECR repository setup for `api-java` container image.
  - AWS App Runner or ECS Fargate setup for serverless container execution.
  - AWS S3 Bucket & CloudFront CDN setup for static React frontend.

- [ ] **Sub-task 8.8: GitHub Actions CI/CD for AWS**
  - Update `.github/workflows/deploy.yml` with AWS credentials, ECR push, and App Runner/ECS deployment steps.
  - Configure GitHub Secrets (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION`).

---

## Progress Log
- **2026-08-07**: Migration roadmap initialized. Scaffolding for Sub-task 8.1 started in `api-java/`.
