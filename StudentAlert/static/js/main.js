// StudentAlert interactions: drag/drop upload, prediction wizard, and charts.
document.addEventListener("DOMContentLoaded", function () {
  const input = document.getElementById("datasetFile");
  const drop = document.getElementById("fileDrop");
  const fileName = document.getElementById("fileName");
  const dropTitle = document.getElementById("dropTitle");
  const dropHint = document.getElementById("dropHint");
  function showFile(file) {
    if (!file) return;
    const ext = file.name.toLowerCase().split(".").pop();
    if (!["csv", "xlsx"].includes(ext)) { fileName.textContent = "Please choose a .csv or .xlsx file."; input.value = ""; return; }
    fileName.textContent = file.name + " · " + (file.size / 1024).toFixed(1) + " KB";
    dropTitle.textContent = "File ready to analyse";
    dropHint.textContent = "Click Analyse students to continue";
  }
  if (input && drop) {
    input.addEventListener("change", () => showFile(input.files[0]));
    ["dragenter", "dragover"].forEach(evt => drop.addEventListener(evt, e => { e.preventDefault(); drop.classList.add("drag-over"); }));
    ["dragleave", "drop"].forEach(evt => drop.addEventListener(evt, e => { e.preventDefault(); drop.classList.remove("drag-over"); }));
    drop.addEventListener("drop", e => { const files = e.dataTransfer && e.dataTransfer.files; if (files && files.length) { input.files = files; showFile(files[0]); } });
  }

  const wizard = document.getElementById("predictionWizard");
  if (wizard) {
    const panels = Array.from(wizard.querySelectorAll("[data-step-panel]"));
    const tabs = Array.from(document.querySelectorAll(".wizard-tab"));
    const prev = document.getElementById("prevStep");
    const next = document.getElementById("nextStep");
    const submit = document.getElementById("submitPrediction");
    const count = document.getElementById("stepCount");
    const progress = document.getElementById("wizardProgress");
    let current = 0;
    function showStep(index) {
      current = index; panels.forEach((p, i) => p.classList.toggle("d-none", i !== current));
      tabs.forEach((t, i) => t.classList.toggle("active", i === current));
      count.textContent = String(current + 1).padStart(2, "0");
      progress.style.width = ((current + 1) / panels.length * 100) + "%";
      prev.disabled = current === 0;
      next.classList.toggle("d-none", current === panels.length - 1);
      submit.classList.toggle("d-none", current !== panels.length - 1);
    }
    function validCurrent() {
      const fields = panels[current].querySelectorAll("input, select, textarea");
      for (const field of fields) { if (!field.checkValidity()) { field.reportValidity(); field.focus(); return false; } }
      return true;
    }
    next.addEventListener("click", () => { if (validCurrent() && current < panels.length - 1) showStep(current + 1); });
    prev.addEventListener("click", () => { if (current > 0) showStep(current - 1); });
    tabs.forEach((tab, i) => tab.addEventListener("click", () => { if (i <= current) showStep(i); else if (validCurrent()) showStep(i); }));
    wizard.addEventListener("submit", e => { for (let i = 0; i < panels.length; i++) { const fields = panels[i].querySelectorAll("input, select, textarea"); for (const field of fields) { if (!field.checkValidity()) { e.preventDefault(); showStep(i); field.reportValidity(); field.focus(); return; } } } });
    showStep(0);
  }
});
