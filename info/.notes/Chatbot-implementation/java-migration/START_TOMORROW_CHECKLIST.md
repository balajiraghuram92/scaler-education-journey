# START TOMORROW: 85-Day Interview Prep Sprint

## Before You Sleep Tonight (30 min)

### 1. Environment Setup
- [ ] Install JDK 21
  ```bash
  # macOS
  brew install openjdk@21
  
  # Linux
  sudo apt-get install openjdk-21-jdk
  
  # Windows
  # Download from oracle.com
  ```

- [ ] Install Maven (for build)
  ```bash
  brew install maven  # macOS
  # or download from maven.apache.org
  ```

- [ ] Install Docker (for local PostgreSQL)
  ```bash
  # Install Docker Desktop from docker.com
  ```

- [ ] Verify installations
  ```bash
  java -version      # Should show 21.x
  mvn -version       # Should show 3.9+
  docker --version   # Should show latest
  ```

### 2. GitHub Setup
- [ ] Create new repository: `neuralascent-java-migration`
  - [ ] Add .gitignore (Java template)
  - [ ] Add README.md (stub)
  - [ ] Clone locally: `/path/to/neuralascent-java-migration`

### 3. Development Environment
- [ ] IDE: IntelliJ IDEA Community (free) or VS Code + Extension Pack for Java
  - Download from jetbrains.com or code.visualstudio.com

- [ ] PostgreSQL: Use Docker instead
  ```bash
  docker run --name postgres-neuralascent \
    -e POSTGRES_DB=neuralascent \
    -e POSTGRES_PASSWORD=secret \
    -p 5432:5432 \
    -d postgres:16
  ```

- [ ] Redis (optional for now, needed Week 2)
  ```bash
  docker run --name redis-neuralascent \
    -p 6379:6379 \
    -d redis:7-alpine
  ```

- [ ] Create project directory structure
  ```bash
  mkdir -p neuralascent-java-migration
  cd neuralascent-java-migration
  ```

---

## Day 1 Morning (7 AM Start)

### Session 1: Create Spring Boot Skeleton (7-9 AM, 2 hrs)

1. **Generate Spring Boot project**
   ```bash
   # Visit start.spring.io or use CLI
   # Select:
   # - Spring Boot 3.3.0
   # - Java 21
   # - Maven
   # - Add dependencies:
   #   * Spring Web
   #   * Spring Data JPA
   #   * PostgreSQL Driver
   #   * Lombok
   #   * Spring Security
   ```

   OR use Maven archetype:
   ```bash
   mvn archetype:generate \
     -DgroupId=com.neuralascent \
     -DartifactId=neuralascent \
     -DarchetypeArtifactId=maven-archetype-quickstart \
     -DinteractiveMode=false
   ```

2. **Verify it compiles**
   ```bash
   mvn clean package
   # Should output: BUILD SUCCESS
   ```

3. **Commit to GitHub**
   ```bash
   git add .
   git commit -m "Day 1: Spring Boot skeleton"
   git push origin main
   ```

4. **Document in README**
   ```markdown
   # NeuralAscent: Java/Spring Migration
   
   ## 85-Day Interview Prep Project
   
   ### What This Is
   Building a secure, scalable AI learning platform demonstrating:
   - Java 21 + Spring Boot 3.3
   - Spring Security (auth + authorization)
   - Spring Data JPA (database)
   - AI gateway with cost controls
   - RAG + evaluation
   - PostgreSQL optimization
   - Docker + Kubernetes
   - AWS deployment
   
   ### Timeline
   - Days 1-30: Sprints 1-9 (platform MVP)
   - Days 31-50: RAG + evaluation
   - Days 51-70: Database optimization
   - Days 71-85: Cloud deployment
   
   ### How to Run Locally
   ```bash
   docker-compose up -d
   mvn spring-boot:run
   ```
   ```

### Session 2: First Entity + Repository (9-11 AM, 2 hrs)

1. **Create AppUser entity** (from Sprint 1 learning plan)
   ```java
   // src/main/java/com/neuralascent/identity/domain/AppUser.java
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
       private UserStatus status = UserStatus.PENDING;
       
       private String passwordHash;
   }
   ```

2. **Create repository**
   ```java
   @Repository
   public interface AppUserRepository extends JpaRepository<AppUser, UUID> {
       Optional<AppUser> findByEmailIgnoreCase(String email);
   }
   ```

