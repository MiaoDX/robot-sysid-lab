// Render the selected WebVTT track below each lesson video instead of over it.
(() => {
  const setupSubtitles = () => {
    const language = document.documentElement.lang === "zh-CN" ? "zh-CN" : "en";
    const label = language === "zh-CN" ? "字幕" : "Subtitles";

    for (const video of document.querySelectorAll("video")) {
      const tracks = [...video.textTracks];
      if (!tracks.length || video.nextElementSibling?.classList.contains("clip-subtitles")) continue;

      const selected = tracks.find((track) => track.language === language) || tracks[0];
      for (const track of tracks) track.mode = track === selected ? "hidden" : "disabled";

      const panel = document.createElement("div");
      panel.className = "clip-subtitles";
      panel.setAttribute("aria-label", label);
      panel.setAttribute("aria-live", "polite");
      video.insertAdjacentElement("afterend", panel);

      // Reserve the tallest cue so subtitle changes do not move the article.
      const reserveSpace = () => {
        const measure = panel.cloneNode(false);
        measure.removeAttribute("aria-live");
        measure.setAttribute("aria-hidden", "true");
        measure.style.minHeight = "";
        measure.style.width = `${panel.getBoundingClientRect().width}px`;
        measure.style.position = "absolute";
        measure.style.visibility = "hidden";
        measure.style.pointerEvents = "none";
        panel.parentElement.append(measure);
        let height = measure.getBoundingClientRect().height;
        for (const cue of selected.cues || []) {
          measure.textContent = cue.text;
          height = Math.max(height, measure.getBoundingClientRect().height);
        }
        measure.remove();
        panel.style.minHeight = `${Math.ceil(height)}px`;
      };
      const trackElement = [...video.querySelectorAll("track")].find((track) => track.track === selected);
      trackElement?.addEventListener("load", reserveSpace);
      new ResizeObserver(reserveSpace).observe(video);
      reserveSpace();

      const render = () => {
        const cues = selected.activeCues ? [...selected.activeCues] : [];
        panel.textContent = cues.map((cue) => cue.text).join("\n").trim();
        panel.classList.toggle("is-active", panel.textContent.length > 0);
      };

      selected.addEventListener("cuechange", render);
      for (const event of ["loadedmetadata", "timeupdate", "seeked", "play", "pause"]) {
        video.addEventListener(event, render);
      }
      render();
    }
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", setupSubtitles, {once: true});
  } else {
    setupSubtitles();
  }
  document.addEventListener("course:media-ready", setupSubtitles);
})();
