const fallbackConfig = {
  machineName: "Roblox Cloud PC",
  providerName: "Not configured",
  remoteAccessUrl: "https://remotedesktop.google.com/access",
  providerConsoleUrl: "",
  parsecUrl: "https://parsec.app/",
  moonlightUrl: "https://moonlight-stream.org/",
  robloxUrl: "https://www.roblox.com/",
  controlEnabled: false,
  statusMode: "browser-only",
};

const routes = {
  remote: {
    name: "Remote access",
    friction: "Configured remote desktop link",
    getUrl: (config) => config.remoteAccessUrl,
  },
  chrome: {
    name: "Chrome Remote Desktop",
    friction: "Requires Chrome Remote Desktop on the cloud PC",
    getUrl: () => "https://remotedesktop.google.com/access",
  },
  parsec: {
    name: "Parsec",
    friction: "Requires Parsec on both devices",
    getUrl: (config) => config.parsecUrl,
  },
  moonlight: {
    name: "Moonlight",
    friction: "Requires Sunshine on the cloud PC",
    getUrl: (config) => config.moonlightUrl,
  },
  roblox: {
    name: "Roblox",
    friction: "Open after remote access connects",
    getUrl: (config) => config.robloxUrl,
  },
  console: {
    name: "Provider console",
    friction: "Cloud billing and instance controls",
    getUrl: (config) => config.providerConsoleUrl,
  },
};

const deviceLabels = {
  phone: "Phone profile ready",
  tablet: "Tablet profile ready",
  desktop: "Desktop profile ready",
};

const regionLabels = {
  auto: "Auto region",
  na: "North America",
  eu: "Europe",
  apac: "Asia Pacific",
  latam: "Latin America",
};

let cloudConfig = { ...fallbackConfig };
let selectedRoute = "remote";
let selectedDevice = "phone";
let currentLatency = null;
let backendReachable = false;

const routeCards = document.querySelectorAll(".route-card");
const segmentButtons = document.querySelectorAll(".segment");
const selectedName = document.querySelector("#selectedName");
const providerName = document.querySelector("#providerName");
const quickLaunch = document.querySelector("#quickLaunch");
const refreshStatus = document.querySelector("#refreshStatus");
const screenMeta = document.querySelector("#screenMeta");
const regionSelect = document.querySelector("#region");
const sessionLength = document.querySelector("#sessionLength");
const sessionValue = document.querySelector("#sessionValue");
const sessionMetric = document.querySelector("#sessionMetric");
const machineRegion = document.querySelector("#machineRegion");
const machineName = document.querySelector("#machineName");
const latencyMetric = document.querySelector("#latencyMetric");
const cloudStatusMetric = document.querySelector("#cloudStatusMetric");
const accessMetric = document.querySelector("#accessMetric");
const panelStatus = document.querySelector("#panelStatus span");
const safeLogin = document.querySelector("#safeLogin");
const controlToken = document.querySelector("#controlToken");
const safetyState = document.querySelector("#safetyState");
const remoteAccessUrl = document.querySelector("#remoteAccessUrl");
const providerConsoleUrl = document.querySelector("#providerConsoleUrl");
const saveLinks = document.querySelector("#saveLinks");
const startMachine = document.querySelector("#startMachine");
const stopMachine = document.querySelector("#stopMachine");
const lastCheck = document.querySelector("#lastCheck");

function refreshIcons() {
  if (window.lucide) {
    window.lucide.createIcons();
  }
}

function loadLocalOverrides() {
  const raw = localStorage.getItem("cloudPcLinks");
  if (!raw) {
    return {};
  }

  try {
    return JSON.parse(raw);
  } catch {
    return {};
  }
}

function saveLocalOverrides() {
  const overrides = {
    remoteAccessUrl: remoteAccessUrl.value.trim(),
    providerConsoleUrl: providerConsoleUrl.value.trim(),
  };
  localStorage.setItem("cloudPcLinks", JSON.stringify(overrides));
  cloudConfig = { ...cloudConfig, ...overrides };
  render("Links saved");
}

async function loadConfig() {
  const localOverrides = loadLocalOverrides();

  try {
    const response = await fetch("/api/config", { cache: "no-store" });
    if (!response.ok) {
      throw new Error(`Config returned ${response.status}`);
    }
    const serverConfig = await response.json();
    cloudConfig = { ...fallbackConfig, ...serverConfig, ...localOverrides };
    backendReachable = true;
  } catch {
    cloudConfig = { ...fallbackConfig, ...localOverrides };
    backendReachable = false;
  }

  remoteAccessUrl.value = cloudConfig.remoteAccessUrl || "";
  providerConsoleUrl.value = cloudConfig.providerConsoleUrl || "";
  render();
}

function updateSafety(message) {
  const safe = safeLogin.checked;
  const selectedUrl = getSelectedUrl();
  safetyState.classList.toggle("is-warn", !safe || !selectedUrl);
  safetyState.querySelector("strong").textContent = safe && selectedUrl ? "Ready" : "Paused";

  if (!safe) {
    safetyState.querySelector("span").textContent = "Enable official login before opening external routes.";
  } else if (!selectedUrl) {
    safetyState.querySelector("span").textContent = "Add a URL for this selected route.";
  } else {
    safetyState.querySelector("span").textContent =
      message || (backendReachable ? "Backend connected. Credentials stay out of the browser." : "Browser-only mode. Run the Node server for live status.");
  }

  quickLaunch.disabled = !safe || !selectedUrl;
}