3. **Create Flyway migration**
   ```sql
   -- src/main/resources/db/migration/V001__create_user_table.sql
   CREATE TABLE app_user (
       id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
       email VARCHAR(255) UNIQUE NOT NULL,
       display_name VARCHAR(255) NOT NULL,
       status VARCHAR(50) NOT NULL DEFAULT 'PENDING',
       password_hash VARCHAR(512),
       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
       updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
   );
   ```

4. **Write first integration test**
   ```java
   @SpringBootTest
   class AppUserRepositoryTest {
       @Autowired
       private AppUserRepository repository;
       
       @Test
       void testSaveAndFind() {
           AppUser user = new AppUser();
           user.setEmail("test@example.com");
           user.setDisplayName("Test User");
           
           repository.save(user);
           
           var found = repository.findByEmailIgnoreCase("test@example.com");
           assertTrue(found.isPresent());
       }
   }
   ```

5. **Commit**
   ```bash
   git add .
   git commit -m "Day 1: AppUser entity + first test"
   git push
   ```

---

## Days 1-7: Sprint 1 Part 1 Detailed Daily Breakdown

### Day 1: Entities (Morning: 4 hrs, Evening: 3 hrs)
- [ ] AppUser + UserRole + UserStatus (7 hrs)
- [ ] Database migrations
- [ ] First integration test passing

### Day 2: Spring Security Config (17 hrs)
- [ ] SecurityConfig class
- [ ] CustomUserDetailsService
- [ ] Password encoder (BCrypt)
- [ ] Authentication tests

### Day 3: Registration Flow (17 hrs)
- [ ] UserInvitation entity
- [ ] UserRegistrationService
- [ ] Registration endpoint
- [ ] Tests for invitation validation

### Day 4: Authorization Model (17 hrs)
- [ ] Enrollment entity
- [ ] VerticalEntitlement entity
- [ ] AccessPolicyService
- [ ] Policy resolution tests

### Day 5: Polish Sprint 1-2 (17 hrs)
- [ ] Integration tests
- [ ] Error handling
- [ ] Cross-user access denial tests
- [ ] Security audit

### Day 6-7: Buffer + Checkpoint (17 hrs)
- [ ] Deploy to local staging
- [ ] Write README section 1
- [ ] Fix bugs
- [ ] Prepare for Week 2

---

## Weekly Checkpoints

### End of Week 1 (Day 7)
```
✅ Sprints 1-2 complete (identity + authorization)
✅ Can login, register, verify enrollment
✅ Authorization checks working
✅ 20+ tests passing
✅ GitHub shows 7 days of commits
```

### End of Week 2 (Day 14)
```
✅ Sprint 3 complete (AI gateway)
✅ Rate limiting working
✅ Quota system atomic
✅ Muse Spark adapter basic
✅ 40+ tests passing
```

### End of Week 3 (Day 21)
```
✅ Sprints 4-5 complete (tutor + admin)
✅ SSE streaming to browser
✅ Admin dashboard basic
✅ 60+ tests passing
```

### End of Week 4 (Day 30)
```
✅ Sprints 1-9 COMPLETE
✅ ~9,000 lines of code
✅ 80+ tests passing
✅ Can demo full platform
✅ Ready for Phase 2 (RAG)
```

---

## Things NOT to Do (Common Mistakes)

