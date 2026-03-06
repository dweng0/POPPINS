import React, { useState } from "react";
import { Box, Text, useApp } from "ink";
import { writeFileSync } from "fs";
import { resolve } from "path";
import {
  BddDocument,
  FeatureData,
  Frontmatter,
  ScenarioData,
} from "./types.js";
import { inferCommand } from "./utils/commands.js";
import { generateBddContent } from "./utils/bddWriter.js";
import TextInput from "./components/TextInput.js";

type AppProps = {
  outputPath?: string;
};

type WizardStep =
  | "language"
  | "framework"
  | "build_cmd"
  | "test_cmd"
  | "lint_cmd"
  | "fmt_cmd"
  | "system_description"
  | "feature_or_done"
  | "feature_name"
  | "feature_action"
  | "scenario_name"
  | "scenario_given"
  | "scenario_when"
  | "scenario_then"
  | "background_given"
  | "complete";

type ScenarioDraft = {
  name: string;
  given: string;
  when: string;
  then: string;
};

type BackgroundDraft = {
  given: string;
};

function getTodayDate(): string {
  const d = new Date();
  const year = d.getFullYear();
  const month = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

export default function App({ outputPath = "BDD.md" }: AppProps) {
  const { exit } = useApp();

  const [step, setStep] = useState<WizardStep>("language");
  const [language, setLanguage] = useState("");
  const [framework, setFramework] = useState("");
  const [buildCmd, setBuildCmd] = useState("");
  const [testCmd, setTestCmd] = useState("");
  const [lintCmd, setLintCmd] = useState("");
  const [fmtCmd, setFmtCmd] = useState("");
  const [systemDescription, setSystemDescription] = useState("");
  const [features, setFeatures] = useState<FeatureData[]>([]);
  const [currentFeatureName, setCurrentFeatureName] = useState("");
  const [currentFeatureBackground, setCurrentFeatureBackground] =
    useState<BackgroundDraft | null>(null);
  const [currentFeatureScenarios, setCurrentFeatureScenarios] = useState<
    ScenarioData[]
  >([]);
  const [scenarioDraft, setScenarioDraft] = useState<Partial<ScenarioDraft>>(
    {},
  );
  const [savedFilePath, setSavedFilePath] = useState("");

  function buildFrontmatter(): Frontmatter {
    return {
      language,
      framework,
      build_cmd: buildCmd,
      test_cmd: testCmd,
      lint_cmd: lintCmd,
      fmt_cmd: fmtCmd,
      birth_date: getTodayDate(),
    };
  }

  function commitCurrentFeature() {
    const feature: FeatureData = {
      name: currentFeatureName,
      background: currentFeatureBackground
        ? { given: currentFeatureBackground.given }
        : null,
      scenarios: [...currentFeatureScenarios],
    };
    setFeatures((prev) => [...prev, feature]);
    setCurrentFeatureName("");
    setCurrentFeatureBackground(null);
    setCurrentFeatureScenarios([]);
    setScenarioDraft({});
  }

  function saveBddFile(allFeatures: FeatureData[]) {
    const doc: BddDocument = {
      frontmatter: buildFrontmatter(),
      system_description: systemDescription,
      features: allFeatures,
    };
    const content = generateBddContent(doc);
    const absPath = resolve(outputPath);
    writeFileSync(absPath, content, "utf-8");
    return absPath;
  }

  // --- Handlers ---

  function handleLanguage(val: string) {
    setLanguage(val);
    setStep("framework");
  }

  function handleFramework(val: string) {
    setFramework(val);
    setStep("build_cmd");
  }

  function handleBuildCmd(val: string) {
    if (val.trim() === "") {
      setBuildCmd(inferCommand(language, "build_cmd"));
    } else {
      setBuildCmd(val.trim());
    }
    setStep("test_cmd");
  }

  function handleTestCmd(val: string) {
    if (val.trim() === "") {
      setTestCmd(inferCommand(language, "test_cmd"));
    } else {
      setTestCmd(val.trim());
    }
    setStep("lint_cmd");
  }

  function handleLintCmd(val: string) {
    if (val.trim() === "") {
      setLintCmd(inferCommand(language, "lint_cmd"));
    } else {
      setLintCmd(val.trim());
    }
    setStep("fmt_cmd");
  }

  function handleFmtCmd(val: string) {
    if (val.trim() === "") {
      setFmtCmd(inferCommand(language, "fmt_cmd"));
    } else {
      setFmtCmd(val.trim());
    }
    setStep("system_description");
  }

  function handleSystemDescription(val: string) {
    setSystemDescription(val.trim());
    setStep("feature_or_done");
  }

  function handleFeatureOrDone(val: string) {
    const lower = val.toLowerCase().trim();
    if (lower === "done" || lower === "d") {
      // Commit any in-progress feature
      const finalFeatures = [...features];
      const path = saveBddFile(finalFeatures);
      setSavedFilePath(path);
      setStep("complete");
      setTimeout(() => exit(), 100);
    } else {
      setStep("feature_name");
    }
  }

  function handleFeatureName(val: string) {
    setCurrentFeatureName(val);
    setStep("feature_action");
  }

  function handleFeatureAction(val: string) {
    const lower = val.toLowerCase().trim();
    if (lower === "scenario" || lower === "s") {
      setScenarioDraft({});
      setStep("scenario_name");
    } else if (lower === "background" || lower === "b") {
      setStep("background_given");
    } else if (lower === "done" || lower === "d") {
      commitCurrentFeature();
      setStep("feature_or_done");
    } else {
      // Default: treat as "add scenario"
      setScenarioDraft({});
      setStep("scenario_name");
    }
  }

  function handleScenarioName(val: string) {
    setScenarioDraft((prev) => ({ ...prev, name: val }));
    setStep("scenario_given");
  }

  function handleScenarioGiven(val: string) {
    setScenarioDraft((prev) => ({ ...prev, given: val }));
    setStep("scenario_when");
  }

  function handleScenarioWhen(val: string) {
    setScenarioDraft((prev) => ({ ...prev, when: val }));
    setStep("scenario_then");
  }

  function handleScenarioThen(val: string) {
    const completed: ScenarioData = {
      name: scenarioDraft.name ?? "",
      given: scenarioDraft.given ?? "",
      when: scenarioDraft.when ?? "",
      then: val,
    };
    setCurrentFeatureScenarios((prev) => [...prev, completed]);
    setScenarioDraft({});
    setStep("feature_action");
  }

  function handleBackgroundGiven(val: string) {
    const bg: BackgroundDraft = { given: val };
    setCurrentFeatureBackground(bg);
    setStep("feature_action");
  }

  // Back navigation
  function goBackFrom(current: WizardStep) {
    switch (current) {
      case "framework":
        setStep("language");
        break;
      case "build_cmd":
        setStep("framework");
        break;
      case "test_cmd":
        setStep("build_cmd");
        break;
      case "lint_cmd":
        setStep("test_cmd");
        break;
      case "fmt_cmd":
        setStep("lint_cmd");
        break;
      case "system_description":
        setStep("fmt_cmd");
        break;
      case "feature_name":
        setStep("feature_or_done");
        break;
      case "feature_action":
        setStep("feature_name");
        break;
      case "scenario_name":
        setStep("feature_action");
        break;
      case "scenario_given":
        setStep("scenario_name");
        break;
      case "scenario_when":
        setStep("scenario_given");
        break;
      case "scenario_then":
        setStep("scenario_when");
        break;
      case "background_given":
        setStep("feature_action");
        break;
      default:
        break;
    }
  }

  // Render
  if (step === "complete") {
    return (
      <Box flexDirection="column">
        <Text color="green">
          BDD file created successfully: {savedFilePath}
        </Text>
      </Box>
    );
  }

  return (
    <Box flexDirection="column" gap={1}>
      <Text color="white">{`  ^ ^
 (o o)  BDD Wizard
  (  )  your friendly sheep
  -  -`}</Text>

      {step === "language" && (
        <Box flexDirection="column">
          <Text>What programming language will you use?</Text>
          <TextInput onSubmit={handleLanguage} placeholder="e.g. typescript" />
        </Box>
      )}

      {step === "framework" && (
        <Box flexDirection="column">
          <Text>What framework will you use?</Text>
          <TextInput
            onSubmit={handleFramework}
            onBack={() => goBackFrom("framework")}
            placeholder="e.g. react, express"
          />
        </Box>
      )}

      {step === "build_cmd" && (
        <Box flexDirection="column">
          <Text>
            Build command? (press Enter to infer from language &quot;
            {language}&quot;)
          </Text>
          <TextInput
            onSubmit={handleBuildCmd}
            onBack={() => goBackFrom("build_cmd")}
            placeholder="leave blank to auto-detect"
          />
        </Box>
      )}

      {step === "test_cmd" && (
        <Box flexDirection="column">
          <Text>
            Test command? (press Enter to infer from language &quot;{language}
            &quot;)
          </Text>
          <TextInput
            onSubmit={handleTestCmd}
            onBack={() => goBackFrom("test_cmd")}
            placeholder="leave blank to auto-detect"
          />
        </Box>
      )}

      {step === "lint_cmd" && (
        <Box flexDirection="column">
          <Text>
            Lint command? (press Enter to infer from language &quot;{language}
            &quot;)
          </Text>
          <TextInput
            onSubmit={handleLintCmd}
            onBack={() => goBackFrom("lint_cmd")}
            placeholder="leave blank to auto-detect"
          />
        </Box>
      )}

      {step === "fmt_cmd" && (
        <Box flexDirection="column">
          <Text>
            Format command? (press Enter to infer from language &quot;{language}
            &quot;)
          </Text>
          <TextInput
            onSubmit={handleFmtCmd}
            onBack={() => goBackFrom("fmt_cmd")}
            placeholder="leave blank to auto-detect"
          />
        </Box>
      )}

      {step === "system_description" && (
        <Box flexDirection="column">
          <Text>Describe the system (optional, press Enter to skip):</Text>
          <TextInput
            onSubmit={handleSystemDescription}
            onBack={() => goBackFrom("system_description")}
            placeholder="A tool that..."
          />
        </Box>
      )}

      {step === "feature_or_done" && (
        <Box flexDirection="column">
          <Text>
            Add a feature? (type feature name and press Enter, or
            &quot;done&quot; to finish)
          </Text>
          <TextInput
            onSubmit={handleFeatureOrDone}
            placeholder='feature name or "done"'
          />
        </Box>
      )}

      {step === "feature_name" && (
        <Box flexDirection="column">
          <Text>Feature name:</Text>
          <TextInput
            onSubmit={handleFeatureName}
            onBack={() => goBackFrom("feature_name")}
            placeholder="Feature name"
          />
        </Box>
      )}

      {step === "feature_action" && (
        <Box flexDirection="column">
          <Text>
            Feature: &quot;{currentFeatureName}&quot;. Add: scenario [s],
            background [b], or done [d]?
          </Text>
          <TextInput
            onSubmit={handleFeatureAction}
            onBack={() => goBackFrom("feature_action")}
            placeholder="s / b / done"
          />
        </Box>
      )}

      {step === "scenario_name" && (
        <Box flexDirection="column">
          <Text>Scenario name:</Text>
          <TextInput
            onSubmit={handleScenarioName}
            onBack={() => goBackFrom("scenario_name")}
            placeholder="Scenario name"
          />
        </Box>
      )}

      {step === "scenario_given" && (
        <Box flexDirection="column">
          <Text>Given (precondition):</Text>
          <TextInput
            onSubmit={handleScenarioGiven}
            onBack={() => goBackFrom("scenario_given")}
            placeholder="the user is..."
          />
        </Box>
      )}

      {step === "scenario_when" && (
        <Box flexDirection="column">
          <Text>When (action):</Text>
          <TextInput
            onSubmit={handleScenarioWhen}
            onBack={() => goBackFrom("scenario_when")}
            placeholder="the user does..."
          />
        </Box>
      )}

      {step === "scenario_then" && (
        <Box flexDirection="column">
          <Text>Then (outcome):</Text>
          <TextInput
            onSubmit={handleScenarioThen}
            onBack={() => goBackFrom("scenario_then")}
            placeholder="the system shows..."
          />
        </Box>
      )}

      {step === "background_given" && (
        <Box flexDirection="column">
          <Text>Background Given (shared precondition):</Text>
          <TextInput
            onSubmit={handleBackgroundGiven}
            onBack={() => goBackFrom("background_given")}
            placeholder="the system is in state..."
          />
        </Box>
      )}
    </Box>
  );
}
