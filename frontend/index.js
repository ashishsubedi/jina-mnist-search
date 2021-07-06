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
          top_k:20
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
      const id_array = image_matches.map(el => el.tags.id)
      const score_obj = {}
      image_matches.forEach(el =>{
        
        score_obj[el.tags.id] = el.tags.score
      })
      console.log(score_obj)

      var result_div = document.getElementById('result-div')
      result_div.innerHTML = ''
      id_array.forEach(id=>{
        const newDiv = document.createElement("div");
        newDiv.setAttribute('id',id)
        result_div.appendChild(newDiv)
      })
      internalCounter = 0
      console.log("Parsing CSV");
      $("#csv").parse({
        config: {
          delimiter: "auto",
          worker: true,
          fastMode:true,
          // chunkSize:8e7,
          complete: function (rows) {
            
            parseCSV(rows,internalCounter,id_set,score_obj);

            
          },
        },
      });
    };
    reader.readAsDataURL(image);
  }
});

const parseCSV = (rows,internalCounter,id_set,score_obj) => {
  
  rows.data.forEach((chunk) => {
    chunk.forEach((text) => {
      if (text[0] === 'l') return;

      
      pixelArray = text.trim().split(',').slice(1)
      // console.log(pixelArray);
      if (id_set.has(internalCounter)){
        // This image is a match
        //DISPLAY IMAGE
        createImageFromPixel(pixelArray,internalCounter,score_obj[internalCounter])
        
      }
      internalCounter ++;
      
      


    });
  });
};


const find_array_from_id = (rows,id) => {
  internalCounter = 0

  rows.data.forEach((chunk) => {
    chunk.forEach((text) => {
      if (text[0] === 'l') return;
      
      
      pixelArray = text.trim().split(',').slice(1)

      if (internalCounter === id) return pixelArray;

      internalCounter ++;
 
    });
  });
  return false;
};

function createImageFromPixel(pixel_data,idx=0,score=0){
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
    data[i]=pixel_data[j];   // set every red pixel element to 255
    data[i+1]=pixel_data[j];   // set every red pixel element to 255
    data[i+2]=pixel_data[j];   // set every red pixel element to 255
    data[i+3]=255; // make this pixel opaque
    j++;
}

// put the modified pixels back on the canvas
ctx.putImageData(imgData,0,0);

// create a new img object
var image=new Image();

// set the img.src to the canvas data url
image.src=canvas.toDataURL();
image.id = idx
var result_div = document.getElementById(idx)

var text = new Text();
text.nodeValue = score

// append the new img object to the page
result_div.appendChild(image);
result_div.appendChild(text);
}