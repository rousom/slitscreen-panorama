let cam;
let strips = [];
const slitHeight = 512;
const stripWidth = 1; // width of each vertical strip (default: 1)
let maxStrips = 720; // default 720

let lastCapture = 0;
let captureInterval = 0.5; // ms (adjust to taste)

let isPaused = false;

function setup() {
  console.log("heyy");
  createCanvas(stripWidth * maxStrips, 512).parent('canvas-wrapper');
  pixelDensity(1); // for consistent pixel access across displays
  frameRate(60); // force 60 FPS if possible
  
  // Get webcam feed (default camera)
  cam = createCapture(VIDEO);
  cam.size(width, height);
  console.log('Canvas:', width, height, 'Cam:', cam.width, cam.height);
  cam.hide(); // hides unmanipulated camera feed / video element
}

function draw() {
  // frameRate(10);
  background(255); // fill unwritten canvas with black

  if (!isPaused) {
    cam.loadPixels();// function sendBufferToPrinter() {

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