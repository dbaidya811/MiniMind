#!/usr/bin/env node

const { spawn } = require("child_process");
const path = require("path");
const fs = require("fs");

const rootDir = path.resolve(__dirname, "..");
const cliScript = path.join(rootDir, "app", "cli.py");

const isWin = process.platform === "win32";
const venvPythonWin = path.join(rootDir, "venv", "Scripts", "python.exe");
const venvPythonUnix = path.join(rootDir, "venv", "bin", "python");

let pythonExec = "python";

if (isWin && fs.existsSync(venvPythonWin)) {
  pythonExec = venvPythonWin;
} else if (!isWin && fs.existsSync(venvPythonUnix)) {
  pythonExec = venvPythonUnix;
}

const child = spawn(pythonExec, [cliScript, ...process.argv.slice(2)], {
  cwd: rootDir,
  stdio: "inherit",
  shell: true,
});

child.on("exit", (code) => {
  process.exit(code || 0);
});