### ❌ Don't:
- Write tests for every line (waste of time, test critical paths only)
- Over-engineer (YAGNI principle — build what you need today)
- Optimize prematurely (get it working first)
- Skip commits (commit daily, good history matters for interview)
- Ignore errors (fix them immediately, don't accumulate debt)
- Code for 12+ hours straight (take breaks, sleep 7+ hrs)

### ✅ Do:
- Commit daily with clear messages
- Test critical security paths thoroughly
- Deploy to staging weekly to catch integration issues
- Document as you go (README updated weekly)
- Ask for help if stuck >1 hour on something
- Take weekends partially off (mental recovery)

---

## Daily Standup Template (Keep a Log)

Create a file `DAILY_LOG.md`:

```markdown
# Daily Progress Log

## Day 1 (Mon)
**What I did:**
- [ ] Created Spring Boot skeleton
- [ ] Built AppUser entity
- [ ] Wrote first test
- [ ] Pushed to GitHub

**What I learned:**
- Spring Data JPA auto-generates queries
- Lombok reduces boilerplate significantly
- Flyway migrations need to be idempotent

**Blockers:**
- None

**Next day plan:**
- Implement Spring Security config

---

## Day 2 (Tue)
**What I did:**
[...]
```

This helps you:
1. Track progress visually
2. Prepare for daily standup (if talking to someone)
3. Review what you learned (interview prep!)

---

## Success Metrics: What "Done" Looks Like

### Day 7 Checkpoint
```bash
cd neuralascent-java-migration
git log --oneline | head -20
# Should show ~20 commits

wc -l $(find src -name "*.java")
# Should show ~1,500-2,000 lines

mvn test
# Should show 20+ tests passing
```

### Day 30 Checkpoint
```bash
git log --oneline | head -50
# Should show ~50 commits

wc -l $(find src -name "*.java")
# Should show ~9,000 lines

mvn test
# Should show 80+ tests passing

# Try to run and login locally
docker-compose up -d
mvn spring-boot:run
# Visit http://localhost:8080/api/v1/me
# Should get 401 (unauthenticated) not 500 (error)
```

---

## Resources You'll Reference

1. **Spring Boot Documentation**
   - https://docs.spring.io/spring-boot/reference/
   - Bookmark: SpringBoot quick start, application properties

2. **Spring Security Guide**
   - https://spring.io/guides/gs/securing-web/
   - Bookmark: CustomUserDetailsService, SecurityFilterChain

3. **Spring Data JPA**
   - https://docs.spring.io/spring-data/jpa/reference/
   - Bookmark: Query derivation, custom queries

4. **Your Java LLD Vertical**
   - Refer to when confused about Java syntax
   - Week 1: Read lessons on interfaces, OOP basics
   - Week 2: Read lessons on design patterns (Strategy, Adapter, Factory)

5. **PostgreSQL Documentation** (reference, not deep dive yet)
   - https://www.postgresql.org/docs/16/
   - You'll use this heavily in Phase 3

---

## If You Get Stuck

### Stuck on Java syntax?
→ Check Java LLD vertical (lessons 1-2)

### Stuck on Spring?
→ Google the error + "spring boot" → find Spring Guide

### Stuck on JPA?
→ Spring Data documentation + Spring guides

### Stuck on design?
→ Re-read the learning plan document's section for that sprint

### Stuck for >1 hour?
→ Skip that feature, come back to it later. Ship imperfect code > no code.

---

## Motivation: Why This Matters

**After Day 30:**
- You'll have shipped more Java code than most 2-3 yr devs
- You can demo a real working app
- You understand Spring Security end-to-end

**After Day 50:**
- You'll have built RAG (very few people have done this)
- Interviewers will be impressed

**After Day 70:**
- You'll understand database optimization at scale
- System design interviews become easier

**After Day 85:**
- You'll be interview-proof across 4 critical areas
- Most senior devs can't talk about all 4 deeply

**In 85 days, you level up 2-3 years of experience.**

---

## One Last Thing

**Screenshot this or print it:**

```
┌─────────────────────────────────────────────┐
│   85-DAY INTERVIEW PREP SPRINT               │
│                                             │
│   Day 1:   Start today ✓                    │
│   Day 30:  Ship platform MVP                │
│   Day 50:  Add RAG + evaluation             │
│   Day 70:  Optimize database + scale        │
│   Day 85:  Deploy to AWS + CI/CD            │
│                                             │
│   Goal: Interview-ready across all 4 areas  │
│   Timeline: Sustainable pace, not burnout   │
│   Result: Production portfolio + job offer  │
│                                             │
│   You've got this. 💪                       │
└─────────────────────────────────────────────┘
```

---

## Tomorrow Morning (6:30 AM)

```
1. Grab coffee ☕
2. Open this checklist
3. Run: mvn archetype:generate [command from above]
4. Setup IDE
5. Create first entity
6. Write first test
7. Commit to GitHub
8. Log in DAILY_LOG.md
9. Go to sleep (7+ hrs)
10. Repeat tomorrow
```

**You're not building the perfect system. You're building a working system that shows you can ship code, learn fast, and solve real problems. That's what interview wins.**

Go build something awesome. 🚀

---

**Questions? Things unclear? Reply with:**
- "Stuck on [topic]"
- "How does [concept] work?"
- "Is [approach] correct?"

I'm here to unblock you.
