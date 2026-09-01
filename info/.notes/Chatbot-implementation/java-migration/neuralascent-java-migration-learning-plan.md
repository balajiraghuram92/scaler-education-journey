# NeuralAscent: .NET to Java/Spring Migration Learning Plan

**Version:** 1.0  
**Target:** ASP.NET Core → Spring Boot 3.3+ (Java 21)  
**Learner Level:** Java Noob → Production-Ready Engineer  
**Timeline:** 18–24 weeks (Sprints 1–12)  
**Learning Approach:** Concurrent Java fundamentals + Spring framework + actual platform migration  
**Reference Materials:** Java LLD Vertical (neuralascent.top/java-lld) + TODO Tracker (§ 1–12)

---

## Table of Contents

1. [Overview & Philosophy](#overview--philosophy)
2. [Java Learning Path Overview](#java-learning-path-overview)
3. [Pre-Migration Setup (Week 0)](#pre-migration-setup-week-0)
4. [Sprint 1: Foundation & Identity Layer](#sprint-1-foundation--identity-layer)
5. [Sprint 2: Authorization & Access Control](#sprint-2-authorization--access-control)
6. [Sprint 3: AI Gateway & Cost Management](#sprint-3-ai-gateway--cost-management)
7. [Sprint 4: Current-Context Learning Tutor](#sprint-4-current-context-learning-tutor)
8. [Sprint 5: Admin Operations Dashboard](#sprint-5-admin-operations-dashboard)
9. [Sprint 6: Persistent Learner State](#sprint-6-persistent-learner-state)
10. [Sprint 7: Conversation Memory & Ownership](#sprint-7-conversation-memory--ownership)
11. [Sprint 8: Engagement Telemetry & Auto-Completion](#sprint-8-engagement-telemetry--auto-completion)
12. [Sprint 9: Support Assistant & Tickets](#sprint-9-support-assistant--tickets)
13. [Sprint 10: Filtered RAG & Cross-Vertical Access](#sprint-10-filtered-rag--cross-vertical-access)
14. [Sprint 11: Evaluation & Production Hardening](#sprint-11-evaluation--production-hardening)
15. [Sprint 12: Java/Spring Completion & .NET Deprecation](#sprint-12-javaspring-completion--net-deprecation)
16. [Appendix: Practice Exercises from Java LLD Vertical](#appendix-practice-exercises-from-java-lld-vertical)

---

## Overview & Philosophy

### Why This Approach?

Instead of learning Java in isolation and then applying it, you'll **learn Java concepts exactly when you need them to solve real platform problems**. Each sprint teaches specific Java/Spring idioms alongside the NeuralAscent refactoring work those concepts enable.

Example: You learn Spring Security authentication in Sprint 1 because P1 (authentication) requires it. You learn Spring Data JPA in Sprint 2 because P2 (authorization) needs database-backed policies. You learn Spring AI in Sprint 3 because P3 (AI gateway) directly uses it.

### Three Parallel Tracks

1. **Learning Track:** Java fundamentals, Spring framework, design patterns.
2. **Migration Track:** Refactoring .NET code into equivalent Java/Spring modules.
3. **Application Track:** Building new features that only make sense in the Java version (e.g., Spring Security policies, Spring Data repositories).

### Your Learning Resources

- **Java LLD Vertical:** Use lessons on interfaces, abstract classes, design patterns, and OOP as reference when confused about Java syntax/concepts.
- **Spring Documentation:** Bookmark and use frequently — Spring Boot has excellent reference docs.
- **TODO Tracker:** Your architecture requirements. Each sprint extracts phases from the TODO and translates them to Java.

---

## Java Learning Path Overview

### Phases of Java Mastery (Mapped to Sprints)

| Sprint | Java Focus | Spring Focus | Platform Phase |
|--------|-----------|--------------|-----------------|
| 1 | Classes, constructors, annotations, dependency injection | Spring Boot setup, Spring Security basics, `@Service`, `@Repository` | P0–P1: Identity |
| 2 | Interfaces, inheritance, polymorphism, generics | Spring Data JPA, entity relationships, queries | P2: Authorization |
| 3 | Exception handling, custom exceptions, sealed classes | Spring Cloud Config, feature flags, API design | P3: AI Gateway |
| 4 | Streams, lambdas, functional programming | Spring MVC, request/response mapping, SSE | P4: Tutor |
| 5 | Collections, sorting, custom comparators | Spring Admin, metrics, actuator | P5: Admin Dashboard |
| 6 | Serialization, JSON, enums | Spring Data JPA auditing, Temporal types | P6: Learner State |
| 7 | Concurrency, threads, synchronization | Spring Session, caching (Redis/Caffeine) | P7: Conversations |
| 8 | Records, sealed classes, text blocks | Spring Events, message queues | P8: Telemetry |
| 9 | Modules & packaging, multi-module builds | Maven/Gradle structure | P9: Support |
| 10 | Advanced generics, reflection (limited!) | Spring Data REST, custom queries | P10: RAG |
| 11 | Performance tuning, profiling, observability | Spring Boot Actuator, Micrometer, Observability | P11: Evaluation |
| 12 | Migration patterns, API contracts, versioning | Spring Cloud Gateway (optional), deprecation strategy | P12: Completion |

### Key Java Features You'll Use (In Order)

1. **Classes & Constructors** (Sprint 1)
2. **Annotations** (Sprint 1 onwards — `@Service`, `@Repository`, `@Transactional`)
3. **Interfaces & Polymorphism** (Sprint 2–3 — provider abstraction, event handling)
4. **Generics** (Sprint 3–4 — generic repositories, type-safe policies)
5. **Streams & Lambdas** (Sprint 4+ — filtering, sorting, transformation)
6. **Exception Handling** (Sprint 3 onwards — custom exceptions for business logic)
7. **Enums** (Sprint 6+ — status, roles, hint levels)
8. **Records** (Sprint 6+ — immutable data transfer objects)
9. **Sealed Classes** (Sprint 7+ — authorization results, routing decisions)
10. **Concurrency** (Sprint 7–8 — thread-safe state, concurrent quotas)

---

## Pre-Migration Setup (Week 0)

### Goal

Set up the Java/Spring project skeleton, confirm tooling, and establish your first "hello world" to a database.

### Learning Objectives

- [ ] Install JDK 21 and verify `java -version`
- [ ] Understand Maven/Gradle build tool basics (we'll use Maven)
- [ ] Create a Spring Boot project from spring.io/start
- [ ] Connect to PostgreSQL from Java code
- [ ] Run your first unit test

### Migration Tasks

- [ ] Create directory structure: `/neuralascent-java`
- [ ] Set up Maven `pom.xml` with:
  - Spring Boot 3.3+
  - Spring Data JPA
  - Spring Security
  - PostgreSQL JDBC driver
  - Lombok (reduce boilerplate)
  - JUnit 5 + Mockito
  - Gradle or Maven (pick one; Maven recommended for this guide)

- [ ] Copy your `.gitignore` from .NET project; add `target/`, `.idea/`, `.vscode/`
- [ ] Create README with environment setup instructions
- [ ] Add `application.properties` or `application.yml` template with PostgreSQL connection string

### Practice Exercise from Java LLD Vertical

**Lesson:** Interfaces & Abstract Classes  
**Task:** Create an interface `ICurriculumService` with a method `findLessonById(Integer id) -> Lesson`. Then create a stub `CurriculumService` implementing it. Use this as your first data-access service.

### Success Criteria

- [ ] `mvn clean package` runs without error
- [ ] You can instantiate a Spring Data repository and query PostgreSQL
- [ ] One JUnit test passes that verifies a repository method
- [ ] Project structure is clean and matches target layout (P12.2)

### Code Example

```java
// src/main/java/com/neuralascent/curriculum/domain/Lesson.java
package com.neuralascent.curriculum.domain;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Entity
@Table(name = "lesson")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class Lesson {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer id;
    
    private String slug;
    private String title;
    private String verticalCode;
    
    // Getters/setters auto-generated by Lombok
}

// src/main/java/com/neuralascent/curriculum/persistence/LessonRepository.java
package com.neuralascent.curriculum.persistence;

import com.neuralascent.curriculum.domain.Lesson;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface LessonRepository extends JpaRepository<Lesson, Integer> {
    Lesson findBySlugAndVerticalCode(String slug, String verticalCode);
}

// src/test/java/com/neuralascent/curriculum/LessonRepositoryTest.java
package com.neuralascent.curriculum;

import com.neuralascent.curriculum.domain.Lesson;
import com.neuralascent.curriculum.persistence.LessonRepository;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import static org.junit.jupiter.api.Assertions.*;

@SpringBootTest
class LessonRepositoryTest {
    @Autowired
    private LessonRepository repository;
    
    @Test
    void testFindBySlug() {
        Lesson lesson = repository.findBySlugAndVerticalCode("polymorphism", "java-lld");
        assertNotNull(lesson);
    }
}
```

---

## Sprint 1: Foundation & Identity Layer

**Duration:** 2–3 weeks  
**.NET Migration Source:** `Program.cs` (auth setup), `Models/User.cs`, authentication middleware  
**TODO Tracker Phases:** P0, P1  
**Java Topics:** Classes, Annotations, Dependency Injection, Spring Security basics

### Overview

In this sprint, you'll migrate the user/identity infrastructure from ASP.NET Core Identity to Spring Security, establish the foundation for authentication, and learn how Java's annotation-driven dependency injection works.

### Learning Objectives

By the end of Sprint 1, you should understand:

- [ ] Java class structure, constructors, and field initialization
- [ ] Annotations and how Spring uses them (e.g., `@Service`, `@Repository`, `@Transactional`)
- [ ] Spring's dependency injection container and how `@Autowired` works
- [ ] Spring Security architecture (SecurityFilterChain, providers, user details)
- [ ] Entity mapping with Spring Data JPA (`@Entity`, `@Table`, relationships)
- [ ] HttpOnly cookies and session management in Spring
- [ ] Difference between .NET's `User.Identity` and Spring Security's `Authentication` principal

### Platform Requirements (from TODO P1)

From the tracker:

- [ ] Add `app_user` entity with UUID, email, display name, status
- [ ] Add roles: `LEARNER`, `SUPPORT_AGENT`, `ADMIN`
- [ ] Add account states: `PENDING`, `ACTIVE`, `SUSPENDED`, `LOCKED`, `DELETED`
- [ ] Use HttpOnly cookies for browser auth
- [ ] Set `Secure`, `SameSite`, expiration policies
- [ ] Add CSRF protection
- [ ] Disable unrestricted registration (invitation-based initially)

### Migration Tasks

#### Task 1: Create User Domain & Database Schema (Week 1)

**Java Concepts:** Classes, enums, JPA annotations

1. Create entity classes:
   ```
   src/main/java/com/neuralascent/identity/domain/
   ├── AppUser.java
   ├── UserRole.java (enum)
   ├── UserStatus.java (enum)
   └── UserSession.java
   ```

2. Create repositories:
   ```
   src/main/java/com/neuralascent/identity/persistence/
   ├── AppUserRepository.java
   └── UserSessionRepository.java
   ```

3. Write migration SQL (Flyway):
   ```
   src/main/resources/db/migration/
   └── V001__create_user_tables.sql
   ```

**Code Example:**

```java
// src/main/java/com/neuralascent/identity/domain/UserRole.java
package com.neuralascent.identity.domain;

public enum UserRole {
    LEARNER("learner"),
    SUPPORT_AGENT("support_agent"),
    ADMIN("admin");
    
    private final String code;
    
    UserRole(String code) {
        this.code = code;
    }
    
    public String getCode() {
        return code;
    }
}

// src/main/java/com/neuralascent/identity/domain/AppUser.java
package com.neuralascent.identity.domain;

import jakarta.persistence.*;
import lombok.*;
import org.hibernate.annotations.CreationTimestamp;
import org.hibernate.annotations.UpdateTimestamp;
import java.time.LocalDateTime;
import java.util.*;

@Entity
@Table(name = "app_user")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class AppUser {
    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;
    
    @Column(unique = true, nullable = false)
    private String email;
    
    @Column(nullable = false)
    private String displayName;
    
    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private UserStatus status = UserStatus.PENDING;
    
    @Column(nullable = false)
    private String passwordHash;
    
    @ElementCollection(fetch = FetchType.EAGER)
    @Enumerated(EnumType.STRING)
    @CollectionTable(name = "user_role", joinColumns = @JoinColumn(name = "user_id"))
    @Column(name = "role")
    private Set<UserRole> roles = new HashSet<>();
    
    @CreationTimestamp
    private LocalDateTime createdAt;
    
    @UpdateTimestamp
    private LocalDateTime updatedAt;
    
    private LocalDateTime lastLoginAt;
}

// src/main/java/com/neuralascent/identity/domain/UserStatus.java
package com.neuralascent.identity.domain;

public enum UserStatus {
    PENDING,
    ACTIVE,
    SUSPENDED,
    LOCKED,
    DELETED
}

// src/main/java/com/neuralascent/identity/persistence/AppUserRepository.java
package com.neuralascent.identity.persistence;

import com.neuralascent.identity.domain.AppUser;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import java.util.Optional;
import java.util.UUID;

@Repository
public interface AppUserRepository extends JpaRepository<AppUser, UUID> {
    Optional<AppUser> findByEmailIgnoreCase(String email);
    boolean existsByEmail(String email);
}
```

**SQL Migration:**

```sql
-- V001__create_user_tables.sql
CREATE TABLE app_user (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    display_name VARCHAR(255) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'PENDING',
    password_hash VARCHAR(512) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login_at TIMESTAMP
);

CREATE TABLE user_role (
    user_id UUID REFERENCES app_user(id) ON DELETE CASCADE,
    role VARCHAR(50) NOT NULL,
    PRIMARY KEY (user_id, role)
);

CREATE INDEX idx_app_user_email ON app_user(LOWER(email));
CREATE INDEX idx_app_user_status ON app_user(status);
```

**Practice Exercise from Java LLD Vertical:**

Review: Lesson on **Interfaces & Abstract Classes**  
Create a `UserValidator` interface with methods for validating email format, password strength, display name length. Implement it in `UserValidatorImpl`. Use this in your user creation service.

**Success Criteria:**

- [ ] `AppUser` entity maps to `app_user` table without errors
- [ ] `AppUserRepository.findByEmailIgnoreCase()` works in a unit test
- [ ] Migration runs with Flyway and creates correct schema
- [ ] No compilation errors

---

#### Task 2: Spring Security Configuration (Week 1–2)

**Java Concepts:** Annotations, dependency injection, lambda expressions

1. Create Spring Security configuration:
   ```
   src/main/java/com/neuralascent/identity/security/
   ├── SecurityConfig.java
   ├── CustomUserDetailsService.java
   ├── JwtTokenProvider.java (for stateless auth if needed)
   └── SecurityAuditService.java
   ```

2. Implement authentication filter chain (no shared API key!)

3. Add password encoding with BCrypt

**Code Example:**

```java
// src/main/java/com/neuralascent/identity/security/SecurityConfig.java
package com.neuralascent.identity.security;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.config.annotation.authentication.builders.AuthenticationManagerBuilder;
import org.springframework.security.config.annotation.method.configuration.EnableMethodSecurity;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.csrf.CookieCsrfTokenRepository;

@Configuration
@EnableWebSecurity
@EnableMethodSecurity(prePostEnabled = true)
public class SecurityConfig {
    
    private final CustomUserDetailsService userDetailsService;
    
    public SecurityConfig(CustomUserDetailsService userDetailsService) {
        this.userDetailsService = userDetailsService;
    }
    
    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }
    
    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            .authorizeHttpRequests(authz -> authz
                .requestMatchers("/api/v1/auth/login").permitAll()
                .requestMatchers("/api/v1/auth/register").permitAll()
                .requestMatchers("/health").permitAll()
                .anyRequest().authenticated()
            )
            .formLogin(form -> form
                .loginProcessingUrl("/api/v1/auth/login")
                .permitAll()
            )
            .logout(logout -> logout
                .logoutUrl("/api/v1/auth/logout")
                .deleteCookies("JSESSIONID")
                .permitAll()
            )
            .sessionManagement(session -> session
                .sessionFixationProtection(org.springframework.security.config.http.SessionFixationProtection.MIGRATEDSESSION)
                .sessionConcurrency(cc -> cc.maximumSessions(5))
            )
            .csrf(csrf -> csrf
                .csrfTokenRepository(CookieCsrfTokenRepository.withHttpOnlyFalse())
            )
            .httpBasic(httpBasic -> {})
            .rememberMe(remember -> remember
                .rememberMeParameter("remember-me")
                .tokenValiditySeconds(86400)
            );
        
        return http.build();
    }
    
    @Bean
    public AuthenticationManager authenticationManager(HttpSecurity http) throws Exception {
        return http.getSharedObject(AuthenticationManagerBuilder.class)
            .userDetailsService(userDetailsService)
            .passwordEncoder(passwordEncoder())
            .and()
            .build();
    }
}

// src/main/java/com/neuralascent/identity/security/CustomUserDetailsService.java
package com.neuralascent.identity.security;

import com.neuralascent.identity.domain.AppUser;
import com.neuralascent.identity.domain.UserStatus;
import com.neuralascent.identity.persistence.AppUserRepository;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.userdetails.*;
import org.springframework.stereotype.Service;
import java.util.stream.Collectors;

@Service
public class CustomUserDetailsService implements UserDetailsService {
    
    private final AppUserRepository userRepository;
    
    public CustomUserDetailsService(AppUserRepository userRepository) {
        this.userRepository = userRepository;
    }
    
    @Override
    public UserDetails loadUserByUsername(String email) throws UsernameNotFoundException {
        AppUser user = userRepository.findByEmailIgnoreCase(email)
            .orElseThrow(() -> new UsernameNotFoundException("User not found: " + email));
        
        if (user.getStatus() == UserStatus.SUSPENDED || user.getStatus() == UserStatus.DELETED) {
            throw new DisabledException("User account is " + user.getStatus().toString().toLowerCase());
        }
        
        return new org.springframework.security.core.userdetails.User(
            user.getEmail(),
            user.getPasswordHash(),
            user.getStatus() == UserStatus.ACTIVE,
            true,
            true,
            user.getStatus() != UserStatus.LOCKED,
            user.getRoles().stream()
                .map(role -> new SimpleGrantedAuthority("ROLE_" + role.name()))
                .collect(Collectors.toSet())
        );
    }
}
```

**Compare to .NET:**

| .NET (ASP.NET Core Identity) | Java (Spring Security) |
|-----|------|
| `User.Identity.IsAuthenticated` | `SecurityContextHolder.getContext().getAuthentication().isAuthenticated()` |
| `User.FindFirst(ClaimTypes.NameIdentifier)` | `SecurityContextHolder.getContext().getAuthentication().getPrincipal()` |
| `User.IsInRole("Admin")` | `SecurityContextHolder.getContext().getAuthentication().getAuthorities()` |
| `IdentityResult` from UserManager | Spring Security throws exceptions (e.g., `UsernameNotFoundException`) |

**Practice Exercise from Java LLD Vertical:**

Review: Lesson on **Exception Handling in Java**  
Create custom exceptions: `UserAlreadyExistsException`, `InvalidPasswordException`, `UserLockedException`. Throw them in your authentication flow and handle them in a `@ControllerAdvice` global exception handler.

**Success Criteria:**

- [ ] CSRF tokens are issued and validated
- [ ] HttpOnly session cookies are set
- [ ] Suspended users receive 403
- [ ] Password is BCrypt-hashed, never plain text
- [ ] Authentication tests pass

---

#### Task 3: User Registration & Invitation Flow (Week 2)

**Java Concepts:** Transactions, custom exceptions, service layer pattern

1. Create `UserRegistrationService`
2. Implement invitation model and repository
3. Add registration endpoint (disabled by default for public)

**Code Example:**

```java
// src/main/java/com/neuralascent/identity/domain/UserInvitation.java
package com.neuralascent.identity.domain;

import jakarta.persistence.*;
import lombok.*;
import java.time.LocalDateTime;
import java.util.UUID;

@Entity
@Table(name = "user_invitation")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class UserInvitation {
    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;
    
    @Column(nullable = false)
    private String email;
    
    @Column(unique = true, nullable = false)
    private String code;
    
    @Column(nullable = false)
    private LocalDateTime expiresAt;
    
    @Column(nullable = false)
    private LocalDateTime createdAt = LocalDateTime.now();
    
    private LocalDateTime acceptedAt;
    
    private UUID issuedByUserId;
    
    @Enumerated(EnumType.STRING)
    private UserStatus statusOnAccept = UserStatus.ACTIVE;
}

// src/main/java/com/neuralascent/identity/service/UserRegistrationService.java
package com.neuralascent.identity.service;

import com.neuralascent.identity.domain.*;
import com.neuralascent.identity.persistence.*;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.time.LocalDateTime;
import java.util.UUID;

@Service
public class UserRegistrationService {
    
    private final AppUserRepository userRepository;
    private final UserInvitationRepository invitationRepository;
    private final PasswordEncoder passwordEncoder;
    
    public UserRegistrationService(
        AppUserRepository userRepository,
        UserInvitationRepository invitationRepository,
        PasswordEncoder passwordEncoder
    ) {
        this.userRepository = userRepository;
        this.invitationRepository = invitationRepository;
        this.passwordEncoder = passwordEncoder;
    }
    
    @Transactional
    public AppUser registerWithInvitation(String email, String displayName, String password, String invitationCode)
        throws InvalidInvitationException {
        
        // Validate invitation
        UserInvitation invitation = invitationRepository.findByCode(invitationCode)
            .orElseThrow(() -> new InvalidInvitationException("Invitation not found"));
        
        if (LocalDateTime.now().isAfter(invitation.getExpiresAt())) {
            throw new InvalidInvitationException("Invitation has expired");
        }
        
        if (invitation.getAcceptedAt() != null) {
            throw new InvalidInvitationException("Invitation already used");
        }
        
        // Check email not already registered
        if (userRepository.existsByEmail(email)) {
            throw new UserAlreadyExistsException("Email already registered");
        }
        
        // Create user
        AppUser user = new AppUser();
        user.setEmail(email);
        user.setDisplayName(displayName);
        user.setPasswordHash(passwordEncoder.encode(password));
        user.setStatus(invitation.getStatusOnAccept());
        user.getRoles().add(UserRole.LEARNER);
        
        AppUser savedUser = userRepository.save(user);
        
        // Mark invitation as accepted
        invitation.setAcceptedAt(LocalDateTime.now());
        invitationRepository.save(invitation);
        
        return savedUser;
    }
    
    @Transactional
    public UserInvitation createInvitation(String email, UserRole initialRole, UUID issuedByUserId) {
        UserInvitation invitation = new UserInvitation();
        invitation.setEmail(email);
        invitation.setCode(generateInvitationCode());
        invitation.setExpiresAt(LocalDateTime.now().plusDays(7));
        invitation.setIssuedByUserId(issuedByUserId);
        
        return invitationRepository.save(invitation);
    }
    
    private String generateInvitationCode() {
        return UUID.randomUUID().toString().replace("-", "");
    }
}

// Custom exceptions
public class InvalidInvitationException extends RuntimeException {
    public InvalidInvitationException(String message) { super(message); }
}

public class UserAlreadyExistsException extends RuntimeException {
    public UserAlreadyExistsException(String message) { super(message); }
}
```

**Success Criteria:**

- [ ] Invitations expire after 7 days
- [ ] Once-only usage enforcement
- [ ] User cannot register without valid invitation
- [ ] Audit trail of who issued invitation to whom
- [ ] Password is hashed before storage

---

### Integration & Testing

**Create Integration Tests:**

```java
// src/test/java/com/neuralascent/identity/IdentityIntegrationTest.java
package com.neuralascent.identity;

import com.neuralascent.identity.domain.*;
import com.neuralascent.identity.persistence.*;
import com.neuralascent.identity.service.UserRegistrationService;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.security.test.context.support.WithMockUser;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.transaction.annotation.Transactional;
import static org.junit.jupiter.api.Assertions.*;

@SpringBootTest
@ActiveProfiles("test")
@Transactional
class IdentityIntegrationTest {
    
    @Autowired
    private UserRegistrationService registrationService;
    
    @Autowired
    private AppUserRepository userRepository;
    
    @Test
    void testRegisterWithValidInvitation() throws Exception {
        // Create invitation
        String invitationCode = "abc123def456";
        UserInvitation invitation = new UserInvitation();
        invitation.setEmail("newuser@example.com");
        invitation.setCode(invitationCode);
        invitation.setExpiresAt(java.time.LocalDateTime.now().plusDays(7));
        // Save via repository
        
        // Register
        AppUser user = registrationService.registerWithInvitation(
            "newuser@example.com",
            "New User",
            "SecurePass123!",
            invitationCode
        );
        
        assertNotNull(user.getId());
        assertEquals(UserStatus.ACTIVE, user.getStatus());
        assertTrue(user.getRoles().contains(UserRole.LEARNER));
    }
    
    @Test
    @WithMockUser(roles = "LEARNER")
    void testSuspendedUserCannotLogin() {
        // Test that suspended users are rejected by CustomUserDetailsService
    }
}
```

### Sprint 1 Deliverables

- [ ] `AppUser`, `UserRole`, `UserStatus` entities defined and mapped
- [ ] Spring Security configured with HttpOnly cookies and CSRF
- [ ] `CustomUserDetailsService` validates user status
- [ ] User registration via invitations
- [ ] Admin bootstrap account creation (documented)
- [ ] All unit & integration tests passing
- [ ] Database migrations applied
- [ ] README with "First Time Setup" instructions

### Success Criteria

- [ ] You can run `mvn clean test` and all identity tests pass
- [ ] You understand the difference between `.NET User.Identity` and Spring Security's `Authentication` principal
- [ ] You can explain why cookies are HttpOnly
- [ ] Invitations are single-use and time-limited
- [ ] Suspended users cannot authenticate

---

## Sprint 2: Authorization & Access Control

**Duration:** 2–3 weeks  
**TODO Tracker Phases:** P2  
**Java Topics:** Interfaces, inheritance, generics, polymorphism, streams  
**Spring Topics:** Spring Data JPA, method-level security, custom annotations

### Overview

Authorization means: after you know who the user is, can they do this action? Sprint 2 teaches you Java interfaces and polymorphism by building an access-policy engine that decides what lesson/vertical/hint-level a learner can access.

### Learning Objectives

By the end of Sprint 2:

- [ ] Define contracts with interfaces and understand polymorphism
- [ ] Use generics to write type-safe policy repositories
- [ ] Use Spring Data JPA `@Query` to write custom SQL safely
- [ ] Implement method-level security with `@PreAuthorize` and custom evaluators
- [ ] Understand the difference between authentication (who?) and authorization (what can they do?)
- [ ] Use streams and lambdas to filter data

### Platform Requirements (from TODO P2)

- [ ] Model content access: enrollment, vertical entitlements, course access
- [ ] Enforce access before retrieval (in SQL when possible, not post-retrieval)
- [ ] Cross-vertical access with policy checks
- [ ] Hint-level disclosure based on policy
- [ ] Solution-visibility control

### Migration Tasks

#### Task 1: Design Access Policy Model (Week 1)

**Java Concepts:** Interfaces, enums, design patterns

Create the access policy data model that determines what a user can access:

```java
// src/main/java/com/neuralascent/authorization/domain/ContentAccess.java
package com.neuralascent.authorization.domain;

import jakarta.persistence.*;
import lombok.*;
import java.util.UUID;

@Entity
@Table(name = "user_vertical_entitlement")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class VerticalEntitlement {
    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;
    
    private UUID userId;
    private String verticalCode; // e.g., "java-lld", "fde-curriculum"
    
    @Enumerated(EnumType.STRING)
    private AccessLevel accessLevel = AccessLevel.VIEW; // VIEW, HINT, SOLUTION
    
    private LocalDateTime grantedAt = LocalDateTime.now();
}

public enum AccessLevel {
    VIEW,           // Can see the lesson
    HINT,           // Can request hints
    SOLUTION        // Can see full solution
}

// src/main/java/com/neuralascent/authorization/domain/AccessPolicy.java
package com.neuralascent.authorization.domain;

import lombok.*;
import java.util.*;

/**
 * Immutable access decision for a user on a specific resource.
 * Returned by AccessPolicyService for authorization checks.
 */
@Value
@Builder
public class AccessPolicy {
    UUID userId;
    Set<String> allowedVerticalIds;
    Set<Integer> allowedCourseIds;
    Boolean currentLessonAccessible;
    Integer maximumHintLevel;       // 0=none, 1=nudge, 2=boundary, 3=pseudocode, 4=fragment, 5=solution
    Boolean solutionAllowed;
    Boolean futureConceptsAllowed;
    Boolean futureExercisesAllowed;
}

// src/main/java/com/neuralascent/authorization/domain/Enrollment.java
package com.neuralascent.authorization.domain;

import jakarta.persistence.*;
import lombok.*;
import java.time.LocalDateTime;
import java.util.UUID;

@Entity
@Table(name = "enrollment")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class Enrollment {
    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;
    
    private UUID userId;
    private Integer courseId;
    
    @Enumerated(EnumType.STRING)
    private EnrollmentStatus status = EnrollmentStatus.ACTIVE;
    
    private LocalDateTime enrolledAt = LocalDateTime.now();
    
    @Enumerated(EnumType.STRING)
    private AccessLevel accessLevel = AccessLevel.HINT;
}

public enum EnrollmentStatus {
    ACTIVE, SUSPENDED, COMPLETED, CANCELLED
}
```

**Practice Exercise from Java LLD Vertical:**

Review: **Interfaces & Polymorphism**  
Create an interface `AccessEvaluator` with a method `canAccess(User, Resource) -> boolean`. Create multiple implementations: `EnrollmentEvaluator`, `VerticalEntitlementEvaluator`, `AdminOverride`. Combine them in a composite `CompositeAccessEvaluator`.

---

#### Task 2: Access Policy Service (Week 1)

**Java Concepts:** Interfaces, generics, composition

```java
// src/main/java/com/neuralascent/authorization/service/AccessPolicyService.java
package com.neuralascent.authorization.service;

import com.neuralascent.authorization.domain.*;
import com.neuralascent.authorization.persistence.*;
import org.springframework.stereotype.Service;
import java.util.*;
import java.util.stream.Collectors;

/**
 * Central authorization service: answers "what can this user do?"
 */
@Service
public class AccessPolicyService {
    
    private final AppUserRepository userRepository;
    private final EnrollmentRepository enrollmentRepository;
    private final VerticalEntitlementRepository verticalEntitlementRepository;
    
    public AccessPolicyService(
        AppUserRepository userRepository,
        EnrollmentRepository enrollmentRepository,
        VerticalEntitlementRepository verticalEntitlementRepository
    ) {
        this.userRepository = userRepository;
        this.enrollmentRepository = enrollmentRepository;
        this.verticalEntitlementRepository = verticalEntitlementRepository;
    }
    
    /**
     * Compute full access policy for a user.
     * Returns immutable AccessPolicy object.
     */
    public AccessPolicy getAccessPolicy(UUID userId) {
        AppUser user = userRepository.findById(userId)
            .orElseThrow(() -> new UserNotFoundException(userId));
        
        // Admins can access everything
        if (user.getRoles().contains(UserRole.ADMIN)) {
            return AccessPolicy.builder()
                .userId(userId)
                .allowedVerticalIds(Set.of("java-lld", "fde-curriculum", "*"))
                .currentLessonAccessible(true)
                .maximumHintLevel(5)
                .solutionAllowed(true)
                .futureConceptsAllowed(true)
                .futureExercisesAllowed(true)
                .build();
        }
        
        // Learners: gather from enrollments + entitlements
        Set<Integer> allowedCourses = enrollmentRepository
            .findActiveByUserId(userId)
            .stream()
            .filter(e -> e.getStatus() == EnrollmentStatus.ACTIVE)
            .map(Enrollment::getCourseId)
            .collect(Collectors.toSet());
        
        Set<String> allowedVerticals = verticalEntitlementRepository
            .findByUserId(userId)
            .stream()
            .map(VerticalEntitlement::getVerticalCode)
            .collect(Collectors.toSet());
        
        int maxHintLevel = verticalEntitlementRepository
            .findByUserId(userId)
            .stream()
            .mapToInt(e -> mapAccessLevelToHintLevel(e.getAccessLevel()))
            .max()
            .orElse(1); // Default: level 1 (nudge)
        
        return AccessPolicy.builder()
            .userId(userId)
            .allowedVerticalIds(allowedVerticals)
            .allowedCourseIds(allowedCourses)
            .currentLessonAccessible(!allowedVerticals.isEmpty())
            .maximumHintLevel(maxHintLevel)
            .solutionAllowed(maxHintLevel >= 5)
            .futureConceptsAllowed(maxHintLevel >= 3)
            .futureExercisesAllowed(maxHintLevel >= 4)
            .build();
    }
    
    /**
     * Check if user can access a specific lesson.
     * Loads lesson from DB to verify it belongs to an allowed vertical.
     */
    public boolean canAccessLesson(UUID userId, Integer lessonId) {
        Lesson lesson = lessonRepository.findById(lessonId)
            .orElseThrow(() -> new LessonNotFoundException(lessonId));
        
        AccessPolicy policy = getAccessPolicy(userId);
        
        // Lesson must belong to an allowed vertical
        return policy.getAllowedVerticalIds().contains(lesson.getVerticalCode());
    }
    
    private int mapAccessLevelToHintLevel(AccessLevel level) {
        return switch (level) {
            case VIEW -> 1;
            case HINT -> 3;
            case SOLUTION -> 5;
        };
    }
}

// src/main/java/com/neuralascent/authorization/service/UserNotFoundException.java
public class UserNotFoundException extends RuntimeException {
    public UserNotFoundException(UUID userId) {
        super("User not found: " + userId);
    }
}
```

**Spring Data Repositories (Generics in Action):**

```java
// src/main/java/com/neuralascent/authorization/persistence/EnrollmentRepository.java
package com.neuralascent.authorization.persistence;

import com.neuralascent.authorization.domain.*;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;
import java.util.*;

@Repository
public interface EnrollmentRepository extends JpaRepository<Enrollment, UUID> {
    
    @Query("SELECT e FROM Enrollment e WHERE e.userId = :userId AND e.status = 'ACTIVE'")
    List<Enrollment> findActiveByUserId(@Param("userId") UUID userId);
    
    // Spring Data auto-generates this query
    List<Enrollment> findByUserIdAndStatus(UUID userId, EnrollmentStatus status);
    
    Optional<Enrollment> findByUserIdAndCourseId(UUID userId, Integer courseId);
}

// Generics: JpaRepository<Enrollment, UUID> means:
// - Entity type = Enrollment
// - ID type = UUID
// Spring will auto-generate type-safe find methods
```

**Practice Exercise from Java LLD Vertical:**

Review: **Generics & Type Bounds**  
Create a generic `PolicyCache<T>` that caches access policies. Use type bounds to ensure only `AccessPolicy` and its subtypes can be cached. Implement cache invalidation on user enrollment changes.

---

#### Task 3: Method-Level Security (Week 2)

**Java Concepts:** Annotations, reflection (transparent to you), lambda expressions

Use Spring Security's `@PreAuthorize` and custom security expressions:

```java
// src/main/java/com/neuralascent/tutor/api/TutorController.java
package com.neuralascent.tutor.api;

import com.neuralascent.authorization.service.AccessPolicyService;
import com.neuralascent.tutor.service.TutorService;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;
import java.util.UUID;

@RestController
@RequestMapping("/api/v1/tutor")
public class TutorController {
    
    private final TutorService tutorService;
    private final AccessPolicyService accessPolicyService;
    
    public TutorController(TutorService tutorService, AccessPolicyService accessPolicyService) {
        this.tutorService = tutorService;
        this.accessPolicyService = accessPolicyService;
    }
    
    /**
     * Only authenticated users can access their own tutor context.
     * Custom check ensures the lessonId belongs to their allowed vertical.
     */
    @PostMapping("/conversations/{conversationId}/messages:stream")
    @PreAuthorize("hasRole('LEARNER') or hasRole('ADMIN')")
    public void streamTutorMessage(
        @PathVariable UUID conversationId,
        @RequestBody MessageRequest request,
        Authentication auth
    ) {
        UUID userId = extractUserIdFromAuth(auth);
        
        // Custom authorization check
        if (!accessPolicyService.canAccessLesson(userId, request.getLessonId())) {
            throw new AccessDeniedException("You cannot access this lesson");
        }
        
        tutorService.streamTutorResponse(userId, conversationId, request);
    }
    
    @GetMapping("/conversations/{id}")
    @PreAuthorize("@conversationAccessEvaluator.canAccess(#auth.principal.name, #id)")
    public ConversationDTO getConversation(
        @PathVariable UUID id,
        Authentication auth
    ) {
        return tutorService.getConversation(id);
    }
    
    private UUID extractUserIdFromAuth(Authentication auth) {
        // Extract from JWT, session, or principal object
        return UUID.fromString(auth.getName()); // Simplified
    }
}

// src/main/java/com/neuralascent/tutor/security/ConversationAccessEvaluator.java
package com.neuralascent.tutor.security;

import com.neuralascent.tutor.persistence.ConversationRepository;
import org.springframework.stereotype.Component;
import java.util.UUID;

/**
 * Custom evaluator for @PreAuthorize expressions.
 * Allows @PreAuthorize("@conversationAccessEvaluator.canAccess(userId, conversationId)")
 */
@Component
public class ConversationAccessEvaluator {
    
    private final ConversationRepository conversationRepository;
    
    public ConversationAccessEvaluator(ConversationRepository conversationRepository) {
        this.conversationRepository = conversationRepository;
    }
    
    public boolean canAccess(String userIdString, UUID conversationId) {
        UUID userId = UUID.fromString(userIdString);
        var conversation = conversationRepository.findById(conversationId)
            .orElse(null);
        
        if (conversation == null) {
            return false; // Conversation not found
        }
        
        // User owns the conversation OR is an admin (checked by caller)
        return conversation.getOwnerUserId().equals(userId);
    }
}
```

**Success Criteria:**

- [ ] Suspended users cannot access any lessons
- [ ] Learner A cannot see Learner B's conversations
- [ ] Cross-vertical denial works: learner asking about FDE gets denied if not enrolled
- [ ] Admins bypass all checks
- [ ] Authorization checks happen before DB access when possible

---

### Integration & Testing

```java
// src/test/java/com/neuralascent/authorization/AuthorizationIntegrationTest.java
package com.neuralascent.authorization;

import static org.junit.jupiter.api.Assertions.*;
import org.junit.jupiter.api.Test;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.boot.test.context.SpringBootTest;

@SpringBootTest
@ActiveProfiles("test")
class AuthorizationIntegrationTest {
    
    @Test
    void testLearnerCannotAccessUnenrolledVertical() {
        // Create learner with access to java-lld only
        // Try to access fde-curriculum lesson
        // Verify ACCESS_DENIED
    }
    
    @Test
    void testCrossVerticalAllowedWhenPolicyPermits() {
        // Enroll learner in both java-lld and fde-curriculum
        // Ask tutor about fde while on java-lld page
        // Verify retrieval uses filtered chunks from fde
    }
}
```

### Sprint 2 Deliverables

- [ ] `Enrollment`, `VerticalEntitlement`, `AccessPolicy` entities
- [ ] `AccessPolicyService` with full policy resolution
- [ ] Custom `@PreAuthorize` evaluators for conversation/lesson access
- [ ] Cross-vertical authorization logic
- [ ] SQL queries that filter by enrollment/entitlement in WHERE clause
- [ ] Comprehensive authorization tests
- [ ] All integration tests passing

### Success Criteria

- [ ] You understand the difference between authentication and authorization
- [ ] You can explain polymorphism using your `AccessEvaluator` implementations
- [ ] You can write a generic Spring Data repository
- [ ] Cross-vertical access is properly denied/allowed by policy
- [ ] No unauthorized content is returned to learners

---

## Sprint 3: AI Gateway & Cost Management

**Duration:** 2–3 weeks  
**TODO Tracker Phases:** P3  
**Java Topics:** Exception handling, sealed classes, custom exceptions, enums  
**Spring Topics:** Spring Cloud Config, feature flags, custom decorators, transactional semantics

### Overview

This sprint teaches you how to safely call expensive external services (the LLM provider) without draining your budget or crashing the system. You'll learn Java's exception hierarchy, sealed classes (for type-safe routing decisions), and transactional guarantees for financial accuracy.

### Learning Objectives

- [ ] Design type-safe routing with sealed classes
- [ ] Use custom exceptions to represent business failures (rate limit, budget, quota)
- [ ] Understand `@Transactional` and acid guarantees for billing
- [ ] Use feature flags to toggle expensive features safely
- [ ] Implement circuit breakers for resilience
- [ ] Map .NET's `Result<T>` pattern to Java sealed classes

### Platform Requirements (from TODO P3)

- [ ] Provider-neutral `IAiChatClient` interface
- [ ] Admission-control pipeline (auth → rate limit → quota → budget → invoke)
- [ ] Token estimation before calling provider
- [ ] Token reconciliation after provider responds
- [ ] Rate limiting per user, IP, endpoint, globally
- [ ] Monetary quotas and budgets
- [ ] Idempotency with `clientRequestId`
- [ ] Global kill switches

### Migration Tasks

#### Task 1: Design Provider-Neutral Interfaces (Week 1)

**Java Concepts:** Interfaces, generics, sealed classes

```java
// src/main/java/com/neuralascent/ai/gateway/domain/ChatRequest.java
package com.neuralascent.ai.gateway.domain;

import lombok.*;
import java.util.List;

/**
 * Application-level AI request, independent of provider shape.
 * Translates to OpenAI-compatible JSON in the adapter.
 */
@Value
@Builder
public class ChatRequest {
    String conversationId;
    String clientRequestId;           // Idempotency key
    List<ChatMessage> messages;
    String systemPrompt;
    Integer maxTokens;
    String reasoningEffort;          // low, medium, high (Muse Spark specific)
    boolean returnStructuredOutput;
}

@Value
@Builder
public class ChatMessage {
    String role;                      // "system", "user", "assistant"
    String content;
    ChatMessageSource source;        // Metadata: is this from learner, LLM, RAG?
}

public enum ChatMessageSource {
    LEARNER_INPUT, SYSTEM, RAG_EVIDENCE, LLM_RESPONSE
}

// src/main/java/com/neuralascent/ai/gateway/domain/ChatResponse.java
package com.neuralascent.ai.gateway.domain;

import lombok.*;
import java.util.Map;

@Value
@Builder
public class ChatResponse {
    String content;
    String finishReason;              // "stop", "length", "tool_calls"
    UsageInfo usage;
    Map<String, Object> structuredOutput;
    String modelId;
    long latencyMs;
    String traceId;
}

@Value
public class UsageInfo {
    int inputTokens;
    int cachedInputTokens;           // Cached prompt tokens (cheaper)
    int outputTokens;
    int reasoningTokens;             // Only Muse Spark
    int totalTokens;
}

// src/main/java/com/neuralascent/ai/gateway/domain/Route.java
package com.neuralascent.ai.gateway.domain;

/**
 * Sealed class ensures exhaustive pattern matching on routing decisions.
 * Only these subtypes are allowed—compiler enforces it.
 */
public sealed interface Route {
    record CurrentContextRoute() implements Route {}
    record CurrentVerticalRagRoute() implements Route {}
    record CrossVerticalRagRoute(String targetVertical) implements Route {}
    record ClarificationRequiredRoute() implements Route {}
    record GeneralKnowledgeRoute() implements Route {}
    record AccessDeniedRoute(String reason) implements Route {}
}

// Sealed class example (Java 21 preview → record):
// switch (route) {
//     case Route.CurrentContextRoute r -> handleCurrentContext();
//     case Route.AccessDeniedRoute r -> return r.reason();
//     // Compiler ensures all cases covered
// }
```

**Practice Exercise from Java LLD Vertical:**

Review: **Sealed Classes & Records**  
Create a sealed `PaymentResult` interface with `Success(Transaction)`, `Failure(String reason)`, `Pending(String reference)`. Use pattern matching in a switch to handle each case.

#### Task 2: Admission Control Pipeline (Week 1–2)

**Java Concepts:** Custom exceptions, decorators, transactional semantics

```java
// src/main/java/com/neuralascent/ai/gateway/service/AiGateway.java
package com.neuralascent.ai.gateway.service;

import com.neuralascent.ai.gateway.domain.*;
import com.neuralascent.authorization.domain.AccessPolicy;
import com.neuralascent.authorization.service.AccessPolicyService;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.util.UUID;

/**
 * Central AI gateway: orchestrates the admission-control pipeline.
 * Every paid AI call passes through here.
 */
@Service
public class AiGateway {
    
    private final AiChatClient chatClient;           // Provider-specific adapter
    private final AccessPolicyService accessPolicy;
    private final RateLimitService rateLimitService;
    private final QuotaService quotaService;
    private final BudgetService budgetService;
    private final TokenEstimator tokenEstimator;
    private final IdempotencyService idempotencyService;
    private final AiInvocationRepository invocationRepository;
    
    /**
     * Main entry point: Process a chat request with full admission control.
     * 
     * Pipeline:
     * 1. Authenticate & authorize
     * 2. Check rate limits
     * 3. Check per-user quota
     * 4. Check global budget
     * 5. Estimate tokens
     * 6. Reserve tokens atomically
     * 7. Check idempotency
     * 8. Invoke provider
     * 9. Reconcile actual usage
     * 
     * @throws RateLimitExceededException if rate limits hit
     * @throws QuotaExceededException if user quota exceeded
     * @throws BudgetExceededException if global budget exhausted
     */
    @Transactional
    public ChatResponse processChat(UUID userId, ChatRequest request) 
        throws AiGatewayException {
        
        // Step 1: Authorization
        AccessPolicy policy = accessPolicy.getAccessPolicy(userId);
        if (!policy.getCurrentLessonAccessible()) {
            throw new AccessDeniedException("User not enrolled in any vertical");
        }
        
        // Step 2: Rate limits
        if (!rateLimitService.allowRequest(userId, request.getConversationId())) {
            throw new RateLimitExceededException("User rate limit exceeded");
        }
        
        // Step 3: Per-user quota
        QuotaStatus quotaStatus = quotaService.checkQuota(userId);
        if (quotaStatus.isExhausted()) {
            throw new QuotaExceededException("Monthly quota exhausted");
        }
        
        // Step 4: Global budget
        if (!budgetService.canAfford(request.getMaxTokens())) {
            throw new BudgetExceededException("Global budget limit reached");
        }
        
        // Step 5: Token estimation
        int estimatedTokens = tokenEstimator.estimateTokens(request);
        
        // Step 6: Reserve atomically (prevent concurrent overspend)
        UsageReservation reservation = quotaService.reserve(
            userId,
            estimatedTokens,
            request.getClientRequestId()
        );
        
        try {
            // Step 7: Check idempotency
            var cached = idempotencyService.findCachedResponse(
                userId,
                request.getClientRequestId()
            );
            if (cached.isPresent()) {
                return cached.get();
            }
            
            // Step 8: Invoke provider
            ChatResponse response = chatClient.chat(request);
            
            // Step 9: Reconcile actual usage
            quotaService.reconcile(
                userId,
                reservation.getId(),
                response.getUsage(),
                response.getModelId()
            );
            
            // Cache for idempotency
            idempotencyService.cache(userId, request.getClientRequestId(), response);
            
            // Log invocation for admin dashboard
            logInvocation(userId, request, response, reservation);
            
            return response;
            
        } catch (Exception e) {
            // Release reservation on failure
            quotaService.rollback(reservation.getId());
            throw e;
        }
    }
    
    private void logInvocation(UUID userId, ChatRequest request, 
                              ChatResponse response, UsageReservation reservation) {
        AiInvocation invocation = new AiInvocation();
        invocation.setUserId(userId);
        invocation.setConversationId(request.getConversationId());
        invocation.setEstimatedTokens(reservation.getEstimatedTokens());
        invocation.setActualInputTokens(response.getUsage().getInputTokens());
        invocation.setActualOutputTokens(response.getUsage().getOutputTokens());
        // ... more fields
        
        invocationRepository.save(invocation);
    }
}

// Custom exceptions (Java exception hierarchy)
public class AiGatewayException extends RuntimeException {
    public AiGatewayException(String message) { super(message); }
    public AiGatewayException(String message, Throwable cause) { super(message, cause); }
}

public class RateLimitExceededException extends AiGatewayException {
    public RateLimitExceededException(String message) { super(message); }
}

public class QuotaExceededException extends AiGatewayException {
    public QuotaExceededException(String message) { super(message); }
}

public class BudgetExceededException extends AiGatewayException {
    public BudgetExceededException(String message) { super(message); }
}

public class AccessDeniedException extends AiGatewayException {
    public AccessDeniedException(String message) { super(message); }
}
```

**Rate Limiting Service (using Redisson or local cache):**

```java
// src/main/java/com/neuralascent/ai/gateway/service/RateLimitService.java
package com.neuralascent.ai.gateway.service;

import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.stereotype.Service;
import java.util.concurrent.TimeUnit;
import java.util.UUID;

@Service
public class RateLimitService {
    
    private final RedisTemplate<String, Integer> redisTemplate;
    private final RateLimitConfig config;
    
    public RateLimitService(RedisTemplate<String, Integer> redisTemplate, RateLimitConfig config) {
        this.redisTemplate = redisTemplate;
        this.config = config;
    }
    
    /**
     * Sliding window rate limiter.
     * Key: user:{userId}:messages:minute
     * Value: current count
     * TTL: 60 seconds (resets automatically)
     */
    public boolean allowRequest(UUID userId, String conversationId) {
        String key = "ratelimit:user:" + userId + ":minute";
        Integer count = redisTemplate.opsForValue().get(key);
        int currentCount = (count == null) ? 0 : count;
        
        if (currentCount >= config.getMessagesPerMinute()) {
            return false; // Limit exceeded
        }
        
        redisTemplate.opsForValue().increment(key);
        if (currentCount == 0) {
            // First request in this window: set expiry
            redisTemplate.expire(key, 60, TimeUnit.SECONDS);
        }
        
        return true;
    }
}

public class RateLimitConfig {
    public int getMessagesPerMinute() { return 6; }
    public int getMessagesPerHour() { return 30; }
    public int getMessagesPerDay() { return 100; }
}
```

**Token Estimation:**

```java
// src/main/java/com/neuralascent/ai/gateway/service/TokenEstimator.java
package com.neuralascent.ai.gateway.service;

import com.neuralascent.ai.gateway.domain.ChatRequest;
import org.springframework.stereotype.Service;

@Service
public class TokenEstimator {
    
    /**
     * Rough token estimation (before calling provider).
     * Use for admission control only; provider gives ground truth.
     * 
     * Rule of thumb: 1 token ≈ 4 characters for English
     */
    public int estimateTokens(ChatRequest request) {
        int messageTokens = request.getMessages().stream()
            .mapToInt(msg -> msg.getContent().length() / 4)
            .sum();
        
        int systemTokens = request.getSystemPrompt().length() / 4;
        
        // Add buffer for reasoning tokens, formatting, etc.
        return messageTokens + systemTokens + 100;
    }
}
```

**Quota Management (transactional):**

```java
// src/main/java/com/neuralascent/ai/gateway/domain/UsageReservation.java
package com.neuralascent.ai.gateway.domain;

import jakarta.persistence.*;
import lombok.*;
import java.time.LocalDateTime;
import java.util.UUID;

@Entity
@Table(name = "ai_usage_reservation")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class UsageReservation {
    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;
    
    private UUID userId;
    private String clientRequestId;           // Idempotency key
    
    private int estimatedTokens;
    private int actualInputTokens;
    private int actualOutputTokens;
    private int actualReasoningTokens;
    
    @Enumerated(EnumType.STRING)
    private ReservationStatus status = ReservationStatus.RESERVED;
    
    private LocalDateTime createdAt = LocalDateTime.now();
    private LocalDateTime reconciliedAt;
}

public enum ReservationStatus {
    RESERVED, COMMITTED, ROLLED_BACK, FAILED
}

// src/main/java/com/neuralascent/ai/gateway/service/QuotaService.java
package com.neuralascent.ai.gateway.service;

import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.util.UUID;

@Service
public class QuotaService {
    
    private final UsageReservationRepository reservationRepository;
    private final AiQuotaPolicyRepository policyRepository;
    
    /**
     * Reserve tokens atomically. Prevents concurrent quota overspend.
     * 
     * @throws QuotaExceededException if reservation would exceed quota
     */
    @Transactional
    public UsageReservation reserve(UUID userId, int estimatedTokens, String clientRequestId) 
        throws QuotaExceededException {
        
        // Check if already reserved (idempotency)
        var existing = reservationRepository.findByUserIdAndClientRequestId(userId, clientRequestId);
        if (existing.isPresent()) {
            return existing.get();
        }
        
        // Load policy for this user
        AiQuotaPolicy policy = policyRepository.findByUserId(userId)
            .orElseThrow(() -> new QuotaPolicyNotFoundException(userId));
        
        // Calculate current month usage
        int currentMonthUsage = reservationRepository
            .sumCommittedTokensByUserAndMonth(userId, LocalDate.now().getYear(), 
                                             LocalDate.now().getMonthValue());
        
        // Check against policy
        if (currentMonthUsage + estimatedTokens > policy.getMonthlyTokenLimit()) {
            throw new QuotaExceededException(
                String.format("Would exceed quota: %d + %d > %d",
                    currentMonthUsage, estimatedTokens, policy.getMonthlyTokenLimit())
            );
        }
        
        // Create reservation
        UsageReservation reservation = new UsageReservation();
        reservation.setUserId(userId);
        reservation.setClientRequestId(clientRequestId);
        reservation.setEstimatedTokens(estimatedTokens);
        reservation.setStatus(ReservationStatus.RESERVED);
        
        return reservationRepository.save(reservation);
    }
    
    /**
     * Commit reservation with actual usage from provider.
     */
    @Transactional
    public void reconcile(UUID userId, UUID reservationId, UsageInfo usage, String modelId) {
        UsageReservation reservation = reservationRepository.findById(reservationId)
            .orElseThrow();
        
        reservation.setActualInputTokens(usage.getInputTokens());
        reservation.setActualOutputTokens(usage.getOutputTokens());
        reservation.setActualReasoningTokens(usage.getReasoningTokens());
        reservation.setStatus(ReservationStatus.COMMITTED);
        reservation.setReconciliedAt(LocalDateTime.now());
        
        reservationRepository.save(reservation);
        
        // Update daily/monthly totals
        updateDailyUsage(userId, usage, modelId);
    }
    
    /**
     * Rollback failed reservation.
     */
    @Transactional
    public void rollback(UUID reservationId) {
        UsageReservation reservation = reservationRepository.findById(reservationId)
            .orElseThrow();
        
        reservation.setStatus(ReservationStatus.ROLLED_BACK);
        reservationRepository.save(reservation);
    }
}
```

**Practice Exercise from Java LLD Vertical:**

Review: **Custom Exceptions & Inheritance**  
Create an exception hierarchy: `AiGatewayException` (base) → `AiProviderException`, `AiQuotaException`, `AiRateLimitException`. Each logs differently. Implement `@ExceptionHandler` in a controller to return appropriate HTTP status codes (429 for rate limit, 402 for quota, 500 for provider error).

**Compare to .NET:**

| .NET | Java |
|-----|------|
| `try-catch` with `HttpRequestException` | `try-catch` with custom exception hierarchy |
| `IConfiguration["Quotas:MonthlyLimit"]` | `@ConfigurationProperties("quotas")` → POJO |
| `IDistributedCache` (Redis) | Spring `RedisTemplate<K, V>` with generics |
| `Result<T>` pattern (custom) | Sealed interfaces for exhaustive matching |

---

#### Task 3: Provider Adapter (Week 2)

**Java Concepts:** Adapter pattern, exception translation

```java
// src/main/java/com/neuralascent/ai/provider/AiChatClient.java
package com.neuralascent.ai.provider;

import com.neuralascent.ai.gateway.domain.*;

/**
 * Provider-neutral interface.
 * Implementations: MuseSparkAdapter, OpenAiAdapter, AnthropicAdapter
 */
public interface AiChatClient {
    ChatResponse chat(ChatRequest request) throws AiProviderException;
}

// src/main/java/com/neuralascent/ai/provider/MuseSparkAdapter.java
package com.neuralascent.ai.provider;

import com.neuralascent.ai.gateway.domain.*;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;
import java.util.*;

/**
 * Adapter for Meta Muse Spark 1.2 (OpenAI-compatible API).
 * Translates internal ChatRequest → OpenAI JSON → provider response → ChatResponse.
 */
@Slf4j
@Service
public class MuseSparkAdapter implements AiChatClient {
    
    private final RestTemplate restTemplate;
    
    @Value("${ai.provider.muse-spark.api-key}")
    private String apiKey;
    
    @Value("${ai.provider.muse-spark.api-url}")
    private String apiUrl;
    
    public MuseSparkAdapter(RestTemplate restTemplate) {
        this.restTemplate = restTemplate;
    }
    
    @Override
    public ChatResponse chat(ChatRequest request) throws AiProviderException {
        try {
            // Translate to OpenAI format
            OpenAiRequest openAiRequest = translateRequest(request);
            
            // Call provider
            long startTime = System.currentTimeMillis();
            OpenAiResponse openAiResponse = callProvider(openAiRequest);
            long latencyMs = System.currentTimeMillis() - startTime;
            
            // Translate back to internal format
            return translateResponse(openAiResponse, latencyMs);
            
        } catch (Exception e) {
            log.error("Muse Spark request failed", e);
            throw new AiProviderException("Muse Spark API error: " + e.getMessage(), e);
        }
    }
    
    private OpenAiRequest translateRequest(ChatRequest request) {
        OpenAiRequest openAi = new OpenAiRequest();
        openAi.setModel("muse-spark-1.2");
        openAi.setMessages(request.getMessages().stream()
            .map(msg -> new OpenAiMessage(msg.getRole(), msg.getContent()))
            .toList()
        );
        openAi.setMaxTokens(request.getMaxTokens());
        openAi.setReasoningEffort(request.getReasoningEffort());
        
        // Add structured output tool if requested
        if (request.isReturnStructuredOutput()) {
            openAi.setTools(List.of(new ToolDefinition("emit_tutor_response", 
                getTutorResponseSchema())));
            openAi.setToolChoice("auto");
        }
        
        return openAi;
    }
    
    private ChatResponse translateResponse(OpenAiResponse openAi, long latencyMs) {
        String content = extractContent(openAi);
        Map<String, Object> structured = extractStructuredOutput(openAi);
        
        return ChatResponse.builder()
            .content(content)
            .finishReason(openAi.getChoices().get(0).getFinishReason())
            .usage(new UsageInfo(
                openAi.getUsage().getPromptTokens(),
                openAi.getUsage().getPromptTokensDetails().getCachedTokens(),
                openAi.getUsage().getCompletionTokens(),
                openAi.getUsage().getCompletionTokensDetails().getReasoningTokens(),
                openAi.getUsage().getTotalTokens()
            ))
            .structuredOutput(structured)
            .modelId("muse-spark-1.2")
            .latencyMs(latencyMs)
            .traceId(openAi.getId())
            .build();
    }
    
    private OpenAiResponse callProvider(OpenAiRequest request) {
        // HTTP call with timeout, retry, circuit breaker
        return restTemplate.postForObject(
            apiUrl + "/v1/chat/completions",
            request,
            OpenAiResponse.class
        );
    }
    
    private String extractContent(OpenAiResponse openAi) {
        var choice = openAi.getChoices().get(0);
        if ("tool_calls".equals(choice.getFinishReason())) {
            // Structured output mode
            return choice.getMessage().getToolCalls().get(0).getFunction().getArguments();
        }
        return choice.getMessage().getContent();
    }
    
    private Map<String, Object> extractStructuredOutput(OpenAiResponse openAi) {
        // Parse tool call JSON if present
        return Collections.emptyMap();
    }
    
    private Map<String, Object> getTutorResponseSchema() {
        // JSON Schema for emit_tutor_response function
        return Map.of(
            "type", "object",
            "properties", Map.of(
                "answerType", Map.of("type", "string"),
                "hintLevel", Map.of("type", "integer"),
                "messageMarkdown", Map.of("type", "string")
            )
        );
    }
}

// Helper DTOs for OpenAI shape
@Data
class OpenAiRequest {
    String model;
    List<OpenAiMessage> messages;
    int maxTokens;
    String reasoningEffort;
    List<ToolDefinition> tools;
    String toolChoice;
}

@Data
@AllArgsConstructor
class OpenAiMessage {
    String role;
    String content;
}

// ... response DTOs similar structure

public class AiProviderException extends RuntimeException {
    public AiProviderException(String message, Throwable cause) { super(message, cause); }
}
```

**Success Criteria:**

- [ ] Provider adapter translates requests without data loss
- [ ] Token counts from provider are reconciled against reservations
- [ ] Circuit breaker prevents cascade failures
- [ ] Timeouts prevent hanging indefinitely
- [ ] Idempotency works: same `clientRequestId` returns cached response

---

### Integration & Testing

```java
// src/test/java/com/neuralascent/ai/gateway/AiGatewayIntegrationTest.java
package com.neuralascent.ai.gateway;

import static org.junit.jupiter.api.Assertions.*;
import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;

@SpringBootTest
class AiGatewayIntegrationTest {
    
    @Test
    void testRateLimitEnforced() {
        // Send 7 requests in a minute
        // 7th should be rejected with 429
    }
    
    @Test
    void testIdempotencyPreventsDuplicate() {
        // Send same request twice with same clientRequestId
        // Should return cached response, single provider call
    }
    
    @Test
    void testQuotaReservationRolls BackOnFailure() {
        // Mock provider to fail
        // Verify reservation is rolled back
        // Verify quota is not consumed
    }
}
```

### Sprint 3 Deliverables

- [ ] `IAiChatClient` interface and first implementation (Muse Spark adapter)
- [ ] Provider-neutral request/response DTOs
- [ ] Full admission-control pipeline with all checks
- [ ] Rate limiting service (Redis-backed)
- [ ] Quota & budget management with atomic reservations
- [ ] Token estimation service
- [ ] Idempotency caching
- [ ] Custom exception hierarchy
- [ ] Exception handler returning appropriate HTTP status codes
- [ ] All integration tests passing
- [ ] `AiInvocation` table for admin dashboard

### Success Criteria

- [ ] You can explain the admission-control pipeline in order
- [ ] You understand sealed classes and pattern matching
- [ ] You know why `@Transactional` matters for billing
- [ ] Rate limit + quota + budget tests pass
- [ ] Provider can be swapped by changing one bean definition
- [ ] Idempotency prevents duplicate charges

---

## Sprint 4: Current-Context Learning Tutor

**Duration:** 2–3 weeks  
**TODO Tracker Phases:** P4  
**Java Topics:** Streams, lambdas, functional programming, optional chaining  
**Spring Topics:** SSE (Server-Sent Events), Spring MVC, streaming responses

### Overview

Now that you've built the foundation (identity, authorization, AI gateway), you'll create the tutor itself—the feature that makes NeuralAscent useful. You'll learn how to stream responses to the browser using SSE, compose complex logic with streams/lambdas, and handle the stateful "where is the learner in the course?" problem.

### Learning Objectives

- [ ] Use Java streams and lambdas to filter, transform, and combine data
- [ ] Implement SSE streaming to browser
- [ ] Design a "context resolver" that determines the current lesson/exercise
- [ ] Build progressive hint logic
- [ ] Validate structured model output (JSON schema)
- [ ] Understand functional composition

### Platform Requirements (from TODO P4)

- [ ] Exact context resolver (lesson/exercise resolved by ID)
- [ ] Progressive hint levels 1–5
- [ ] Structured tutor output with schema validation
- [ ] Streaming protocol to browser
- [ ] Ownership and authorization checks before tutor invocation

### Migration Tasks

#### Task 1: Page Context & Exact Resolver (Week 1)

**Java Concepts:** Streams, optional chaining, immutability

```java
// src/main/java/com/neuralascent/tutor/domain/PageContext.java
package com.neuralascent.tutor.domain;

import lombok.*;
import java.util.Optional;

/**
 * Immutable claim about what page/exercise the browser is on.
 * This is untrusted input — client claims it's on lesson X.
 * Server verifies and loads authoritative data.
 */
@Value
@Builder
public class PageContext {
    String vertical;                          // e.g., "java-lld"
    String moduleSlug;
    String lessonSlug;
    Optional<Integer> lessonId;              // Client-provided hint
    Optional<Integer> exerciseId;            // Client-provided hint
    Optional<String> selectedCode;           // Untrusted editor content
    Optional<String> visibleSectionAnchor;   // Which HTML section in viewport
}

// src/main/java/com/neuralascent/tutor/service/TutorContextResolver.java
package com.neuralascent.tutor.service;

import com.neuralascent.authorization.service.AccessPolicyService;
import com.neuralascent.curriculum.persistence.LessonRepository;
import com.neuralascent.tutor.domain.PageContext;
import org.springframework.stereotype.Service;
import java.util.UUID;
import java.util.Optional;

/**
 * Resolves the true, authoritative context of what the learner is working on.
 * 
 * Trust model:
 * - Browser sends PageContext claiming "I'm on lesson X"
 * - Resolver loads lesson X from DB (don't trust client claim)
 * - Resolver verifies user is enrolled in that lesson's vertical
 * - If ID wrong/unauthorized: return error, not guessing via RAG
 */
@Service
public class TutorContextResolver {
    
    private final LessonRepository lessonRepository;
    private final ExerciseRepository exerciseRepository;
    private final AccessPolicyService accessPolicy;
    
    public TutorContextResolver(
        LessonRepository lessonRepository,
        ExerciseRepository exerciseRepository,
        AccessPolicyService accessPolicy
    ) {
        this.lessonRepository = lessonRepository;
        this.exerciseRepository = exerciseRepository;
        this.accessPolicy = accessPolicy;
    }
    
    /**
     * Resolve context by trusting only the numeric IDs, not page claims.
     */
    public TutorContext resolve(UUID userId, PageContext claim) 
        throws ContextResolutionException {
        
        // If browser provided lessonId, resolve it
        if (claim.getLessonId().isPresent()) {
            return resolveByLessonId(userId, claim.getLessonId().get(), claim);
        }
        
        // If exerciseId provided, resolve its lesson
        if (claim.getExerciseId().isPresent()) {
            return resolveByExerciseId(userId, claim.getExerciseId().get(), claim);
        }
        
        // If no ID: this is a malformed context. Don't guess.
        throw new ContextResolutionException("No lessonId or exerciseId provided");
    }
    
    private TutorContext resolveByLessonId(UUID userId, Integer lessonId, PageContext claim) 
        throws ContextResolutionException {
        
        // Load lesson from DB (authoritative)
        var lesson = lessonRepository.findById(lessonId)
            .orElseThrow(() -> new ContextResolutionException("Lesson not found: " + lessonId));
        
        // Verify user can access this vertical
        if (!accessPolicy.canAccessLesson(userId, lessonId)) {
            throw new ContextResolutionException("Access denied to lesson: " + lessonId);
        }
        
        return TutorContext.builder()
            .userId(userId)
            .lesson(lesson)
            .exercise(Optional.empty())
            .selectedCode(claim.getSelectedCode())
            .visibleSection(claim.getVisibleSectionAnchor())
            .build();
    }
    
    private TutorContext resolveByExerciseId(UUID userId, Integer exerciseId, PageContext claim)
        throws ContextResolutionException {
        
        // Load exercise and its lesson
        var exercise = exerciseRepository.findById(exerciseId)
            .orElseThrow(() -> new ContextResolutionException("Exercise not found: " + exerciseId));
        
        var lesson = lessonRepository.findById(exercise.getLessonId())
            .orElseThrow(() -> new ContextResolutionException("Lesson not found"));
        
        // Verify access to this lesson/vertical
        if (!accessPolicy.canAccessLesson(userId, lesson.getId())) {
            throw new ContextResolutionException("Access denied");
        }
        
        return TutorContext.builder()
            .userId(userId)
            .lesson(lesson)
            .exercise(Optional.of(exercise))
            .selectedCode(claim.getSelectedCode())
            .visibleSection(claim.getVisibleSectionAnchor())
            .build();
    }
}

// Immutable resolved context
@Value
@Builder
public class TutorContext {
    UUID userId;
    Lesson lesson;
    Optional<Exercise> exercise;
    Optional<String> selectedCode;
    Optional<String> visibleSection;
}

public class ContextResolutionException extends RuntimeException {
    public ContextResolutionException(String message) { super(message); }
}
```

**Practice Exercise from Java LLD Vertical:**

Review: **Streams & Functional Programming**  
Stream a list of lessons; filter by vertical; map to lesson titles; sort by module; collect into a nested structure (Map<Module, List<Lesson>>).

#### Task 2: Progressive Hints (Week 1)

**Java Concepts:** Enums, switch expressions

```java
// src/main/java/com/neuralascent/tutor/domain/HintLevel.java
package com.neuralascent.tutor.domain;

public enum HintLevel {
    NONE(0, "No hint"),
    NUDGE(1, "Conceptual nudge or guiding question"),
    BOUNDARY(2, "Responsibility boundaries, interfaces"),
    PSEUDOCODE(3, "Algorithm or pseudocode"),
    FRAGMENT(4, "Limited signature or method fragment"),
    SOLUTION(5, "Full solution");
    
    private final int level;
    private final String description;
    
    HintLevel(int level, String description) {
        this.level = level;
        this.description = description;
    }
    
    public int getLevel() { return level; }
    public String getDescription() { return description; }
    
    public static HintLevel fromLevel(int level) {
        return switch (level) {
            case 0 -> NONE;
            case 1 -> NUDGE;
            case 2 -> BOUNDARY;
            case 3 -> PSEUDOCODE;
            case 4 -> FRAGMENT;
            case 5 -> SOLUTION;
            default -> throw new IllegalArgumentException("Unknown level: " + level);
        };
    }
}

// src/main/java/com/neuralascent/tutor/service/ProgressiveHintService.java
package com.neuralascent.tutor.service;

import com.neuralascent.authorization.domain.AccessPolicy;
import com.neuralascent.tutor.domain.*;
import org.springframework.stereotype.Service;
import java.util.UUID;

@Service
public class ProgressiveHintService {
    
    private final ExerciseAttemptRepository attemptRepository;
    private final ExerciseHintRepository hintRepository;
    
    /**
     * Determine which hint level to grant based on:
     * - User's policy (max allowed)
     * - User's attempt count (progressive disclosure)
     * - Previous hints issued (don't repeat)
     */
    public HintLevel decideHintLevel(
        UUID userId,
        Integer exerciseId,
        AccessPolicy userPolicy,
        HintLevel requested
    ) throws HintDenialException {
        
        // Cap at user's policy maximum
        int maxAllowedLevel = userPolicy.getMaximumHintLevel();
        if (requested.getLevel() > maxAllowedLevel) {
            throw new HintDenialException(
                String.format("Your policy allows hints up to level %d", maxAllowedLevel)
            );
        }
        
        // Check if user already got this hint level
        var existingHint = hintRepository.findByUserAndExerciseAndLevel(userId, exerciseId, requested);
        if (existingHint.isPresent()) {
            // Return cached hint (learner requested same level again)
            return requested;
        }
        
        // Check attempt count (learner must attempt before hints)
        int attempts = attemptRepository.countByUserAndExercise(userId, exerciseId);
        if (attempts == 0 && requested.getLevel() > HintLevel.NUDGE.getLevel()) {
            throw new HintDenialException("Try the exercise first, then ask for hints");
        }
        
        return requested;
    }
}

public class HintDenialException extends RuntimeException {
    public HintDenialException(String message) { super(message); }
}
```

#### Task 3: Tutor Service & Streaming (Week 2)

**Java Concepts:** Stream API, functional composition, exception handling  
**Spring Topics:** SSE, streaming responses

```java
// src/main/java/com/neuralascent/tutor/service/TutorService.java
package com.neuralascent.tutor.service;

import com.neuralascent.ai.gateway.domain.*;
import com.neuralascent.ai.gateway.service.AiGateway;
import com.neuralascent.authorization.service.AccessPolicyService;
import com.neuralascent.curriculum.domain.Lesson;
import com.neuralascent.curriculum.persistence.LessonRepository;
import com.neuralascent.tutor.domain.*;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.util.*;
import java.util.stream.Collectors;

@Service
public class TutorService {
    
    private final AiGateway aiGateway;
    private final TutorContextResolver contextResolver;
    private final AccessPolicyService accessPolicy;
    private final ProgressiveHintService hintService;
    private final ConversationRepository conversationRepository;
    private final ConversationMessageRepository messageRepository;
    private final TutorResponseValidator responseValidator;
    
    /**
     * Main entry point: process learner message and stream tutor response.
     * 
     * 1. Resolve exact context (lesson/exercise)
     * 2. Check access policy
     * 3. Prepare tutor prompt (learner context + question + hints)
     * 4. Call AI gateway with admission control
     * 5. Validate structured output
     * 6. Enforce solution disclosure policy
     * 7. Stream response events to browser
     * 8. Persist conversation
     */
    @Transactional
    public void streamTutorResponse(
        UUID userId,
        UUID conversationId,
        MessageRequest request,
        ResponseEventSink eventSink
    ) throws TutorException {
        
        try {
            // Step 1: Resolve context
            TutorContext context = contextResolver.resolve(userId, request.getPageContext());
            
            // Step 2: Access control
            if (!accessPolicy.canAccessLesson(userId, context.getLesson().getId())) {
                throw new TutorException("Access denied to this lesson");
            }
            
            // Step 3: Prepare prompt
            String systemPrompt = buildTutorSystemPrompt(context);
            List<ChatMessage> messages = buildTutorMessages(userId, context, request);
            
            // Step 4: Call AI gateway
            ChatRequest aiRequest = ChatRequest.builder()
                .conversationId(conversationId.toString())
                .clientRequestId(UUID.randomUUID().toString()) // Idempotency
                .systemPrompt(systemPrompt)
                .messages(messages)
                .maxTokens(1500)
                .reasoningEffort("low")  // Current context, no extra reasoning needed
                .returnStructuredOutput(true)
                .build();
            
            ChatResponse aiResponse = aiGateway.processChat(userId, aiRequest);
            
            // Step 5: Validate & parse structured output
            TutorResponse tutorResponse = responseValidator.validate(aiResponse);
            
            // Step 6: Enforce policy (block solution if not allowed)
            if (!accessPolicy.getAccessPolicy(userId).isSolutionAllowed() &&
                tutorResponse.getSolutionDisclosure() == SolutionDisclosure.FULL) {
                tutorResponse = tutorResponse.withSolutionDisclosure(SolutionDisclosure.PARTIAL);
            }
            
            // Step 7: Stream events
            eventSink.emit(new TutorEvent.Accepted(conversationId));
            eventSink.emit(new TutorEvent.Route(tutorResponse.getRoute()));
            eventSink.emit(new TutorEvent.Content(tutorResponse.getMessageMarkdown()));
            
            // Stream token by token if using SSE
            for (String token : tutorResponse.getMessageMarkdown().split(" ")) {
                eventSink.emit(new TutorEvent.Token(token));
            }
            
            eventSink.emit(new TutorEvent.Complete(tutorResponse));
            
            // Step 8: Persist conversation
            persistConversation(userId, conversationId, request, tutorResponse);
            
        } catch (TutorException e) {
            eventSink.emit(new TutorEvent.Error(e.getMessage()));
            throw e;
        }
    }
    
    private String buildTutorSystemPrompt(TutorContext context) {
        return String.format("""
            You are a progressive, Socratic learning tutor for %s.
            
            Current lesson: %s
            Exercise: %s
            
            Guidelines:
            - Ask clarifying questions, don't immediately solve
            - Build toward understanding through reflection
            - Reference specific concepts from the lesson
            - Guide the learner to discover the solution
            """,
            context.getLesson().getVerticalCode(),
            context.getLesson().getTitle(),
            context.getExercise().map(e -> e.getTitle()).orElse("(review mode)")
        );
    }
    
    private List<ChatMessage> buildTutorMessages(UUID userId, TutorContext context, MessageRequest request) {
        return List.of(
            ChatMessage.builder()
                .role("system")
                .content(buildTutorSystemPrompt(context))
                .source(ChatMessageSource.SYSTEM)
                .build(),
            ChatMessage.builder()
                .role("user")
                .content(String.format(
                    "Lesson: %s\nExercise: %s\nMy question: %s\nMy attempt:\n```\n%s\n```",
                    context.getLesson().getTitle(),
                    context.getExercise().map(e -> e.getTitle()).orElse("N/A"),
                    request.getMessage(),
                    context.getSelectedCode().orElse("(no code yet)")
                ))
                .source(ChatMessageSource.LEARNER_INPUT)
                .build()
        );
    }
    
    private void persistConversation(UUID userId, UUID conversationId, 
                                    MessageRequest request, TutorResponse response) {
        // Save message and response to database
        ConversationMessage message = new ConversationMessage();
        message.setConversationId(conversationId);
        message.setRole("user");
        message.setContent(request.getMessage());
        message.setTimestamp(LocalDateTime.now());
        
        messageRepository.save(message);
    }
}

// Immutable request
@Value
public class MessageRequest {
    String message;
    PageContext pageContext;
}

// Events streamed to browser
public sealed interface TutorEvent {
    record Accepted(UUID conversationId) implements TutorEvent {}
    record Route(String routeDecision) implements TutorEvent {}
    record Content(String markdown) implements TutorEvent {}
    record Token(String token) implements TutorEvent {}
    record Complete(TutorResponse response) implements TutorEvent {}
    record Error(String message) implements TutorEvent {}
}

// Sink to emit events (abstraction for SSE, WebSocket, etc.)
public interface ResponseEventSink {
    void emit(TutorEvent event) throws IOException;
}
```

#### Task 4: Controller & SSE Streaming (Week 2)

**Java Concepts:** Lambda expressions, exception handling

```java
// src/main/java/com/neuralascent/tutor/api/TutorController.java
package com.neuralascent.tutor.api;

import com.neuralascent.tutor.service.TutorService;
import com.neuralascent.tutor.domain.*;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.http.codec.ServerSentEvent;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;
import reactor.core.publisher.Flux;
import java.util.UUID;

@RestController
@RequestMapping("/api/v1/tutor")
public class TutorController {
    
    private final TutorService tutorService;
    
    public TutorController(TutorService tutorService) {
        this.tutorService = tutorService;
    }
    
    /**
     * Stream tutor response as Server-Sent Events.
     * Client connects, sends question, receives streaming response.
     */
    @PostMapping(
        path = "/conversations/{conversationId}/messages:stream",
        produces = MediaType.TEXT_EVENT_STREAM_VALUE
    )
    public Flux<ServerSentEvent<String>> streamTutorMessage(
        @PathVariable UUID conversationId,
        @RequestBody MessageRequest request,
        Authentication auth
    ) {
        UUID userId = extractUserIdFromAuth(auth);
        
        return Flux.create(emitter -> {
            ResponseEventSink sink = event -> {
                String json = serializeEvent(event); // Convert to JSON
                emitter.next(ServerSentEvent.builder()
                    .id(UUID.randomUUID().toString())
                    .event(event.getClass().getSimpleName())
                    .data(json)
                    .build());
            };
            
            try {
                tutorService.streamTutorResponse(userId, conversationId, request, sink);
                emitter.complete();
            } catch (Exception e) {
                emitter.error(e);
            }
        });
    }
    
    @GetMapping("/conversations")
    public ResponseEntity<?> listConversations(Authentication auth) {
        // List user's conversations
        return ResponseEntity.ok("[]");
    }
    
    private UUID extractUserIdFromAuth(Authentication auth) {
        return UUID.fromString(auth.getName());
    }
    
    private String serializeEvent(TutorEvent event) {
        // Use Jackson or similar
        return "";
    }
}
```

**Browser Client (TypeScript):**

```typescript
// src/components/TutorChat.tsx
const response = await fetch('/api/v1/tutor/conversations/123/messages:stream', {
  method: 'POST',
  body: JSON.stringify({
    message: "How do I use the Strategy pattern?",
    pageContext: {
      vertical: 'java-lld',
      lessonId: 42,
      selectedCode: "// my code..."
    }
  })
});

const reader = response.body!.getReader();
const decoder = new TextDecoder();

while (true) {
  const { done, value } = await reader.read();
  if (done) break;
  
  const event = JSON.parse(decoder.decode(value));
  
  switch (event.event) {
    case 'Content':
      setTutorMessage(event.data);
      break;
    case 'Complete':
      setLoading(false);
      break;
    case 'Error':
      setError(event.data);
      break;
  }
}
```

**Practice Exercise from Java LLD Vertical:**

Review: **Design Patterns (Strategy)**  
Your tutor uses different strategies for different routes (hint strategy, cross-vertical strategy, clarification strategy). Create a `TutorStrategy` interface and implement: `HintStrategy`, `ClarificationStrategy`, `CrossVerticalStrategy`. Use the route decision to select which strategy to apply.

### Sprint 4 Deliverables

- [ ] `TutorContextResolver` that loads exact lesson/exercise by ID
- [ ] `ProgressiveHintService` with attempt-based disclosure
- [ ] `TutorService` orchestrating full request → response flow
- [ ] SSE controller streaming events to browser
- [ ] `TutorResponse` validated against JSON schema
- [ ] Ownership checks preventing cross-learner access
- [ ] Integration tests for streaming flow
- [ ] Client-side SSE handler

### Success Criteria

- [ ] You can explain "exact context" vs. RAG guessing
- [ ] You understand streams and lambda expressions
- [ ] Progressive hints work: level 1 then 2 then 3 as user attempts
- [ ] Solution policy is enforced (blocked if not allowed)
- [ ] SSE streams are properly terminated
- [ ] Browser receives events in correct order
- [ ] Learner A cannot hijack Learner B's conversation

---

## Sprint 5–12 Summary

Due to length constraints, here's the roadmap for the remaining sprints:

### **Sprint 5: Admin Operations Dashboard (2–3 weeks)**

**Java Focus:** Annotations, @Transactional, aggregation queries, metrics  
**Spring Focus:** Spring Boot Actuator, Micrometer, custom metrics  
**Tasks:**
- [ ] Expose `/actuator/metrics` for usage, latency, error rates
- [ ] Build admin DTO layer for dashboard (usage, top users, token breakdown)
- [ ] Implement audit logging for all setting changes
- [ ] Create admin authorization checks (`@PreAuthorize("hasRole('ADMIN')")`)

---

### **Sprint 6: Persistent Learner State (2–3 weeks)**

**Java Focus:** Enums, temporal types, optimistic concurrency, JPA relationships  
**Spring Focus:** Spring Data JPA auditing, `@CreationTimestamp`, `@UpdateTimestamp`  
**Tasks:**
- [ ] `LearnerLessonProgress` (status, first opened, completed, reopened)
- [ ] `MCQAttempt` (attempt history, not just final answer)
- [ ] `ExerciseCheckpoint` (code snapshots, compiler errors)
- [ ] Resume experience (restore last active lesson + checkpoint)

---

### **Sprint 7: Conversation Memory & Ownership (2 weeks)**

**Java Focus:** Concurrency, thread-safe caching, serialization  
**Spring Focus:** Spring Session (Redis-backed sessions), Spring Cache  
**Tasks:**
- [ ] `Conversation` and `ConversationMessage` entities with ownership
- [ ] Bounded memory (recent turns + server-generated summary)
- [ ] Conversation history UI (list, search, delete, archive)
- [ ] Delete/redaction of retained prompts

---

### **Sprint 8: Engagement Telemetry & Auto-Completion (2 weeks)**

**Java Focus:** Events, message queues, batching  
**Spring Focus:** Spring Events (`@EventListener`), async processing  
**Tasks:**
- [ ] Frontend telemetry aggregation (bounded events)
- [ ] Server-side completion policy evaluation
- [ ] Automatic lesson completion based on policy
- [ ] Manual reset/reopen override

---

### **Sprint 9: Support Assistant & Tickets (2–3 weeks)**

**Java Focus:** State machines, transitions, audit trails  
**Spring Focus:** Spring Events for state transitions, transactional outbox  
**Tasks:**
- [ ] `SupportTicket` and `TicketEvent` (immutable state transitions)
- [ ] Separate support prompt and routing
- [ ] Contact form → ticket creation
- [ ] Admin support queue & assignment
- [ ] Tutor-to-support handoff

---

### **Sprint 10: Filtered RAG & Cross-Vertical Access (3 weeks)**

**Java Focus:** Advanced generics, metadata filtering, sealed interfaces  
**Spring Focus:** Spring Data custom queries, pgvector (vector DB)  
**Tasks:**
- [ ] Content ingestion with chunk metadata
- [ ] Transactional outbox for published content
- [ ] pgvector similarity search with metadata filters
- [ ] Denied access behavior (fallback to current vertical)
- [ ] Evaluation suite for retrieval quality

---

### **Sprint 11: Evaluation & Production Hardening (2–3 weeks)**

**Java Focus:** Profiling, benchmarking, observability  
**Spring Focus:** Spring Boot Actuator, OpenTelemetry, structured logging  
**Tasks:**
- [ ] Evaluation datasets (routing, retrieval, tutor correctness)
- [ ] Structured logging with trace IDs
- [ ] Secret redaction in logs
- [ ] Chaos tests (provider outage, DB latency)
- [ ] Cost per completed exercise metric

---

### **Sprint 12: Java/Spring Completion & .NET Deprecation (4 weeks)**

**Java Focus:** Evolutionary architecture, API contracts, versioning  
**Spring Focus:** Spring Cloud Gateway (optional strangler pattern)  
**Tasks:**
- [ ] Freeze versioned HTTP contracts
- [ ] Parity tests (.NET vs. Java endpoints)
- [ ] Incremental route migration (reverse proxy)
- [ ] Rollback strategy & traffic rollback
- [ ] Decommission .NET modules one by one
- [ ] Performance comparison (latency, throughput, cost)

---

## Appendix: Practice Exercises from Java LLD Vertical

Use your Java LLD vertical as reference for these concepts:

### Module 1: OOP Basics
- [ ] Create a `Lesson` class with constructor, getters, setters
- [ ] Create an `Exercise` interface and multiple implementations
- [ ] Understand inheritance vs. composition

### Module 2: Design Patterns
- [ ] Implement the Strategy pattern for tutor routing
- [ ] Implement the Factory pattern for AI provider adapters
- [ ] Implement the Builder pattern for request/response DTOs

### Module 3: Collections & Streams
- [ ] Use streams to filter/map/reduce lesson collections
- [ ] Implement a custom comparator for sorting
- [ ] Use `Optional` instead of null checks

### Module 4: Exception Handling
- [ ] Create a custom exception hierarchy
- [ ] Implement global exception handler with `@ControllerAdvice`
- [ ] Use try-with-resources for database connections

### Module 5: Concurrency
- [ ] Understand `synchronized` vs. `Lock`
- [ ] Implement thread-safe quota caching
- [ ] Use `AtomicInteger` for concurrent counters

---

## Final Integration

### Pre-Launch Checklist

- [ ] All 12 sprints completed
- [ ] 100+ integration tests passing
- [ ] Zero bugs in security critical paths (auth, authorization, quota)
- [ ] Load test: 50 concurrent users, 6 msg/min each
- [ ] Cost simulation: daily budget, monthly quota enforcement
- [ ] Provider failover tested
- [ ] .NET endpoints deprecated, traffic migrated
- [ ] Team trained on Java/Spring codebase
- [ ] Runbook for on-call support

### Learning Outcome

By the end of this 18–24 week journey, you will have:

1. **Java Mastery:**
   - Written ~15K lines of production Java code
   - Used all major Java features (classes, interfaces, streams, concurrency, exceptions)
   - Understood design patterns through implementing them

2. **Spring Expertise:**
   - Built a secure, multi-tenant app with Spring Security
   - Used Spring Data JPA, Spring MVC, Spring Events, Spring AI
   - Understood transactional semantics, dependency injection, configuration

3. **Architecture & Engineering:**
   - Designed a secure multi-user platform from first principles
   - Migrated a complex system (.NET → Java) without downtime
   - Built observability, cost controls, and resilience into production code

4. **Interview Readiness:**
   - Can discuss authentication, authorization, rate limiting, quotas
   - Can explain sealed classes, streams, functional composition
   - Can design a scalable, cost-managed AI platform
   - Can show a real GitHub repository with 12 phases of incremental delivery

This is exactly the kind of project that wins senior/staff engineer interviews at Hyderabad tech companies and AI engineering roles.

---

## Quick Reference: Java Concepts by Sprint

| Sprint | Java Concept | Why It Matters | Example |
|--------|------------|----------------|---------|
| 1 | Classes, constructors, annotations | Foundation of every Java program | `@Entity`, `@Repository` |
| 2 | Interfaces, polymorphism | Design flexible, swappable components | `AccessEvaluator` implementations |
| 3 | Sealed classes, custom exceptions | Type-safe, exhaustive error handling | `Route`, `AiGatewayException` |
| 4 | Streams, lambdas | Functional data transformation | Filter lessons by vertical |
| 5 | Annotations, `@Transactional` | Declarative behavior | Metrics, auditing |
| 6 | Enums, temporal types, JPA | Model state and time accurately | Progress status, timestamps |
| 7 | Concurrency, caching | Handle simultaneous requests safely | Thread-safe quotas, Redis cache |
| 8 | Events, async processing | Decouple components | `@EventListener` for telemetry |
| 9 | State machines, immutability | Model workflows precisely | Ticket lifecycle |
| 10 | Advanced generics, custom queries | Type-safe, efficient data access | Generic repositories, metadata filtering |
| 11 | Observability, profiling | Understand production behavior | Metrics, structured logging |
| 12 | API contracts, versioning | Evolve without breaking clients | Frozen endpoints, parity tests |

---

**Good luck on your migration journey!** You're building something genuinely useful (a learning platform) while becoming a production-ready engineer. That combination is rare and valuable.

End of Learning Plan.