function updateRouteButtons() {
  routeCards.forEach((card) => {
    const isSelected = card.dataset.route === selectedRoute;
    card.classList.toggle("is-selected", isSelected);
    const iconButton = card.querySelector(".icon-button");
    iconButton.innerHTML = `<i data-lucide="${isSelected ? "check" : "circle"}"></i>`;
  });
  refreshIcons();
}

function getSelectedUrl() {
  const route = routes[selectedRoute];
  return route ? route.getUrl(cloudConfig) : "";
}

function formatSessionDuration(minutes) {
  const duration = Number(minutes);
  const hours = Math.floor(duration / 60);
  const remainingMinutes = duration % 60;

  if (duration < 60) {
    return `${duration} min`;
  }

  if (remainingMinutes === 0) {
    return `${hours} hr`;
  }

  return `${hours} hr ${remainingMinutes} min`;
}

function render(message) {
  const route = routes[selectedRoute];
  const sessionLabel = formatSessionDuration(sessionLength.value);
  selectedName.textContent = route.name;
  providerName.textContent = cloudConfig.providerName || "Not configured";
  machineName.textContent = cloudConfig.machineName || "Roblox Cloud PC";
  screenMeta.textContent = deviceLabels[selectedDevice];
  machineRegion.textContent = regionLabels[regionSelect.value];
  sessionValue.textContent = sessionLabel;
  sessionMetric.textContent = sessionLabel;
  accessMetric.textContent = selectedRoute === "remote" ? "Remote" : route.name;
  panelStatus.textContent = backendReachable ? "Backend connected" : "Browser-only mode";
  startMachine.disabled = !backendReachable || !cloudConfig.controlEnabled;
  stopMachine.disabled = !backendReachable || !cloudConfig.controlEnabled;
  updateSafety(message || route.friction);
  updateRouteButtons();
}

function setDevice(device) {
  selectedDevice = device;
  segmentButtons.forEach((button) => {
    button.classList.toggle("is-active", button.dataset.device === device);
  });
  render();
}

function selectRoute(routeKey) {
  selectedRoute = routeKey;
  render();
}

function runNetworkCheck() {
  const start = performance.now();
  requestAnimationFrame(() => {
    requestAnimationFrame(() => {
      const frameLatency = Math.round(performance.now() - start);
      const connection = navigator.connection || navigator.webkitConnection;
      const downlinkHint = connection?.downlink ? Math.round(connection.downlink) : null;
      currentLatency = Math.max(24, frameLatency + (downlinkHint ? Math.max(0, 80 - downlinkHint * 8) : 54));
      latencyMetric.textContent = `${currentLatency} ms`;
    });
  });
}

async function refreshCloudStatus() {
  if (!backendReachable) {
    cloudStatusMetric.textContent = "No backend";
    lastCheck.textContent = "Browser-only";
    render("Run the Node server for machine status.");
    return;
  }

  refreshStatus.disabled = true;
  cloudStatusMetric.textContent = "Checking";

  try {
    const response = await fetch("/api/status", { cache: "no-store" });
    const payload = await response.json();
    if (!response.ok) {
      throw new Error(payload.error || `Status returned ${response.status}`);
    }
    cloudStatusMetric.textContent = payload.statusLabel || payload.status || "Unknown";
    lastCheck.textContent = new Date(payload.checkedAt).toLocaleTimeString();
    render(payload.detail || "Status refreshed.");
  } catch (error) {
    cloudStatusMetric.textContent = "Error";
    lastCheck.textContent = "Failed";
    render(error.message || "Status check failed.");
  } finally {
    refreshStatus.disabled = false;
  }
}

async function machineAction(action) {
  if (!backendReachable || !cloudConfig.controlEnabled) {
    render("Machine control is not configured.");
    return;
  }

  const token = controlToken.value.trim();
  if (!token) {
    render("Enter the control token for start/stop.");
    return;
  }

  const targetButton = action === "start" ? startMachine : stopMachine;
  targetButton.disabled = true;

  try {
    const response = await fetch(`/api/machine/${action}`, {
      method: "POST",
      headers: { "x-control-token": token },
    });
    const payload = await response.json();
    if (!response.ok) {
      throw new Error(payload.error || `${action} returned ${response.status}`);
    }
    render(payload.detail || `${action} command sent.`);
    await refreshCloudStatus();
  } catch (error) {
    render(error.message || `${action} failed.`);
  } finally {
    targetButton.disabled = !backendReachable || !cloudConfig.controlEnabled;
  }
}

function launchSelectedRoute() {
  const url = getSelectedUrl();
  if (!url) {
    render("Add a URL for this selected route.");
    return;
  }
  window.open(url, "_blank", "noopener,noreferrer");
}

routeCards.forEach((card) => {
  card.addEventListener("click", () => selectRoute(card.dataset.route));
});

segmentButtons.forEach((button) => {
  button.addEventListener("click", () => setDevice(button.dataset.device));
});

regionSelect.addEventListener("change", render);
sessionLength.addEventListener("input", render);
safeLogin.addEventListener("change", () => render());
quickLaunch.addEventListener("click", launchSelectedRoute);
refreshStatus.addEventListener("click", refreshCloudStatus);
saveLinks.addEventListener("click", saveLocalOverrides);
startMachine.addEventListener("click", () => machineAction("start"));
stopMachine.addEventListener("click", () => machineAction("stop"));

loadConfig().then(() => {
  runNetworkCheck();
  refreshCloudStatus();
});
refreshIcons();
