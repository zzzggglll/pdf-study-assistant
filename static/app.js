const fileInput = document.getElementById("file-input");
const dropzone = document.getElementById("dropzone");
const submitBtn = document.getElementById("submit-btn");
const resetBtn = document.getElementById("reset-btn");
const copyBtn = document.getElementById("copy-btn");
const statusHint = document.getElementById("status-hint");
const resultBox = document.getElementById("result-box");
const resultMode = document.getElementById("result-mode");
const toast = document.getElementById("toast");
const goalInputs = document.querySelectorAll('input[name="goal"]');
const scenarioInputs = document.querySelectorAll('input[name="scenario"]');

let selectedFile = null;
let toastTimer = null;

function showToast(message, ok = false) {
  toast.textContent = message;
  toast.classList.toggle("ok", ok);
  toast.hidden = false;

  if (toastTimer) {
    window.clearTimeout(toastTimer);
  }

  toastTimer = window.setTimeout(() => {
    toast.hidden = true;
    toastTimer = null;
  }, 3600);
}

function setStatus(text) {
  statusHint.textContent = text;
  statusHint.classList.toggle("is-complete", text === "完成");
}

function setLoading(loading) {
  submitBtn.disabled = loading;
  submitBtn.textContent = loading ? "生成中..." : "生成考点总结";
}

function getSelectedInput(inputs) {
  return Array.from(inputs).find((input) => input.checked) || null;
}

function getSelectedMode() {
  const goalInput = getSelectedInput(goalInputs);
  const scenarioInput = getSelectedInput(scenarioInputs);
  const goalLabel = goalInput?.dataset.label || "考前冲刺";
  const scenarioLabel = scenarioInput?.dataset.label || "自主复习";

  return {
    goal: goalInput?.value || "exam",
    scenario: scenarioInput?.value || "self_study",
    goalLabel,
    scenarioLabel,
    text: `${goalLabel} · ${scenarioLabel}`,
  };
}

function updateModePreview() {
  const mode = getSelectedMode();
  resultMode.textContent = `当前模式：${mode.text}`;
}

function openFilePicker() {
  fileInput.value = "";
  fileInput.click();
}

function handleFiles(files) {
  if (!files || !files.length) {
    return;
  }

  const file = files[0];
  if (file.type !== "application/pdf") {
    selectedFile = null;
    showToast("仅支持 PDF 文件");
    setStatus("请选择 PDF 文件");
    return;
  }

  selectedFile = file;
  setStatus(`已选择文件：${file.name}`);
}

dropzone.addEventListener("click", openFilePicker);
dropzone.addEventListener("keydown", (event) => {
  if (event.key === "Enter" || event.key === " ") {
    event.preventDefault();
    openFilePicker();
  }
});

fileInput.addEventListener("change", (event) => {
  handleFiles(event.target.files);
});

dropzone.addEventListener("dragover", (event) => {
  event.preventDefault();
  dropzone.classList.add("dragover");
});

dropzone.addEventListener("dragleave", () => {
  dropzone.classList.remove("dragover");
});

dropzone.addEventListener("drop", (event) => {
  event.preventDefault();
  dropzone.classList.remove("dragover");
  handleFiles(event.dataTransfer.files);
});

submitBtn.addEventListener("click", async () => {
  const mode = getSelectedMode();

  if (!selectedFile) {
    showToast("请先选择 PDF 文件");
    return;
  }

  const formData = new FormData();
  formData.append("file", selectedFile);
  formData.append("goal", mode.goal);
  formData.append("scenario", mode.scenario);

  setLoading(true);
  setStatus(`生成中：${mode.text}`);
  resultBox.textContent = "生成中...";
  resultMode.textContent = `当前模式：${mode.text}`;

  try {
    const response = await fetch("/api/summarize", {
      method: "POST",
      body: formData,
    });
    const data = await response.json();

    if (!data.ok) {
      throw new Error(data.error || "生成失败");
    }

    resultBox.textContent = data.summary;
    showToast("生成完成", true);
    setStatus("完成");
    resultMode.textContent = `当前模式：${data.goal_label} · ${data.scenario_label}`;
  } catch (error) {
    resultBox.textContent = "生成失败";
    showToast(error.message || "请求失败");
    setStatus("请检查文件后重试");
  } finally {
    setLoading(false);
  }
});

resetBtn.addEventListener("click", () => {
  selectedFile = null;
  fileInput.value = "";
  resultBox.textContent = "等待上传并生成...";
  setStatus("准备就绪");
  updateModePreview();
});

copyBtn.addEventListener("click", async () => {
  const text = resultBox.textContent.trim();
  if (!text) {
    showToast("没有可复制的内容");
    return;
  }

  try {
    await navigator.clipboard.writeText(text);
    showToast("已复制到剪贴板", true);
  } catch {
    showToast("复制失败，请手动选择");
  }
});

goalInputs.forEach((input) => {
  input.addEventListener("change", updateModePreview);
});

scenarioInputs.forEach((input) => {
  input.addEventListener("change", updateModePreview);
});

updateModePreview();
