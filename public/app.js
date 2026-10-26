/*
  Encrypt and decrypt call /api/cipher. Auto-crack calls /api/crack.
  Both routes use caesar_cipher.py. Auto-crack also calls the Free Dictionary API
  and the spinner stays up until that search reaches 90% English.
*/

const form = document.querySelector("#cipher-form");
const messageInput = document.querySelector("#message");
const shiftInput = document.querySelector("#shift");
const shiftField = document.querySelector("#shift-field");
const errorText = document.querySelector("#form-error");
const resultEmpty = document.querySelector("#result-empty");
const resultWorking = document.querySelector("#result-working");
const resultBlock = document.querySelector("#result");
const originalMessage = document.querySelector("#original-message");
const shiftEnteredLabel = document.querySelector("#shift-entered-label");
const shiftEntered = document.querySelector("#shift-entered");
const shiftUsedLabel = document.querySelector("#shift-used-label");
const shiftUsed = document.querySelector("#shift-used");
const confidenceRow = document.querySelector("#confidence-row");
const confidenceText = document.querySelector("#confidence");
const resultLabel = document.querySelector("#result-label");
const resultText = document.querySelector("#result-text");
const runButton = document.querySelector("#run-button");

function showError(message) {
  errorText.hidden = false;
  errorText.textContent = message;
}

function clearError() {
  errorText.hidden = true;
  errorText.textContent = "";
}

function readShift(rawValue) {
  const trimmed = rawValue.trim();

  // The same whole numbers Python accepts with int(), including +3 and -1.
  if (!/^[+-]?\d+$/.test(trimmed)) {
    return null;
  }

  return Number(trimmed);
}

function selectedMode() {
  return form.elements.mode.value;
}

function syncShiftField() {
  shiftField.hidden = selectedMode() === "crack";
}

function setWorking(isWorking, cracking) {
  runButton.disabled = isWorking;
  runButton.textContent = isWorking && cracking ? "Cracking..." : "Run";
  resultWorking.hidden = !(isWorking && cracking);
  if (isWorking && cracking) {
    resultEmpty.hidden = true;
    resultBlock.hidden = true;
  }
}

async function readResponse(response) {
  try {
    return await response.json();
  } catch (error) {
    return null;
  }
}

function showCipherResult(data) {
  shiftEnteredLabel.textContent = "Shift entered";
  shiftUsedLabel.textContent = "Shift used";
  originalMessage.textContent = data.original;
  shiftEntered.textContent = String(data.shiftEntered);
  shiftUsed.textContent = `${data.shiftUsed} (wrapped into 0-25)`;
  confidenceRow.hidden = true;
  resultLabel.textContent = data.label;
  resultText.textContent = data.result;
  resultEmpty.hidden = true;
  resultBlock.hidden = false;
}

function showCrackResult(data) {
  const wordCount = `${data.matched} of ${data.words} words`;
  shiftEnteredLabel.textContent = "Shifts tried";
  shiftUsedLabel.textContent = "Shift found";
  originalMessage.textContent = data.original;
  shiftEntered.textContent = data.words === 0 ? "None" : `${data.shiftsTried} of 26`;
  shiftUsed.textContent = data.words === 0 ? "None" : String(data.shiftUsed);
  confidenceText.textContent = data.confident
    ? `${data.confidence}% (${wordCount})`
    : `${data.confidence}% (${wordCount}). Below 90%.`;
  confidenceRow.hidden = data.words === 0;
  resultLabel.textContent = data.label;
  resultText.textContent = data.result;
  resultEmpty.hidden = true;
  resultBlock.hidden = false;
}

async function showResult(message, shift, mode) {
  const cracking = mode === "crack";
  const response = await fetch(cracking ? "/api/crack" : "/api/cipher", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: cracking
      ? JSON.stringify({ message: message })
      : JSON.stringify({ message: message, shift: shift, mode: mode }),
  });

  const data = await readResponse(response);
  if (data === null) {
    showError("The cipher service returned an unreadable response.");
    return;
  }

  if (!response.ok) {
    showError(data.error || "The cipher could not run.");
    return;
  }

  if (cracking) {
    showCrackResult(data);
  } else {
    showCipherResult(data);
  }
}

form.addEventListener("submit", async function (event) {
  event.preventDefault();
  clearError();

  const message = messageInput.value;
  if (message === "") {
    showError("Enter a message.");
    return;
  }

  const shift = readShift(shiftInput.value);
  const mode = selectedMode();
  if (mode !== "crack" && shift === null) {
    showError("Invalid shift. Enter a whole number such as 3 or -1.");
    return;
  }

  setWorking(true, mode === "crack");

  try {
    await showResult(message, shift, mode);
  } catch (error) {
    showError("Could not reach the cipher service.");
  } finally {
    setWorking(false, false);
  }
});

document.querySelectorAll('input[name="mode"]').forEach(function (input) {
  input.addEventListener("change", syncShiftField);
});

document.querySelector("#clear-button").addEventListener("click", function () {
  form.reset();
  syncShiftField();
  clearError();
  setWorking(false, false);
  resultBlock.hidden = true;
  resultEmpty.hidden = false;
});

document.querySelectorAll(".sample").forEach(function (button) {
  button.addEventListener("click", async function () {
    const cracking = button.dataset.mode === "crack";
    form.elements.mode.value = button.dataset.mode;
    messageInput.value = button.dataset.message;
    if (button.dataset.shift) {
      shiftInput.value = button.dataset.shift;
    }
    syncShiftField();
    clearError();
    setWorking(true, cracking);

    try {
      await showResult(
        button.dataset.message,
        button.dataset.shift ? Number(button.dataset.shift) : null,
        button.dataset.mode
      );
    } catch (error) {
      showError("Could not reach the cipher service.");
    } finally {
      setWorking(false, false);
    }
  });
});
