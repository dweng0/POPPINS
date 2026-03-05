---
language: typescript
framework: react-vite, react-ink
build_cmd: npm run build
test_cmd: npm test
lint_cmd: npm run lint
fmt_cmd: npm run format
birth_date: 2026-03-05
---

You must only write code and tests that meet the features and scenarios of this behaviour driven development document. Never use emojis in your code or tests.

System: A react cli tool that allows you to create a BDD file in the same format as this one. using react-ink

    Feature: Add the front matter to the BDD file
        As a user
        I want to be able to put in the what language and framework i wish to build my project in
        So that it can be added to my BDD file and used for my project.

        Background: [Optional — shared precondition for all scenarios in this feature]
            Given [shared precondition]

        Scenario: Allow a user to specify the language
            Given the user is prompted for a programming language
            When the user inputs a programming language
            Then the programming language is added to the frontmatter of the bdd file

        Scenario: Allow a user to specify the framework
            Given the user is prompted for a framework
            When the user inputs a framework
            Then the framework is added to the frontmatter of the bdd file

        Scenario: Allow a user to optionally specify the build command
            Given the user is prompted for a build command
            When the user inputs a build command
            Then the build command is added to the frontmatter of the bdd file

        Scenario: Allow a user to not need to provide a build command
            Given the user is prompted for a build command
            When the user doesn't know what to put for the build command
            Then the build should be worked out by the tool and added to the frontmatter of the bdd file

        Scenario: Allow a user to optionally specify the test command
            Given the user is prompted for a test command
            When the user inputs a test command
            Then the test command is added to the frontmatter of the bdd file

        Scenario: Allow a user to not need to provide a test command
            Given the user is prompted for a test command
            When the user doesn't know what to put for the test command
            Then the test command should be worked out by the tool and added to the frontmatter of the bdd file

        Scenario: Allow a user to optionally specify the lint command
            Given the user is prompted for a lint command
            When the user inputs a lint command
            Then the lint command is added to the frontmatter of the bdd file

        Scenario: Allow a user to not need to provide a lint command
            Given the user is prompted for a lint command
            When the user doesn't know what to put for the lint command
            Then the lint command should be worked out by the tool and added to the frontmatter of the bdd file

        Scenario: Allow a user to optionally specify the format command
            Given the user is prompted for a format command
            When the user inputs a format command
            Then the format command is added to the frontmatter of the bdd file

        Scenario: Allow a user to not need to provide a format command
            Given the user is prompted for a format command
            When the user doesn't know what to put for the format command
            Then the format command should be worked out by the tool and added to the frontmatter of the bdd file

        Scenario: The birthdate of the project should be added to the frontmatter of the bdd file
            Given the user has completed the frontmatter questions
            When the frontmatter is added to the bdd file
            Then the birthdate of the project should be added to the frontmatter of the bdd file

        Scenario: The user should be able to not provide a system description through user input
            Given the user has completed the frontmatter questions
            When the frontmatter is added to the bdd file
            Then the user should be prompted with an input field for a description of the system.
            When the user doesn't know what to put for the system description
            Then the system description should be left out of the bdd file

        Scenario: Adding features to the BDD file through user input
            Given the user has completed the description of the system
            When the user is prompted to add a feature
            Then the user should be able to add a feature to the BDD file.
            When the feature is added to the BDD file
            Then the user should be prompted to add a scenario or background to the feature or add another feature to the BDD file.

        Scenario: A user wants to be able to provide a Scenario for a feature through user input
            Given the user has added a feature to the BDD file
            When the user is prompted to add a scenario to the feature
            Then the user should be able to add a scenario to the feature in the BDD file.
            When the scenario is added to the feature in the BDD file
            Then the user should be prompted to add another scenario to the feature or add another feature to the BDD file.
        Scenario: a user should be able to add 0 or more backgrounds to a feature through user input
            Given the user has added a feature to the BDD file
            When the user is prompted to add a background to the feature
            Then the user should be able to add a background to the feature in the BDD file.
            When the background is added to the feature in the BDD file
            Then the user should be prompted to add another background to the feature or add a scenario to the feature or add another feature to the BDD file.
        Scenario: Adding scenarios to the feature through user input
            Given the user has added a feature to the BDD file
            When the user is prompted to add a scenario to the feature
            Then the user should be given a guided input for each part of the scenario (scenario name, given, when, then)
            When the user has completed the guided input for the scenario
            Then the user should be prompted to add another scenario to the feature or add another feature to the BDD file.
        Scenario: Cancelling adding a scenario to the feature through user input
            Given the user has added a feature to the BDD file
            When the user is prompted to add a scenario to the feature
            Then the user should be given a guided input for each part of the scenario (scenario name, given, when, then)
            When the user has wants to go to the previous guided input
            Then the user should be taken to the previous guided input for the scenario
            When the user is at the first guided input for the scenario and wants to go back
            Then the user should be taken back to the prompt asking if they want to add a scenario or feature to the BDD file.
        Scenario: Cancelling adding a background to the feature through user input
            Given the user has added a feature to the BDD file
            When the user is prompted to add a background to the feature
            Then the user should be given a guided input for each part of the background (background name, given)
            When the user has wants to go to the previous guided input
            Then the user should be taken to the previous guided input for the background
            When the user is at the first guided input for the background and wants to go back
            Then the user should be taken back to the prompt asking if they want to add a scenario or feature to the BDD file.
        Scenario: Completing the BDD
            Given the user has added all the features, scenarios and backgrounds they want to the BDD file
            When the user is prompted to complete the BDD file
            Then the user should be able to complete the BDD file and have it saved to their project.
            When the BDD file is saved to their project
            Then the user should be given a success message that their BDD file has been created and saved to their project.

    Feature: Distribution
        As a user
        I want to be able to build and run the tool easily
        So that I can use it without needing to understand the internals

        Scenario: A user can build the tool using a build script
            Given the user has cloned the repository
            When the user runs the build script
            Then the tool should be compiled and ready to use

    Feature: Application branding
        As a user
        I want to see a sheep mascot when I open the application
        So that the tool feels welcoming and distinctive

        Scenario: A sheep mascot is displayed when the application starts
            Given the user opens the application
            When the application starts
            Then a sheep mascot should be displayed in the terminal

