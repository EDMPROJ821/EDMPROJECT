const mainLinks = document.querySelectorAll(".main-link");
  const sections = document.querySelectorAll("section");

  mainLinks.forEach(link => {
    link.addEventListener("click", (e) => {
      e.preventDefault();
      const targetId = link.getAttribute("href").substring(1);

      mainLinks.forEach(l => l.classList.remove("active"));
      link.classList.add("active");

      sections.forEach(sec => sec.classList.remove("active"));
      document.getElementById(targetId).classList.add("active");
    });
  });

  // Descriptive nested tabs
  const descTabs = document.querySelectorAll(".desc-tab");
  const descContents = document.querySelectorAll(".desc-content");

  descTabs.forEach(button => {
    button.addEventListener("click", () => {
      const tabId = "desc-" + button.dataset.tab;

      descTabs.forEach(btn => btn.classList.remove("active"));
      button.classList.add("active");

      descContents.forEach(content => content.classList.remove("active"));
      document.getElementById(tabId).classList.add("active");
    });
  });

  // Predictive nested tabs
  const predTabs = document.querySelectorAll(".pred-tab");
  const predContents = document.querySelectorAll(".pred-content");

  predTabs.forEach(button => {
    button.addEventListener("click", () => {
      const tabId = "pred-" + button.dataset.tab;

      predTabs.forEach(btn => btn.classList.remove("active"));
      button.classList.add("active");

      predContents.forEach(content => content.classList.remove("active"));
      document.getElementById(tabId).classList.add("active");
    });
  });