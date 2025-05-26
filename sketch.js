let cam;
let strips = [];
const slitHeight = 480;
const stripWidth = 2; // width of each vertical strip
const maxStrips = 640; // default 640

let lastCapture = 0;
let captureInterval = 1; // ms (adjust to taste)

let isPaused = false;

//Testkommentar für GitHub

function setup() {
    createCanvas(stripWidth * maxStrips, 480);
    pixelDensity(1); // for consistent pixel access across displays
    frameRate(60); // force 60 FPS if possible

    // Get webcam feed (default camera)
    cam = createCapture(VIDEO);
    cam.size(width, height);
    // cam.hide(); // hides unmanipulated camera feed / video element

    let slider = createSlider(0.1, 100, 20); // min, max, initial
    slider.input(() => {
        captureInterval = slider.value();
    });

    let pauseBtn = createButton('Pause');
    pauseBtn.position(10, height + 10);
    pauseBtn.mousePressed(() => {
    isPaused = !isPaused;
    pauseBtn.html(isPaused ? 'Resume' : 'Pause');
  });
}


function draw() {
    background(0); // fill unwritten canvas with black

    if (!isPaused) {
        cam.loadPixels();

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

        for (let y = 0; y < slitHeight; y++) {
            for (let x = 0; x < stripWidth; x++) {
                let camX = xStart + x;
                let i = 4 * ((yStart + y) * cam.width + camX);       // source index
                let j = 4 * (y * stripWidth + x);                    // target index
                strip.pixels[j] = cam.pixels[i];
                strip.pixels[j + 1] = cam.pixels[i + 1];
                strip.pixels[j + 2] = cam.pixels[i + 2];
                strip.pixels[j + 3] = 255;
            }
        }
        strip.updatePixels();
        strips.push(strip);
    }

   

    // Blended rendering (not working will)
    // for (let i = 0; i < strips.length - 1; i++) {
    //     let A = strips[i];
    //     let B = strips[i + 1];

    //     for (let x = 0; x < stripWidth; x++) {
    //     let blendFactor = x / stripWidth;
    //     let blendedColumn = createImage(1, slitHeight);
    //     blendedColumn.loadPixels();

    //     A.loadPixels();
    //     B.loadPixels();

    //     for (let y = 0; y < slitHeight; y++) {
    //         let idx = 4 * (y * stripWidth + x); // x-th column in strip A and B

    //         let c1 = color(
    //         A.pixels[idx],
    //         A.pixels[idx + 1],
    //         A.pixels[idx + 2],
    //         A.pixels[idx + 3]
    //         );
    //         let c2 = color(
    //         B.pixels[idx],
    //         B.pixels[idx + 1],
    //         B.pixels[idx + 2],
    //         B.pixels[idx + 3]
    //         );

    //         let c = lerpColor(c1, c2, blendFactor);

    //         let bi = 4 * y;
    //         blendedColumn.pixels[bi] = red(c);
    //         blendedColumn.pixels[bi + 1] = green(c);
    //         blendedColumn.pixels[bi + 2] = blue(c);
    //         blendedColumn.pixels[bi + 3] = 255;
    //     }

    //     blendedColumn.updatePixels();

    //     image(blendedColumn, (i * stripWidth) + x, 0, 1, slitHeight);
    //     }
    // }

    // // Draw slitscan visualization
    // for (let i = 0; i < strips.length; i++) {
    //     let alpha = map(i, 0, strips.length - 1, 50, 255); // fade older strips
    //     tint(255, alpha); // apply alpha to the image
    //     image(strips[i], i * stripWidth, 0, stripWidth, height);
    // }
    // noTint(); // reset for other drawings

    for (let i = 0; i < strips.length; i++) {
        image(strips[i], i * stripWidth, 0, stripWidth, height);
    }
    

    
}