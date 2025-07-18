const scan = document.getElementsByClassName("scan-select");
const port = document.getElementsByClassName("portrait-select");
const manu = document.getElementsByClassName("manual-select");

const scanIcon = document.getElementsByClassName("scan-icon")[0];
const portIcon = document.getElementsByClassName("port-icon")[0];
const manuIcon = document.getElementsByClassName("manu-icon")[0];

const menuIcons = document.getElementsByClassName("menu-icon");

const screens = document.getElementsByClassName("screen");

const person_height = document.getElementById("person_height");

function clear_screens() {
  for (let i = 0; i < screens.length; i++) {
    screens[i].style.display = "none";
  }
}
clear_screens();
document.getElementById("start").style.display = "block";
const selection_length = 2;

for (let i = 0; i < selection_length; i++) {
  scan[i].style.visibility = "hidden";
  port[i].style.visibility = "visible";
  manu[i].style.visibility = "hidden";
}
portIcon.setAttribute("id", "selected-icon");

// Connect to Flask WebSocket server (make sure the port matches)
const socket = io("http://127.0.0.1:5051");
socket.on("error", (err) => {
  console.log("socket error: " + err);
});

socket.on("connect", () => {
  console.log("✅ Connected to WebSocket server");
  // Send a message to Flask
  socket.emit("message_from_client", { msg: "Hey Flask!" });
});

socket.on("update_start_mode", (data) => {
  console.log(`set start mode ${data.mode}`);
  for (let i = 0; i < menuIcons.length; i++) {
    menuIcons[i].removeAttribute("id");
  }
  switch (data.mode) {
    case "portrait":
      for (let i = 0; i < selection_length; i++) {
        scan[i].style.visibility = "hidden";
        port[i].style.visibility = "visible";
        manu[i].style.visibility = "hidden";
      }
      portIcon.setAttribute("id", "selected-icon");
      break;
    case "manual":
      for (let i = 0; i < selection_length; i++) {
        scan[i].style.visibility = "hidden";
        port[i].style.visibility = "hidden";
        manu[i].style.visibility = "visible";
      }
      manuIcon.setAttribute("id", "selected-icon");
      break;
    case "scan":
      for (let i = 0; i < selection_length; i++) {
        scan[i].style.visibility = "visible";
        port[i].style.visibility = "hidden";
        manu[i].style.visibility = "hidden";
      }
      scanIcon.setAttribute("id", "selected-icon");
      break;
    default:
      break;
  }
  // You can now trigger things in your UI or logic
});

socket.on("update_screen", (data) => {
  console.log(`set screen ${data.screen}`);
  clear_screens();
  document.getElementById(data.screen).style.display = "block";
});

socket.on("update_height", (data) => {
  console.log(`set height ${data.height}`);
  let h = data.height;
  console.log(h);
  person_height.innerHTML = h;
});

socket.on("update_canvas_width_for", (data) => {
  console.log(`update canvas width for ${data.mode} mode`);
  let _canvasWidth = 720;
  switch (data.mode) {
    case "portrait":
      _canvasWidth = 1150;
      // resizeCanvasWidth(720 * 3);
      break;
    case "scan":
      _canvasWidth = 950;
      // resizeCanvasWidth(720 * 3);
      break;
    case "manual":
      _canvasWidth = 720;
      // resizeCanvasWidth(720 * 1);
      break;
    default:
      return;
  }
  resizeCanvasWidth(_canvasWidth);
  getElementById("defaultCanvas0").width = _canvasWidth;

});

socket.on("print_canvas", (data) => {
  console.log(` print request: ${data.print}`);
  if (data.print) {
    sendPrintRequest();
  }
});

socket.on("pause_canvas", (data) => {
  console.log(` print request: ${data.pause}`);
  isPaused = data.pause;
  // if (data.pause) {
  // }
});

function resizeCanvasWidth(pixels) {
  strips = [];
  const newMaxStrips = Math.floor(pixels / stripWidth);
  maxStrips = newMaxStrips;
  resizeCanvas(stripWidth * maxStrips, slitHeight);
  console.log(`Canvas resized to ${stripWidth * maxStrips}x${slitHeight}`);
}

document.addEventListener("keydown", function (e) {
  if (e.code === "Space") {
    e.preventDefault(); // prevent scrolling or form submission
    e.stopPropagation(); // 👈 prevent p5 or others from interfering
    setTimeout(() => sendCanvasToServer(), 0);
    return false;
  }
});

function sendPrintRequest() {
  const canvas = document.querySelector("canvas");

  canvas.toBlob(async function (blob) {
    if (!blob) {
      console.error("Failed to convert canvas to blob.");
      return;
    }

    const formData = new FormData();
    formData.append("image", blob, "canvas.png");

    try {
      const res = await fetch("http://localhost:5052/upload", {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        const errorText = await res.text();
        console.error(
          `Upload failed: ${res.status} ${res.statusText}\n${errorText}`
        );
        return;
      }

      const responseText = await res.text();
      console.log("✅ Server says:", responseText);
    } catch (err) {
      console.error("❌ Network or server error:", err);
    }
  }, "image/png");
}
