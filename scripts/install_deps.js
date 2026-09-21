const { execSync } = require("child_process");
const path = require("path");

function installPythonRequirements() {
  const reqPath = path.resolve(__dirname, "..", "requirements.txt");
  
  console.log("\nChecking Python dependencies for MiniMind...");

  const pythonCmd = process.platform === "win32" ? "python" : "python3";

  try {
    console.log("Installing Python requirements via pip (this may take a few moments)...");
    execSync(`${pythonCmd} -m pip install -r "${reqPath}"`, {
      stdio: "inherit"
    });
    console.log("All Python dependencies installed successfully!\n");
  } catch (error) {
    console.warn("\nWarning: Automatic pip installation failed or Python is not found in PATH.");
    console.warn(`Please run: pip install -r "${reqPath}" manually.\n`);
  }
}

installPythonRequirements();