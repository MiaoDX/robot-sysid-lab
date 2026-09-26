// Lecture controls. Revealing a step keeps the current media element alive.
(() => {
  const data = window.presentationData;
  if (!data?.slides.length) return;

  const $ = (id) => document.getElementById(id);
  const stage = $("slide");
  const params = new URLSearchParams(location.search);
  let current = 0;
  let step = 1;
  let rendered = -1;
  let camera = params.get("camera") === "1";
  let recording = params.get("record") === "1";
  const clampStep = (value) => Math.min(data.slides[current].steps, Math.max(1, Number.isFinite(value) ? Math.trunc(value) : 1));

  function readLocation() {
    const index = data.slides.findIndex((item) => `#${item.id}` === location.hash);
    current = index < 0 ? 0 : index;
    step = clampStep(Number(new URLSearchParams(location.search).get("step")));
  }

  function updateUrl() {
    const url = new URL(location.href);
    url.hash = data.slides[current].id;
    url.searchParams.set("step", step);
    if (recording) url.searchParams.set("record", "1");
    else url.searchParams.delete("record");
    if (camera) url.searchParams.set("camera", "1");
    else url.searchParams.delete("camera");
    history.replaceState(null, "", url);
  }

  function icons() {
    window.lucide?.createIcons({attrs: {"aria-hidden": "true"}});
  }

  const chapterButtons = data.segments.map((name, index) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "chapter";
    button.setAttribute("aria-label", name);
    const label = document.createElement("span");
    label.className = "chapter-name";
    label.textContent = name;
    const track = document.createElement("span");
    track.className = "chapter-track";
    const fill = document.createElement("span");
    fill.className = "chapter-fill";
    track.append(fill);
    button.append(label, track);
    button.addEventListener("click", () => {
      current = data.slides.findIndex((item) => item.chapter === index);
      step = 1;
      render();
    });
    $("chapters").append(button);
    return button;
  });

  function updateProgress() {
    const item = data.slides[current];
    chapterButtons.forEach((button, index) => {
      const pages = data.slides.filter((page) => page.chapter === index);
      const total = pages.reduce((sum, page) => sum + page.steps, 0);
      const completed = pages.reduce((sum, page) => {
        const position = data.slides.indexOf(page);
        return sum + (position < current ? page.steps : position === current ? step : 0);
      }, 0);
      button.querySelector(".chapter-fill").style.transform = `scaleX(${completed / total})`;
      if (index === item.chapter) button.setAttribute("aria-current", "step");
      else button.removeAttribute("aria-current");
    });
    $("position").textContent = `${String(current + 1).padStart(2, "0")} / ${String(data.slides.length).padStart(2, "0")}`;
    $("step-position").textContent = data.lang === "zh-CN" ? `第 ${step} / ${item.steps} 步` : `Step ${step} / ${item.steps}`;
    $("previous").disabled = current === 0 && step === 1;
    $("next").disabled = current === data.slides.length - 1 && step === item.steps;
  }

  function updateReveals() {
    const final = step === data.slides[current].steps;
    for (const element of stage.querySelectorAll("[data-step]")) {
      const target = Number(element.dataset.step);
      element.classList.toggle("is-hidden", target > step);
      element.classList.toggle("is-past", target < step && !final);
      element.inert = target > step;
      if (target > step) element.setAttribute("aria-hidden", "true");
      else element.removeAttribute("aria-hidden");
    }
  }

  function updateView() {
    document.body.classList.toggle("recording", recording);
    document.body.classList.toggle("camera-visible", camera);
    $("record-toggle").setAttribute("aria-pressed", String(recording));
    $("camera-toggle").setAttribute("aria-pressed", String(camera));
    $("exit-recording").hidden = !recording;
    stage.querySelector(".camera-guide")?.remove();
    if (camera) {
      const guide = document.createElement("div");
      guide.className = "camera-guide";
      guide.setAttribute("aria-hidden", "true");
      guide.textContent = data.lang === "zh-CN" ? "讲师安全区 · 4:3" : "Instructor safe area · 4:3";
      stage.append(guide);
    }
  }

  function render() {
    const changed = rendered !== current;
    if (changed) {
      stage.querySelectorAll("video").forEach((video) => video.pause());
      const item = data.slides[current];
      stage.className = `slide ${item.className || ""}`;
      stage.innerHTML = `<div class="slide-content">${item.render()}</div>`;
      for (const element of stage.querySelectorAll("[data-math]")) {
        window.katex?.render(element.dataset.math, element, {displayMode: false, throwOnError: false, trust: false});
      }
      for (const choice of stage.querySelectorAll(".choice")) {
        choice.addEventListener("click", () => {
          for (const sibling of stage.querySelectorAll(".choice")) {
            sibling.classList.remove("correct", "incorrect");
            sibling.setAttribute("aria-pressed", String(sibling === choice));
          }
          choice.classList.add(choice.dataset.correct === "true" ? "correct" : "incorrect");
          step = item.steps;
          render();
        });
      }
      $("notes").replaceChildren();
      const note = document.createElement("p");
      note.textContent = item.notes;
      $("notes").append(note);
      document.dispatchEvent(new Event("course:media-ready"));
      rendered = current;
    }
    updateReveals();
    updateProgress();
    updateView();
    updateUrl();
    icons();
    if (changed && matchMedia("(max-width: 600px)").matches) scrollTo({top: 0, behavior: "instant"});
  }

  function advance(direction) {
    if (direction > 0) {
      if (step < data.slides[current].steps) step++;
      else if (current < data.slides.length - 1) { current++; step = 1; }
    } else if (step > 1) step--;
    else if (current > 0) { current--; step = data.slides[current].steps; }
    render();
  }

  $("previous").addEventListener("click", () => advance(-1));
  $("next").addEventListener("click", () => advance(1));
  document.addEventListener("keydown", (event) => {
    if (event.altKey || event.ctrlKey || event.metaKey || event.target.closest("video,input,textarea,select,[contenteditable]")) return;
    if (event.key === " " && event.target.closest("button,a,summary")) return;
    if (["ArrowRight", "PageDown", " "].includes(event.key)) { event.preventDefault(); advance(1); }
    else if (["ArrowLeft", "PageUp"].includes(event.key)) { event.preventDefault(); advance(-1); }
    else if (event.key === "Home") { event.preventDefault(); current = 0; step = 1; render(); }
    else if (event.key === "End") { event.preventDefault(); current = data.slides.length - 1; step = data.slides[current].steps; render(); }
    else if (event.key === "Escape" && recording) exitRecording();
  });

  $("notes-toggle").addEventListener("click", () => {
    const open = $("notes").hidden;
    $("notes-toggle").setAttribute("aria-pressed", String(open));
    $("notes").hidden = !open;
  });
  $("camera-toggle").addEventListener("click", () => { camera = !camera; render(); });
  $("record-toggle").addEventListener("click", () => {
    recording = !recording;
    $("notes").hidden = true;
    $("notes-toggle").setAttribute("aria-pressed", "false");
    render();
  });
  function exitRecording() { recording = false; render(); $("record-toggle").focus({preventScroll: true}); }
  $("exit-recording").addEventListener("click", exitRecording);

  const fullscreen = $("fullscreen-toggle");
  fullscreen.disabled = !document.fullscreenEnabled;
  fullscreen.addEventListener("click", async () => {
    try {
      if (document.fullscreenElement) await document.exitFullscreen();
      else await document.documentElement.requestFullscreen();
    } catch { fullscreen.setAttribute("data-tooltip", data.lang === "zh-CN" ? "浏览器未允许全屏" : "Fullscreen was not allowed"); }
  });
  document.addEventListener("fullscreenchange", () => fullscreen.setAttribute("aria-pressed", String(Boolean(document.fullscreenElement))));
  addEventListener("hashchange", () => { readLocation(); render(); });
  addEventListener("popstate", () => { readLocation(); render(); });
  readLocation();
  render();
})();
