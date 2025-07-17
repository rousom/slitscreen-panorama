
const scan = document.getElementsByClassName("scan-select");
const port = document.getElementsByClassName("portrait-select");
const manu = document.getElementsByClassName("manual-select");

const scanIcon = document.getElementsByClassName("scan-icon")[0];
const portIcon = document.getElementsByClassName("port-icon")[0];
const manuIcon = document.getElementsByClassName("manu-icon")[0];

const menuIcons = document.getElementsByClassName("menu-icon");

const screens = document.getElementsByClassName("screen");

function clear_screens() {
  for (let i = 0; i < screens.length; i++) {
    screens[i].style.display = "none";
  }
}
clear_screens();

document.getElementById("start").style.display = "block";

const selection_length = 2;

// Connect to Flask WebSocket server (make sure the port matches)
const socket = io("http://127.0.0.1:5051");
socket.on('error', err => {
  console.log("socket error: " + err);
})


socket.on("connect", () => {
  console.log("✅ Connected to WebSocket server");

  // Send a message to Flask
  socket.emit("message_from_client", { msg: "Hey Flask!" });
});

socket.on("message_from_server", (data) => {
  console.log("🛰️ Message from Flask:", data.msg);
});

socket.on("reply", (data) => {
  console.log("🔁 Reply:", data.msg);
});

socket.on("controller_event", (data) => {
  console.log(`🎮 Controller button ${data.button} pressed!`);
  // You can now trigger things in your UI or logic
});

socket.on("update_start_mode", (data) => {
  console.log(`set start mode ${data.mode}`);
  setMenuSelection(data.mode);
  // You can now trigger things in your UI or logic
});

socket.on("update_screen", (data) => {
  console.log(`set screen ${data.screen}`);
  clear_screens();
  switch (data.screen) {
    case "portrait_tutorial":
      document.getElementById("portrait_tutorial").style.display = "block";
      break;
    case "wait":
      document.getElementById("wait").style.display = "block";
      break;
    case "print":
      document.getElementById("print").style.display = "block";
      break;
    default:
      return;
  }
});

function setMenuSelection(mode) {
  for (let i = 0; i < menuIcons.length; i++) {
    menuIcons[i].removeAttribute("id");
  }
  switch (mode) {
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
}

for (let i = 0; i < selection_length; i++) {
  scan[i].style.visibility = "hidden";
  port[i].style.visibility = "visible";
  manu[i].style.visibility = "hidden";
}
portIcon.setAttribute("id", "selected-icon");

const gamepads = {};

function gamepadHandler(event, connected) {
  const gamepad = event.gamepad;
  // Note:
  // gamepad === navigator.getGamepads()[gamepad.index]

  if (connected) {
    gamepads[gamepad.index] = gamepad;
  } else {
    delete gamepads[gamepad.index];
  }
}

// window.addEventListener(
//   "gamepadconnected",
//   (e) => {
//     console.log("gamepad connected");
//     gamepadHandler(e, true);
//     setInterval(function () {
//       gameLoop();
//     }, 100);
//   },
//   false
// );
// window.addEventListener(
//   "gamepaddisconnected",
//   (e) => {
//     gamepadHandler(e, false);
//   },
//   false
// );

// var pressCool = false;

// function gameLoop() {
//   let gp = gamepads[0];

//   // for (let i = 0; i < 40; i++) {
//   //   if (gp.buttons[i].pressed) {
//   //      console.log(i);
//   //   }
//   // }

//   // console.log("presscool: " + pressCool);
//   if (!pressCool) {
//     let x = gp.axes[0];
//     let y = gp.axes[1];
//     if (x == -1) {
//       selectmode("left");
//       pressCool = true;
//     } else if (x == 1) {
//       selectmode("right");
//       pressCool = true;
//     }

//     if (gp.buttons[0].pressed) {
//       console.log("PRINT");
//       pressCool = true;
//       sendCanvasToServer();
//     }
//     // if (gp.buttons[2].pressed) {
//     //   console.log("2");
//     // }
//     if (gp.buttons[1].pressed) {
//       pressCool = true;
//       console.log("FREZZE PLEASE");
//     }
//     // if (gp.buttons[3].pressed) {
//     //   console.log("3");
//     // }
//     if (gp.buttons[14].pressed) {
//       selectmode("left");
//       pressCool = true;
//     }
//     if (gp.buttons[15].pressed) {
//       selectmode("right");
//       pressCool = true;
//     }
//     setTimeout(function () {
//       if (pressCool) {
//         pressCool = false;
//       }
//     }, 800);
//   }
// }

window.addEventListener(
  "keydown",
  (event) => {
    if (event.defaultPrevented) {
      return; // Do nothing if the event was already processed
    }

    switch (event.key) {
      case "ArrowLeft":
        selectmode("left");
        break;
      case "ArrowRight":
        selectmode("right");
        break;
      default:
        return; // Quit when this doesn't handle the key event.
    }

    // Cancel the default action to avoid it being handled twice
    event.preventDefault();
  },
  true
);


// let selected_mode = 1

// function selectmode(key) {
//   for (let i = 0; i < menuIcons.length; i++) {
//     menuIcons[i].removeAttribute("id");
//   }
//   switch (key) {
//     case "left":
//       switch (selected_mode) {
//         case 0: //scan selected
//           scanIcon.setAttribute("id", "selected-icon");
//           break;
//         case 1: //port > scan
//           selected_mode--;
//           for (let i = 0; i < selection_length; i++) {
//             scan[i].style.visibility = "visible";
//             port[i].style.visibility = "hidden";
//             manu[i].style.visibility = "hidden";
//           }
//           scanIcon.setAttribute("id", "selected-icon");
//           break;
//         case 2: //manual > port
//           selected_mode--;
//           for (let i = 0; i < selection_length; i++) {
//             scan[i].style.visibility = "hidden";
//             port[i].style.visibility = "visible";
//             manu[i].style.visibility = "hidden";
//           }
//           portIcon.setAttribute("id", "selected-icon");

//           break;
//         default:
//           break;
//       }
//       break;
//     case "right":
//       switch (selected_mode) {
//         case 0: //scan > port
//           selected_mode++;
//           for (let i = 0; i < selection_length; i++) {
//             scan[i].style.visibility = "hidden";
//             port[i].style.visibility = "visible";
//             manu[i].style.visibility = "hidden";
//           }
//           portIcon.setAttribute("id", "selected-icon");

//           break;
//         case 1: //port > manu
//           selected_mode++;
//           for (let i = 0; i < selection_length; i++) {
//             scan[i].style.visibility = "hidden";
//             port[i].style.visibility = "hidden";
//             manu[i].style.visibility = "visible";
//           }
//           manuIcon.setAttribute("id", "selected-icon");

//           break;
//         case 2: //manual selected
//           manuIcon.setAttribute("id", "selected-icon");

//           break;
//         default:
//           break;
//       }
//       break;
//     default:
//       return; // Quit when this doesn't handle the key event.
//   }
// }

document.addEventListener("keydown", function (e) {
  if (e.code === "Space") {
    e.preventDefault(); // prevent scrolling or form submission
    e.stopPropagation(); // 👈 prevent p5 or others from interfering
    setTimeout(() => sendCanvasToServer(), 0);
    return false;
  }
});

function sendCanvasToServer() {
  const canvas = document.querySelector("canvas");

  canvas.toBlob(async function (blob) {
    if (!blob) {
      console.error("Failed to convert canvas to blob.");
      return;
    }

    const formData = new FormData();
    formData.append("image", blob, "canvas.png");

    try {
      const res = await fetch("http://localhost:5051/upload", {
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
