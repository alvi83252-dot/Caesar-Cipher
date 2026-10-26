/*
  The page collects a message and a shift, then asks /api/cipher to run it.
  That route calls encrypt and decrypt in caesar_cipher.py, so the web page
  and the console program use one implementation.
*/

const form = document.querySelector("#cipher-form");
const messageInput = document.querySelector("#message");
const shiftInput = document.querySelector("#shift");
const errorText = document.querySelector("#form-error");
const resultEmpty = document.querySelector("#result-empty");
const resultBlock = document.querySelector("#result");
const originalMessage = document.querySelector("#original-message");
const shiftEntered = document.querySelector("#shift-entered");
const shiftUsed = document.querySelector("#shift-used");
const resultLabel = document.querySelector("#result-label");
const resultText = document.querySelector("#result-text");

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

async function showResult(message, shift, mode) {
  const response = await fetch("/api/cipher", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message: message, shift: shift, mode: mode }),
  });

  let data = {};
  try {
    data = await response.json();
  } catch (error) {
    showError("The cipher service returned an unreadable response.");
    return;
  }

  if (!response.ok) {
    showError(data.error || "The cipher could not run.");
    return;
  }

  originalMessage.textContent = data.original;
  shiftEntered.textContent = String(data.shiftEntered);
  shiftUsed.textContent = `${data.shiftUsed} (wrapped into 0-25)`;
  resultLabel.textContent = data.label;
  resultText.textContent = data.result;

  resultEmpty.hidden = true;
  resultBlock.hidden = false;
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
  if (shift === null) {
    showError("Invalid shift. Enter a whole number such as 3 or -1.");
    return;
  }

  const mode = form.elements.mode.value;
  const runButton = document.querySelector("#run-button");
  runButton.disabled = true;

  try {
    await showResult(message, shift, mode);
  } catch (error) {
    showError("Could not reach the cipher service.");
  } finally {
    runButton.disabled = false;
  }
});

document.querySelector("#clear-button").addEventListener("click", function () {
  form.reset();
  clearError();
  resultBlock.hidden = true;
  resultEmpty.hidden = false;
});

document.querySelectorAll(".sample").forEach(function (button) {
  button.addEventListener("click", function () {
    form.elements.mode.value = button.dataset.mode;
    messageInput.value = button.dataset.message;
    shiftInput.value = button.dataset.shift;
    clearError();
    showResult(
      button.dataset.message,
      Number(button.dataset.shift),
      button.dataset.mode
    ).catch(function () {
      showError("Could not reach the cipher service.");
    });
  });
});
