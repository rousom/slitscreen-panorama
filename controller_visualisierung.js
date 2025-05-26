// Verbindung zum Python Socket.IO Server (Adresse ggf. anpassen)
const socket = io("http://localhost:5500");

// Element dynamisch erzeugen
document.addEventListener("DOMContentLoaded", () => {
  // Erstelle Titel und Anzeigeelement
  const heading = document.createElement("h1");
  heading.textContent = "🎮 Controller-Daten";

  const pre = document.createElement("pre");
  pre.id = "controllerData";
  pre.textContent = "Warte auf Daten...";

  // Füge Elemente zum Body hinzu
  document.body.style.fontFamily = "monospace";
  document.body.style.background = "#111";
  document.body.style.color = "#0f0";
  document.body.style.padding = "2em";
  document.body.appendChild(heading);
  document.body.appendChild(pre);

  // WebSocket-Events
  socket.on("controller_data", data => {
    pre.textContent = JSON.stringify(data, null, 2);
  });

  socket.on("connect", () => {
    console.log("✅ Verbunden mit Server");
  });

  socket.on("disconnect", () => {
    console.log("❌ Verbindung getrennt");
  });
});
