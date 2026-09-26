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
