let cam;
let strips = [];
const slitHeight = 512;
const stripWidth = 1; // width of each vertical strip (default: 1)
const maxStrips = 720; // default 640

let lastCapture = 0;
let captureInterval = 0.5; // ms (adjust to taste)

let isPaused = false;

function setup() {
  createCanvas(stripWidth * maxStrips, 512).parent('canvas-wrapper');
  pixelDensity(1); // for consistent pixel access across displays
  frameRate(60); // force 60 FPS if possible

  // Get webcam feed (default camera)
  cam = createCapture(VIDEO);
  cam.size(width, height);
  cam.hide(); // hides unmanipulated camera feed / video element

  // let slider = createSlider(0.1, 100, 20); // min, max, initial
  // slider.input(() => {
  //   captureInterval = slider.value();
  // });

  // let pauseBtn = createButton("Pause");
  // pauseBtn.position(10, height + 10);
  // pauseBtn.mousePressed(() => {
  //   isPaused = !isPaused;
  //   pauseBtn.html(isPaused ? "Resume" : "Pause");
  // });
}

function draw() {
  // frameRate(10);
  background(0); // fill unwritten canvas with black

  if (!isPaused) {
    cam.loadPixels();// function sendBufferToPrinter() {
//   // Transpose from [640][512] to flat array of 512 rows × 640 cols
//   let transposed = [];
//   for (let y = 0; y < BUFFER_HEIGHT; y++) {
//     for (let x = 0; x < BUFFER_WIDTH; x++) {
//       transposed.push(buffer[x][y]);
//     }
//   }

//   fetch("http://localhost:5050/print-buffer", {
//     method: "POST",
//     headers: { "Content-Type": "application/json" },
//     body: JSON.stringify({
//       width: BUFFER_WIDTH,
//       height: BUFFER_HEIGHT,
//       pixels: transposed,
//     }),
//   })
//     .then((res) => res.text())
//     .then(console.log);

//   buffer = []; // reset for next round
// }

// function sendStripToPrinter(bwRow) {
//   console.log(bwRow)
//   fetch('http://localhost:5050/print_array', {
//     method: 'POST',
//     headers: { 'Content-Type': 'application/json' },
//     body: JSON.stringify(bwRow)
//   })
//   .then(res => res.text())
//   .then(txt => console.log(txt))
//   .catch(err => console.error(err));
// }


    if (millis() - lastCapture > captureInterval) {
      captureStrip(); // ← Move your strip logic into this function
      lastCapture = millis();
    }

    if (strips.length > maxStrips) {
      strips.shift();
    }
  }

  function captureStrip() {
    // Get the center strip from webcam
    let yStart = height / 2 - slitHeight / 2; // only useful, if stripHeight is not the same as camera feed / canvas height
    let xStart = floor(cam.width / 2 - stripWidth / 2);
    let strip = createImage(stripWidth, slitHeight);
    strip.loadPixels();

    bwArray = [];
    let bwRow = [];

    for (let y = 0; y < slitHeight; y++) {
      for (let x = 0; x < stripWidth; x++) {
        let camX = xStart + x;
        let i = 4 * ((yStart + y) * cam.width + camX); // source index
        let j = 4 * (y * stripWidth + x); // target index
        strip.pixels[j] = cam.pixels[i]; // red pixeld
        strip.pixels[j + 1] = cam.pixels[i + 1]; // blue pixels
        strip.pixels[j + 2] = cam.pixels[i + 2]; // green pixels
        strip.pixels[j + 3] = 255; // opacity
        let r = cam.pixels[i];
        let g = cam.pixels[i + 1];
        let b = cam.pixels[i + 2];
        let avg = (r + g + b) / 3;
        bwRow.push(avg > 127 ? 1 : 0); // 1 = white, 0 = black)
      }
      // if (buffer.length < BUFFER_WIDTH) {
      //   buffer.push(strip);
      // }
    }

    strip.updatePixels();
    strips.push(strip);
  }

  for (let i = 0; i < strips.length; i++) {
    image(strips[i], i * stripWidth, 0, stripWidth, height);
  }
}

// window.addEventListener("keydown", function(e) {
//   if (e.code === "Space" && e.target === document.body) {
//     e.preventDefault(); // Stop scrolling or other default behavior
//   }
// });

// // Send strip to Python while spacebar is held
// function keyReleased(event) {
//   if (key === " ") {
//     event.preventDefault?.();  // prevent if it's a real keyboard event
//     sendCanvasToServer();
//     return false; // ← This also prevents default browser behavior
//     // if (buffer.length === BUFFER_WIDTH) {
//     //   console.log(buffer); // Check what you're sending
//     //   sendBufferToPrinter();
//     // } else {
//     //   console.log("Buffer not full yet.");
//     // }
//   }
// }

// function sendCanvasToServer() {
//   let canvas = document.querySelector('canvas');
//   canvas.toBlob(function(blob) {
//     let formData = new FormData();
//     formData.append('image', blob, 'canvas.png');

//     fetch('http://localhost:5051/upload', {
//       method: 'POST',
//       body: formData
//     })
//     .then(res => res.text())
//     .then(data => {
//       console.log('Server says:', data);
//     })
//     .catch(err => {
//       console.error('Error:', err);
//     });
//   }, 'image/png');
// }