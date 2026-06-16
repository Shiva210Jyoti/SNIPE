const form = document.getElementById("shorten-form");
const urlInput = document.getElementById("url-input");
const submitBtn = document.getElementById("submit-btn");
const errorMsg = document.getElementById("error-msg");
const resultBox = document.getElementById("result");
const shortLink = document.getElementById("short-link");
const originalUrl = document.getElementById("original-url");
const copyBtn = document.getElementById("copy-btn");

function showError(message) {
  errorMsg.textContent = message;
  errorMsg.classList.remove("hidden");
  resultBox.classList.add("hidden");
}

function hideError() {
  errorMsg.classList.add("hidden");
}

function showResult(data) {
  shortLink.href = data.short_url;
  shortLink.textContent = data.short_url;
  originalUrl.textContent = data.original_url;
  resultBox.classList.remove("hidden");
}

copyBtn.addEventListener("click", async () => {
  const text = shortLink.textContent;
  try {
    await navigator.clipboard.writeText(text);
    copyBtn.textContent = "Copied!";
    setTimeout(() => {
      copyBtn.textContent = "Copy";
    }, 2000);
  } catch {
    showError("Could not copy to clipboard.");
  }
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  hideError();

  const url = urlInput.value.trim();
  if (!url) {
    showError("Please enter a URL.");
    return;
  }

  submitBtn.disabled = true;
  submitBtn.textContent = "Shortening...";

  try {
    const response = await fetch("/api/v1/urls", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url }),
    });

    const data = await response.json();

    if (!response.ok) {
      const detail = data.detail;
      const message = Array.isArray(detail)
        ? detail.map((item) => item.msg).join(", ")
        : detail || "Something went wrong.";
      showError(message);
      return;
    }

    showResult(data);
  } catch {
    showError("Network error. Is the server running?");
  } finally {
    submitBtn.disabled = false;
    submitBtn.textContent = "Shorten";
  }
});
