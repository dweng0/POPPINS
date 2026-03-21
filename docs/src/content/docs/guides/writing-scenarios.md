---
title: Writing BDD Scenarios
description: How to write effective Gherkin scenarios that the agent can implement.
---

The agent builds exactly what's in `BDD.md` — nothing more, nothing less. Writing good scenarios is the most important thing you do.

## Structure of BDD.md

```yaml
---
language: typescript          # rust | python | go | node | typescript | java
framework: react-vite         # informational — helps the agent pick the right tools
build_cmd: npm run build
test_cmd: npm test
lint_cmd: npm run lint
fmt_cmd: npm run format
birth_date: 2026-01-01        # project start date (used for day counter)
---
```

Below the frontmatter, write plain Gherkin:

```gherkin
System: A REST API for task management

    Feature: Task CRUD
        As an API consumer
        I want to create, read, update and delete tasks
        So that I can manage work items programmatically

        Scenario: Create a task
            Given the API is running
            When I POST /tasks with {"title": "Buy milk"}
            Then I receive a 201 response
            And the response body contains the task with an ID
```

## Scenario priority

**Top of the file = highest priority.** The agent works top-to-bottom, picking the first uncovered or failing scenario.

If you want something built first, put it at the top of `BDD.md`.

## Tips for effective scenarios

### Be specific — one behaviour per scenario

```gherkin
# Good — testable, focused
Scenario: Empty search returns no results
    Given the database has 10 tasks
    When I search for "nonexistent"
    Then I receive an empty list

# Bad — too vague
Scenario: Search works
    Given some tasks
    When I search
    Then I get results
```

### Make `Then` clauses observable

The agent needs to write an assertion. If your `Then` clause isn't testable, the agent will struggle.

```gherkin
# Good — clear assertion
Then the response status is 404
Then the task list contains exactly 3 items
Then the error message includes "not found"

# Bad — how does the agent test this?
Then the system is in a good state
Then the user is happy
```

### Keep scenarios independent

Each scenario should stand on its own. Don't rely on state from previous scenarios.

```gherkin
# Good — self-contained
Scenario: Delete a task
    Given I have created a task with ID 1
    When I DELETE /tasks/1
    Then I receive a 204 response

# Bad — depends on "Create a task" running first
Scenario: Delete a task
    When I DELETE /tasks/1
    Then I receive a 204 response
```

### Use Background for shared setup

```gherkin
Feature: Task management
    Background:
        Given the database is empty
        And I have a valid auth token

    Scenario: Create a task
        When I POST /tasks with {"title": "Buy milk"}
        Then I receive a 201 response

    Scenario: List tasks
        When I GET /tasks
        Then I receive an empty list
```

## Supported languages

The `language` field in frontmatter tells poppins which toolchain to set up:

| Language | What gets installed |
|----------|-------------------|
| `typescript` | Node.js, npm, TypeScript compiler |
| `python` | Python venv, pip |
| `rust` | Cargo, rustc, clippy |
| `go` | Go toolchain |
| `java` | JDK, Maven or Gradle |
| `node` | Node.js, npm |
