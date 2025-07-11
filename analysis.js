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

  function setupSubTabs(tabGroup, tabBtnClass, contentClass) {
  document.querySelectorAll(`.${tabBtnClass}`).forEach(button => {
    button.addEventListener('click', () => {
      document.querySelectorAll(`.${tabBtnClass}`).forEach(btn => btn.classList.remove('active'));
      button.classList.add('active');

      document.querySelectorAll(`.${contentClass}`).forEach(content => content.classList.remove('active'));
      const targetId = button.getAttribute('data-target');
      document.getElementById(targetId).classList.add('active');
    });
  });
}

// Init all sub-tab groups
setupSubTabs('region', 'region-sub-tab', 'region-sub-content');
setupSubTabs('industry', 'industry-sub-tab', 'industry-sub-content');
setupSubTabs('growth', 'growth-sub-tab', 'growth-sub-content');
setupSubTabs('share', 'share-sub-tab', 'share-sub-content');

// Main tab switch logic (existing)
document.querySelectorAll('.desc-tab').forEach(mainTab => {
  mainTab.addEventListener('click', () => {
    document.querySelectorAll('.desc-tab').forEach(t => t.classList.remove('active'));
    mainTab.classList.add('active');

    document.querySelectorAll('.desc-content').forEach(c => c.classList.remove('active'));
    const target = mainTab.getAttribute('data-tab');
    document.getElementById(`desc-${target}`).classList.add('active');
  });
});

  // MAIN TAB SWITCHING
  document.querySelectorAll('.desc-tab').forEach(mainTab => {
    mainTab.addEventListener('click', () => {
      // Remove 'active' class from all main tabs
      document.querySelectorAll('.desc-tab').forEach(t => t.classList.remove('active'));
      // Add 'active' to clicked main tab
      mainTab.classList.add('active');

      // Hide all .desc-content sections
      document.querySelectorAll('.desc-content').forEach(section => section.classList.remove('active'));

      // Show only the matching tab section
      const target = mainTab.getAttribute('data-tab');
      document.getElementById(`desc-${target}`).classList.add('active');
    });
  });


   function setupSubTabs(tabGroup, tabBtnClass, contentClass) {
    document.querySelectorAll(`.${tabBtnClass}`).forEach(button => {
      button.addEventListener('click', () => {
        document.querySelectorAll(`.${tabBtnClass}`).forEach(btn => btn.classList.remove('active'));
        button.classList.add('active');

        document.querySelectorAll(`.${contentClass}`).forEach(content => content.classList.remove('active'));
        const targetId = button.getAttribute('data-target');
        document.getElementById(targetId).classList.add('active');
      });
    });
  }

  // Predictive main tabs
  document.querySelectorAll('.pred-tab').forEach(mainTab => {
    mainTab.addEventListener('click', () => {
      document.querySelectorAll('.pred-tab').forEach(t => t.classList.remove('active'));
      mainTab.classList.add('active');

      document.querySelectorAll('.pred-content').forEach(c => c.classList.remove('active'));
      const target = mainTab.getAttribute('data-tab');
      document.getElementById(`pred-${target}`).classList.add('active');
    });
  });

  // Setup predictive sub-tab groups
  setupSubTabs('forecast-region', 'forecast-region-sub-tab', 'forecast-region-sub-content');
  setupSubTabs('forecast-industry', 'forecast-industry-sub-tab', 'forecast-industry-sub-content');
  setupSubTabs('model-summary', 'model-sub-tab', 'model-sub-content');

  function fadeIn(element) {
  element.style.opacity = 0;
  element.style.display = 'block';

  let opacity = 0;
  const fade = setInterval(() => {
    opacity += 0.05;
    element.style.opacity = opacity;
    if (opacity >= 1) clearInterval(fade);
  }, 10);
}

function fadeToTab(tabClass, contentClass) {
  document.querySelectorAll(`.${tabClass}`).forEach(btn => {
    btn.addEventListener('click', () => {
      const targetId = btn.getAttribute('data-target');
      const targetEl = document.getElementById(targetId);

      document.querySelectorAll(`.${contentClass}`).forEach(el => {
        el.style.display = 'none';
      });

      fadeIn(targetEl);
    });
  });
}

// Example usage:
fadeToTab('region-sub-tab', 'region-sub-content');

  function openModal(id) {
    document.getElementById(id).style.display = "block";
  }

  function closeModal(id) {
    document.getElementById(id).style.display = "none";
  }

  // Optional: close modal when clicking outside
  window.onclick = function (event) {
    const modals = document.querySelectorAll(".gdp-modal");
    modals.forEach(modal => {
      if (event.target == modal) {
        modal.style.display = "none";
      }
    });
  }
