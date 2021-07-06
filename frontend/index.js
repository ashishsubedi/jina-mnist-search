document.getElementById("submit").addEventListener("click", function (e) {
  e.preventDefault();
  image_el = document.getElementById("image");

  if (image_el.files.length > 0) {
    if (!image_el.files[0].type.startsWith("image")) return false;

    image = image_el.files[0];
    const reader = new FileReader();

    reader.onloadend = async () => {
      const base64String = reader.result
        .replace("data:", "")
        .replace(/^.+,/, "");
      post_data = JSON.stringify({
        parameters: {
          image_uri: base64String,
        },
      });

      res = await fetch("http://localhost:12345/search", {
        method: "POST",
        body: post_data,
        headers: {
          "content-type": "application/json",
        },
      });

      console.log("res", res);
      data = await res.json();
      console.log("data", data);
      image_matches = data.data.docs[0].matches;
      console.log("matches", image_matches);
      
      const id_set = new Set(image_matches.map(el => el.tags.id))

      console.log(id_set);
      console.log("Parsing CSV");
      $("#csv").parse({
        config: {
          delimiter: "auto",
          worker: true,
          fastMode:true,
          chunk: function (rows) {
            // console.log(rows)
            parseCSV(rows,id_set,image_matches);
            
          },
        },
      });
    };
    reader.readAsDataURL(image);
  }
});

const parseCSV = (rows,id_set,image_matches) => {
  internalCounter = 0

  rows.data.forEach((chunk) => {
    chunk.forEach((text) => {
      if (text[0] === 'l') return;
      
      
      textArray = text.trim().split(',')
      // console.log(textArray);
      internalCounter ++;
      if (id_set.has(internalCounter)){
        // This image is a match
        //DISPLAY IMAGE
        createImageFromPixel(textArray.slice(1))
        
      }
      


    });
  });
};

function createImageFromPixel(image_matches){
  // create an offscreen canvas
var canvas=document.createElement("canvas");
var ctx=canvas.getContext("2d");

// size the canvas to your desired image
canvas.width=28;
canvas.height=28;

// get the imageData and pixel array from the canvas
var imgData=ctx.getImageData(0,0,28,28);
var data=imgData.data;
let j = 0
// manipulate some pixel elements
for(var i=0;i<data.length;i+=4){
    data[i]=image_matches[j];   // set every red pixel element to 255
    data[i+1]=image_matches[j];   // set every red pixel element to 255
    data[i+2]=image_matches[j];   // set every red pixel element to 255
    data[i+3]=255; // make this pixel opaque
    j++;
}
console.log("Image",data)

// put the modified pixels back on the canvas
ctx.putImageData(imgData,0,0);

// create a new img object
var image=new Image();

// set the img.src to the canvas data url
image.src=canvas.toDataURL();

// append the new img object to the page
document.body.appendChild(image);
}