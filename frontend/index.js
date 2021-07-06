document.getElementById("submit").addEventListener("click", function (e) {
  e.preventDefault();
  image_el = document.getElementById("image");

  if (image_el.files.length > 0) {
    if (!image_el.files[0].type.startsWith("image")) return false;

    image = image_el.files[0];
    const reader = new FileReader();

    reader.onloadend = async () => {
        const base64String = reader.result
        .replace('data:', '')
        .replace(/^.+,/, '');
      post_data = JSON.stringify({
        parameters: {
          image_uri: base64String,
        },
      });
     console.log(post_data);

      res = await fetch("http://localhost:12345/search", {
        method: "POST",
        body: post_data,
      });

      console.log("res", res);
      data = await res.json();
      console.log("data", data);
    };
    reader.readAsDataURL(image);
  }
});
