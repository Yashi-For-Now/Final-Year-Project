$(document).ready(function () {
  var counter = 0;

  $("#addWifi").click(function () {
    if (counter < 2) {
      counter++;

      var newWifiFields = $(".form-group").eq(0).clone();

      newWifiFields.find("input").val("");

      $("#wifiForm").append(newWifiFields);

      var newWifiField = $(".form-group").eq(1).clone();

      newWifiField.find("input").val("");

      $("#wifiForm").append(newWifiField);
    } else {
      alert("You can only add upto 3 MAC Addresses.");
    }
  });

  document.getElementById("getLocation").addEventListener("click", function () {
    // Get form data
    var form = document.getElementById("wifiForm");
    var formData = new FormData(form);

    // Send form data to the server
    fetch("/submit", {
      method: "POST",
      body: formData,
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error("Failed to get location");
        }
        return response.json();
      })
      .then((data) => {
        // Process the response
        alert("Latitude: " + data.latitude + "\nLongitude: " + data.longitude);
      })
      .catch((error) => {
        // Handle errors
        alert("Failed to get location: " + error.message);
      });
  });

  $("#quit").click(function () {
    $("#wifiForm").trigger("reset");
    counter = 0;
  });
});
